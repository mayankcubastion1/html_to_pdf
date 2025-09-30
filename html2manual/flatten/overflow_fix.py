"""Remove scrollable containers and fixed heights."""
from __future__ import annotations

import re
from typing import List

from bs4 import BeautifulSoup

INLINE_OVERFLOW_PATTERN = re.compile(r"overflow(-[xy])?\s*:\s*(auto|scroll)", re.IGNORECASE)
HEIGHT_PATTERN = re.compile(r"height\s*:\s*\d+px", re.IGNORECASE)


def _rewrite_inline_style(style_value: str) -> str:
    updated = INLINE_OVERFLOW_PATTERN.sub(lambda m: f"overflow{m.group(1) or ''}: visible", style_value)
    updated = HEIGHT_PATTERN.sub("height: auto", updated)
    return updated


def _rewrite_style_block(css_text: str, selectors: List[str]) -> str:
    css_text = INLINE_OVERFLOW_PATTERN.sub(lambda m: f"overflow{m.group(1) or ''}: visible", css_text)
    for selector in selectors:
        pattern = re.compile(rf"({re.escape(selector)}[^{{]*{{[^}}]*?)height\s*:\s*\d+px", re.IGNORECASE | re.DOTALL)
        css_text = pattern.sub(lambda m: m.group(1) + "height: auto", css_text)
    return css_text


def apply_overflow_fix(html: str, selectors: List[str]) -> str:
    """Apply overflow fixes to inline and embedded styles."""

    soup = BeautifulSoup(html, "html.parser")
    for element in soup.find_all(style=True):
        original = element.get("style")
        if isinstance(original, list):
            original = " ".join(original)
        if not isinstance(original, str) or not original:
            continue
        element["style"] = _rewrite_inline_style(original)

    for style in soup.find_all("style"):
        if style.string is not None:
            style.string = _rewrite_style_block(str(style.string), selectors)

    return str(soup)


__all__ = ["apply_overflow_fix"]
