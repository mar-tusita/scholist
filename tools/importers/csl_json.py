"""CSL-JSON → scholist publications.yaml 変換"""

import json
import re
from . import BaseImporter

_TYPE_MAP = {
    'article-journal':   'journal',
    'article-magazine':  'misc',
    'article-newspaper': 'misc',
    'paper-conference':  'conference',
    'book':              'book',
    'chapter':           'book',
    'entry-encyclopedia':'book',
    'thesis':            'thesis',
    'report':            'report',
    'patent':            'patent',
    'speech':            'talk',
    'article':           'misc',
    'broadcast':         'misc',
    'dataset':           'misc',
    'figure':            'misc',
    'graphic':           'misc',
    'interview':         'misc',
    'manuscript':        'misc',
    'map':               'misc',
    'pamphlet':          'misc',
    'post':              'misc',
    'post-weblog':       'misc',
    'review':            'misc',
    'review-book':       'misc',
    'song':              'misc',
    'treaty':            'misc',
    'webpage':           'misc',
}

_KNOWN = {
    'id', 'type', 'title', 'author', 'editor', 'issued', 'abstract', 'language',
    'DOI', 'URL', 'note', 'page', 'volume', 'issue', 'number',
    'container-title', 'publisher', 'publisher-place', 'ISBN', 'ISSN',
    'chapter-number', 'section', 'genre', 'jurisdiction',
    'event', 'event-title', 'event-place',
    'title-short', 'shortTitle',
}

_SKIP = {
    'categories', 'accessed', 'source', 'call-number', 'collection-title',
    'collection-number', 'edition', 'annote', 'keyword', 'archive',
    'archive_location', 'archive-place',
}


def _assemble_name(person: dict | str) -> str:
    if isinstance(person, str):
        return person
    literal = person.get('literal', '')
    if literal:
        return literal
    family = person.get('family', '')
    given = person.get('given', '')
    if family and given:
        return f'{family} {given}'
    return family or given


def _parse_date(issued: dict | None) -> tuple[str | None, bool]:
    """(date_str, month_unknown) を返す。date-parts の先頭要素を使用。"""
    if not issued or not isinstance(issued, dict):
        return None, False
    parts = issued.get('date-parts', [])
    if not parts or not parts[0]:
        return None, False
    dp = parts[0]
    year = dp[0] if len(dp) > 0 else None
    month = dp[1] if len(dp) > 1 else None
    day = dp[2] if len(dp) > 2 else None
    if not year:
        return None, False
    if month and day:
        return f'{year}-{int(month):02d}-{int(day):02d}', False
    if month:
        return f'{year}-{int(month):02d}', False
    return f'{year}-01', True


