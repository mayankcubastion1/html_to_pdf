"""Robust HTML text decoding helpers."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

from charset_normalizer import from_path

FALLBACK_ENCODINGS: Iterable[str] = ("utf-8", "cp932", "shift_jis", "euc_jp", "iso-8859-1")


def read_text(path: Path) -> str:
    """Read text from *path* trying multiple encodings."""

    try:
        detection = from_path(path)
        best = detection.best()
        if best:
            return str(best)
    except Exception:
        pass

    for encoding in FALLBACK_ENCODINGS:
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="ignore")


__all__ = ["read_text", "FALLBACK_ENCODINGS"]
