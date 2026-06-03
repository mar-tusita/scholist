import datetime
import xml.etree.ElementTree as ET
import pytest
from build import (validate, sort_entries, highlight_authors, read_version,
                   generate_sitemap, generate_feed, _entry_description)


# ── validate ──────────────────────────────────────────────────────────────

class TestValidate:
    def test_ok(self):
        entries = [
            {"id": "a", "type": "conference", "title": "タイトル",  "authors": ["山田 太郎"]},
            {"id": "b", "type": "journal",    "title_en": "Title",  "authors": ["山田 太郎"]},
            {"id": "c", "type": "talk",       "title": "T", "title_en": "T", "authors": ["山田 太郎"]},
        ]
        validate(entries)

    def test_duplicate_id(self):
        entries = [
            {"id": "dup", "type": "conference", "title": "A", "authors": ["山田 太郎"]},
            {"id": "dup", "type": "journal",    "title": "B", "authors": ["山田 太郎"]},
        ]
        with pytest.raises(SystemExit) as exc:
            validate(entries)
        assert exc.value.code == 1

    def test_missing_title(self):
        entries = [{"id": "a", "type": "conference", "authors": ["山田 太郎"]}]
        with pytest.raises(SystemExit) as exc:
            validate(entries)
        assert exc.value.code == 1

    def test_invalid_type(self):
        entries = [{"id": "a", "type": "unknown", "title": "T", "authors": ["山田 太郎"]}]
        with pytest.raises(SystemExit) as exc:
            validate(entries)
        assert exc.value.code == 1

    def test_all_valid_types(self):
        valid_types = ["conference", "journal", "talk", "patent", "award", "book",
                       "misc", "other", "thesis", "report"]
        entries = [{"id": t, "type": t, "title": "T", "authors": ["山田 太郎"]} for t in valid_types]
        validate(entries)

    def test_multiple_errors_reported(self):
        entries = [
            {"id": "dup", "type": "conference", "title": "A", "authors": ["山田 太郎"]},
            {"id": "dup", "type": "bad_type"},        # ID重複 + title欠落 + 不明type + authors欠落
        ]
        with pytest.raises(SystemExit) as exc:
            validate(entries)
        assert exc.value.code == 1


# ── validate: 追加フィールド ──────────────────────────────────────────────

def _entry(**kwargs):
    base = {"id": "a", "type": "misc", "title": "T", "authors": ["山田 太郎"]}
    base.update(kwargs)
    return [base]


class TestValidateId:
    def test_valid_alphanumeric(self):
        validate(_entry(id="yamada-2024-ipsj"))

    def test_valid_underscore(self):
        validate(_entry(id="my_entry_01"))

    def test_invalid_space(self):
        with pytest.raises(SystemExit):
            validate(_entry(id="has space"))

    def test_invalid_slash(self):
        with pytest.raises(SystemExit):
            validate(_entry(id="has/slash"))

    def test_invalid_dot(self):
        with pytest.raises(SystemExit):
            validate(_entry(id="has.dot"))


class TestValidateAuthors:
    def test_single_author(self):
        validate(_entry(authors=["山田 太郎"]))

    def test_multiple_authors(self):
        validate(_entry(authors=["山田 太郎", "鈴木 花子"]))

    def test_empty_list(self):
        with pytest.raises(SystemExit):
            validate(_entry(authors=[]))

    def test_missing(self):
        entry = [{"id": "a", "type": "misc", "title": "T"}]
        with pytest.raises(SystemExit):
            validate(entry)


class TestValidateScope:
    def test_domestic(self):
        validate(_entry(scope="domestic"))

    def test_international(self):
        validate(_entry(scope="international"))

    def test_none_ok(self):
        validate(_entry())

    def test_invalid(self):
        with pytest.raises(SystemExit):
            validate(_entry(scope="foreign"))


class TestValidateRegisteredAt:
    def test_valid(self):
        validate(_entry(registered_at="2024-03-20"))

    def test_none_ok(self):
        validate(_entry())

    def test_invalid_format(self):
        with pytest.raises(SystemExit):
            validate(_entry(registered_at="2024/03/20"))

    def test_year_month_rejected(self):
        with pytest.raises(SystemExit):
            validate(_entry(registered_at="2024-03"))

    def test_invalid_day(self):
        with pytest.raises(SystemExit):
            validate(_entry(registered_at="2024-02-30"))


