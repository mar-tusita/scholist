"""BibTeX → scholist publications.yaml 変換"""

try:
    import bibtexparser
    from bibtexparser.bparser import BibTexParser
    from bibtexparser.customization import convert_to_unicode
except ImportError:
    raise ImportError(
        "bibtexparser が必要です: pip install 'bibtexparser>=1.3,<2.0'"
    )

from . import BaseImporter

_MONTH_MAP = {
    'jan': '01', 'january': '01',   'feb': '02', 'february': '02',
    'mar': '03', 'march': '03',     'apr': '04', 'april': '04',
    'may': '05',                    'jun': '06', 'june': '06',
    'jul': '07', 'july': '07',      'aug': '08', 'august': '08',
    'sep': '09', 'september': '09', 'oct': '10', 'october': '10',
    'nov': '11', 'november': '11',  'dec': '12', 'december': '12',
    **{str(i): f'{i:02d}' for i in range(1, 13)},
}


def _split_authors(author_str: str) -> list[str]:
    return [a.strip() for a in author_str.split(' and ') if a.strip()]


def _make_date(year: str, month: str) -> str | None:
    if not year:
        return None
    m = _MONTH_MAP.get(month.lower().strip()) if month else None
    return f"{year}-{m}" if m else f"{year}-01"


def _normalize_pages(pages: str) -> str:
    return pages.replace('--', '-').strip() if pages else ''


class BibTeXImporter(BaseImporter):

    def load(self, filepath: str) -> list[dict]:
        parser = BibTexParser(common_strings=True)
        parser.customization = convert_to_unicode
        with open(filepath, encoding='utf-8', errors='replace') as f:
            db = bibtexparser.load(f, parser=parser)

        entries = []
        for raw in db.entries:
            entry = self._convert(raw)
            if entry:
                entries.append(entry)
        return entries

    def _convert(self, raw: dict) -> dict | None:
        etype = raw.get('ENTRYTYPE', 'misc').lower()
        eid   = raw.get('ID', '')
        if not eid:
            self.warn("ID のないエントリをスキップしました")
            return None

        # ---- 型の決定 ----
        if etype == 'article':
            if raw.get('journal'):
                stype = 'journal'
            elif raw.get('booktitle'):
                stype = 'conference'
            else:
                stype = 'misc'
                self.warn(f"{eid}: @article に journal も booktitle もないため misc に変換")
        elif etype in ('inproceedings', 'proceedings', 'conference'):
            stype = 'conference'
        elif etype == 'book':
            stype = 'book'
        elif etype == 'incollection':
            stype = 'book'
        elif etype == 'phdthesis':
            stype = 'thesis'
        elif etype == 'mastersthesis':
            stype = 'thesis'
        elif etype == 'techreport':
            stype = 'report'
        else:
            stype = 'misc'
            if etype not in ('misc', 'unpublished', 'manual', 'online', 'electronic'):
                self.warn(f"{eid}: @{etype} は misc に変換")

        entry: dict = {'id': eid, 'type': stype}

        # ---- タイトル（英語と仮定） ----
        title = raw.get('title', '').replace('{', '').replace('}', '').strip()
        if title:
            entry['title_en'] = title

        # ---- 著者 ----
        authors_raw = raw.get('author', '')
        if authors_raw:
            entry['authors'] = _split_authors(authors_raw)
            self.warn(f"{eid}: 著者名は BibTeX 形式のまま（「姓, 名」形式）。必要に応じて修正してください")
        else:
            entry['authors'] = []
            self.warn(f"{eid}: 著者が見つかりません")

        # ---- 日付 ----
        year  = raw.get('year', '').strip()
        month = raw.get('month', '').strip()
        date  = _make_date(year, month)
        if date:
            entry['date'] = date
            if not month:
                self.warn(f"{eid}: month がないため {date}（1月）に設定。正しい月に修正してください")
        elif year:
            self.warn(f"{eid}: 年 ({year}) を date に変換できません。手動で設定してください")

        # ---- abstract ----
        abstract = raw.get('abstract', '').strip()
        if abstract:
            entry['abstract'] = abstract

        # ---- URL / DOI ----
        doi = raw.get('doi', '').strip()
        url = raw.get('url', '').strip()
        if doi:
            entry['url'] = f'https://doi.org/{doi}'
        elif url:
            entry['url'] = url

        # ---- note（既存 + 変換不能フィールド） ----
        note_parts = []
        if raw.get('note'):
            note_parts.append(raw['note'])

        # ---- 種別固有フィールド ----
        source: dict = {}
        unmapped: dict = {}

        known = {'ENTRYTYPE', 'ID', 'title', 'author', 'year', 'month',
                 'abstract', 'doi', 'url', 'note'}

        if stype == 'journal':
            source['journal_name'] = raw.get('journal', '')
            if raw.get('volume'):
                try:
                    source['volume'] = int(raw['volume'])
                except ValueError:
                    source['volume'] = raw['volume']
            if raw.get('number'):
                try:
                    source['number'] = int(raw['number'])
                except ValueError:
                    source['number'] = raw['number']
            if raw.get('pages'):
                source['pages'] = _normalize_pages(raw['pages'])
            if doi:
                source['doi'] = doi
            known |= {'journal', 'volume', 'number', 'pages'}

        elif stype == 'conference':
            if raw.get('booktitle'):
                source['proceedings'] = raw['booktitle'].replace('{', '').replace('}', '')
            if raw.get('pages'):
                source['pages'] = _normalize_pages(raw['pages'])
            if raw.get('organization'):
                entry['organization'] = raw['organization']
            if raw.get('address'):
                entry['location'] = raw['address']
            known |= {'booktitle', 'pages', 'organization', 'address'}

        elif stype == 'book':
            if raw.get('publisher'):
                source['publisher'] = raw['publisher']
            if raw.get('isbn'):
                source['isbn'] = raw['isbn']
            if raw.get('editor'):
                source['editors'] = _split_authors(raw['editor'])
            if raw.get('chapter'):
                source['chapter'] = raw['chapter']
            if raw.get('pages'):
                source['pages'] = _normalize_pages(raw['pages'])
            if etype == 'incollection' and raw.get('booktitle'):
                note_parts.append(f"[import: booktitle={raw['booktitle']}]")
            known |= {'publisher', 'isbn', 'editor', 'chapter', 'pages', 'booktitle'}

        elif stype == 'thesis':
            if raw.get('school'):
                source['institution'] = raw['school']
            if etype == 'phdthesis':
                source['degree'] = 'doctoral'
            elif etype == 'mastersthesis':
                source['degree'] = 'master'
            known |= {'school', 'type'}

        elif stype == 'report':
            if raw.get('institution'):
                source['institution'] = raw['institution']
            if raw.get('number'):
                source['number'] = raw['number']
            known |= {'institution', 'number', 'type'}

        # ---- 変換できなかったフィールド → note ----
        for k, v in raw.items():
            if k not in known and v and v.strip():
                unmapped[k] = v.strip()
        if unmapped:
            note_parts.append('[import: ' + ', '.join(f'{k}={v}' for k, v in unmapped.items()) + ']')

        if source:
            entry['source'] = source
        if note_parts:
            entry['note'] = ' / '.join(note_parts)

        return entry
