"""Each printed Open AT document is the print of its current page: the record
``scripts/pdf_records/<document>_pdf.json`` names the SHA-256 of the PDF and
of every file it was printed from, and this lane compares them with the
files as they are. A change to a page, a picture or the builder without a
new print fails here (quick lane, standard library only; no browser needed).

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

import hashlib
import json

import pytest

from scripts import build_open_at_pdf as b
from scripts.generate_outline_sheets import MODEL_VERSION

REBUILD = "run `python scripts/build_open_at_pdf.py --document all` and commit the PDFs and their records"
DOCUMENTS = list(b.DOCUMENTS)


def record(document: str) -> dict:
    b.configure(document)
    assert b.RECORD.exists(), f"{b.RECORD.relative_to(b.ROOT).as_posix()} is missing; {REBUILD}"
    return json.loads(b.RECORD.read_text(encoding="utf-8"))


def test_every_document_has_a_page() -> None:
    for document in DOCUMENTS:
        b.configure(document)
        assert b.SOURCE.exists(), f"{b.SOURCE.relative_to(b.ROOT).as_posix()} is missing"


def test_the_covers_print_the_model_version() -> None:
    assert b.MODEL_VERSION == MODEL_VERSION, "the PDF covers' version is not the model's"


@pytest.mark.parametrize("document", DOCUMENTS)
def test_pdf_is_the_print_of_the_current_page(document: str) -> None:
    rec = record(document)
    assert b.OUT_PDF.exists(), f"{b.OUT_PDF.relative_to(b.ROOT).as_posix()} is missing; {REBUILD}"
    assert hashlib.sha256(b.OUT_PDF.read_bytes()).hexdigest() == rec["pdf_sha256"], f"{b.OUT_PDF.name} changed; {REBUILD}"
    now = b.input_digests()
    stale = sorted(path for path, digest in now.items() if rec["inputs"].get(path) != digest)
    extra = sorted(set(rec["inputs"]) - set(now))
    assert not stale and not extra, f"{document} printed from different files: changed {stale}, gone {extra}; {REBUILD}"


@pytest.mark.parametrize("document", DOCUMENTS)
def test_record_describes_an_accessible_print(document: str) -> None:
    rec = record(document)
    assert rec["pages"] >= 1 and rec["bookmarks"] >= len(b.section_titles()) + 1, rec
    assert rec["pictures"] == len(b.image_alts()), f"{rec['pictures']} figures in the PDF for {len(b.image_alts())} pictures"
    assert rec["links"] >= 1
    assert rec["pdf"] == b.OUT_PDF.relative_to(b.ROOT).as_posix()