class TestValidateFiles:
    def test_with_path(self):
        validate(_entry(files=[{"label": "PDF", "path": "files/x.pdf"}]))

    def test_with_url(self):
        validate(_entry(files=[{"label": "PDF", "url": "https://example.com/x.pdf"}]))

    def test_empty_list_ok(self):
        validate(_entry(files=[]))

    def test_no_files_field_ok(self):
        validate(_entry())

    def test_missing_both(self):
        with pytest.raises(SystemExit):
            validate(_entry(files=[{"label": "PDF"}]))

    def test_second_entry_invalid(self):
        with pytest.raises(SystemExit):
            validate(_entry(files=[
                {"label": "Slides", "path": "files/x.pdf"},
                {"label": "PDF"},
            ]))


class TestValidatePaperType:
    def test_full(self):
        validate(_entry(type="journal", paper_type="full"))

    def test_short(self):
        validate(_entry(type="journal", paper_type="short"))

    def test_none_ok(self):
        validate(_entry(type="journal"))

    def test_invalid_for_journal(self):
        with pytest.raises(SystemExit):
            validate(_entry(type="journal", paper_type="extended"))

    def test_ignored_for_non_journal(self):
        validate(_entry(type="conference", paper_type="extended"))


class TestValidatePatentStatus:
    def _patent(self, status=None):
        src = {"patent_number": "特許第1号", "country": "JP"}
        if status is not None:
            src["status"] = status
        return [{"id": "a", "type": "patent", "title": "T",
                 "authors": ["山田 太郎"], "source": src}]

    def test_granted(self):
        validate(self._patent("granted"))

    def test_applied(self):
        validate(self._patent("applied"))

    def test_none_ok(self):
        validate(self._patent())

    def test_invalid(self):
        with pytest.raises(SystemExit):
            validate(self._patent("pending"))

    def test_ignored_for_non_patent(self):
        validate(_entry(type="misc"))


class TestValidateDegree:
    def _thesis(self, degree=None):
        src = {"institution": "○○大学"}
        if degree is not None:
            src["degree"] = degree
        return [{"id": "a", "type": "thesis", "title": "T",
                 "authors": ["山田 太郎"], "source": src}]

    def test_doctoral(self):
        validate(self._thesis("doctoral"))

    def test_master(self):
        validate(self._thesis("master"))

    def test_bachelor(self):
        validate(self._thesis("bachelor"))

    def test_none_ok(self):
        validate(self._thesis())

    def test_invalid(self):
        with pytest.raises(SystemExit):
            validate(self._thesis("phd"))

    def test_ignored_for_non_thesis(self):
        validate(_entry(type="report"))


# ── エラー出力形式 ────────────────────────────────────────────────────────

class TestErrorOutput:
    _bad = [{"id": "a", "type": "misc", "title": "T", "authors": [], "date": "bad"}]

    def test_local_format_uses_stderr(self, capsys, monkeypatch):
        monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
        with pytest.raises(SystemExit):
            validate(self._bad)
        captured = capsys.readouterr()
        assert "ERROR:" in captured.err
        assert "::error" not in captured.out

    def test_ci_format_uses_annotation(self, capsys, monkeypatch):
        monkeypatch.setenv("GITHUB_ACTIONS", "true")
        with pytest.raises(SystemExit):
            validate(self._bad)
        captured = capsys.readouterr()
        assert "::error file=data/publications.yaml::" in captured.out
        assert "ERROR:" not in captured.err

    def test_ci_annotation_contains_message(self, capsys, monkeypatch):
        monkeypatch.setenv("GITHUB_ACTIONS", "true")
        bad = [{"id": "a", "type": "misc", "title": "T",
                "authors": ["山田 太郎"], "date": "2024/01/01"}]
        with pytest.raises(SystemExit):
            validate(bad)
        out = capsys.readouterr().out
        assert "date" in out
        assert "::error file=data/publications.yaml::" in out


# ── sort_entries ──────────────────────────────────────────────────────────

