from __future__ import annotations

from pathlib import Path

from html2manual.audit import audit_html, audit_manual


def test_audit_flags_scrollable_container(sample_html: Path) -> None:
    issues = audit_html(sample_html)
    assert any("Scrollable container" in issue.issue for issue in issues)


def test_audit_flags_missing_assets(tmp_path: Path) -> None:
    html = tmp_path / "missing.html"
    html.write_text(
        """
        <html>
            <body>
                <img src="missing.png" />
                <a href="missing_page.html">Broken</a>
            </body>
        </html>
        """,
        encoding="utf-8",
    )
    issues = audit_html(html)
    descriptions = {issue.issue for issue in issues}
    assert any(issue.startswith("Missing asset") for issue in descriptions)
    assert any(issue.startswith("Broken link") for issue in descriptions)


def test_audit_manual_collects_all(tmp_path: Path) -> None:
    html1 = tmp_path / "a.html"
    html1.write_text("<html><body><div style='overflow:auto'></div></body></html>", encoding="utf-8")
    html2 = tmp_path / "b.html"
    html2.write_text("<html><body><img src='missing.png'/></body></html>", encoding="utf-8")
    issues = audit_manual(tmp_path, "*.html")
    assert len(issues) >= 2
    assert {issue.file for issue in issues} == {html1, html2}
