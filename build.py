#!/usr/bin/env python3
"""静的サイト生成スクリプト"""

import argparse
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader


VALID_TYPES = {"conference", "journal", "talk", "patent", "award", "book", "misc", "other"}
VALID_SCOPES = {"domestic", "international"}
VALID_PAPER_TYPES = {"full", "short"}
VALID_PATENT_STATUSES = {"applied", "granted"}

_DATE_RE = re.compile(r"^\d{4}-\d{2}(-\d{2})?$")
_ID_RE = re.compile(r"^[a-zA-Z0-9_-]+$")


def _valid_date(value):
    if value is None:
        return True
    s = str(value)
    if not _DATE_RE.match(s):
        return False
    fmt = "%Y-%m-%d" if len(s) == 10 else "%Y-%m"
    try:
        datetime.strptime(s, fmt)
        return True
    except ValueError:
        return False


def read_version(base_dir):
    toml_path = base_dir / "pyproject.toml"
    if not toml_path.exists():
        return "unknown"
    if sys.version_info >= (3, 11):
        import tomllib
        with open(toml_path, "rb") as f:
            return tomllib.load(f)["project"]["version"]
    text = toml_path.read_text(encoding="utf-8")
    m = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
    return m.group(1) if m else "unknown"


def load_yaml(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def validate(entries):
    ids = set()
    errors = []
    for e in entries:
        eid = e.get("id", "<no id>")

        # id: 重複チェック
        if eid in ids:
            errors.append(f"id が重複しています: {eid}")
        ids.add(eid)

        # id: 使用可能文字チェック（英数字・ハイフン・アンダースコアのみ）
        if eid != "<no id>" and not _ID_RE.match(str(eid)):
            errors.append(f"id='{eid}': id に使用できない文字が含まれています（英数字・ハイフン・アンダースコアのみ）")

        # title / title_en: 少なくとも一方が必要
        if not e.get("title") and not e.get("title_en"):
            errors.append(f"id={eid}: title または title_en が必要です")

        # type: 定義済み8種のみ
        if e.get("type") not in VALID_TYPES:
            errors.append(f"id={eid}: 不明な type '{e.get('type')}'")

        # authors: 必須・空リスト禁止
        authors = e.get("authors")
        if not authors:
            errors.append(f"id={eid}: authors は1名以上必要です")

        # date: 形式チェック
        if not _valid_date(e.get("date")):
            errors.append(f"id={eid}: date の形式が不正です: '{e.get('date')}'（YYYY-MM-DD または YYYY-MM）")

        # registered_at: 形式チェック（YYYY-MM-DD のみ）
        rat = e.get("registered_at")
        if rat is not None:
            s = str(rat)
            if not (re.match(r"^\d{4}-\d{2}-\d{2}$", s) and _valid_date(s)):
                errors.append(f"id={eid}: registered_at の形式が不正です: '{rat}'（YYYY-MM-DD）")

        # scope: domestic / international のみ
        scope = e.get("scope")
        if scope is not None and scope not in VALID_SCOPES:
            errors.append(f"id={eid}: scope は 'domestic' または 'international' でなければなりません: '{scope}'")

        # files: 各要素に path か url が必要
        for i, f in enumerate(e.get("files") or []):
            if not f.get("path") and not f.get("url"):
                errors.append(f"id={eid}: files[{i}] に path または url が必要です")

        # paper_type: journal のみ検証
        paper_type = e.get("paper_type")
        if paper_type is not None and e.get("type") == "journal" and paper_type not in VALID_PAPER_TYPES:
            errors.append(f"id={eid}: paper_type は 'full' または 'short' でなければなりません: '{paper_type}'")

        # source.status: patent のみ検証
        if e.get("type") == "patent":
            status = (e.get("source") or {}).get("status")
            if status is not None and status not in VALID_PATENT_STATUSES:
                errors.append(f"id={eid}: source.status は 'applied' または 'granted' でなければなりません: '{status}'")

    if errors:
        in_ci = os.environ.get("GITHUB_ACTIONS") == "true"
        for err in errors:
            if in_ci:
                # GitHub Actions のアノテーションとして表示される
                print(f"::error file=data/publications.yaml::{err}")
            else:
                print(f"ERROR: {err}", file=sys.stderr)
        sys.exit(1)


def sort_entries(entries):
    def key(e):
        d = e.get("date")
        if d is None:
            return ("9999-99", 0)
        return (str(d), 0)

    indexed = [(i, e) for i, e in enumerate(entries)]
    indexed.sort(key=lambda t: (t[1].get("date") is None, str(t[1].get("date") or ""), t[0]), reverse=False)
    # date降順、同日はYAML記述順（安定ソート）、nullは末尾
    indexed.sort(key=lambda t: (t[1].get("date") is not None, str(t[1].get("date") or "")), reverse=True)
    return [e for _, e in indexed]


def highlight_authors(authors, highlight_list, style):
    result = []
    for author in authors:
        if author in highlight_list:
            result.append({"name": author, "highlight": True, "style": style})
        else:
            result.append({"name": author, "highlight": False, "style": style})
    return result


def render_site(config, entries, output_dir, template_dir, version):
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=True,
    )
    env.globals["config"] = config
    env.globals["scholist_version"] = version

    hl_authors = config.get("highlight_authors", [])
    hl_style = config.get("highlight_style", "underline")

    for entry in entries:
        entry["_authors_hl"] = highlight_authors(entry.get("authors", []), hl_authors, hl_style)

    # 一覧ページ
    tmpl_index = env.get_template("index.html.j2")
    index_html = tmpl_index.render(entries=entries, config=config)
    index_path = output_dir / "index.html"
    index_path.write_text(index_html, encoding="utf-8")
    print(f"生成: {index_path}")

    # 詳細ページ
    tmpl_entry = env.get_template("entry.html.j2")
    for entry in entries:
        entry_dir = output_dir / "entries" / entry["id"]
        entry_dir.mkdir(parents=True, exist_ok=True)
        entry_html = tmpl_entry.render(entry=entry, config=config)
        entry_path = entry_dir / "index.html"
        entry_path.write_text(entry_html, encoding="utf-8")
        print(f"生成: {entry_path}")


def copy_dir(src, dst):
    if src.exists():
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        print(f"コピー: {src} -> {dst}")


def main():
    parser = argparse.ArgumentParser(description="scholist 静的サイト生成")
    parser.add_argument("--output", default="public", help="出力ディレクトリ（デフォルト: public/）")
    args = parser.parse_args()

    base_dir = Path(__file__).parent
    output_dir = base_dir / args.output
    template_dir = base_dir / "templates"
    static_dir = base_dir / "static"
    files_dir = base_dir / "files"

    version = read_version(base_dir)
    config = load_yaml(base_dir / "data" / "config.yaml")
    data = load_yaml(base_dir / "data" / "publications.yaml")
    entries = data.get("entries", [])

    validate(entries)
    entries = sort_entries(entries)

    output_dir.mkdir(parents=True, exist_ok=True)

    render_site(config, entries, output_dir, template_dir, version)

    copy_dir(static_dir, output_dir / "static")
    copy_dir(files_dir, output_dir / "files")

    print(f"\n完了: {output_dir}/")


if __name__ == "__main__":
    main()
