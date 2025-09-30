"""wkhtmltopdf rendering backend."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import List, Sequence


class WkhtmlRenderer:
    """Render HTML files to PDF using wkhtmltopdf with chunking support."""

    def __init__(
        self,
        *,
        executable: Path | None = None,
        page_size: str = "A4",
        margin_top: str = "10mm",
        margin_bottom: str = "10mm",
        margin_left: str = "10mm",
        margin_right: str = "10mm",
        zoom: float = 1.0,
        chunk_size: int = 50,
    ) -> None:
        self.executable = executable
        self.page_size = page_size
        self.margin_top = margin_top
        self.margin_bottom = margin_bottom
        self.margin_left = margin_left
        self.margin_right = margin_right
        self.zoom = zoom
        self.chunk_size = max(1, chunk_size)

    @property
    def command(self) -> str:
        if self.executable:
            return str(self.executable)
        resolved = shutil.which("wkhtmltopdf")
        if not resolved:
            raise FileNotFoundError("wkhtmltopdf executable not found on PATH")
        return resolved

    def _build_args(self, inputs: Sequence[Path], output: Path) -> List[str]:
        args = [
            self.command,
            "--enable-local-file-access",
            "--print-media-type",
            "--page-size",
            self.page_size,
            "--margin-top",
            self.margin_top,
            "--margin-bottom",
            self.margin_bottom,
            "--margin-left",
            self.margin_left,
            "--margin-right",
            self.margin_right,
            "--zoom",
            str(self.zoom),
        ]
        args.extend(str(path) for path in inputs)
        args.append(str(output))
        return args

    def _run(self, args: Sequence[str]) -> None:
        subprocess.run(args, check=True)

    def _chunk(self, files: Sequence[Path]) -> List[List[Path]]:
        if len(files) <= self.chunk_size:
            return [list(files)]
        chunks: List[List[Path]] = []
        current: List[Path] = []
        for html in files:
            current.append(html)
            if len(current) >= self.chunk_size:
                chunks.append(current)
                current = []
        if current:
            chunks.append(current)
        return chunks

    def render(self, section_name: str, html_files: Sequence[Path], output_dir: Path) -> List[Path]:
        output_dir.mkdir(parents=True, exist_ok=True)
        chunks = self._chunk(html_files)
        outputs: List[Path] = []
        for index, chunk in enumerate(chunks, start=1):
            suffix = f"_{index:02d}" if len(chunks) > 1 else ""
            output_file = output_dir / f"{section_name}{suffix}.pdf"
            args = self._build_args(chunk, output_file)
            self._run(args)
            outputs.append(output_file)
        return outputs


__all__ = ["WkhtmlRenderer"]
