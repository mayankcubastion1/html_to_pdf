"""Image inlining utilities."""
from __future__ import annotations

import base64
import mimetypes
from pathlib import Path
from typing import Optional

from bs4 import BeautifulSoup

from .css_inliner import embed_css_urls


def _as_string(value: object) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, (list, tuple)):
        for entry in value:
            if entry:
                return str(entry)
        return None
    return str(value)


def _encode_image(path: Path) -> Optional[str]:
    if not path.exists():
        return None
    mime, _ = mimetypes.guess_type(path)
    if mime is None:
        mime = "application/octet-stream"
    data = path.read_bytes()
    encoded = base64.b64encode(data).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def inline_images(html: str, html_path: Path) -> str:
    """Inline image tags and inline-style backgrounds."""

    soup = BeautifulSoup(html, "html.parser")
    for img in soup.find_all("img"):
        src = _as_string(img.get("src"))
        if not src or src.startswith("data:"):
            continue
        asset_path = (html_path.parent / src).resolve()
        data_uri = _encode_image(asset_path)
        if data_uri:
            img["src"] = data_uri

    for tag in soup.find_all(style=True):
        style_value = _as_string(tag.get("style"))
        if style_value:
            tag["style"] = embed_css_urls(style_value, html_path.parent)

    return str(soup)


__all__ = ["inline_images"]
