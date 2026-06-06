# For developers

## Setup

```bash
pip install -r requirements-dev.txt
```

This installs `pytest` in addition to the production dependencies.

## Running tests

```bash
pytest -v
```

`tests/test_build.py` contains unit tests for `build.py` logic functions (`validate`, `sort_entries`, `highlight_authors`, `read_version`, `generate_sitemap`).

When modifying `build.py`, verify that all tests continue to pass.

## Local build verification

```bash
python build.py
```

Open `public/index.html` in a browser to verify behavior.

## File structure (tool side)

| File | Purpose |
| --- | --- |
| `build.py` | Static site generator |
| `templates/` | Jinja2 templates |
| `static/` | CSS and JavaScript |
| `data/` | Sample data (used as test fixtures) |
| `tests/` | pytest test suite |
| `pyproject.toml` | Version and pytest configuration |
| `requirements.txt` | Production dependencies (PyYAML, Jinja2) |
| `requirements-dev.txt` | Development dependencies (pytest) |

## Release procedure

1. Update the version in `pyproject.toml`
2. Finalize the `[Unreleased]` section in `CHANGELOG.md` as `[vX.Y.Z] - YYYY-MM-DD`
3. Commit and push:

   ```bash
   git add pyproject.toml CHANGELOG.md
   git commit -m "chore: release X.Y.Z"
   git push origin main
   ```

4. Create and push a tag (this triggers the full Release + zip upload automatically):

   ```bash
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```

> **Writing release notes manually:** If you run `gh release create vX.Y.Z --title "..." --notes "..."` before step 4, the workflow will skip creating the Release and only upload the zip.
