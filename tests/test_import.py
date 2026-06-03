"""tools/importers のユニットテスト"""

import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / 'tools'))

from importers.hayagriva import HayagrivaImporter


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
