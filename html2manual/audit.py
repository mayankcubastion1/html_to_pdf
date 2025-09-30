"""Manual content auditing utilities."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List

from bs4 import BeautifulSoup

from .flatten.encoding import read_text

SCROLL_PATTERN = re.compile(r"overflow(?:-[xy])?\s*:\s*(auto|scroll)", re.IGNORECASE)
EXTERNAL_PROTOCOLS = ("http://", "https://", "mailto:", "tel:")


@dataclass(slots=True)
class AuditIssue:
    """Represents a potential problem discovered during an audit."""

    file: Path
    issue: str
    suggestion: str


def _is_external(reference: str) -> bool:
    return reference.startswith(EXTERNAL_PROTOCOLS) or reference.startswith("#") or reference.startswith("data:")


def _resolve_reference(html_path: Path, reference: str) -> Path:
    return (html_path.parent / reference).resolve()


def audit_html(path: Path) -> List[AuditIssue]:
    """Audit a single HTML file for scrollable containers and missing assets."""

    html = read_text(path)
    soup = BeautifulSoup(html, "html.parser")
    issues: List[AuditIssue] = []

    for element in soup.find_all(style=True):
        style_attr = element.get("style")
        if isinstance(style_attr, list):
            style_attr = " ".join(style_attr)
        if isinstance(style_attr, str) and SCROLL_PATTERN.search(style_attr):
            issues.append(
                AuditIssue(
                    file=path,
                    issue="Scrollable container detected",
                    suggestion="Enable overflow_fix or adjust CSS to use height:auto and overflow:visible.",
                )
            )

    for style_tag in soup.find_all("style"):
        content = style_tag.string
        if content and SCROLL_PATTERN.search(str(content)):
            issues.append(
                AuditIssue(
                    file=path,
                    issue="Stylesheet defines overflow:auto/scroll",
                    suggestion="Update stylesheet or include selector in overflow_fix_selectors.",
                )
            )

    for tag_name, attribute in ("img", "src"), ("script", "src"), ("link", "href"):
        for tag in soup.find_all(tag_name):
            value = tag.get(attribute)
            if isinstance(value, list):
                value = value[0] if value else None
            if not isinstance(value, str) or not value or _is_external(value):
                continue
            if tag_name == "link":
                rel = tag.get("rel")
                rel_values = {entry.lower() for entry in rel} if isinstance(rel, list) else {str(rel).lower()} if rel else set()
                if rel_values and "stylesheet" not in rel_values:
                    continue
            asset_path = _resolve_reference(path, value)
            if not asset_path.exists():
                issues.append(
                    AuditIssue(
                        file=path,
                        issue=f"Missing asset: {value}",
                        suggestion="Ensure the file exists relative to the HTML document or adjust the reference.",
                    )
                )

    for anchor in soup.find_all("a", href=True):
        href = anchor.get("href")
        if isinstance(href, list):
            href = href[0] if href else None
        if not isinstance(href, str) or not href or _is_external(href):
            continue
        target = _resolve_reference(path, href)
        if target.suffix.lower() in {".html", ".htm"} and not target.exists():
            issues.append(
                AuditIssue(
                    file=path,
                    issue=f"Broken link: {href}",
                    suggestion="Update the anchor href to a valid document or remove the link.",
                )
            )

    return issues


def audit_manual(input_dir: Path, pattern: str) -> List[AuditIssue]:
    """Audit all HTML files matching ``pattern`` relative to ``input_dir``."""

    issues: List[AuditIssue] = []
    for html_file in sorted(input_dir.glob(pattern)):
        issues.extend(audit_html(html_file))
    return issues


__all__ = ["AuditIssue", "audit_html", "audit_manual"]
