"""tools/importers のユニットテスト"""

import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / 'tools'))

from importers.hayagriva import HayagrivaImporter
from importers.ris import RISImporter


# ---- Hayagriva (PyYAML のみ必要なので常に実行) ----

HAYAGRIVA_JOURNAL = """\
yamada2023:
  type: article
  title: サンプル論文
  author:
    - Yamada, Taro
    - Suzuki, Hanako
  date: 2023-09
  page-range: 1-12
  serial-number:
    doi: 10.xxxx/sample
  parent:
    type: periodical
    title: 情報処理学会論文誌
    volume: 64
    issue: 9
"""

HAYAGRIVA_CONFERENCE = """\
yamada2024conf:
  type: article
  title: Conference Paper
  language: en
  author: Yamada, Taro
  date: 2024-03
  page-range: 100-110
  parent:
    type: proceedings
    title: Proc. of SIC 2024
    organization: IEEE
    location: Tokyo
"""

HAYAGRIVA_THESIS = """\
yamada2021phd:
  type: thesis
  title: 博士論文タイトル
  author: Yamada, Taro
  date: 2021-03
  organization: ○○大学大学院
  genre: Doctoral dissertation
"""

HAYAGRIVA_MISC = """\
yamada2020misc:
  type: misc
  title: その他エントリ
  author: Yamada, Taro
  date: 2020-01
  note: 備考
"""


def _load_str(yaml_str: str):
    import tempfile, os
    importer = HayagrivaImporter()
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yml',
                                     delete=False, encoding='utf-8') as f:
        f.write(yaml_str)
        name = f.name
    try:
        return importer.load(name), importer.warnings
    finally:
        os.unlink(name)


class TestHayagrivaJournal:
    def setup_method(self):
        self.entries, self.warnings = _load_str(HAYAGRIVA_JOURNAL)
        self.e = self.entries[0]

    def test_type(self):
        assert self.e['type'] == 'journal'

    def test_id(self):
        assert self.e['id'] == 'yamada2023'

    def test_title_japanese(self):
        assert self.e.get('title') == 'サンプル論文'
        assert 'title_en' not in self.e

    def test_authors(self):
        assert self.e['authors'] == ['Yamada, Taro', 'Suzuki, Hanako']

    def test_date(self):
        assert self.e['date'] == '2023-09'

    def test_source_journal(self):
        assert self.e['source']['journal_name'] == '情報処理学会論文誌'
        assert self.e['source']['volume'] == 64
        assert self.e['source']['number'] == 9
        assert self.e['source']['pages'] == '1-12'

    def test_doi_to_url(self):
        assert self.e['url'] == 'https://doi.org/10.xxxx/sample'


class TestHayagrivaConference:
    def setup_method(self):
        self.entries, _ = _load_str(HAYAGRIVA_CONFERENCE)
        self.e = self.entries[0]

    def test_type(self):
        assert self.e['type'] == 'conference'

    def test_title_en_from_language(self):
        assert self.e.get('title_en') == 'Conference Paper'
        assert 'title' not in self.e

    def test_source_proceedings(self):
        assert self.e['source']['proceedings'] == 'Proc. of SIC 2024'

    def test_organization_and_location(self):
        assert self.e['organization'] == 'IEEE'
        assert self.e['location'] == 'Tokyo'


class TestHayagrivaThesis:
    def setup_method(self):
        self.entries, _ = _load_str(HAYAGRIVA_THESIS)
        self.e = self.entries[0]

    def test_type(self):
        assert self.e['type'] == 'thesis'

    def test_degree(self):
        assert self.e['source']['degree'] == 'doctoral'

    def test_institution(self):
        assert self.e['source']['institution'] == '○○大学大学院'


class TestHayagrivaMisc:
    def setup_method(self):
        self.entries, _ = _load_str(HAYAGRIVA_MISC)
        self.e = self.entries[0]

    def test_type(self):
        assert self.e['type'] == 'misc'

    def test_note(self):
        assert self.e['note'] == '備考'


# ---- BibTeX (bibtexparser が必要) ----

bibtexparser = pytest.importorskip('bibtexparser',
                                    reason='bibtexparser が未インストール')

from importers.bibtex import BibTeXImporter

BIBTEX_JOURNAL = r"""
@article{yamada2023journal,
  author  = {Yamada, Taro and Suzuki, Hanako},
  title   = {Sample Journal Article},
  journal = {IPSJ Journal},
  year    = {2023},
  month   = sep,
  volume  = {64},
  number  = {9},
  pages   = {1--12},
  doi     = {10.xxxx/sample},
}
"""