class TestValidateDate:
    def _e(self, date):
        return [{"id": "a", "type": "misc", "title": "T", "authors": ["山田 太郎"], "date": date}]

    def test_full_date(self):
        validate(self._e("2024-03-15"))

    def test_year_month(self):
        validate(self._e("2023-09"))

    def test_null(self):
        validate(self._e(None))

    def test_no_date_field(self):
        validate([{"id": "a", "type": "misc", "title": "T", "authors": ["山田 太郎"]}])

    def test_datetime_date_object(self):
        validate(self._e(datetime.date(2024, 3, 15)))

    def test_invalid_separator(self):
        with pytest.raises(SystemExit):
            validate(self._e("2024/03/15"))

    def test_invalid_month(self):
        with pytest.raises(SystemExit):
            validate(self._e("2024-13-01"))

    def test_invalid_day(self):
        with pytest.raises(SystemExit):
            validate(self._e("2024-02-30"))

    def test_year_only(self):
        with pytest.raises(SystemExit):
            validate(self._e("2024"))

    def test_wrong_length(self):
        with pytest.raises(SystemExit):
            validate(self._e("24-03-15"))


class TestSortEntries:
    def test_date_descending(self):
        entries = [
            {"id": "old",  "date": "2020-01-01"},
            {"id": "new",  "date": "2024-03-15"},
            {"id": "mid",  "date": "2021-06-01"},
        ]
        result = sort_entries(entries)
        assert [e["id"] for e in result] == ["new", "mid", "old"]

    def test_same_date_preserves_yaml_order(self):
        entries = [
            {"id": "first",  "date": "2024-03-15"},
            {"id": "second", "date": "2024-03-15"},
            {"id": "third",  "date": "2024-03-15"},
        ]
        result = sort_entries(entries)
        assert [e["id"] for e in result] == ["first", "second", "third"]

    def test_null_date_at_end(self):
        entries = [
            {"id": "no-date-1", "date": None},
            {"id": "dated",     "date": "2023-01-01"},
            {"id": "no-date-2", "date": None},
        ]
        result = sort_entries(entries)
        assert result[0]["id"] == "dated"
        assert result[1]["id"] == "no-date-1"
        assert result[2]["id"] == "no-date-2"

    def test_null_date_preserves_yaml_order_among_nulls(self):
        entries = [
            {"id": "null-a", "date": None},
            {"id": "null-b", "date": None},
        ]
        result = sort_entries(entries)
        assert [e["id"] for e in result] == ["null-a", "null-b"]

    def test_year_month_format(self):
        entries = [
            {"id": "older", "date": "2023-06"},
            {"id": "newer", "date": "2023-12"},
        ]
        result = sort_entries(entries)
        assert result[0]["id"] == "newer"

    def test_mixed_null_and_dated(self):
        entries = [
            {"id": "null",  "date": None},
            {"id": "2022",  "date": "2022-01-01"},
            {"id": "2024a", "date": "2024-03-15"},
            {"id": "2024b", "date": "2024-03-15"},
        ]
        result = sort_entries(entries)
        assert result[0]["id"] == "2024a"
        assert result[1]["id"] == "2024b"
        assert result[2]["id"] == "2022"
        assert result[3]["id"] == "null"

    def test_empty(self):
        assert sort_entries([]) == []

    def test_single(self):
        entries = [{"id": "a", "date": "2024-01-01"}]
        assert sort_entries(entries) == entries


# ── highlight_authors ─────────────────────────────────────────────────────

class TestHighlightAuthors:
    def test_match(self):
        result = highlight_authors(["山田 太郎", "鈴木 花子"], ["山田 太郎"], "underline")
        assert result[0]["highlight"] is True
        assert result[0]["style"] == "underline"
        assert result[1]["highlight"] is False

    def test_no_match(self):
        result = highlight_authors(["鈴木 花子"], ["山田 太郎"], "bold")
        assert result[0]["highlight"] is False

    def test_case_sensitive(self):
        result = highlight_authors(["T. Yamada"], ["t. yamada"], "bold")
        assert result[0]["highlight"] is False

    def test_multiple_variants(self):
        hl = ["山田 太郎", "Taro Yamada", "T. Yamada"]
        result = highlight_authors(["T. Yamada", "鈴木 花子", "Taro Yamada"], hl, "bold")
        assert result[0]["highlight"] is True
        assert result[1]["highlight"] is False
        assert result[2]["highlight"] is True

    def test_bold_style(self):
        result = highlight_authors(["山田 太郎"], ["山田 太郎"], "bold")
        assert result[0]["style"] == "bold"

    def test_empty_authors(self):
        assert highlight_authors([], ["山田 太郎"], "underline") == []

    def test_empty_highlight_list(self):
        result = highlight_authors(["山田 太郎"], [], "underline")
        assert result[0]["highlight"] is False

    def test_preserves_order(self):
        authors = ["C", "A", "B"]
        result = highlight_authors(authors, ["A"], "underline")
        assert [r["name"] for r in result] == ["C", "A", "B"]


