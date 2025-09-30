"""Top level package for html2manual."""

from .config import Html2ManualConfig, load_config
from .pipeline import build_manuals

__all__ = [
    "Html2ManualConfig",
    "load_config",
    "build_manuals",
]
