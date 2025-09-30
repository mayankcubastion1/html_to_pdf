"""Rendering backends for html2manual."""

from .wkhtml import WkhtmlRenderer
from .playwright import PlaywrightRenderer
from .merge import PdfMerger

__all__ = ["WkhtmlRenderer", "PlaywrightRenderer", "PdfMerger"]
