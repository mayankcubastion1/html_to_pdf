# html2manual

html2manual converts a directory of HTML manuals into sectioned PDFs. It flattens
each HTML page by inlining assets, applies overflow fixes, groups pages using a
menu definition (with automatic fallbacks), and renders PDFs via wkhtmltopdf
with an optional Playwright fallback.

## Quickstart

```bash
pip install -e .[dev]
html2manual init  # writes html2manual.yaml
html2manual build --config html2manual.yaml
```

The repository ships with `examples/sample_manual` which demonstrates a simple
menu-driven project.

## Prerequisites

- Python 3.11
- [wkhtmltopdf](https://wkhtmltopdf.org/) available on your PATH (or provide
  `wkhtmltopdf_path` in the config)
- Optional fallback: Playwright (`pip install playwright` and run
  `playwright install chromium`)

## Commands

- `html2manual init` – create a sample configuration file.
- `html2manual flatten` – flatten HTML files into `output_dir/flattened`.
- `html2manual render` – render pre-flattened HTML to PDFs.
- `html2manual build` – full pipeline (parse → flatten → render).
- `html2manual audit` – detect scrollable containers and overflow issues.

## Configuration

Configuration is provided via `html2manual.yaml` or CLI overrides. Key options:

- `input_dir`, `output_dir`
- `menu_file`, `contents_glob`
- Rendering options: `page_size`, `margin_*`, `zoom`
- Inlining toggles: `css_inline`, `js_inline`, `images_inline`
- Overflow control: `overflow_fix_enable`, `overflow_fix_selectors`
- Renderer fallback: `playwright_fallback`
- `chunk_size` to avoid Windows command line limits
- Menu fallback selection via `fallback_strategy`

## Examples

### With a menu

The sample project contains `menu.html` that defines sections using
`display('file','title','/SECTION/...')`. The parser groups the referenced files
into the corresponding sections.

### Without a menu

When `menu.html` is absent the fallback strategy groups files by filename prefix
(e.g. `chapter1_intro.html`, `chapter1_overview.html`). This behaviour can be
configured through the `fallback_strategy` configuration key (`single`, `prefix`,
or `subfolder`).

## Troubleshooting

- **Blank pages** – ensure CSS/JS resources resolve correctly. The flattening
  stage reports missing assets via warnings in structured logs.
- **Scrollbars in output** – run `html2manual audit` to discover problematic
  containers and adjust the `overflow_fix_selectors` configuration.
- **Missing images** – verify paths in the source HTML. The inliner attempts to
  resolve relative paths from each HTML file's directory and `html2manual audit`
  reports unresolved assets.
- **PDF merge issues** – chunked rendering merges using `pypdf`. Confirm the
  intermediate chunk PDFs are produced and not corrupt.

## Sample Configuration

```yaml
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
```

## Development

- `make lint` – run linters (ruff + black).
- `make typecheck` – run mypy.
- `make test` – run pytest.
- `make all` – run the full suite.

The project also provides a Nox configuration and CI workflow that run the same
checks.
