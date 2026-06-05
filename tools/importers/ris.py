"""RIS → scholist publications.yaml 変換"""

import re
from . import BaseImporter

_TY_MAP = {
    'JOUR': 'journal', 'EJOU': 'journal', 'MGZN': 'journal',
    'ABST': 'journal', 'JFULL': 'journal',
    'CONF': 'conference', 'CPAPER': 'conference',
    'BOOK': 'book', 'EBOOK': 'book',
    'CHAP': 'book', 'ECHAP': 'book',
    'THES': 'thesis',
    'RPRT': 'report',
    'PAT': 'patent',
}

_MISC_TY = {'MISC', 'GEN', 'UNPB', 'UNPUBLISHED'}

_SKIP_UNMAPPED = {
    'KW', 'LA', 'DB', 'DP', 'LB', 'LI', 'LK', 'RI', 'RP',
    'Y2', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8',
    'CA', 'CN', 'TA', 'ST', 'M2', 'M3', 'M4', 'M5', 'M6',
}


def _parse_ris(text: str) -> list[dict]:
    """RIS テキストをパースし、タグ→値（またはリスト）の dict リストを返す"""
    records: list[dict] = []
    current: dict | None = None

    for line in text.splitlines():
        if not line.strip():
            continue

        m = re.match(r'^([A-Z][A-Z0-9])\s{1,2}-\s?(.*)', line)
        if not m:
            continue

        tag = m.group(1)
        val = m.group(2).strip()

        if tag == 'TY':
            current = {}
            records.append(current)
            current['TY'] = val
            continue

        if current is None:
            continue

        if tag == 'ER':
            current = None
            continue

        if not val:
            continue

        existing = current.get(tag)
        if existing is None:
            current[tag] = val
        elif isinstance(existing, list):
            existing.append(val)
        else:
            current[tag] = [existing, val]

    return records


def _get(rec: dict, *keys: str) -> str:
    """複数タグ候補から最初に見つかった文字列を返す"""
    for k in keys:
        v = rec.get(k)
        if v:
            return v[0].strip() if isinstance(v, list) else str(v).strip()
    return ''


def _get_list(rec: dict, *keys: str) -> list[str]:
    """複数タグ候補から全値をフラットなリストで返す"""
    result = []
    for k in keys:
        v = rec.get(k)
        if not v:
            continue
        if isinstance(v, list):
            result.extend(s.strip() for s in v if s.strip())
        elif str(v).strip():
            result.append(str(v).strip())
    return result


def _parse_date(py_str: str, da_str: str) -> tuple[str | None, bool]:
    """
    PY/Y1 または DA から (date_str, month_unknown) を返す。
    RIS 日付形式: YYYY/MM/DD/ または YYYY/MM/ または YYYY
    """
    raw = da_str or py_str
    if not raw:
        return None, False

    m = re.match(r'^(\d{4})/(\d{1,2})/(\d{1,2})/?', raw)
    if m:
        y, mo, d = m.group(1), m.group(2).zfill(2), m.group(3).zfill(2)
        return f'{y}-{mo}-{d}', False

    m = re.match(r'^(\d{4})/(\d{1,2})/?', raw)
    if m:
        y, mo = m.group(1), m.group(2).zfill(2)
        return f'{y}-{mo}', False

    m = re.match(r'^(\d{4})', raw)
    if m:
        return f'{m.group(1)}-01', True

    return None, False


