from __future__ import annotations

from pathlib import Path
import pytest


@pytest.fixture()
def assets_dir(tmp_path: Path) -> Path:
    assets = tmp_path / "assets"
    assets.mkdir()
    return assets


@pytest.fixture()
def sample_html(tmp_path: Path, assets_dir: Path) -> Path:
    css = assets_dir / "style.css"
    css.write_text(".box { background: url('image.png'); }", encoding="utf-8")
    js = assets_dir / "script.js"
    js.write_text("console.log('hi');", encoding="utf-8")
    img = assets_dir / "image.png"
    img.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 10)
    html = tmp_path / "page.html"
    html.write_text(
        """
        <html>
        <head>
            <link rel="stylesheet" href="assets/style.css">
        </head>
        <body>
            <div class="box" style="overflow:auto;height:100px;background:url('assets/image.png');">
                <img src="assets/image.png" />
            </div>
            <script src="assets/script.js"></script>
        </body>
        </html>
        """,
        encoding="utf-8",
    )
    return html
