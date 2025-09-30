"""Parser for Mitsubishi Fuso style menu files."""
from __future__ import annotations

import re
from collections import OrderedDict
from pathlib import Path
from typing import List

from . import SectionMapping

DISPLAY_PATTERN = re.compile(r"display\('([^']+)',\s*'([^']+)',\s*'(/[^']+)'\)")


class MFTBCMenuParser:
    """Parse menu files with ``display('file','title','/SECTION/...')`` entries."""

    name = "mftbc"

    def parse(self, menu_path: Path, contents_dir: Path) -> SectionMapping:
        text = menu_path.read_text(encoding="utf-8", errors="ignore")
        matches = DISPLAY_PATTERN.findall(text)
        sections: "OrderedDict[str, List[Path]]" = OrderedDict()
        for file_name, _title, section_path in matches:
            section_key = section_path.strip("/").split("/")[0]
            sections.setdefault(section_key, [])
            resolved = (contents_dir / file_name).resolve()
            if resolved not in sections[section_key]:
                sections[section_key].append(resolved)
        return dict(sections)


__all__ = ["MFTBCMenuParser", "DISPLAY_PATTERN"]
