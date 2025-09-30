"""CSS inlining helpers."""
from __future__ import annotations

import base64
import mimetypes
import re
from pathlib import Path
from typing import Optional

from bs4 import BeautifulSoup

from .encoding import read_text

URL_PATTERN = re.compile(r"url\((?P<quote>['\"]?)(?!data:)(?P<path>[^)\"']+)(?P=quote)\)")


def _as_string(value: object) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, (list, tuple)):
        for entry in value:
            if entry:
                return str(entry)
        return None
    return str(value)


def _encode_asset(path: Path) -> Optional[str]:
    if not path.exists():
        return None
    mime, _ = mimetypes.guess_type(path)
    if mime is None:
        mime = "application/octet-stream"
    data = path.read_bytes()
    encoded = base64.b64encode(data).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def _resolve_asset(base_dir: Path, asset_ref: str) -> Optional[Path]:
    if re.match(r"^[a-zA-Z]+://", asset_ref):
        return None
    candidate = Path(asset_ref)
    if not candidate.is_absolute():
        candidate = (base_dir / asset_ref).resolve()
    if candidate.exists():
        return candidate
    return None


def embed_css_urls(css_text: str, base_dir: Path) -> str:
    """Rewrite ``url(...)`` references to inline data URIs where possible."""

    def repl(match: re.Match[str]) -> str:
        asset_ref = match.group("path").strip()
        asset_path = _resolve_asset(base_dir, asset_ref)
        if not asset_path:
            return match.group(0)
        data_uri = _encode_asset(asset_path)
        if not data_uri:
            return match.group(0)
        return f"url('{data_uri}')"

    return URL_PATTERN.sub(repl, css_text)


def inline_css(html: str, html_path: Path) -> str:
    """Inline external stylesheet links into the HTML document."""

    soup = BeautifulSoup(html, "html.parser")
    for link in soup.find_all("link", rel=lambda value: value and "stylesheet" in value):
        href = _as_string(link.get("href"))
        if not href:
            continue
        asset_path = _resolve_asset(html_path.parent, href)
        if not asset_path:
            continue
        css_text = read_text(asset_path)
        css_text = embed_css_urls(css_text, asset_path.parent)
        style_tag = soup.new_tag("style")
        style_tag.string = css_text
        link.replace_with(style_tag)

    for style in soup.find_all("style"):
        if style.string is not None:
            style.string = embed_css_urls(str(style.string), html_path.parent)

    return str(soup)


__all__ = ["inline_css", "embed_css_urls"]