BIBTEX_CONFERENCE = r"""
@inproceedings{yamada2024conf,
  author    = {Yamada, Taro},
  title     = {Sample Conference Paper},
  booktitle = {Proceedings of SIC 2024},
  year      = {2024},
  pages     = {100--110},
  organization = {IEEE},
  address   = {Tokyo},
}
"""

BIBTEX_THESIS = r"""
@phdthesis{yamada2021phd,
  author = {Yamada, Taro},
  title  = {Doctoral Thesis Title},
  school = {University of Example},
  year   = {2021},
}
"""

BIBTEX_MISC_UNMAPPED = r"""
@misc{yamada2020misc,
  author   = {Yamada, Taro},
  title    = {Misc Entry},
  year     = {2020},
  howpublished = {Web},
  keywords = {test},
}
"""


def _load_bib_str(bib_str: str):
    import tempfile, os
    importer = BibTeXImporter()
    with tempfile.NamedTemporaryFile(mode='w', suffix='.bib',
                                     delete=False, encoding='utf-8') as f:
        f.write(bib_str)
        name = f.name
    try:
        return importer.load(name), importer.warnings
    finally:
        os.unlink(name)


class TestBibTeXJournal:
    def setup_method(self):
        self.entries, self.warnings = _load_bib_str(BIBTEX_JOURNAL)
        self.e = self.entries[0]

    def test_type(self):
        assert self.e['type'] == 'journal'

    def test_id(self):
        assert self.e['id'] == 'yamada2023journal'

    def test_title_en(self):
        assert self.e.get('title_en') == 'Sample Journal Article'

    def test_authors(self):
        assert self.e['authors'] == ['Yamada, Taro', 'Suzuki, Hanako']

    def test_date_with_month(self):
        assert self.e['date'] == '2023-09'

    def test_source(self):
        src = self.e['source']
        assert src['journal_name'] == 'IPSJ Journal'
        assert src['volume'] == 64
        assert src['number'] == 9
        assert src['pages'] == '1-12'
        assert src['doi'] == '10.xxxx/sample'

    def test_doi_url(self):
        assert self.e['url'] == 'https://doi.org/10.xxxx/sample'


class TestBibTeXConference:
    def setup_method(self):
        self.entries, _ = _load_bib_str(BIBTEX_CONFERENCE)
        self.e = self.entries[0]

    def test_type(self):
        assert self.e['type'] == 'conference'

    def test_source_proceedings(self):
        assert self.e['source']['proceedings'] == 'Proceedings of SIC 2024'

    def test_pages_normalized(self):
        assert '--' not in self.e['source']['pages']

    def test_organization_and_location(self):
        assert self.e['organization'] == 'IEEE'
        assert self.e['location'] == 'Tokyo'


class TestBibTeXThesis:
    def setup_method(self):
        self.entries, _ = _load_bib_str(BIBTEX_THESIS)
        self.e = self.entries[0]

    def test_type(self):
        assert self.e['type'] == 'thesis'

    def test_degree(self):
        assert self.e['source']['degree'] == 'doctoral'

    def test_institution(self):
        assert self.e['source']['institution'] == 'University of Example'


class TestBibTeXUnmapped:
    def setup_method(self):
        self.entries, self.warnings = _load_bib_str(BIBTEX_MISC_UNMAPPED)
        self.e = self.entries[0]

    def test_type(self):
        assert self.e['type'] == 'misc'

    def test_unmapped_in_note(self):
        assert '[import:' in self.e.get('note', '')

    def test_date_no_month_warn(self):
        assert any('month' in w for w in self.warnings)


# ---- RIS (標準ライブラリのみ・常に実行) ----

RIS_JOURNAL = """\
TY  - JOUR
ID  - yamada2023ris
AU  - Yamada, Taro
AU  - Suzuki, Hanako
TI  - Sample RIS Journal Article
JO  - IPSJ Journal
VL  - 64
IS  - 9
SP  - 1
EP  - 12
PY  - 2023/09/
DO  - 10.xxxx/sample
AB  - This is an abstract.
ER  -
"""

RIS_CONFERENCE = """\
TY  - CONF
ID  - yamada2024risconf
AU  - Yamada, Taro
TI  - Sample RIS Conference Paper
T2  - Proceedings of SIC 2024
SP  - 100
EP  - 110
PY  - 2024/03/15/
PB  - IEEE
CY  - Tokyo
ER  -
"""

RIS_THESIS = """\
TY  - THES
ID  - yamada2021risphd
AU  - Yamada, Taro
TI  - Doctoral Thesis Title
PB  - University of Example
PY  - 2021
M1  - PhD Dissertation
ER  -
"""

