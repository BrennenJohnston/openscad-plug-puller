"""Quick-lane tests for the helpers in ``tests/mesh_comparison.py`` that the
release library and fixture scripts use to keep an unchanged STL as
committed: ``binary_stl_facets`` and ``same_shape``.

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import json
import struct
from pathlib import Path

import trimesh

from tests.mesh_comparison import MeshComparator, binary_stl_facets, drop_collapsed_triangles, same_shape

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _box(size: float = 10.123456789, shift: float = 0.0) -> trimesh.Trimesh:
    box = trimesh.creation.box(extents=(size, size * 0.7, size * 0.3))
    box.apply_translation((shift, 0.0, 0.0))
    return box


def test_binary_stl_facets(tmp_path: Path) -> None:
    binary, text = tmp_path / "box_binary.stl", tmp_path / "box_text.stl"
    _box().export(binary, file_type="stl")
    _box().export(text, file_type="stl_ascii")
    assert binary_stl_facets(binary) == 12
    assert binary_stl_facets(text) is None


def test_same_shape_text_beside_binary(tmp_path: Path) -> None:
    binary, text = tmp_path / "box_binary.stl", tmp_path / "box_text.stl"
    _box().export(binary, file_type="stl")
    _box().export(text, file_type="stl_ascii")
    assert same_shape(text, binary)
    assert same_shape(_box(), _box())


def test_same_shape_sees_a_change() -> None:
    assert not same_shape(_box(), _box(size=10.133456789)), "a 0.01 mm larger box is a different shape"
    assert not same_shape(_box(), _box(shift=0.001)), "a box moved by 0.001 mm is a different shape"


def test_drop_collapsed_triangles(tmp_path: Path) -> None:
    """A triangle whose corners coincide, as binary STL's 32-bit coordinates
    leave behind where an edge was shorter than they can hold, opens the
    mesh; dropping it closes the mesh and leaves every other triangle."""
    path = tmp_path / "box_with_collapsed_triangle.stl"
    box = _box()
    box.export(path, file_type="stl")
    a, b = box.vertices[0].tolist(), box.vertices[1].tolist()
    collapsed = struct.pack("<12fH", 0.0, 0.0, 0.0, *a, *a, *b, 0)
    data = path.read_bytes()
    count = int.from_bytes(data[80:84], "little")
    path.write_bytes(data[:80] + (count + 1).to_bytes(4, "little") + data[84:] + collapsed)
    assert binary_stl_facets(path) == 13
    assert not trimesh.load(path).is_watertight
    assert drop_collapsed_triangles(path) == 1
    assert path.read_bytes() == data, "the header and the other triangles stay byte for byte"
    assert trimesh.load(path).is_watertight
    assert drop_collapsed_triangles(path) == 0


def test_comparator_catches_a_drift_like_the_ignored_plug_numbers(tmp_path: Path) -> None:
    """A fixture once rendered 0.77 % smaller in volume while its plug numbers
    were being ignored, and the comparison still passed it. The committed
    tolerances must fail that drift. A flat box made 0.77 % taller gives the
    same volume drift while its area (0.17 %) and its size (0.04 mm) change
    too little for the old limits."""
    config = json.loads((PROJECT_ROOT / "tests" / "compare_config.json").read_text(encoding="utf-8"))
    reference, drifted = tmp_path / "reference.stl", tmp_path / "drifted.stl"
    trimesh.creation.box(extents=(40.0, 30.0, 5.0)).export(reference)
    trimesh.creation.box(extents=(40.0, 30.0, 5.0 * 1.0077)).export(drifted)
    assert not MeshComparator(config).compare(reference, drifted).passed, (
        "a 0.77 % volume drift must fail the fixture comparison")


def test_same_shape_needs_watertight_meshes() -> None:
    open_box = _box()
    open_box.update_faces([i != 0 for i in range(len(open_box.faces))])
    assert not open_box.is_watertight
    assert not same_shape(open_box, _box())
