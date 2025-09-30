from __future__ import annotations

from pathlib import Path

import pytest
from pypdf import PdfWriter

from html2manual.render.merge import PdfMerger
from html2manual.render.wkhtml import WkhtmlRenderer


def _write_dummy_pdf(path: Path) -> None:
    writer = PdfWriter()
    writer.add_blank_page(width=10, height=10)
    with path.open("wb") as handle:
        writer.write(handle)


def test_wkhtml_renderer_chunks(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    renderer = WkhtmlRenderer(chunk_size=2)
    renderer.executable = Path("/usr/bin/wkhtmltopdf")
    html_files = []
    for idx in range(5):
        html = tmp_path / f"file{idx}.html"
        html.write_text("<html></html>", encoding="utf-8")
        html_files.append(html)

    def fake_run(args: list[str]) -> None:
        _write_dummy_pdf(Path(args[-1]))

    monkeypatch.setattr(renderer, "_run", fake_run)
    outputs = renderer.render("section", html_files, tmp_path)
    assert len(outputs) == 3
    for pdf in outputs:
        assert pdf.exists()


def test_pdf_merger(tmp_path: Path) -> None:
    pdf1 = tmp_path / "chunk1.pdf"
    pdf2 = tmp_path / "chunk2.pdf"
    _write_dummy_pdf(pdf1)
    _write_dummy_pdf(pdf2)
    merger = PdfMerger()
    merged = merger.merge([pdf1, pdf2], tmp_path / "merged.pdf")
    assert merged.exists()
    assert merged.read_bytes().startswith(b"%PDF")