class CSLJSONImporter(BaseImporter):
    format_name = 'csl-json'

    def load(self, filepath: str) -> list[dict]:
        with open(filepath, encoding='utf-8', errors='replace') as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("CSL-JSON ファイルのトップレベルは配列でなければなりません")

        entries = []
        for i, item in enumerate(data):
            if not isinstance(item, dict):
                self.warn(f"エントリ {i + 1}: オブジェクトでないためスキップ")
                continue
            entry = self._convert(item, index=i)
            if entry:
                entries.append(entry)
        return entries

    def _convert(self, item: dict, index: int) -> dict | None:
        csl_type = str(item.get('type', '')).strip()
        stype = _TYPE_MAP.get(csl_type, 'misc')
        if csl_type and csl_type not in _TYPE_MAP:
            self.warn(f"エントリ {index + 1}: type={csl_type} は misc に変換")

        # ---- ID ----
        eid = str(item.get('id', '')).strip()
        if not eid:
            eid = f'csl-import-{index + 1}'
            self.warn(f"エントリ {index + 1}: id がないため '{eid}' を仮割当て。手動で修正してください")

        eid_clean = re.sub(r'[^A-Za-z0-9_-]', '-', eid)
        if eid_clean != eid:
            self.warn(f"'{eid}': ID に使用できない文字があるため '{eid_clean}' に変換")
            eid = eid_clean

        entry: dict = {'id': eid, 'type': stype}

        # ---- タイトル ----
        title = str(item.get('title', '')).strip()
        if title:
            lang = str(item.get('language', '')).lower()
            if lang.startswith('ja'):
                entry['title'] = title
            else:
                entry['title_en'] = title

        # ---- 著者 ----
        authors_raw = item.get('author', [])
        if isinstance(authors_raw, list) and authors_raw:
            entry['authors'] = [_assemble_name(a) for a in authors_raw]
            self.warn(f"{eid}: 著者名の姓名の順序を確認してください（family + given の順で結合）")
        else:
            entry['authors'] = []
            self.warn(f"{eid}: 著者が見つかりません")

        # ---- 日付 ----
        date, month_unknown = _parse_date(item.get('issued'))
        if date:
            entry['date'] = date
            if month_unknown:
                self.warn(f"{eid}: 月情報がないため {date}（1月）に設定。正しい月に修正してください")

        # ---- abstract / language ----
        abstract = str(item.get('abstract', '')).strip()
        if abstract:
            entry['abstract'] = abstract
        lang = str(item.get('language', '')).strip()
        if lang:
            entry['language'] = lang

        # ---- URL / DOI ----
        doi = str(item.get('DOI', '')).strip()
        url = str(item.get('URL', '')).strip()
        if doi:
            entry['url'] = doi if doi.startswith('http') else f'https://doi.org/{doi}'
        elif url:
            entry['url'] = url

        # ---- 種別固有フィールド ----
        source: dict = {}
        note_parts = []
        note_val = str(item.get('note', '')).strip()
        if note_val:
            note_parts.append(note_val)

        pages = str(item.get('page', '')).strip()

        if stype == 'journal':
            ct = str(item.get('container-title', '')).strip()
            if ct:
                source['journal_name'] = ct
            vol = item.get('volume')
            if vol is not None:
                try:
                    source['volume'] = int(vol)
                except (ValueError, TypeError):
                    source['volume'] = str(vol)
            iss = item.get('issue')
            if iss is not None:
                try:
                    source['number'] = int(iss)
                except (ValueError, TypeError):
                    source['number'] = str(iss)
            if pages:
                source['pages'] = pages
            if doi and not doi.startswith('http'):
                source['doi'] = doi

        elif stype == 'conference':
            ct = str(item.get('container-title', '')).strip()
            if ct:
                source['proceedings'] = ct
            if pages:
                source['pages'] = pages
            org = str(item.get('publisher', '')).strip()
            if org:
                entry['organization'] = org
            loc = str(item.get('publisher-place', '')).strip()
            if loc:
                entry['location'] = loc

        elif stype == 'book':
            pb = str(item.get('publisher', '')).strip()
            if pb:
                source['publisher'] = pb
            isbn = str(item.get('ISBN', '')).strip()
            if isbn:
                source['isbn'] = isbn
            editors_raw = item.get('editor', [])
            if isinstance(editors_raw, list) and editors_raw:
                source['editors'] = [_assemble_name(e) for e in editors_raw]
            chapter = str(item.get('chapter-number', '') or item.get('section', '')).strip()
            if chapter:
                source['chapter'] = chapter
            if pages:
                source['pages'] = pages
            ct = str(item.get('container-title', '')).strip()
            if ct and csl_type == 'chapter':
                note_parts.append(f'[import: container-title={ct}]')

        elif stype == 'thesis':
            pb = str(item.get('publisher', '')).strip()
            if pb:
                source['institution'] = pb
            genre = str(item.get('genre', '')).lower()
            if 'doctoral' in genre or 'phd' in genre:
                source['degree'] = 'doctoral'
            elif 'master' in genre:
                source['degree'] = 'master'
            elif 'bachelor' in genre:
                source['degree'] = 'bachelor'

        elif stype == 'report':
            pb = str(item.get('publisher', '')).strip()
            if pb:
                source['institution'] = pb
            num = str(item.get('number', '')).strip()
            if num:
                source['number'] = num

        elif stype == 'patent':
            pnum = str(item.get('number', '')).strip()
            if pnum:
                source['patent_number'] = pnum
            jurisdiction = str(item.get('jurisdiction', '') or item.get('publisher-place', '')).strip()
            if jurisdiction:
                source['country'] = jurisdiction

        elif stype == 'talk':
            event = str(item.get('event-title', '') or item.get('event', '')).strip()
            if event:
                source['description'] = event
            loc = str(item.get('event-place', '') or item.get('publisher-place', '')).strip()
            if loc:
                entry['location'] = loc

        elif stype == 'misc':
            ct = str(item.get('container-title', '')).strip()
            if ct:
                source['description'] = ct

        # ---- 変換できなかったフィールド → note ----
        unmapped: dict[str, str] = {}
        for k, v in item.items():
            if k in _KNOWN or k in _SKIP:
                continue
            if v:
                unmapped[k] = str(v)
        if unmapped:
            note_parts.append('[import: ' + ', '.join(f'{k}={v}' for k, v in unmapped.items()) + ']')

        if source:
            entry['source'] = source
        if note_parts:
            entry['note'] = ' / '.join(note_parts)

        return entry


IMPORTER_CLASS = CSLJSONImporter
