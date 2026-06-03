#!/usr/bin/env python3
"""静的サイト生成スクリプト"""

import argparse
import os
import re
import shutil
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader


VALID_TYPES = {"conference", "journal", "talk", "patent", "award", "book", "misc", "other", "thesis", "report"}
VALID_SCOPES = {"domestic", "international"}
VALID_PAPER_TYPES = {"full", "short"}
VALID_PATENT_STATUSES = {"applied", "granted"}
VALID_DEGREES = {"bachelor", "master", "doctoral"}

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

        # source.degree: thesis のみ検証
        if e.get("type") == "thesis":
            degree = (e.get("source") or {}).get("degree")
            if degree is not None and degree not in VALID_DEGREES:
                errors.append(f"id={eid}: source.degree は 'bachelor', 'master', 'doctoral' のいずれかでなければなりません: '{degree}'")

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


_SEARCHTEXT_EXCLUDE = {
    'id', 'type', 'date', 'registered_at',
    'scope', 'paper_type', 'invited', 'reviewed',
    'language', 'highlight_style', 'status', 'country',
}


def build_searchtext(entry):
    """エントリの全文字列値をフラット化して検索用テキストを生成する。"""
    parts = []

    def collect(obj, key=None):
        if key in _SEARCHTEXT_EXCLUDE:
            return
        if isinstance(obj, str):
            parts.append(obj)
        elif isinstance(obj, list):
            for item in obj:
                collect(item)
        elif isinstance(obj, dict):
            for k, v in obj.items():
                collect(v, key=k)

    collect({k: v for k, v in entry.items() if not k.startswith('_')})
    return ' '.join(parts).lower()


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
        entry["_searchtext"] = build_searchtext(entry)

    # 一覧ページ
    tmpl_index = env.get_template("index.html.j2")
    index_html = tmpl_index.render(entries=entries, config=config)
    index_path = output_dir / "index.html"
    index_path.write_text(index_html, encoding="utf-8")
    print(f"生成: {index_path}")

    # 詳細ページ
    tmpl_entry = env.get_template("entry.html.j2")
    for i, entry in enumerate(entries):
        prev_entry = entries[i - 1] if i > 0 else None
        next_entry = entries[i + 1] if i < len(entries) - 1 else None
        entry_dir = output_dir / "entries" / entry["id"]
        entry_dir.mkdir(parents=True, exist_ok=True)
        entry_html = tmpl_entry.render(
            entry=entry,
            prev_entry=prev_entry,
            next_entry=next_entry,
            config=config,
        )
        entry_path = entry_dir / "index.html"
        entry_path.write_text(entry_html, encoding="utf-8")
        print(f"生成: {entry_path}")


def _sitemap_date(entry):
    """registered_at → date の順で YYYY-MM-DD を返す。なければ None。"""
    for field in ("registered_at", "date"):
        val = entry.get(field)
        if val is None:
            continue
        s = str(val)
        if re.match(r"^\d{4}-\d{2}-\d{2}$", s):
            return s
        if re.match(r"^\d{4}-\d{2}$", s):
            return s + "-01"
    return None


def generate_sitemap(config, entries, output_dir):
    base_url = config.get("base_url", "").rstrip("/")
    if not base_url:
        return

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        "  <url>",
        f"    <loc>{base_url}/</loc>",
        "  </url>",
    ]
    for entry in entries:
        lines.append("  <url>")
        lines.append(f"    <loc>{base_url}/entries/{entry['id']}/</loc>")
        lastmod = _sitemap_date(entry)
        if lastmod:
            lines.append(f"    <lastmod>{lastmod}</lastmod>")
        lines.append("  </url>")
    lines.append("</urlset>")

    sitemap_path = output_dir / "sitemap.xml"
    sitemap_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"生成: {sitemap_path}")


_ATOM_NS = "http://www.w3.org/2005/Atom"
ET.register_namespace("", _ATOM_NS)


def _atom(tag):
    return f"{{{_ATOM_NS}}}{tag}"


