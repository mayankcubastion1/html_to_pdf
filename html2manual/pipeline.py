"""Pipeline orchestration for html2manual."""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Dict, List

import structlog

from .config import Html2ManualConfig
from .flatten.html_processor import HtmlProcessor
from .menu_parser import SectionMapping, iter_entry_point_parsers
from .menu_parser.fallback_contents import FallbackStrategy, fallback_sections
from .menu_parser.mftbc_menu import MFTBCMenuParser
from .render.merge import PdfMerger
from .render.playwright import PlaywrightRenderer
from .render.wkhtml import WkhtmlRenderer

LOGGER = structlog.get_logger(__name__)


def parse_sections(config: Html2ManualConfig) -> SectionMapping:
    menu_path = config.input_dir / config.menu_file
    if menu_path.exists():
        parsers = [MFTBCMenuParser(), *iter_entry_point_parsers()]
        for parser in parsers:
            try:
                sections = parser.parse(menu_path, config.input_dir)
            except Exception as exc:  # pragma: no cover - plugin errors logged
                LOGGER.warning("menu_parser_failed", parser=parser.name, error=str(exc))
                continue
            if sections:
                LOGGER.info("menu_parser_selected", parser=parser.name, sections=len(sections))
                return sections
    LOGGER.info("menu_fallback", strategy=config.fallback_strategy)
    return fallback_sections(
        config.input_dir, config.contents_glob, FallbackStrategy(mode=config.fallback_strategy)
    )


def flatten_sections(config: Html2ManualConfig, sections: SectionMapping) -> Dict[str, List[Path]]:
    processor = HtmlProcessor(
        css_inline=config.css_inline,
        js_inline=config.js_inline,
        images_inline=config.images_inline,
        overflow_fix_enable=config.overflow_fix_enable,
        overflow_selectors=config.overflow_fix_selectors,
    )
    flattened_root = config.output_dir / "flattened"
    flattened_root.mkdir(parents=True, exist_ok=True)
    flattened: Dict[str, List[Path]] = {}
    for section, files in sections.items():
        section_dir = flattened_root / section
        section_dir.mkdir(parents=True, exist_ok=True)
        flattened_paths: List[Path] = []
        for html_file in files:
            if not html_file.exists():
                LOGGER.warning("flatten_missing_file", file=str(html_file))
                continue
            destination = section_dir / html_file.name
            result = processor.flatten_to_file(html_file, destination)
            if result.warnings:
                for warning in result.warnings:
                    LOGGER.warning("flatten_warning", file=str(html_file), warning=warning)
            flattened_paths.append(destination)
        flattened[section] = flattened_paths
    return flattened


def render_sections(config: Html2ManualConfig, flattened: Dict[str, List[Path]]) -> Dict[str, Path]:
    renderer = WkhtmlRenderer(
        executable=config.wkhtmltopdf_path,
        page_size=config.page_size,
        margin_top=config.margin_top,
        margin_bottom=config.margin_bottom,
        margin_left=config.margin_left,
        margin_right=config.margin_right,
        zoom=config.zoom,
        chunk_size=config.chunk_size,
    )
    merger = PdfMerger()
    output_manuals: Dict[str, Path] = {}
    manuals_dir = config.output_dir / "Manuals"
    manuals_dir.mkdir(parents=True, exist_ok=True)

    for section, files in flattened.items():
        LOGGER.info("render_section_start", section=section, files=len(files))
        chunk_pdfs: List[Path]
        try:
            chunk_pdfs = renderer.render(section, files, manuals_dir)
        except (FileNotFoundError, subprocess.CalledProcessError) as exc:
            LOGGER.warning("wkhtml_render_failed", section=section, error=str(exc))
            if not config.playwright_fallback:
                raise
            LOGGER.info("playwright_fallback_start", section=section)
            fallback = PlaywrightRenderer(
                page_size=config.page_size,
                margin_top=config.margin_top,
                margin_bottom=config.margin_bottom,
                margin_left=config.margin_left,
                margin_right=config.margin_right,
                zoom=config.zoom,
            )
            chunk_pdfs = fallback.render(section, files, manuals_dir)
        if len(chunk_pdfs) > 1:
            merged_path = manuals_dir / f"{section}.pdf"
            merger.merge(chunk_pdfs, merged_path)
            output_manuals[section] = merged_path
            for extra in chunk_pdfs:
                extra.unlink(missing_ok=True)
        else:
            output_manuals[section] = chunk_pdfs[0]
        LOGGER.info("render_section_complete", section=section, pdf=str(output_manuals[section]))
    return output_manuals


def build_manuals(config: Html2ManualConfig) -> Dict[str, Path]:
    sections = parse_sections(config)
    flattened = flatten_sections(config, sections)
    manuals = render_sections(config, flattened)
    return manuals


__all__ = ["build_manuals", "parse_sections", "flatten_sections", "render_sections"]
