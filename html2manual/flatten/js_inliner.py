"""JavaScript inlining utilities."""
from __future__ import annotations

from pathlib import Path

from bs4 import BeautifulSoup

from .encoding import read_text


def inline_js(html: str, html_path: Path) -> str:
    """Inline external script tags."""

    soup = BeautifulSoup(html, "html.parser")
    for script in soup.find_all("script", src=True):
        src_attr = script.get("src")
        if isinstance(src_attr, list):
            src_attr = src_attr[0] if src_attr else None
        if not isinstance(src_attr, str) or not src_attr:
            continue
        asset_path = (html_path.parent / src_attr).resolve()
        if not asset_path.exists():
            continue
        script_text = read_text(asset_path)
        new_tag = soup.new_tag("script")
        new_tag.string = script_text
        script.replace_with(new_tag)
    return str(soup)


__all__ = ["inline_js"]
