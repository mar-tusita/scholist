# 既存データのインポート

BibTeX・Hayagriva・RIS・CSL-JSON 形式で管理していた文献データを `publications.yaml` に変換できます。

## セットアップ

```bash
pip install -r requirements-tools.txt
```

`bibtexparser` が追加でインストールされます（BibTeX のみ必要、RIS・Hayagriva・CSL-JSON は不要）。

## 対応フォーマット

| `--format` | 形式 | 外部依存 |
| --- | --- | --- |
| `bibtex` | BibTeX（`.bib`） | `bibtexparser`（`requirements-tools.txt`） |
| `hayagriva` | Hayagriva YAML（`.yml`） | なし |
| `ris` | RIS（`.ris`）— Zotero・Mendeley・EndNote 等 | なし |
| `csl-json` | CSL-JSON（`.json`）— Zotero・Pandoc 等 | なし |

## 使い方

```bash
# BibTeX から変換して標準出力に出力
python tools/import.py --format bibtex refs.bib

# ファイルに書き出す
python tools/import.py --format bibtex refs.bib --output data/publications.yaml

# 既存の publications.yaml に追記（ID 重複をチェックしてスキップ）
python tools/import.py --format bibtex refs.bib --append data/publications.yaml

# Hayagriva から変換
python tools/import.py --format hayagriva refs.yml --append data/publications.yaml

# RIS から変換（Zotero・Mendeley 等のエクスポートファイル）
python tools/import.py --format ris refs.ris --append data/publications.yaml

# CSL-JSON から変換（Zotero・Pandoc 等のエクスポートファイル）
python tools/import.py --format csl-json refs.json --append data/publications.yaml
```

変換できなかったフィールドは `note` に `[import: field=value]` 形式で記録されます。
著者名フォーマット（BibTeX: 「姓, 名」形式）や月なし日付など、確認が必要な点は
stderr に警告として出力されます。

## カスタムインポーターの追加

独自フォーマットのインポーターを追加できます。`tools/importers/` に以下の形式でファイルを作成するだけで、`import.py` が自動的に検出します。**`import.py` 本体の修正は不要です。**

```python
# tools/importers/my_format.py
from . import BaseImporter

class MyFormatImporter(BaseImporter):
    format_name = 'my_format'   # --format に渡す名前

    def load(self, filepath: str) -> list[dict]:
        # filepath を読み込み、scholist エントリ形式の dict のリストを返す
        entries = []
        # ... 変換処理 ...
        return entries

IMPORTER_CLASS = MyFormatImporter  # 必須：このモジュール変数で検出される
```

追加後は依存パッケージをインストールして確認：

```bash
python tools/import.py --help
# --format に my_format が追加されていれば成功
```

> **sync との共存：** `importers/my_format.py` は scholist にないファイルなので、sync で上書き・削除されることはありません。
