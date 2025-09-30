"""PDF merging utilities."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

from pypdf import PdfReader, PdfWriter


class PdfMerger:
    """Merge multiple PDF chunks into a single file."""

    def merge(self, pdf_paths: Iterable[Path], output_path: Path) -> Path:
        writer = PdfWriter()
        for pdf in pdf_paths:
            reader = PdfReader(str(pdf))
            for page in reader.pages:
                writer.add_page(page)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("wb") as handle:
            writer.write(handle)
        return output_path


__all__ = ["PdfMerger"]
