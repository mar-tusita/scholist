import datetime
import pytest
from build import validate, sort_entries, highlight_authors, read_version


# ── validate ──────────────────────────────────────────────────────────────

class TestValidate:
    def test_ok(self):
        entries = [
            {"id": "a", "type": "conference", "title": "タイトル"},
            {"id": "b", "type": "journal",    "title_en": "Title"},
            {"id": "c", "type": "talk",       "title": "T", "title_en": "T"},
        ]
        validate(entries)  # 例外・sys.exit が起きなければ合格

    def test_duplicate_id(self):
        entries = [
            {"id": "dup", "type": "conference", "title": "A"},
            {"id": "dup", "type": "journal",    "title": "B"},
        ]
        with pytest.raises(SystemExit) as exc:
            validate(entries)
        assert exc.value.code == 1

    def test_missing_title(self):
        entries = [{"id": "a", "type": "conference"}]
        with pytest.raises(SystemExit) as exc:
            validate(entries)
        assert exc.value.code == 1

    def test_invalid_type(self):
        entries = [{"id": "a", "type": "unknown", "title": "T"}]
        with pytest.raises(SystemExit) as exc:
            validate(entries)
        assert exc.value.code == 1

    def test_all_valid_types(self):
        valid_types = ["conference", "journal", "talk", "patent", "award", "book", "misc", "other"]
        entries = [{"id": t, "type": t, "title": "T"} for t in valid_types]
        validate(entries)

    def test_multiple_errors_reported(self):
        entries = [
            {"id": "dup", "type": "conference", "title": "A"},
            {"id": "dup", "type": "bad_type"},        # ID重複 + title欠落 + 不明type
        ]
        with pytest.raises(SystemExit) as exc:
            validate(entries)
        assert exc.value.code == 1


# ── sort_entries ──────────────────────────────────────────────────────────

class TestValidateDate:
    def _e(self, date):
        return [{"id": "a", "type": "misc", "title": "T", "date": date}]

    def test_full_date(self):
        validate(self._e("2024-03-15"))

    def test_year_month(self):
        validate(self._e("2023-09"))

    def test_null(self):
        validate(self._e(None))

    def test_no_date_field(self):
        validate([{"id": "a", "type": "misc", "title": "T"}])

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
