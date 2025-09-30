from __future__ import annotations

from pathlib import Path

from html2manual.menu_parser.fallback_contents import FallbackStrategy, fallback_sections
from html2manual.menu_parser.mftbc_menu import MFTBCMenuParser


def test_menu_parser_parses_display_entries(tmp_path: Path) -> None:
    menu = tmp_path / "menu.html"
    contents = tmp_path / "Contents"
    contents.mkdir()
    (contents / "page1.html").write_text("<html></html>", encoding="utf-8")
    (contents / "page2.html").write_text("<html></html>", encoding="utf-8")
    menu.write_text(
        "display('Contents/page1.html','Page 1','/SECTION1/Intro');\n"
        "display('Contents/page2.html','Page 2','/SECTION1/Intro');",
        encoding="utf-8",
    )
    parser = MFTBCMenuParser()
    sections = parser.parse(menu, tmp_path)
    assert list(sections.keys()) == ["SECTION1"]
    assert [path.name for path in sections["SECTION1"]] == ["page1.html", "page2.html"]


def test_fallback_prefix_strategy(tmp_path: Path) -> None:
    contents = tmp_path / "docs"
    contents.mkdir()
    for name in ["alpha_intro.html", "alpha_details.html", "beta_start.html"]:
        (contents / name).write_text("<html></html>", encoding="utf-8")
    sections = fallback_sections(contents, "*.html", FallbackStrategy(mode="prefix"))
    assert set(sections.keys()) == {"alpha", "beta"}
    assert [path.name for path in sections["alpha"]] == ["alpha_details.html", "alpha_intro.html"]
