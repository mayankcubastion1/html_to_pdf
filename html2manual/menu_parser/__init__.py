"""Menu parsing plugins for html2manual."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Protocol, cast

from importlib import metadata
from importlib.metadata import EntryPoint

SectionMapping = Dict[str, List[Path]]


class MenuParser(Protocol):
    """Protocol describing a menu parser plugin."""

    name: str

    def parse(self, menu_path: Path, contents_dir: Path) -> SectionMapping:
        """Parse the provided menu file and return a mapping of sections to HTML paths."""


def _load_menu_entry_points() -> Iterable[EntryPoint]:
    try:
        return metadata.entry_points(group="html2manual.menu_parsers")
    except TypeError:  # pragma: no cover - older importlib.metadata versions
        entries = metadata.entry_points()
        if hasattr(entries, "get"):
            legacy_raw: object = entries.get("html2manual.menu_parsers", [])
            legacy: Iterable[EntryPoint] = cast(Iterable[EntryPoint], legacy_raw)
            return legacy
        return ()


def iter_entry_point_parsers() -> Iterable[MenuParser]:
    """Yield menu parser plugins exposed via entry points."""

    for entry_point in _load_menu_entry_points():
        loaded = entry_point.load()
        if isinstance(loaded, type):
            parser: MenuParser = loaded()  # type: ignore[call-arg]
        else:
            parser = loaded  # type: ignore[assignment]
        yield parser


__all__ = ["MenuParser", "SectionMapping", "iter_entry_point_parsers"]
