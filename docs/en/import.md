# Importing existing data

You can convert publication data from BibTeX, Hayagriva, RIS, or CSL-JSON format into `publications.yaml`.

## Setup

```bash
pip install -r requirements-tools.txt
```

This installs `bibtexparser` in addition to the production dependencies (required for BibTeX only; RIS, Hayagriva, and CSL-JSON have no extra dependencies).

## Supported formats

| `--format` | Format | Extra dependency |
| --- | --- | --- |
| `bibtex` | BibTeX (`.bib`) | `bibtexparser` (in `requirements-tools.txt`) |
| `hayagriva` | Hayagriva YAML (`.yml`) | none |
| `ris` | RIS (`.ris`) — Zotero, Mendeley, EndNote, etc. | none |
| `csl-json` | CSL-JSON (`.json`) — Zotero, Pandoc, etc. | none |

## Usage

```bash
# Convert from BibTeX and print to stdout
python tools/import.py --format bibtex refs.bib

# Write to a file
python tools/import.py --format bibtex refs.bib --output data/publications.yaml

# Append to an existing publications.yaml (duplicate IDs are skipped)
python tools/import.py --format bibtex refs.bib --append data/publications.yaml

# Convert from Hayagriva
python tools/import.py --format hayagriva refs.yml --append data/publications.yaml

# Convert from RIS (exported from Zotero, Mendeley, etc.)
python tools/import.py --format ris refs.ris --append data/publications.yaml

# Convert from CSL-JSON (exported from Zotero, Pandoc, etc.)
python tools/import.py --format csl-json refs.json --append data/publications.yaml
```

Fields that cannot be mapped are recorded in `note` as `[import: field=value]`.
Issues such as author name format ("Last, First" style) or missing month information are printed to stderr as warnings.

## Adding a custom importer

You can add your own importers for custom formats. Just create a file in `tools/importers/` with the structure below — `import.py` detects it automatically. **No changes to `import.py` itself are needed.**

```python
# tools/importers/my_format.py
from . import BaseImporter

class MyFormatImporter(BaseImporter):
    format_name = 'my_format'  # name to pass to --format

    def load(self, filepath: str) -> list[dict]:
        # Read filepath and return a list of scholist entry dicts
        entries = []
        # ... conversion logic ...
        return entries

IMPORTER_CLASS = MyFormatImporter  # required: this module variable enables discovery
```

After adding, install any required dependencies and verify:

```bash
python tools/import.py --help
# my_format should appear in --format choices
```

> **Sync compatibility:** `importers/my_format.py` does not exist in scholist, so it will never be overwritten or deleted by sync.
