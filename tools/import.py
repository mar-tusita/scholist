#!/usr/bin/env python3
"""scholist インポートツール

使い方:
  python tools/import.py --format bibtex refs.bib
  python tools/import.py --format hayagriva refs.yml --output data/publications.yaml
  python tools/import.py --format bibtex refs.bib --append data/publications.yaml
"""

import argparse
import datetime
import sys
from pathlib import Path

import yaml

# importers を tools/ 直下からも呼べるようにパスを通す
sys.path.insert(0, str(Path(__file__).parent))


def load_importer(fmt: str):
    if fmt == 'bibtex':
        from importers.bibtex import BibTeXImporter
        return BibTeXImporter()
    if fmt == 'hayagriva':
        from importers.hayagriva import HayagrivaImporter
        return HayagrivaImporter()
    raise ValueError(f"未対応のフォーマット: {fmt}。対応: bibtex, hayagriva")


def make_header(fmt: str, filepath: str, n_entries: int, warnings: list[str]) -> str:
    lines = [
        f"# Imported from: {filepath} ({fmt})",
        f"# Date: {datetime.date.today()}",
        f"# Entries: {n_entries}",
        f"# Warnings: {len(warnings)}",
    ]
    if warnings:
        lines.append("#")
        for w in warnings:
            lines.append(f"# WARNING: {w}")
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(
        description="BibTeX / Hayagriva を scholist の publications.yaml に変換する"
    )
    parser.add_argument('input', help='入力ファイルパス')
    parser.add_argument('--format', '-f', required=True,
                        choices=['bibtex', 'hayagriva'],
                        help='入力フォーマット')
    parser.add_argument('--output', '-o',
                        help='出力先ファイル（省略時: 標準出力）')
    parser.add_argument('--append', '-a',
                        help='既存の publications.yaml に追記するファイルパス')
    args = parser.parse_args()

    # ---- インポート ----
    importer = load_importer(args.format)
    try:
        entries = importer.load(args.input)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    warnings = importer.warnings
    header = make_header(args.format, args.input, len(entries), warnings)

    # ---- 標準エラーに警告を表示 ----
    for w in warnings:
        print(f"WARNING: {w}", file=sys.stderr)

    # ---- --append: 既存ファイルに追記 ----
    if args.append:
        append_path = Path(args.append)
        existing_entries = []
        existing_ids = set()
        if append_path.exists():
            with open(append_path, encoding='utf-8') as f:
                existing = yaml.safe_load(f) or {}
            existing_entries = existing.get('entries', [])
            existing_ids = {e.get('id') for e in existing_entries}

        added = []
        for e in entries:
            if e.get('id') in existing_ids:
                print(f"WARNING: id={e['id']} は既に存在するためスキップ", file=sys.stderr)
            else:
                added.append(e)

        all_entries = existing_entries + added
        yaml_text = yaml.dump(
            {'entries': all_entries},
            allow_unicode=True, default_flow_style=False,
            indent=2, sort_keys=False
        )
        with open(append_path, 'w', encoding='utf-8') as f:
            f.write(yaml_text)
        print(f"追記完了: {len(added)} 件追加 → {append_path}", file=sys.stderr)
        return

    # ---- 通常出力 ----
    yaml_text = yaml.dump(
        {'entries': entries},
        allow_unicode=True, default_flow_style=False,
        indent=2, sort_keys=False
    )
    output = header + yaml_text

    if args.output:
        Path(args.output).write_text(output, encoding='utf-8')
        print(f"出力: {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(output)


if __name__ == '__main__':
    main()