def _entry_description(entry):
    """bibliography 形式の説明文を生成する（Atom feed の content 用）"""
    parts = []
    authors = entry.get("authors") or []
    if authors:
        parts.append(", ".join(authors))
    title = entry.get("title") or entry.get("title_en") or ""
    if title:
        parts.append(title)

    src = entry.get("source") or {}
    etype = entry.get("type", "")
    venue_info = []

    if etype == "conference":
        if src.get("proceedings"):
            venue_info.append(src["proceedings"])
        elif entry.get("venue"):
            venue_info.append(entry["venue"])
        if src.get("pages"):
            venue_info.append(f"pp. {src['pages']}")
    elif etype == "journal":
        if src.get("journal_name"):
            venue_info.append(src["journal_name"])
        if src.get("volume") is not None:
            vol = f"Vol. {src['volume']}"
            if src.get("number") is not None:
                vol += f", No. {src['number']}"
            venue_info.append(vol)
        if src.get("pages"):
            venue_info.append(f"pp. {src['pages']}")
    elif etype == "talk":
        if entry.get("venue"):
            venue_info.append(entry["venue"])
    elif etype == "award":
        if src.get("award_name"):
            venue_info.append(src["award_name"])
        if src.get("org_giving_award"):
            venue_info.append(src["org_giving_award"])
    elif etype == "patent":
        if src.get("patent_number"):
            venue_info.append(src["patent_number"])
    elif etype == "book":
        if src.get("publisher"):
            venue_info.append(src["publisher"])
        if src.get("pages"):
            venue_info.append(f"pp. {src['pages']}")
    elif etype == "thesis":
        if src.get("institution"):
            venue_info.append(src["institution"])
        deg_map = {
            "doctoral": "Doctoral dissertation",
            "master": "Master's thesis",
            "bachelor": "Bachelor's thesis",
        }
        if src.get("degree") in deg_map:
            venue_info.append(deg_map[src["degree"]])
    elif etype == "report":
        if src.get("institution"):
            venue_info.append(src["institution"])
        if src.get("number"):
            venue_info.append(src["number"])
    else:
        if src.get("description"):
            venue_info.append(src["description"])

    if venue_info:
        parts.append(", ".join(venue_info))

    d = entry.get("date")
    if d:
        parts.append(str(d)[:4])

    return ". ".join(parts) + "." if parts else ""


def generate_feed(config, entries, output_dir):
    base_url = config.get("base_url", "").rstrip("/")
    if not base_url:
        return

    dated = [(e, _sitemap_date(e)) for e in entries if _sitemap_date(e)]
    most_recent = max((d for _, d in dated), default=None) if dated else "1970-01-01"

    root = ET.Element(_atom("feed"))
    ET.SubElement(root, _atom("title")).text = config.get("site_title", "Publications")
    ET.SubElement(root, _atom("id")).text = base_url + "/"
    ET.SubElement(root, _atom("link"), rel="alternate", href=base_url + "/")
    ET.SubElement(root, _atom("link"), rel="self", href=base_url + "/feed.xml")
    ET.SubElement(root, _atom("updated")).text = f"{most_recent}T00:00:00Z"

    for entry, date_str in dated:
        e_el = ET.SubElement(root, _atom("entry"))
        title = entry.get("title") or entry.get("title_en") or ""
        ET.SubElement(e_el, _atom("id")).text = f"{base_url}/entries/{entry['id']}/"
        ET.SubElement(e_el, _atom("title")).text = title
        ET.SubElement(e_el, _atom("link"), href=f"{base_url}/entries/{entry['id']}/")
        ET.SubElement(e_el, _atom("published")).text = f"{date_str}T00:00:00Z"
        ET.SubElement(e_el, _atom("updated")).text = f"{date_str}T00:00:00Z"
        for author in (entry.get("authors") or []):
            a_el = ET.SubElement(e_el, _atom("author"))
            ET.SubElement(a_el, _atom("name")).text = author
        ET.SubElement(e_el, _atom("content"), type="text").text = _entry_description(entry)

    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    feed_path = output_dir / "feed.xml"
    tree.write(feed_path, encoding="UTF-8", xml_declaration=True)
    print(f"生成: {feed_path}")


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
    generate_sitemap(config, entries, output_dir)
    generate_feed(config, entries, output_dir)

    copy_dir(static_dir, output_dir / "static")
    copy_dir(files_dir, output_dir / "files")

    print(f"\n完了: {output_dir}/")


if __name__ == "__main__":
    main()