# ── read_version ──────────────────────────────────────────────────────────

class TestReadVersion:
    def test_reads_version(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nname = "scholist"\nversion = "1.2.3"\n',
            encoding="utf-8",
        )
        assert read_version(tmp_path) == "1.2.3"

    def test_missing_file_returns_unknown(self, tmp_path):
        assert read_version(tmp_path) == "unknown"

    def test_version_with_prerelease(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nversion = "0.2.0-beta.1"\n',
            encoding="utf-8",
        )
        assert read_version(tmp_path) == "0.2.0-beta.1"


# ── generate_sitemap ──────────────────────────────────────────────────────

class TestGenerateSitemap:
    _entries = [
        {"id": "a", "type": "misc", "title": "A", "authors": ["X"],
         "registered_at": "2024-03-20", "date": "2024-03-15"},
        {"id": "b", "type": "misc", "title": "B", "authors": ["X"],
         "date": "2023-09"},
        {"id": "c", "type": "misc", "title": "C", "authors": ["X"],
         "date": None},
    ]

    def _cfg(self, base_url="https://example.com"):
        return {"base_url": base_url, "site_title": "Test"}

    def test_generates_file(self, tmp_path):
        generate_sitemap(self._cfg(), self._entries, tmp_path)
        assert (tmp_path / "sitemap.xml").exists()

    def test_skips_if_base_url_empty(self, tmp_path):
        generate_sitemap(self._cfg(""), self._entries, tmp_path)
        assert not (tmp_path / "sitemap.xml").exists()

    def test_skips_if_base_url_missing(self, tmp_path):
        generate_sitemap({"site_title": "T"}, self._entries, tmp_path)
        assert not (tmp_path / "sitemap.xml").exists()

    def test_contains_index_and_entries(self, tmp_path):
        generate_sitemap(self._cfg(), self._entries, tmp_path)
        xml = (tmp_path / "sitemap.xml").read_text()
        assert "<loc>https://example.com/</loc>" in xml
        assert "<loc>https://example.com/entries/a/</loc>" in xml
        assert "<loc>https://example.com/entries/b/</loc>" in xml

    def test_lastmod_prefers_registered_at(self, tmp_path):
        generate_sitemap(self._cfg(), self._entries, tmp_path)
        xml = (tmp_path / "sitemap.xml").read_text()
        assert "<lastmod>2024-03-20</lastmod>" in xml

    def test_lastmod_year_month_appends_day(self, tmp_path):
        generate_sitemap(self._cfg(), self._entries, tmp_path)
        xml = (tmp_path / "sitemap.xml").read_text()
        assert "<lastmod>2023-09-01</lastmod>" in xml

    def test_no_lastmod_when_no_date(self, tmp_path):
        generate_sitemap(self._cfg(), self._entries, tmp_path)
        xml = (tmp_path / "sitemap.xml").read_text()
        assert xml.count("<lastmod>") == 2

    def test_trailing_slash_stripped(self, tmp_path):
        generate_sitemap(self._cfg("https://example.com/"), self._entries, tmp_path)
        xml = (tmp_path / "sitemap.xml").read_text()
        assert "//entries" not in xml
        assert "<loc>https://example.com/</loc>" in xml

    def test_valid_xml_header(self, tmp_path):
        generate_sitemap(self._cfg(), self._entries, tmp_path)
        xml = (tmp_path / "sitemap.xml").read_text()
        assert xml.startswith('<?xml version="1.0" encoding="UTF-8"?>')


