from __future__ import annotations

from pathlib import Path
from html2manual.flatten.css_inliner import embed_css_urls, inline_css
from html2manual.flatten.image_inliner import inline_images
from html2manual.flatten.js_inliner import inline_js
from html2manual.flatten.overflow_fix import apply_overflow_fix
from html2manual.flatten.html_processor import HtmlProcessor


def test_css_inliner_inlines_link_styles(sample_html: Path) -> None:
    html = sample_html.read_text(encoding="utf-8")
    inlined = inline_css(html, sample_html)
    assert "<link" not in inlined
    assert "background: url('data:" in inlined


def test_js_inliner_inlines_external_scripts(sample_html: Path) -> None:
    html = sample_html.read_text(encoding="utf-8")
    inlined = inline_js(html, sample_html)
    assert "script.js" not in inlined
    assert "console.log('hi');" in inlined


def test_image_inliner_replaces_img_sources(sample_html: Path) -> None:
    html = sample_html.read_text(encoding="utf-8")
    inlined = inline_images(html, sample_html)
    assert "src=\"data:" in inlined


def test_background_image_embedding(assets_dir: Path, sample_html: Path) -> None:
    css = (assets_dir / "style.css").read_text(encoding="utf-8")
    embedded = embed_css_urls(css, assets_dir)
    assert "data:image/png;base64" in embedded


def test_overflow_fix_inline_and_style_block(sample_html: Path) -> None:
    html = sample_html.read_text(encoding="utf-8")
    fixed = apply_overflow_fix(html, [".box"])
    assert "overflow:auto" not in fixed
    assert "height: auto" in fixed


def test_overflow_fix_style_tag() -> None:
    html = """
    <html>
    <head><style>.box { overflow: scroll; height: 120px; }</style></head>
    <body></body>
    </html>
    """
    fixed = apply_overflow_fix(html, [".box"])
    assert "overflow: visible" in fixed
    assert "height: auto" in fixed


def test_html_processor_runs_full_pipeline(sample_html: Path) -> None:
    processor = HtmlProcessor()
    result = processor.flatten(sample_html)
    assert "data:image/png" in result.html
    assert "console.log('hi');" in result.html
