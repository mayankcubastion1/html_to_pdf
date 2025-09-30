"""Configuration models and helpers for :mod:`html2manual`."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel, Field, ConfigDict, field_validator

DEFAULT_CONFIG_FILE = Path("html2manual.yaml")


class Html2ManualConfig(BaseModel):
    """Pydantic model describing configuration for html2manual."""

    input_dir: Path = Field(..., description="Directory containing the HTML manual content.")
    output_dir: Path = Field(..., description="Directory to place generated artifacts.")
    menu_file: str = Field("menu.html", description="Menu file used to infer sections.")
    contents_glob: str = Field(
        "Contents/**/*.html", description="Glob pattern for discovering HTML content when no menu is present."
    )
    fallback_strategy: str = Field(
        "prefix",
        description="Fallback grouping strategy when no menu parser succeeds (single, prefix, or subfolder).",
    )
    wkhtmltopdf_path: Optional[Path] = Field(
        None, description="Optional path to wkhtmltopdf binary; falls back to PATH if not provided."
    )
    page_size: str = Field("A4", description="Page size passed to the renderer.")
    margin_top: str = Field("10mm", description="Top margin for PDFs.")
    margin_bottom: str = Field("10mm", description="Bottom margin for PDFs.")
    margin_left: str = Field("10mm", description="Left margin for PDFs.")
    margin_right: str = Field("10mm", description="Right margin for PDFs.")
    zoom: float = Field(1.0, description="Zoom level for wkhtmltopdf or Playwright rendering.")
    overflow_fix_enable: bool = Field(True, description="Enable removing overflow scroll containers during flattening.")
    overflow_fix_selectors: List[str] = Field(
        default_factory=lambda: [".container"],
        description="CSS selectors targeted when removing overflow styles.",
    )
    images_inline: bool = Field(True, description="Inline image assets via base64 data URIs.")
    css_inline: bool = Field(True, description="Inline external CSS stylesheets.")
    js_inline: bool = Field(True, description="Inline external JavaScript files.")
    playwright_fallback: bool = Field(
        True, description="Enable Playwright rendering fallback when wkhtmltopdf is unavailable or fails."
    )
    chunk_size: int = Field(
        50,
        description="Maximum number of HTML files to render per chunk when invoking wkhtmltopdf on Windows to avoid argument limits.",
    )
    verbose: bool = Field(False, description="Enable verbose (debug) logging output.")

    model_config = ConfigDict(arbitrary_types_allowed=True, validate_assignment=True)

    @field_validator("input_dir", "output_dir", mode="before")
    @classmethod
    def _expand_paths(cls, value: Any) -> Path:
        if isinstance(value, Path):
            return value
        return Path(value).expanduser().resolve()

    @field_validator("fallback_strategy")
    @classmethod
    def _validate_strategy(cls, value: str) -> str:
        allowed = {"single", "prefix", "subfolder"}
        if value not in allowed:
            raise ValueError(f"fallback_strategy must be one of {sorted(allowed)}")
        return value


def _load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Configuration file {path} must contain a mapping at the top level.")
    return data


def load_config(config_path: Optional[Path] = None, overrides: Optional[Dict[str, Any]] = None) -> Html2ManualConfig:
    """Load configuration from YAML and optional overrides."""

    path = (config_path or DEFAULT_CONFIG_FILE).expanduser().resolve()
    data: Dict[str, Any] = {}
    data.update(_load_yaml(path))

    overrides = overrides or {}
    # Flatten dotted overrides into nested dicts for convenience.
    for key, value in overrides.items():
        if value is None:
            continue
        data[key] = value

    if "input_dir" not in data or "output_dir" not in data:
        raise ValueError("Configuration must define both 'input_dir' and 'output_dir'.")

    return Html2ManualConfig(**data)


__all__ = ["Html2ManualConfig", "load_config", "DEFAULT_CONFIG_FILE"]
