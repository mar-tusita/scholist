"""Hayagriva → scholist publications.yaml 変換"""

import yaml
from . import BaseImporter

_DEGREE_MAP = {
    'doctoral dissertation': 'doctoral', 'phd': 'doctoral',
    "master's thesis": 'master',  'master': 'master',
    "bachelor's thesis": 'bachelor', 'bachelor': 'bachelor',
}


def _detect_degree(genre: str) -> str | None:
    g = genre.lower().strip()
    for key, val in _DEGREE_MAP.items():
        if key in g:
            return val
    return None


def _resolve_type(htype: str, parent: dict) -> str:
    htype = htype.lower()
    ptype = (parent.get('type', '') if isinstance(parent, dict) else '').lower()

    if htype == 'article':
        if ptype in ('periodical', 'journal', 'magazine', 'newspaper'):
            return 'journal'
        if ptype in ('proceedings', 'conference', 'anthology'):
            return 'conference'
        return 'misc'
    if htype in ('thesis',):
        return 'thesis'
    if htype in ('report',):
        return 'report'
    if htype in ('patent',):
        return 'patent'
    if htype in ('book', 'chapter'):
        return 'book'
    return 'misc'


def _get_serial(item: dict, key: str) -> str:
    sn = item.get('serial-number', {})
    if isinstance(sn, str):
        return sn if key == 'serial' else ''
    if isinstance(sn, dict):
        return sn.get(key, '')
    return ''


class HayagrivaImporter(BaseImporter):

    def load(self, filepath: str) -> list[dict]:
        with open(filepath, encoding='utf-8') as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            raise ValueError("Hayagriva ファイルのトップレベルは mapping でなければなりません")

        entries = []
        for key, item in data.items():
            if not isinstance(item, dict):
                self.warn(f"{key}: 値が mapping でないためスキップ")
                continue
            entry = self._convert(key, item)
            if entry:
                entries.append(entry)
        return entries

    def _convert(self, key: str, item: dict) -> dict:
        parent = item.get('parent', {})
        if isinstance(parent, list):
            parent = parent[0] if parent else {}

        stype = _resolve_type(item.get('type', 'misc'), parent)
        entry: dict = {'id': key, 'type': stype}

        # ---- タイトル ----
        title = item.get('title', '')
        lang  = item.get('language', '')
        if title:
            if lang and lang.lower().startswith('en'):
                entry['title_en'] = str(title)
            else:
                entry['title'] = str(title)

        # ---- 著者 ----
        author = item.get('author', [])
        if isinstance(author, str):
            author = [author]
        if author:
            entry['authors'] = [str(a) for a in author]
            self.warn(f"{key}: 著者名は Hayagriva 形式のまま（「姓, 名」形式の場合あり）。確認してください")
        else:
            entry['authors'] = []
            self.warn(f"{key}: 著者が見つかりません")

        # ---- 日付 ----
        date = item.get('date', '')
        if date:
            entry['date'] = str(date)

        # ---- abstract / note ----
        if item.get('abstract'):
            entry['abstract'] = str(item['abstract'])
        if item.get('language'):
            entry['language'] = str(item['language'])

        # ---- URL / DOI ----
        url = item.get('url', '')
        if isinstance(url, dict):
            url = url.get('value', '')
        doi = _get_serial(item, 'doi')
        if doi:
            entry['url'] = f'https://doi.org/{doi}'
        elif url:
            entry['url'] = str(url)

        # ---- 種別固有フィールド ----
        source: dict = {}
        note_parts = []
        if item.get('note'):
            note_parts.append(str(item['note']))

        if stype == 'journal' and isinstance(parent, dict):
            if parent.get('title'):
                source['journal_name'] = str(parent['title'])
            if parent.get('volume') is not None:
                source['volume'] = parent['volume']
            if parent.get('issue') is not None:
                source['number'] = parent['issue']
            if item.get('page-range'):
                source['pages'] = str(item['page-range'])

        elif stype == 'conference':
            pparent = parent if isinstance(parent, dict) else {}
            if pparent.get('title'):
                source['proceedings'] = str(pparent['title'])
            if item.get('page-range'):
                source['pages'] = str(item['page-range'])
            if pparent.get('organization'):
                entry['organization'] = str(pparent['organization'])
            if pparent.get('location'):
                entry['location'] = str(pparent['location'])

        elif stype == 'thesis':
            if item.get('organization'):
                source['institution'] = str(item['organization'])
            genre = str(item.get('genre', ''))
            if genre:
                deg = _detect_degree(genre)
                if deg:
                    source['degree'] = deg
                else:
                    note_parts.append(f"[import: genre={genre}]")

        elif stype == 'report':
            if item.get('organization'):
                source['institution'] = str(item['organization'])
            sn = _get_serial(item, 'serial')
            if sn:
                source['number'] = sn

        elif stype == 'patent':
            sn = item.get('serial-number', '')
            if isinstance(sn, str):
                source['patent_number'] = sn
            elif isinstance(sn, dict):
                source['patent_number'] = sn.get('serial', '') or str(sn)

        elif stype == 'book':
            p = parent if isinstance(parent, dict) else item
            if p.get('publisher'):
                source['publisher'] = str(p['publisher'])
            isbn = _get_serial(p, 'isbn') or _get_serial(item, 'isbn')
            if isbn:
                source['isbn'] = isbn
            if item.get('page-range'):
                source['pages'] = str(item['page-range'])

        elif stype == 'misc':
            desc_parts = []
            if isinstance(parent, dict) and parent.get('title'):
                desc_parts.append(str(parent['title']))
            if desc_parts:
                source['description'] = '; '.join(desc_parts)

        if source:
            entry['source'] = source

        if item.get('organization') and 'organization' not in entry:
            entry['organization'] = str(item['organization'])

        if note_parts:
            entry['note'] = ' / '.join(note_parts)

        return entry
