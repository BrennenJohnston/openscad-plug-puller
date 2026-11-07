"""The picture registry, ``Documentation/images.json``, and the pictures.

Every picture under ``Photos/`` has a record and every record a picture; a
picture's name says its subject and view, never a step number or a camera's
name; an imported photograph is the file its record says; every picture a
page of ``Documentation/`` or a guide source shows from ``Photos/`` is
registered for use in a guide, and the page's alt text is the record's
(the Visual Assembly Guide may put "Step N:" in front). With
``RELEASE_CHECK=1`` every used picture must have been reviewed by the owner.
The MakerWorld pictures follow the same naming ban on camera names.

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "Documentation" / "images.json"
PHOTOS = ROOT / "Photos"
NAME = re.compile(r"^(overview|part|stage|finished|render|frame|visual|screen)-[a-z0-9-]+\.(jpg|png)$")
CAMERA = re.compile(r"^(IMG|DSC|PXL|DCIM|\d{8}_\d{6})", re.I)
_IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)\)")
PAGES = sorted((ROOT / "Documentation").glob("*.md")) + sorted((ROOT / "docs" / "guides" / "source").glob("*.md"))


def records():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def test_every_picture_has_a_record_and_every_record_a_picture() -> None:
    on_disk = sorted(p.relative_to(PHOTOS).as_posix() for p in PHOTOS.rglob("*") if p.is_file() and p.suffix in (".jpg", ".png"))
    registered = sorted(f"{r['group']}/{r['name']}" for r in records())
    assert on_disk == registered


@pytest.mark.parametrize("folder", ["Photos", "MakerWorld_Photos"])
def test_no_camera_names(folder: str) -> None:
    bad = [p.name for p in (ROOT / folder).rglob("*") if p.is_file() and CAMERA.match(p.name)]
    assert not bad, f"camera-style file names in {folder}/: {bad}"


def test_names_say_subject_and_view() -> None:
    bad = [r["name"] for r in records() if not NAME.match(r["name"])]
    assert not bad, f"names outside the pattern: {bad}"


def test_review_states_are_known() -> None:
    assert {r["alt_status"] for r in records()} <= {"none", "draft", "reviewed"}


def test_imported_photographs_are_their_records_files() -> None:
    for r in records():
        if r["origin"]["kind"] != "photo":
            continue
        path = PHOTOS / r["group"] / r["name"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == r["origin"]["imported_sha256"], (
            f"{r['name']} is not the imported file; run python scripts/photo_import.py")


def used_pictures():
    for page in PAGES:
        for alt, src in _IMAGE.findall(page.read_text(encoding="utf-8")):
            if "Photos/" in src and "MakerWorld_Photos/" not in src:
                yield page, alt, src.split("Photos/", 1)[1]


def test_every_used_picture_is_registered_with_its_alt_text() -> None:
    by_path = {f"{r['group']}/{r['name']}": r for r in records()}
    for page, alt, rel in used_pictures():
        assert rel in by_path, f"{page.name} shows {rel}, which is not registered"
        rec = by_path[rel]
        assert rec["use"] == "guide", f"{page.name} shows {rel}, registered as {rec['use']}"
        if "Visual_Assembly_Guide" in page.name:
            continue
        assert alt == rec["alt"], f"{page.name}: the alt text of {rel} differs from its record"


@pytest.mark.skipif(os.environ.get("RELEASE_CHECK") != "1", reason="RELEASE_CHECK=1 only, before a release")
def test_every_used_picture_is_reviewed() -> None:
    by_path = {f"{r['group']}/{r['name']}": r for r in records()}
    unreviewed = sorted({rel for _page, _alt, rel in used_pictures() if by_path[rel]["alt_status"] != "reviewed"})
    assert not unreviewed, f"pictures in use whose descriptions the owner has not reviewed: {unreviewed}"