RIS_PATENT = """\
TY  - PAT
ID  - yamada2021rispat
AU  - Yamada, Taro
TI  - Sample Patent
M1  - 特許第1234567号
CY  - JP
PY  - 2021/11/
ER  -
"""

RIS_UNKNOWN_TY = """\
TY  - ELEC
ID  - yamada2020risweb
AU  - Yamada, Taro
TI  - Web Page Entry
PY  - 2020
ER  -
"""

RIS_NO_ID = """\
TY  - MISC
AU  - Yamada, Taro
TI  - No ID Entry
PY  - 2022
ER  -
"""

RIS_YEAR_ONLY = """\
TY  - JOUR
ID  - yamada2019risyear
AU  - Yamada, Taro
TI  - Year Only Date
JO  - Some Journal
PY  - 2019
ER  -
"""


def _load_ris_str(ris_str: str):
    import tempfile, os
    importer = RISImporter()
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ris',
                                     delete=False, encoding='utf-8') as f:
        f.write(ris_str)
        name = f.name
    try:
        return importer.load(name), importer.warnings
    finally:
        os.unlink(name)


class TestRISJournal:
    def setup_method(self):
        self.entries, self.warnings = _load_ris_str(RIS_JOURNAL)
        self.e = self.entries[0]

    def test_type(self):
        assert self.e['type'] == 'journal'

    def test_id(self):
        assert self.e['id'] == 'yamada2023ris'

    def test_title_en(self):
        assert self.e.get('title_en') == 'Sample RIS Journal Article'

    def test_authors(self):
        assert self.e['authors'] == ['Yamada, Taro', 'Suzuki, Hanako']

    def test_date(self):
        assert self.e['date'] == '2023-09'

    def test_source(self):
        src = self.e['source']
        assert src['journal_name'] == 'IPSJ Journal'
        assert src['volume'] == 64
        assert src['number'] == 9
        assert src['pages'] == '1-12'
        assert src['doi'] == '10.xxxx/sample'

    def test_doi_url(self):
        assert self.e['url'] == 'https://doi.org/10.xxxx/sample'

    def test_abstract(self):
        assert self.e['abstract'] == 'This is an abstract.'


class TestRISConference:
    def setup_method(self):
        self.entries, _ = _load_ris_str(RIS_CONFERENCE)
        self.e = self.entries[0]

    def test_type(self):
        assert self.e['type'] == 'conference'

    def test_source_proceedings(self):
        assert self.e['source']['proceedings'] == 'Proceedings of SIC 2024'

    def test_pages(self):
        assert self.e['source']['pages'] == '100-110'

    def test_date_full(self):
        assert self.e['date'] == '2024-03-15'

    def test_organization_and_location(self):
        assert self.e['organization'] == 'IEEE'
        assert self.e['location'] == 'Tokyo'


class TestRISThesis:
    def setup_method(self):
        self.entries, _ = _load_ris_str(RIS_THESIS)
        self.e = self.entries[0]

    def test_type(self):
        assert self.e['type'] == 'thesis'

    def test_institution(self):
        assert self.e['source']['institution'] == 'University of Example'

    def test_degree_from_m1(self):
        assert self.e['source']['degree'] == 'doctoral'


class TestRISPatent:
    def setup_method(self):
        self.entries, _ = _load_ris_str(RIS_PATENT)
        self.e = self.entries[0]

    def test_type(self):
        assert self.e['type'] == 'patent'

    def test_patent_number(self):
        assert self.e['source']['patent_number'] == '特許第1234567号'

    def test_country(self):
        assert self.e['source']['country'] == 'JP'


class TestRISUnknownType:
    def setup_method(self):
        self.entries, self.warnings = _load_ris_str(RIS_UNKNOWN_TY)
        self.e = self.entries[0]

    def test_type_fallback_to_misc(self):
        assert self.e['type'] == 'misc'

    def test_warn_unknown_ty(self):
        assert any('ELEC' in w for w in self.warnings)


class TestRISNoID:
    def setup_method(self):
        self.entries, self.warnings = _load_ris_str(RIS_NO_ID)
        self.e = self.entries[0]

    def test_auto_id_assigned(self):
        assert self.e['id'].startswith('ris-import-')

    def test_warn_no_id(self):
        assert any('ID タグがない' in w for w in self.warnings)


class TestRISYearOnly:
    def setup_method(self):
        self.entries, self.warnings = _load_ris_str(RIS_YEAR_ONLY)
        self.e = self.entries[0]

    def test_date_fallback(self):
        assert self.e['date'] == '2019-01'

    def test_warn_month_unknown(self):
        assert any('月情報がない' in w for w in self.warnings)
