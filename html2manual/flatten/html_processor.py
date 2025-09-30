"""High level HTML flattening orchestration."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

from . import css_inliner, image_inliner, js_inliner
from .encoding import read_text
from .overflow_fix import apply_overflow_fix


@dataclass
class FlattenResult:
    html: str
    warnings: List[str]


class HtmlProcessor:
    """Run a configurable flattening pipeline on HTML files."""

    def __init__(
        self,
        *,
        css_inline: bool = True,
        js_inline: bool = True,
        images_inline: bool = True,
        overflow_fix_enable: bool = True,
        overflow_selectors: Iterable[str] | None = None,
    ) -> None:
        self.css_inline = css_inline
        self.js_inline = js_inline
        self.images_inline = images_inline
        self.overflow_fix_enable = overflow_fix_enable
        self.overflow_selectors = list(overflow_selectors or [".container"])

    def flatten(self, path: Path) -> FlattenResult:
        html = read_text(path)
        warnings: List[str] = []

        if self.css_inline:
            html = css_inliner.inline_css(html, path)
        if self.js_inline:
            html = js_inliner.inline_js(html, path)
        if self.images_inline:
            html = image_inliner.inline_images(html, path)
        if self.overflow_fix_enable:
            html = apply_overflow_fix(html, self.overflow_selectors)

        return FlattenResult(html=html, warnings=warnings)

    def flatten_to_file(self, path: Path, destination: Path) -> FlattenResult:
        result = self.flatten(path)
        destination.write_text(result.html, encoding="utf-8")
        return result


__all__ = ["HtmlProcessor", "FlattenResult"]
