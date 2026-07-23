"""OpenSCAD CLI runner for plug-puller v5 STL validation.

Wraps the ``openscad`` command-line interface so pytest can render the v5
parametric model with arbitrary ``-D`` overrides, time-limit it, and capture
stdout/stderr for diagnostics.

Adapted from ``braille-stl-generator-openscad/tests/openscad_runner.py`` with
the CloudCompare hooks removed — the plug-puller validation pipeline compares
OpenSCAD output against its own golden fixtures via :mod:`trimesh` only.

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import json
import logging
import os
import platform
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class OpenSCADResult:
    """Result of an OpenSCAD CLI execution."""

    success: bool
    output_path: Optional[Path]
    stdout: str
    stderr: str
    returncode: int
    duration_seconds: float
    command: str


class OpenSCADNotFoundError(Exception):
    """Raised when the OpenSCAD executable cannot be found."""


class OpenSCADRunner:
    """Render OpenSCAD ``.scad`` files to STL with explicit parameters.

    Responsibilities:
      * Locate the ``openscad`` executable (PATH first, then per-platform
        defaults) and verify it runs.
      * Detect / opt-in to the Manifold backend (much faster booleans on
        2024+ nightlies).
      * Build a ``-D key=value`` command line for the model under test.
      * Execute with a watchdog timeout and structured result reporting.
    """

    def __init__(
        self,
        openscad_path: Optional[Path] = None,
        default_timeout_seconds: int = 300,
        use_manifold: Optional[bool] = None,
        enforce_version: Optional[str] = None,
    ) -> None:
        self.openscad_path = openscad_path or self._find_openscad()
        self.default_timeout_seconds = default_timeout_seconds
        self._verify_openscad()
        self.version_string = self.get_version()
        self.use_manifold = (
            use_manifold if use_manifold is not None else self._detect_manifold_support()
        )
        if enforce_version:
            self._enforce_version(enforce_version)

    def _find_openscad(self) -> Path:
        env_path = os.environ.get("OPENSCAD_PATH")
        if env_path:
            p = Path(env_path)
            if p.exists():
                return p

        which = shutil.which("openscad")
        if which:
            return Path(which)

        system = platform.system()
        if system == "Windows":
            candidates = [
                Path(r"C:\Program Files\OpenSCAD (Nightly)\openscad.exe"),
                Path(r"C:\Program Files\OpenSCAD (Nightly)\openscad.com"),
                Path(r"C:\Program Files\OpenSCAD\openscad.exe"),
                Path(r"C:\Program Files (x86)\OpenSCAD\openscad.exe"),
            ]
        elif system == "Darwin":
            candidates = [Path("/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD")]
        elif system == "Linux":
            candidates = [
                Path("/usr/bin/openscad"),
                Path("/usr/local/bin/openscad"),
                Path("/snap/bin/openscad"),
            ]
        else:
            candidates = []

        for p in candidates:
            if p.exists():
                return p

        raise OpenSCADNotFoundError(
            "OpenSCAD executable not found. Set OPENSCAD_PATH or install "
            "OpenSCAD 2026.01.03+ (nightly recommended)."
        )

    def _verify_openscad(self) -> None:
        try:
            result = subprocess.run(
                [str(self.openscad_path), "--version"],
                capture_output=True,
                text=True,
                timeout=15,
            )
        except Exception as exc:  # noqa: BLE001 — surface as our own error
            raise OpenSCADNotFoundError(
                f"OpenSCAD at {self.openscad_path} failed to run: {exc}"
            ) from exc
        version_output = (result.stdout or result.stderr).strip()
        logger.info("Found OpenSCAD: %s", version_output)

    def _detect_manifold_support(self) -> bool:
        try:
            result = subprocess.run(
                [str(self.openscad_path), "--help"],
                capture_output=True,
                text=True,
                timeout=15,
            )
        except Exception:  # noqa: BLE001
            return False
        help_text = result.stdout or result.stderr
        has_manifold = "--backend" in help_text and "Manifold" in help_text
        if has_manifold:
            logger.info("Manifold backend detected — enabling for renders.")
        return has_manifold

    def get_version(self) -> str:
        result = subprocess.run(
            [str(self.openscad_path), "--version"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        return (result.stdout or result.stderr).strip()

    def _enforce_version(self, required_version: str) -> None:
        if required_version not in self.version_string:
            raise OpenSCADNotFoundError(
                "OpenSCAD version mismatch.\n"
                f"  Required: {required_version}\n"
                f"  Found:    {self.version_string}\n"
                "Install the matching nightly to reproduce golden fixtures."
            )
        logger.info("OpenSCAD version check passed: %s", required_version)

    def check_manifold_backend(self, require_manifold: bool = False) -> bool:
        if require_manifold and not self.use_manifold:
            raise OpenSCADNotFoundError(
                "Manifold backend is required but not available in this "
                "OpenSCAD build. Install OpenSCAD 2026.01.03+ nightly."
            )
        return self.use_manifold

    def generate_stl(
        self,
        scad_file: Path,
        output_stl: Path,
        parameters: Optional[Dict[str, Any]] = None,
        timeout_seconds: Optional[int] = None,
    ) -> OpenSCADResult:
        if not scad_file.exists():
            raise FileNotFoundError(f"OpenSCAD file not found: {scad_file}")

        output_stl.parent.mkdir(parents=True, exist_ok=True)
        cmd = self._build_command(scad_file, output_stl, parameters)
        timeout = timeout_seconds or self.default_timeout_seconds

        logger.info("Rendering %s -> %s", scad_file.name, output_stl.name)
        logger.debug("Command: %s", " ".join(cmd))

        start = time.time()
        process: Optional[subprocess.Popen[bytes]] = None
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=scad_file.parent,
            )

            # Drain stdout/stderr continuously on background threads.
            # OpenSCAD's console output (echo diagnostics, warnings) can
            # exceed the OS pipe buffer (~4 KB anonymous pipes on Windows);
            # leaving the pipes unread until exit deadlocks the render — the
            # process blocks on a full pipe while we wait for it to finish.
            # (Bit us when the fit_derived echo block grew past the buffer.)
            import threading

            stdout_chunks: list[bytes] = []
            stderr_chunks: list[bytes] = []

            def _drain(stream, sink: list) -> None:
                for chunk in iter(lambda: stream.read(8192), b""):
                    sink.append(chunk)
                stream.close()

            readers = [
                threading.Thread(
                    target=_drain, args=(process.stdout, stdout_chunks), daemon=True
                ),
                threading.Thread(
                    target=_drain, args=(process.stderr, stderr_chunks), daemon=True
                ),
            ]
            for reader in readers:
                reader.start()

            last_report = start
            while True:
                rc = process.poll()
                if rc is not None:
                    for reader in readers:
                        reader.join(timeout=5)
                    break

                elapsed = time.time() - start
                if elapsed > timeout:
                    logger.error("OpenSCAD timed out after %ds — killing", timeout)
                    self._kill_process_tree(process.pid)
                    return OpenSCADResult(
                        success=False,
                        output_path=None,
                        stdout="",
                        stderr=f"Process timed out after {timeout} seconds",
                        returncode=-1,
                        duration_seconds=elapsed,
                        command=" ".join(cmd),
                    )

                if time.time() - last_report >= 15:
                    logger.info("  ... still rendering (%ds elapsed)", int(elapsed))
                    last_report = time.time()

                time.sleep(0.25)

            duration = time.time() - start
            stdout_data = b"".join(stdout_chunks)
            stderr_data = b"".join(stderr_chunks)
            stdout_str = stdout_data.decode("utf-8", errors="replace") if stdout_data else ""
            stderr_str = stderr_data.decode("utf-8", errors="replace") if stderr_data else ""
            success = process.returncode == 0 and output_stl.exists()

            if not success:
                logger.error("OpenSCAD failed (returncode=%s)", process.returncode)
                if stderr_str:
                    logger.error("stderr: %s", stderr_str)

            return OpenSCADResult(
                success=success,
                output_path=output_stl if success else None,
                stdout=stdout_str,
                stderr=stderr_str,
                returncode=process.returncode,
                duration_seconds=duration,
                command=" ".join(cmd),
            )

        except Exception as exc:  # noqa: BLE001
            duration = time.time() - start
            logger.error("OpenSCAD execution error: %s", exc)
            if process is not None:
                self._kill_process_tree(process.pid)
            return OpenSCADResult(
                success=False,
                output_path=None,
                stdout="",
                stderr=str(exc),
                returncode=-1,
                duration_seconds=duration,
                command=" ".join(cmd),
            )

    def _kill_process_tree(self, pid: int) -> None:
        try:
            if platform.system() == "Windows":
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(pid)],
                    capture_output=True,
                    timeout=10,
                )
            else:
                import signal

                os.killpg(os.getpgid(pid), signal.SIGTERM)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to kill process tree %s: %s", pid, exc)

    def _build_command(
        self,
        scad_file: Path,
        output_stl: Path,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> List[str]:
        cmd: List[str] = [
            str(self.openscad_path),
            "-o",
            str(output_stl),
        ]
        if self.use_manifold:
            cmd.extend(["--backend", "Manifold"])
        if parameters:
            for key, value in parameters.items():
                cmd.extend(["-D", self._format_parameter(key, value)])
        cmd.append(str(scad_file))
        return cmd

    @staticmethod
    def _format_parameter(key: str, value: Any) -> str:
        if isinstance(value, bool):
            return f"{key}={str(value).lower()}"
        if isinstance(value, (int, float)):
            return f"{key}={value}"
        if isinstance(value, str):
            escaped = value.replace('"', '\\"')
            return f'{key}="{escaped}"'
        return f'{key}="{value}"'

    def generate_stl_from_json(
        self,
        scad_file: Path,
        output_stl: Path,
        params_json: Path,
        timeout_seconds: Optional[int] = None,
    ) -> OpenSCADResult:
        with open(params_json, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        parameters = data.get("parameters", data)
        return self.generate_stl(
            scad_file=scad_file,
            output_stl=output_stl,
            parameters=parameters,
            timeout_seconds=timeout_seconds,
        )


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Render Plug Puller v5 OpenSCAD model to STL."
    )
    parser.add_argument("scad_file", type=Path, help="Input .scad file")
    parser.add_argument("output_stl", type=Path, help="Output STL file")
    parser.add_argument("--params-json", type=Path, help="JSON with parameters")
    parser.add_argument("--timeout", type=int, default=300, help="Timeout (s)")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    try:
        runner = OpenSCADRunner()
        logger.info("Using OpenSCAD: %s", runner.get_version())
        if args.params_json:
            result = runner.generate_stl_from_json(
                scad_file=args.scad_file,
                output_stl=args.output_stl,
                params_json=args.params_json,
                timeout_seconds=args.timeout,
            )
        else:
            result = runner.generate_stl(
                scad_file=args.scad_file,
                output_stl=args.output_stl,
                timeout_seconds=args.timeout,
            )

        if result.success:
            logger.info(
                "STL generated in %.1fs -> %s", result.duration_seconds, result.output_path
            )
            return 0
        logger.error("STL generation failed: %s", result.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        logger.error("Error: %s", exc, exc_info=args.verbose)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