# ── generate_feed ─────────────────────────────────────────────────────────

class TestGenerateFeed:
    _entries = [
        {"id": "a", "type": "journal", "title": "タイトルA", "authors": ["山田 太郎"],
         "registered_at": "2024-03-20", "date": "2024-03-15",
         "source": {"journal_name": "情報処理学会論文誌", "volume": 64, "number": 9, "pages": "1-12"}},
        {"id": "b", "type": "conference", "title_en": "Title B", "authors": ["T. Yamada"],
         "date": "2023-09",
         "source": {"proceedings": "Proc. of SIC 2023", "pages": "100-111"}},
        {"id": "c", "type": "misc", "title": "タイトルC", "authors": ["山田 太郎"],
         "date": None},
    ]

    def _cfg(self, base_url="https://example.com"):
        return {"base_url": base_url, "site_title": "テスト業績一覧"}

    def test_generates_file(self, tmp_path):
        generate_feed(self._cfg(), self._entries, tmp_path)
        assert (tmp_path / "feed.xml").exists()

    def test_skips_if_no_base_url(self, tmp_path):
        generate_feed(self._cfg(""), self._entries, tmp_path)
        assert not (tmp_path / "feed.xml").exists()

    def test_excludes_entries_without_date(self, tmp_path):
        generate_feed(self._cfg(), self._entries, tmp_path)
        tree = ET.parse(tmp_path / "feed.xml")
        ns = {"a": "http://www.w3.org/2005/Atom"}
        ids = [e.find("a:id", ns).text for e in tree.findall("a:entry", ns)]
        assert any("/a/" in i for i in ids)
        assert any("/b/" in i for i in ids)
        assert not any("/c/" in i for i in ids)

    def test_uses_registered_at_over_date(self, tmp_path):
        generate_feed(self._cfg(), self._entries, tmp_path)
        xml = (tmp_path / "feed.xml").read_text(encoding="utf-8")
        assert "2024-03-20T00:00:00Z" in xml

    def test_year_month_date_gets_day(self, tmp_path):
        generate_feed(self._cfg(), self._entries, tmp_path)
        xml = (tmp_path / "feed.xml").read_text(encoding="utf-8")
        assert "2023-09-01T00:00:00Z" in xml

    def test_atom_namespace(self, tmp_path):
        generate_feed(self._cfg(), self._entries, tmp_path)
        xml = (tmp_path / "feed.xml").read_text(encoding="utf-8")
        assert "http://www.w3.org/2005/Atom" in xml

    def test_valid_xml(self, tmp_path):
        generate_feed(self._cfg(), self._entries, tmp_path)
        ET.parse(tmp_path / "feed.xml")  # raises if invalid

    def test_description_contains_author_and_title(self, tmp_path):
        generate_feed(self._cfg(), self._entries, tmp_path)
        xml = (tmp_path / "feed.xml").read_text(encoding="utf-8")
        assert "山田 太郎" in xml
        assert "タイトルA" in xml

    def test_description_contains_journal_info(self, tmp_path):
        generate_feed(self._cfg(), self._entries, tmp_path)
        xml = (tmp_path / "feed.xml").read_text(encoding="utf-8")
        assert "情報処理学会論文誌" in xml
        assert "Vol. 64" in xml

    def test_entry_description_journal(self):
        entry = {"type": "journal", "title": "T", "authors": ["A"],
                 "date": "2024-01",
                 "source": {"journal_name": "JN", "volume": 1, "number": 2, "pages": "1-10"}}
        desc = _entry_description(entry)
        assert "A" in desc
        assert "T" in desc
        assert "JN" in desc
        assert "Vol. 1, No. 2" in desc
        assert "pp. 1-10" in desc
        assert "2024" in desc

    def test_entry_description_conference(self):
        entry = {"type": "conference", "title": "T", "authors": ["A"],
                 "date": "2023-03",
                 "source": {"proceedings": "Proc", "pages": "1-5"}}
        desc = _entry_description(entry)
        assert "Proc" in desc
        assert "pp. 1-5" in desc

    def test_entry_description_no_date(self):
        entry = {"type": "misc", "title": "T", "authors": ["A"]}
        desc = _entry_description(entry)
        assert "T" in desc
        assert desc.endswith(".")
