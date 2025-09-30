"""Command line interface for html2manual."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

import typer
from rich.console import Console
from rich.table import Table

from .audit import AuditIssue, audit_manual
from .config import Html2ManualConfig, load_config
from .logging_setup import configure_logging
from .pipeline import build_manuals, flatten_sections, parse_sections, render_sections

app = typer.Typer(help="Generate manuals from HTML content.")
console = Console()

SAMPLE_CONFIG = """# html2manual configuration
input_dir: examples/sample_manual
output_dir: build
menu_file: menu.html
contents_glob: Contents/**/*.html
page_size: A4
margin_top: 10mm
margin_bottom: 10mm
margin_left: 10mm
margin_right: 10mm
zoom: 1.0
overflow_fix_enable: true
overflow_fix_selectors:
  - .container
images_inline: true
css_inline: true
js_inline: true
playwright_fallback: true
chunk_size: 25
fallback_strategy: prefix
"""


def _load_runtime_config(
    config_path: Optional[Path],
    input_dir: Optional[Path],
    output_dir: Optional[Path],
    verbose: bool,
) -> Html2ManualConfig:
    overrides: Dict[str, Path | str] = {}
    if input_dir:
        overrides["input_dir"] = input_dir
    if output_dir:
        overrides["output_dir"] = output_dir
    config = load_config(config_path, overrides)
    log_level = "DEBUG" if verbose or config.verbose else "INFO"
    configure_logging(log_level)
    return config


@app.command()
def init(config_path: Path = typer.Option(Path("html2manual.yaml"), help="Path to write configuration.")) -> None:
    """Write a sample configuration file."""

    if config_path.exists():
        typer.echo(f"Config file {config_path} already exists.")
        raise typer.Exit(code=1)
    config_path.write_text(SAMPLE_CONFIG, encoding="utf-8")
    typer.echo(f"Sample configuration written to {config_path}")


@app.command()
def flatten(
    config: Optional[Path] = typer.Option(None, help="Path to configuration file."),
    input_dir: Optional[Path] = typer.Option(None, help="Override input directory."),
    output_dir: Optional[Path] = typer.Option(None, help="Override output directory."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging."),
) -> None:
    cfg = _load_runtime_config(config, input_dir, output_dir, verbose)
    sections = parse_sections(cfg)
    flattened = flatten_sections(cfg, sections)
    typer.echo(f"Flattened {sum(len(v) for v in flattened.values())} files into {cfg.output_dir / 'flattened'}")


@app.command()
def render(
    config: Optional[Path] = typer.Option(None, help="Path to configuration file."),
    input_dir: Optional[Path] = typer.Option(None, help="Override input directory."),
    output_dir: Optional[Path] = typer.Option(None, help="Override output directory."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging."),
) -> None:
    cfg = _load_runtime_config(config, input_dir, output_dir, verbose)
    flattened_root = cfg.output_dir / "flattened"
    if not flattened_root.exists():
        typer.echo("Flattened directory not found. Run 'html2manual flatten' first.")
        raise typer.Exit(code=1)
    flattened: Dict[str, List[Path]] = {}
    for section_dir in flattened_root.iterdir():
        if section_dir.is_dir():
            flattened[section_dir.name] = sorted(section_dir.glob("*.html"))
    manuals = render_sections(cfg, flattened)
    typer.echo(f"Rendered {len(manuals)} manuals to {cfg.output_dir / 'Manuals'}")


@app.command()
def build(
    config: Optional[Path] = typer.Option(None, help="Path to configuration file."),
    input_dir: Optional[Path] = typer.Option(None, help="Override input directory."),
    output_dir: Optional[Path] = typer.Option(None, help="Override output directory."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging."),
) -> None:
    cfg = _load_runtime_config(config, input_dir, output_dir, verbose)
    manuals = build_manuals(cfg)
    typer.echo(json.dumps({k: str(v) for k, v in manuals.items()}, indent=2))


@app.command()
def audit(
    config: Optional[Path] = typer.Option(None, help="Path to configuration file."),
    input_dir: Optional[Path] = typer.Option(None, help="Override input directory."),
    output_dir: Optional[Path] = typer.Option(None, help="Override output directory."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging."),
) -> None:
    cfg = _load_runtime_config(config, input_dir, output_dir, verbose)
    issues: List[AuditIssue] = audit_manual(cfg.input_dir, cfg.contents_glob)
    if not issues:
        console.print("[green]No audit issues detected.[/green]")
        return

    table = Table(title="Audit Issues")
    table.add_column("File", style="cyan")
    table.add_column("Issue", style="magenta")
    table.add_column("Suggestion", style="green")

    for issue in issues:
        relative = issue.file.relative_to(cfg.input_dir) if issue.file.is_relative_to(cfg.input_dir) else issue.file
        table.add_row(str(relative), issue.issue, issue.suggestion)

    console.print(table)
    console.print(f"[yellow]{len(issues)} issue(s) detected across {len({i.file for i in issues})} file(s).[/yellow]")


if __name__ == "__main__":
    app()