class RISImporter(BaseImporter):
    format_name = 'ris'

    def load(self, filepath: str) -> list[dict]:
        with open(filepath, encoding='utf-8', errors='replace') as f:
            text = f.read()

        records = _parse_ris(text)
        entries = []
        for i, rec in enumerate(records):
            entry = self._convert(rec, index=i)
            if entry:
                entries.append(entry)
        return entries

    def _convert(self, rec: dict, index: int) -> dict | None:
        ty = rec.get('TY', '').strip().upper()
        if not ty:
            self.warn(f"エントリ {index + 1}: TY タグがないためスキップ")
            return None

        stype = _TY_MAP.get(ty, 'misc')
        if ty not in _TY_MAP and ty not in _MISC_TY:
            self.warn(f"エントリ {index + 1}: TY={ty} は misc に変換")

        # ---- ID ----
        eid = _get(rec, 'ID').strip()
        if not eid:
            eid = f'ris-import-{index + 1}'
            self.warn(f"エントリ {index + 1}: ID タグがないため '{eid}' を仮割当て。手動で修正してください")

        eid_clean = re.sub(r'[^A-Za-z0-9_-]', '-', eid)
        if eid_clean != eid:
            self.warn(f"'{eid}': ID に使用できない文字があるため '{eid_clean}' に変換")
            eid = eid_clean

        entry: dict = {'id': eid, 'type': stype}

        # ---- タイトル（英語と仮定） ----
        title = _get(rec, 'TI', 'T1')
        if title:
            entry['title_en'] = title

        # ---- 著者 ----
        authors = _get_list(rec, 'AU', 'A1', 'A2', 'A3', 'A4')
        if authors:
            entry['authors'] = authors
            self.warn(f"{eid}: 著者名は RIS 形式のまま（「姓, 名」形式の場合あり）。確認してください")
        else:
            entry['authors'] = []
            self.warn(f"{eid}: 著者が見つかりません")

        # ---- 日付 ----
        py_str = _get(rec, 'PY', 'Y1')
        da_str = _get(rec, 'DA')
        date, month_unknown = _parse_date(py_str, da_str)
        if date:
            entry['date'] = date
            if month_unknown:
                self.warn(
                    f"{eid}: 月情報がないため {date}（1月）に設定。正しい月に修正してください"
                )

        # ---- abstract ----
        abstract = _get(rec, 'AB', 'N2')
        if abstract:
            entry['abstract'] = abstract

        # ---- URL / DOI ----
        doi = _get(rec, 'DO')
        url = _get(rec, 'UR')
        if doi:
            entry['url'] = doi if doi.startswith('http') else f'https://doi.org/{doi}'
        elif url:
            entry['url'] = url

        # ---- ページ（共通） ----
        sp = _get(rec, 'SP')
        ep = _get(rec, 'EP')
        pages = f'{sp}-{ep}' if sp and ep else (sp or ep)

        # ---- 種別固有フィールド ----
        source: dict = {}
        note_parts = []
        n1 = _get(rec, 'N1')
        if n1:
            note_parts.append(n1)

        known = {
            'TY', 'ID', 'ER',
            'TI', 'T1', 'AU', 'A1', 'A2', 'A3', 'A4',
            'PY', 'Y1', 'DA',
            'AB', 'N2',
            'DO', 'UR', 'N1',
            'SP', 'EP',
        }

        if stype == 'journal':
            jname = _get(rec, 'JO', 'JF', 'JA', 'J1', 'J2', 'T2')
            if jname:
                source['journal_name'] = jname
            vl = _get(rec, 'VL', 'VO')
            if vl:
                try:
                    source['volume'] = int(vl)
                except ValueError:
                    source['volume'] = vl
            is_ = _get(rec, 'IS')
            if is_:
                try:
                    source['number'] = int(is_)
                except ValueError:
                    source['number'] = is_
            if pages:
                source['pages'] = pages
            if doi and not doi.startswith('http'):
                source['doi'] = doi
            known |= {'JO', 'JF', 'JA', 'J1', 'J2', 'T2', 'VL', 'VO', 'IS'}

        elif stype == 'conference':
            proceedings = _get(rec, 'T2', 'BT', 'T3')
            if proceedings:
                source['proceedings'] = proceedings
            if pages:
                source['pages'] = pages
            org = _get(rec, 'PB')
            if org:
                entry['organization'] = org
            loc = _get(rec, 'CY', 'AD')
            if loc:
                entry['location'] = loc
            known |= {'T2', 'BT', 'T3', 'VL', 'VO', 'IS', 'PB', 'CY', 'AD'}

        elif stype == 'book':
            pb = _get(rec, 'PB')
            if pb:
                source['publisher'] = pb
            sn = _get(rec, 'SN')
            if sn:
                source['isbn'] = sn
            if pages:
                source['pages'] = pages
            t2 = _get(rec, 'T2', 'BT')
            if t2 and ty in ('CHAP', 'ECHAP'):
                note_parts.append(f'[import: booktitle={t2}]')
            known |= {'PB', 'SN', 'T2', 'BT', 'CY', 'AD'}

        elif stype == 'thesis':
            inst = _get(rec, 'PB', 'AD')
            if inst:
                source['institution'] = inst
            degree_hint = (_get(rec, 'M1') + ' ' + _get(rec, 'ET')).lower()
            if 'doctoral' in degree_hint or 'phd' in degree_hint:
                source['degree'] = 'doctoral'
            elif 'master' in degree_hint:
                source['degree'] = 'master'
            elif 'bachelor' in degree_hint:
                source['degree'] = 'bachelor'
            known |= {'PB', 'AD', 'M1', 'ET'}

        elif stype == 'report':
            inst = _get(rec, 'PB', 'AD')
            if inst:
                source['institution'] = inst
            num = _get(rec, 'M1', 'IS')
            if num:
                source['number'] = num
            known |= {'PB', 'AD', 'M1', 'IS'}

        elif stype == 'patent':
            pnum = _get(rec, 'M1', 'SN')
            if pnum:
                source['patent_number'] = pnum
            cy = _get(rec, 'CY', 'AD')
            if cy:
                source['country'] = cy
            known |= {'M1', 'SN', 'CY', 'AD'}

        elif stype == 'misc':
            desc = _get(rec, 'T2', 'BT', 'JO', 'JF')
            if desc:
                source['description'] = desc
            known |= {'T2', 'BT', 'JO', 'JF', 'VL', 'VO', 'IS', 'PB', 'CY', 'AD', 'SN'}

        # ---- 変換できなかったフィールド → note ----
        unmapped: dict[str, str] = {}
        for k, v in rec.items():
            if k in known or k in _SKIP_UNMAPPED:
                continue
            val_str = ', '.join(v) if isinstance(v, list) else str(v)
            if val_str.strip():
                unmapped[k] = val_str.strip()
        if unmapped:
            note_parts.append('[import: ' + ', '.join(f'{k}={v}' for k, v in unmapped.items()) + ']')

        if source:
            entry['source'] = source
        if note_parts:
            entry['note'] = ' / '.join(note_parts)

        return entry


IMPORTER_CLASS = RISImporter
