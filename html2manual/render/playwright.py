"""Playwright based rendering fallback."""
from __future__ import annotations

from pathlib import Path
from typing import List, Sequence


class PlaywrightRenderer:
    """Render HTML files to PDF using Playwright's headless Chromium."""

    def __init__(
        self,
        *,
        page_size: str = "A4",
        margin_top: str = "10mm",
        margin_bottom: str = "10mm",
        margin_left: str = "10mm",
        margin_right: str = "10mm",
        zoom: float = 1.0,
    ) -> None:
        self.page_size = page_size
        self.margin_top = margin_top
        self.margin_bottom = margin_bottom
        self.margin_left = margin_left
        self.margin_right = margin_right
        self.zoom = zoom

    def render(self, section_name: str, html_files: Sequence[Path], output_dir: Path) -> List[Path]:
        from playwright.sync_api import sync_playwright  # type: ignore

        output_dir.mkdir(parents=True, exist_ok=True)
        outputs: List[Path] = []
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context()
            for index, html_file in enumerate(html_files, start=1):
                page = context.new_page()
                page.goto(html_file.as_uri(), wait_until="networkidle")
                page.emulate_media(media="print")
                output_file = output_dir / f"{section_name}_{index:02d}.pdf"
                page.pdf(
                    path=str(output_file),
                    format=self.page_size,
                    print_background=True,
                    margin={
                        "top": self.margin_top,
                        "bottom": self.margin_bottom,
                        "left": self.margin_left,
                        "right": self.margin_right,
                    },
                    scale=self.zoom,
                )
                outputs.append(output_file)
                page.close()
            context.close()
            browser.close()
        return outputs


__all__ = ["PlaywrightRenderer"]
