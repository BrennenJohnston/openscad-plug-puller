"""The listing's plain-Markdown export and the shot list are what their
pages give today (quick lane, standard library only).

License: PolyForm Noncommercial 1.0.0
"""

from __future__ import annotations

from scripts import listing_description_markdown, shot_list


def test_listing_description_is_current() -> None:
    assert listing_description_markdown.main(["--check"]) == 0, (
        "run python scripts/listing_description_markdown.py")


def test_shot_list_is_current() -> None:
    assert shot_list.main(["--check"]) == 0, "run python scripts/shot_list.py"
