"""Fallback strategies when no explicit menu is provided."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List

from . import SectionMapping


@dataclass
class FallbackStrategy:
    """Configuration for fallback grouping."""

    mode: str = "single"

    def group(self, files: Iterable[Path]) -> SectionMapping:
        files = list(sorted(files))
        if self.mode == "single":
            return {"manual": files}
        if self.mode == "prefix":
            grouped: Dict[str, List[Path]] = defaultdict(list)
            for file in files:
                prefix = file.stem.split("_")[0]
                grouped[prefix].append(file)
            return dict(grouped)
        if self.mode == "subfolder":
            grouped = defaultdict(list)
            for file in files:
                key = file.parent.name or "root"
                grouped[key].append(file)
            return dict(grouped)
        raise ValueError(f"Unknown fallback strategy: {self.mode}")


def discover_html_files(input_dir: Path, pattern: str) -> List[Path]:
    return sorted(input_dir.glob(pattern))


def fallback_sections(input_dir: Path, pattern: str, strategy: FallbackStrategy) -> SectionMapping:
    files = discover_html_files(input_dir, pattern)
    return strategy.group(files)


__all__ = ["FallbackStrategy", "fallback_sections", "discover_html_files"]
