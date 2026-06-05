# CLAUDE.md — scholist 仕様書

## プロジェクト概要

**scholist** — 個人（または小人数グループ）の研究業績データをYAML形式で管理し、静的HTMLとして生成・公開するWebツール。

- GitHubリポジトリ名：`scholist`
- GitHub Pages URL：`https://mar-tusita.github.io/scholist/`

- **データ管理**：YAMLテキストファイル（`data/publications.yaml`）
- **生成方法**：Pythonスクリプト（`build.py`）でJinja2テンプレートからHTML生成
- **配信**：GitHub Pages（初期運用）または nginx（本格運用）
- **添付ファイル**：同リポジトリ内 `files/` ディレクトリに配置

---

## ディレクトリ構成

```text
publications/
├── CLAUDE.md                        # 本ファイル
├── data/
│   ├── publications.yaml            # 業績データ本体
│   └── config.yaml                  # 表示設定（著者ハイライト等）
├── files/                           # PDF・PPT等の添付ファイル置き場
│   └── (例) 2024-conf-001-slides.pdf
├── templates/
│   ├── index.html.j2                # 一覧ページテンプレート
│   └── entry.html.j2                # 詳細ページテンプレート
├── static/
│   ├── style.css
│   └── export.js                    # YAML/JSON/BibTeX/Hayagriva書き出し処理
├── build.py                         # 静的サイト生成スクリプト
├── extras/
│   └── sync-from-scholist.yml       # template zip に同梱する sync ワークフローのマスター
├── tools/                           # 補助ツール
│   ├── import.py                    # BibTeX/Hayagriva インポート CLI
│   └── importers/
│       ├── __init__.py              # BaseImporter 基底クラス
│       ├── bibtex.py                # BibTeX 変換
│       └── hayagriva.py             # Hayagriva 変換
├── public/                          # 生成物（nginxまたはGitHub Pagesで配信）
│   ├── index.html
│   ├── entries/
│   │   └── <id>/
│   │       └── index.html
│   └── files/                       # files/ をそのままコピー
└── .github/
    └── workflows/
        ├── build.yml                # push時に自動生成・デプロイ
        ├── test.yml                 # push/PR時にpytest実行
        └── release-asset.yml        # タグ push時にリリース asset 生成
```

---

## データスキーマ

### `data/config.yaml`

```yaml
# 著者ハイライト設定
highlight_authors:
  - "山田 太郎"
  - "Taro Yamada"
  - "T. Yamada"
highlight_style: underline   # bold または underline

# サイト設定
site_title: "研究業績一覧"

# 初回訪問者（localStorage 未設定）に表示する言語
# auto: ブラウザ言語を検出（ja → 日本語、それ以外 → 英語）
# ja:   常に日本語で開始  / en: 常に英語で開始
default_language: auto

# 一覧ページの初期表示件数（「さらに表示」で同数ずつ追加）
# 0 または未設定の場合は全件表示
entries_per_page: 30

# サイトの公開 URL（og:url / sitemap 用）末尾スラッシュなし
# 例: https://username.github.io/publications
# 空文字または未設定の場合、og:url と sitemap.xml は出力しない
base_url: ""
```

### `data/publications.yaml`

全エントリは `entries:` キーの下にリストで記述する。

#### 共通フィールド（全種別）

| フィールド | 型 | 必須 | 説明 |
| --- | --- | --- | --- |
| `id` | string | ✅ | 一意ID（手動命名、自由形式） |
| `type` | enum | ✅ | 種別（下記10種） |
| `title` | string | △ | 日本語タイトル（`title_en` と少なくとも一方必須） |
| `title_en` | string | △ | 英語タイトル（`title` と少なくとも一方必須） |
| `authors` | list[string] | ✅ | 著者リスト（順序を保持） |
| `date` | string | | 発表日・公開日（`YYYY-MM-DD` または `YYYY-MM`） |
| `registered_at` | string | | エントリ登録日（`YYYY-MM-DD`） |
| `organization` | string | | 学会名・組織名 |
| `presenter` | string | | 登壇者（会議・講演の場合） |
| `files` | list | | 添付ファイルリスト（下記参照） |
| `url` | string | | DOI または外部URL |
| `abstract` | string | | アブストラクト（詳細ページに表示、BibTeX に出力、OGP の og:description に優先使用） |
| `language` | string | | 言語コード（ISO 639-1: `ja`、`en` 等）。Hayagriva エクスポート時のタイトル選択に使用 |
| `note` | string | | 備考 |

`files` の各要素：
```yaml
files:
  - label: "発表スライド"
    path: "files/2024-conf-001-slides.pdf"   # files/ 以下への相対パス
  - label: "論文PDF"
    url: "https://example.com/paper.pdf"     # 外部URLの場合
```

#### 種別（`type`）の定義

```text
conference  国内会議・国際会議
journal     国内論文誌・国際論文誌
talk        講演
patent      特許
award       受賞
book        書籍
thesis      学位論文（学士・修士・博士）
report      技術レポート
misc        解説等
other       その他
```

#### 種別固有フィールド

**`conference`（国内会議・国際会議）**

| フィールド | 型 | 説明 |
| --- | --- | --- |
| `scope` | enum | `domestic`（国内）/ `international`（国際） |
| `invited` | bool | 招待講演か |
| `reviewed` | bool | 査読有りか |
| `venue` | string | 会議名 |
| `venue_abbr` | string | 略称（例: `IPSJ`） |
| `location` | string | 開催地 |
| `source` | object | 出典情報（下記） |

`source` の構造（conference）:
```yaml
source:
  proceedings: "情報処理学会第86回全国大会講演論文集"
  pages: "1-123 -- 1-124"
```

**`journal`（国内論文誌・国際論文誌）**

| フィールド | 型 | 説明 |
| --- | --- | --- |
| `scope` | enum | `domestic` / `international` |
| `reviewed` | bool | 査読有りか |
| `paper_type` | enum | `full`（フルペーパー）/ `short`（ショートペーパー） |
| `source` | object | 出典情報（下記） |

`source` の構造（journal）:
```yaml
source:
  journal_name: "情報処理学会論文誌"
  volume: 67
  number: 4
  pages: "111-122"
  doi: "10.1234/ipsj.67.111"
```

**`talk`（講演）**

| フィールド | 型 | 説明 |
| --- | --- | --- |
| `invited` | bool | 招待講演か |
| `venue` | string | 講演場所・イベント名 |
| `location` | string | 開催地 |
| `source` | object | `description: "自由記述"` |

**`patent`（特許）**

`source` の構造:
```yaml
source:
  patent_number: "特許第1234567号"
  country: "JP"
  status: granted   # applied（出願）/ granted（登録）
```

**`award`（受賞）**

`source` の構造:
```yaml
source:
  award_name: "優秀論文賞"
  org_giving_award: "情報処理学会"
```

**`book`（書籍）**

`source` の構造:
```yaml
source:
  publisher: "オーム社"
  isbn: "978-4-274-XXXXX-X"
  editors:
    - "編者 太郎"
  chapter: "第3章"
  pages: "45-89"
```

**`thesis`（学位論文）**

| フィールド | 型 | 説明 |
| --- | --- | --- |
| `source` | object | 出典情報（下記） |

`source` の構造:
```yaml
source:
  institution: "○○大学大学院"
  degree: doctoral   # bachelor（学士）/ master（修士）/ doctoral（博士）
```

BibTeX マッピング：`doctoral` → `@phdthesis`、`master` → `@mastersthesis`、`bachelor` → `@misc`

**`report`（技術レポート）**

| フィールド | 型 | 説明 |
| --- | --- | --- |
| `source` | object | 出典情報（下記） |

`source` の構造:
```yaml
source:
  institution: "○○大学情報学研究科"
  number: "TR-2024-001"
```

BibTeX マッピング：`@techreport`

**`misc`（解説等）・`other`（その他）**

`source` の構造:
```yaml
source:
  description: "自由記述（誌名・媒体名など）"
```

#### YAMLサンプルエントリ

```yaml
entries:
  - id: "yamada-2024-ipsj-example"
    type: conference
    title: "サンプル論文タイトル"
    title_en: "Sample Paper Title"
    authors:
      - "山田 太郎"
      - "鈴木 花子"
    date: "2024-03-15"
    registered_at: "2024-03-20"
    organization: "情報処理学会"
    presenter: "山田 太郎"
    scope: domestic
    invited: false
    reviewed: false
    venue: "情報処理学会 第86回全国大会"
    venue_abbr: "IPSJ"
    location: "東京"
    source:
      proceedings: "情報処理学会第86回全国大会講演論文集"
      pages: "1-1 -- 1-2"
    files:
      - label: "発表スライド"
        path: "files/yamada-2024-ipsj-example-slides.pdf"
    url: "https://doi.org/xxxx"
    note: ""
```

---

## ソート規則

1. `date` 降順（新しい順）
2. `date` が同一の場合 → YAMLファイル内の記述順（Pythonの安定ソートを利用）
3. `date` が null のエントリ → 最後尾

---

## 機能仕様

### 一覧ページ（`public/index.html`）

- 統計サマリー：ヘッダー直下に総件数・年範囲・種別ごとの件数チップを表示
- 1行1エントリで表示
- デフォルト表示順：上記ソート規則に従う
- ページネーション：`entries_per_page` 件ずつ表示し「さらに表示」「全件表示」ボタンで追加
- フィルタ機能（JavaScript）：
  - 種別（type）
  - 年（date の年部分）
  - 国内/国際（scope）
  - 査読有無（reviewed）
  - 招待有無（invited）
  - フィルタ条件は URL クエリパラメータに保持（共有・リロード対応）
  - パラメータ一覧：

    | パラメータ | 値の例 | 対応フィールド |
    | --- | --- | --- |
    | `type` | `journal` | 種別（10種） |
    | `year` | `2024` | date の年部分（4桁） |
    | `scope` | `domestic` | `domestic` / `international` |
    | `reviewed` | `true` | `true` / `false` |
    | `invited` | `true` | `true` / `false` |
    | `q` | `yamada` | 全文検索語（`build_searchtext` の出力に対して照合） |

- インクリメンタル検索（JavaScript）：`build_searchtext()` で生成した全文字列を対象
  - title・title_en・abstract・authors・venue・organization・source 内の全文字列フィールド等
  - id・type・date・scope 等の構造フィールドは除外
- 全件エクスポートボタン：YAML / JSON / BibTeX / Hayagriva / RIS / CSL-JSON / 参考文献テキスト
- 各行には詳細ページへのリンクを含む
- ページ上部に JA / EN 言語切り替えボタン（`default_language` 設定に連動）

### 詳細ページ（`public/entries/<id>/index.html`）

- 全フィールドを整形して表示（アブストラクトも表示）
- 添付ファイルへのリンク（`files/` 内のパスは相対パスで解決）
- 外部URL（DOI等）へのリンク
- 著者ハイライト：`config.yaml` の `highlight_authors` リストと照合し、一致する著者名に `highlight_style` を適用
- 「このエントリをエクスポート」ボタン：YAML / JSON / BibTeX / Hayagriva / RIS / CSL-JSON / 参考文献テキスト（1件）
- 前後ナビゲーション：一覧と同じソート順で「← 前の業績」「次の業績 →」リンクを表示
- OGP / Twitter Card メタタグ：`og:title`・`og:description`（abstract 優先）・`og:url`（`base_url` 設定時）
- 印刷用 CSS（`@media print`）

### 著者ハイライト

- `config.yaml` の `highlight_authors` に複数の表記ゆれを列挙できる
- 著者リストを表示する際、一致する名前に `bold` または `underline` のスタイルを適用
- 完全一致で照合（大文字小文字を区別する）

### エクスポート機能（JavaScript、クライアントサイド）

**YAML / JSON**：保持データをそのまま出力（整形あり）

**BibTeX**：種別ごとに以下のエントリタイプにマッピング

| 種別 | BibTeXエントリタイプ |
| --- | --- |
| `conference` | `@inproceedings` |
| `journal` | `@article` |
| `talk` | `@misc` |
| `patent` | `@misc` |
| `award` | `@misc` |
| `book` | `@book` |
| `thesis` | `@phdthesis` / `@mastersthesis` / `@misc`（`degree` による） |
| `report` | `@techreport` |
| `misc` | `@misc` |
| `other` | `@misc` |

BibTeXのフィールドマッピング（主要なもの）：

| YAMLフィールド | BibTeXフィールド |
| --- | --- |
| `title` / `title_en` | `title` |
| `authors` | `author`（` and ` で結合） |
| `date` の年部分 | `year` |
| `source.journal_name` | `journal` |
| `source.volume` | `volume` |
| `source.number` | `number` |
| `source.pages` | `pages` |
| `source.doi` | `doi` |
| `source.proceedings` | `booktitle` |
| `source.publisher` | `publisher` |
| `abstract` | `abstract` |
| `organization` | `organization` |
| `url` | `url` |

**Hayagriva**：種別ごとに Hayagriva YAML 形式（[typst/hayagriva](https://github.com/typst/hayagriva)）に変換

| scholist 種別 | Hayagriva 型 | 備考 |
| --- | --- | --- |
| `conference` | `article` + `proceedings` parent | `source.proceedings` を parent title に |
| `journal` | `article` + `periodical` parent | 巻・号は parent に |
| `book` | `book` / `chapter` | `source.chapter` or `source.pages` があれば `chapter` |
| `thesis` | `thesis` | `source.degree` → `genre`、`source.institution` → `organization` |
| `report` | `report` | `source.number` → `serial-number.serial` |
| `patent` | `patent` | `source.patent_number` → `serial-number` |
| `talk` / `award` / `misc` / `other` | `misc` | |

- `title` / `title_en` のどちらを使うかは `language` フィールドで制御（`en` → `title_en`、それ以外 → `title`）
- `abstract` がある場合は Hayagriva の `abstract` フィールドに出力
- `url` が `https://doi.org/...` の場合は `serial-number.doi` に変換

**RIS**：種別ごとに `TY` タグにマッピング

| scholist 種別 | RIS `TY` | 備考 |
| --- | --- | --- |
| `journal` | `JOUR` | |
| `conference` | `CONF` | |
| `book` | `BOOK` / `CHAP` | `source.chapter` or `source.pages` があれば `CHAP` |
| `thesis` | `THES` | `source.degree` → `M1`（"Doctoral dissertation" 等） |
| `report` | `RPRT` | |
| `patent` | `PAT` | |
| `talk` / `award` | `GEN` | |
| `misc` / `other` | `MISC` | |

日付は `YYYY/MM/DD/`・`YYYY/MM/`・`YYYY/` 形式。ページは `SP`/`EP` に分割（` -- ` 区切り対応）。

**CSL-JSON**：種別ごとに CSL type にマッピング

| scholist 種別 | CSL `type` | 備考 |
| --- | --- | --- |
| `journal` | `article-journal` | |
| `conference` | `paper-conference` | |
| `book` | `book` / `chapter` | `source.chapter` or `source.pages` があれば `chapter` |
| `thesis` | `thesis` | `source.degree` → `genre` |
| `report` | `report` | |
| `patent` | `patent` | |
| `talk` | `speech` | |
| `award` / `misc` / `other` | `article` | |

著者名は `{"literal": "山田 太郎"}` 形式（family/given への分割なし）。日付は `issued.date-parts` 形式。

**参考文献テキスト（reftext）**：日本語学術論文風の人間可読テキスト（`.txt`）を出力

出力形式：`著者1, 著者2: "タイトル", 出典情報 (年).`

- 著者名は加工なし（略称化・並び順変更なし）
- ページ数は `pp.X-Y` 形式（全種別で統一）
- `award` は award_name を引用符なしで主体とし `org_giving_award` を続ける
- `thesis` は degree → `博士論文` / `修士論文` / `学士論文` に変換

| 種別 | 出典部の構成 |
| --- | --- |
| `journal` | 誌名, Vol.X, No.Y, pp.P1-P2 |
| `conference` | 論文集名（または会議名）, 開催地, pp.P1-P2 |
| `talk` | 説明（または会場名）, 開催地 |
| `thesis` | 学位種別（博士論文等）, 機関名 |
| `report` | Technical Report 番号, 機関名 |
| `patent` | 特許番号, 国 |
| `book` | 出版社, 章, pp.P1-P2 |
| `misc` / `other` | source.description |
| `award` | award_name, org_giving_award（タイトルに引用符なし） |

---

## `build.py` の仕様

```text
使い方: python build.py [--output public/]

処理手順:
1. pyproject.toml からバージョン番号を読み込む（Python 3.11+ は tomllib、それ以前は正規表現）
2. data/config.yaml を読み込む
3. data/publications.yaml を読み込む
4. バリデーション：
   - id の重複チェック・使用可能文字チェック（英数字・ハイフン・アンダースコア）
   - title / title_en の少なくとも一方が存在するか
   - authors が1名以上存在するか
   - type が定義済み10種のいずれかか
   - date・registered_at のフォーマット（YYYY-MM-DD または YYYY-MM）と値の妥当性
   - scope・paper_type・source.status・source.degree の列挙値チェック
   - files の各要素に path または url が存在するか
   - エラーは stderr に出力。GitHub Actions 環境では ::error:: アノテーション形式で出力
5. ソート（date降順、同日はYAML記述順、null は末尾）
6. 各エントリに `_searchtext`（全文検索用文字列）と `_authors_hl`（ハイライト情報）を付与
7. Jinja2でテンプレートをレンダリング（バージョン番号を `scholist_version` としてテンプレートに渡す）
   - public/index.html（一覧ページ）
   - public/entries/<id>/index.html（詳細ページ、全エントリ分）
8. base_url が設定されている場合、public/sitemap.xml を生成
9. base_url が設定されている場合、public/feed.xml（Atom フィード）を生成
10. static/ を public/static/ にコピー
11. files/ を public/files/ にコピー

依存パッケージ（requirements.txt に記載）:
  PyYAML
  Jinja2
```

---

## `tools/import.py` の仕様

```text
使い方: python tools/import.py --format <形式> <入力ファイル> [オプション]

オプション:
  --format, -f  利用可能な形式（起動時に自動検出）（必須）
  --output, -o  出力先ファイル（省略時: 標準出力）
  --append, -a  既存の publications.yaml に追記（ID 重複はスキップ）

処理の特徴:
- 変換できなかったフィールドは note に [import: field=value] 形式で記録
- 著者名フォーマット（BibTeX: 「姓, 名」形式）は変換せずそのまま出力し警告
- 月なし日付（year のみ）は YYYY-01 に設定し警告
- stderr に WARNING として問題点を出力
```

### プラグインアーキテクチャ

`import.py` は起動時に `importers/` ディレクトリを `pkgutil.iter_modules` でスキャンし、
`IMPORTER_CLASS` 変数と `format_name` クラス属性を持つモジュールを自動登録する。
`--format` の選択肢と description はその結果から動的に生成される。

**新フォーマットの追加方法：**

```python
# tools/importers/my_format.py
from . import BaseImporter

class MyFormatImporter(BaseImporter):
    format_name = 'my_format'   # --format に渡す名前

    def load(self, filepath: str) -> list[dict]:
        ...  # エントリ dict のリストを返す

IMPORTER_CLASS = MyFormatImporter  # このモジュール変数で検出される
```

- `import.py` 本体を修正する必要はない
- 依存パッケージが未インストールの場合、そのインポーターは自動的に非表示になる
- ユーザーが `importers/` に追加したファイルは sync で消えない（scholist にないファイルは git checkout で削除されない）

### 型マッピング（BibTeX → scholist）

| BibTeX 型 | scholist 型 | 判定条件 |
| --- | --- | --- |
| `@article` | `journal` | `journal` フィールドあり |
| `@article` | `conference` | `booktitle` フィールドあり |
| `@article` | `misc` | どちらもない |
| `@inproceedings` / `@proceedings` | `conference` | |
| `@book` | `book` | |
| `@incollection` | `book` | chapter 相当 |
| `@phdthesis` | `thesis`（degree: doctoral） | |
| `@mastersthesis` | `thesis`（degree: master） | |
| `@techreport` | `report` | |
| その他 | `misc` | |

### 型マッピング（Hayagriva → scholist）

| Hayagriva 型 + parent | scholist 型 |
| --- | --- |
| `article` + `periodical` parent | `journal` |
| `article` + `proceedings` / `conference` parent | `conference` |
| `thesis` | `thesis`（`genre` フィールドから degree を推定） |
| `report` | `report` |
| `patent` | `patent` |
| `book` / `chapter` | `book` |
| その他 | `misc` |

### 型マッピング（RIS → scholist）

| RIS `TY` | scholist 型 |
| --- | --- |
| `JOUR` / `EJOU` / `MGZN` / `ABST` / `JFULL` | `journal` |
| `CONF` / `CPAPER` | `conference` |
| `BOOK` / `EBOOK` | `book` |
| `CHAP` / `ECHAP` | `book`（chapter 相当） |
| `THES` | `thesis`（`M1` / `ET` フィールドから degree を推定） |
| `RPRT` | `report` |
| `PAT` | `patent` |
| その他 | `misc` |

主なタグマッピング：`AU` → `authors`、`TI`/`T1` → `title_en`、`PY`/`Y1`/`DA` → `date`、`DO` → `url`（DOI）、
`JO`/`JF` → `source.journal_name`（journal）、`T2`/`BT` → `source.proceedings`（conference）、
`VL` → `source.volume`、`IS` → `source.number`、`SP`/`EP` → `source.pages`。
日付形式 `YYYY/MM/DD/`・`YYYY/MM/`・`YYYY` を解析。`YYYY` のみの場合は `YYYY-01` に設定して警告。
ID タグ不在時は `ris-import-N` を自動割当て。外部依存なし（標準ライブラリのみ）。

### 型マッピング（CSL-JSON → scholist）

| CSL-JSON `type` | scholist 型 |
| --- | --- |
| `article-journal` | `journal` |
| `paper-conference` | `conference` |
| `book` / `chapter` / `entry-encyclopedia` | `book` |
| `thesis` | `thesis`（`genre` フィールドから degree を推定） |
| `report` | `report` |
| `patent` | `patent` |
| `speech` | `talk` |
| その他 | `misc` |

主なフィールドマッピング：`author[{family,given}]` → `authors`（`family given` 形式に結合）、`title` → `title_en`（`language: ja` の場合は `title`）、`issued.date-parts` → `date`、`DOI` → `url`（DOI）、`container-title` → `source.journal_name`（journal）または `source.proceedings`（conference）、`volume`/`issue` → `source.volume`/`source.number`、`publisher` → `source.institution`（thesis/report）または `organization`（conference）、`genre` → `source.degree`（thesis）。
`issued.date-parts` が年のみの場合は `YYYY-01` に設定して警告。`id` 不在時は `csl-import-N` を自動割当て。外部依存なし（標準ライブラリのみ）。

依存パッケージ（requirements-tools.txt に記載）:
  bibtexparser >= 1.3, < 2.0（BibTeX インポート時のみ必要）

---

## GitHub Actions

### `build.yml`（自動ビルド・デプロイ）

- トリガー：`data/`・`files/`・`templates/`・`static/`・`build.py`・`requirements.txt` への push、および `workflow_dispatch`
- 処理：
  1. Python 環境セットアップ
  2. `pip install -r requirements.txt`
  3. `python build.py`
  4. `public/` を GitHub Pages にデプロイ（`peaceiris/actions-gh-pages` 使用、`gh-pages` ブランチ）

### `test.yml`（自動テスト）

- トリガー：`main` ブランチへの push / PR
- 処理：`pip install -r requirements-dev.txt` → `pytest -v`

### `release-asset.yml`（リリース asset 生成）

- トリガー：`v*` タグ push、および `workflow_dispatch`（タグ指定）
- 処理：開発ファイルを除いた `scholist-vX.Y.Z-template.zip` を生成し GitHub Release にアタッチ
- 除外対象：`tests/`・`requirements-dev.txt`・`.github/workflows/test.yml`・`CLAUDE.md`・`.markdownlint.json`・`TODO.md`
- `extras/sync-from-scholist.yml` を `.github/workflows/sync-from-scholist.yml` として zip に同梱

---

## nginx 運用時の設定例

```nginx
server {
    listen 80;
    server_name your-domain.example.com;
    root /path/to/publications/public;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

`build.py` 実行後に `public/` をnginxのルートとして配信するだけでよい。

---

## 配布パッケージ・sync の対象ファイル

**「配布パッケージ（template zip）に含まれるファイル」と「sync-from-scholist.yml の取り込み対象」は常に一致させる。**
新しいファイルやディレクトリを追加したとき、以下を忘れずに更新すること。

| 更新先 | ファイル |
| --- | --- |
| `.github/workflows/release-asset.yml` | `cp -r` の列挙 |
| `extras/sync-from-scholist.yml` | `git checkout upstream/${REF} --` の列挙 |
| `README.md`・`README.en.md` | ツールファイル表と手動 sync コマンド |

**現在の対象ファイル一覧：**

```text
build.py
templates/
static/
tools/                  ← BibTeX/Hayagriva インポート CLI
requirements.txt
requirements-tools.txt  ← tools/ の依存パッケージ
pyproject.toml
README.md
README.en.md
LICENSE
.gitignore
.github/workflows/build.yml   （手動のみ：GITHUB_TOKEN 制限）
.github/workflows/sync-from-scholist.yml  （extras/ 経由のみ）
```

**sync しない（ユーザーデータ）：**

```text
data/
files/
CHANGELOG.md
```

---

## 実装上の注意事項

- `extras/sync-from-scholist.yml` は **ユーザーのリポジトリ向けワークフロー**であり、scholist 自身の `.github/workflows/` には置かない。
  もし scholist の `.github/workflows/` に置くと GitHub Actions がここで実行しようとするため、
  「scholist が scholist から自分自身へ sync する」という無意味な動作になる。
  そのため `extras/` を"配布物専用の置き場"として使い、`release-asset.yml` が zip 作成時に
  `.github/workflows/` へコピーする構造にしている。

- `public/` ディレクトリは生成物なので `.gitignore` に含めるか、GitHub Pages デプロイ専用ブランチ（`gh-pages`）に出力する
- エクスポート機能（YAML/JSON/BibTeX/Hayagriva/RIS/CSL-JSON/参考文献テキスト）はすべてクライアントサイドJavaScriptで実装し、サーバサイド処理を不要にする
- BibTeXの `author` フィールドは `山田 太郎 and 鈴木 花子` のように ` and ` で結合する（姓名の順序はデータそのままを使用）
- GitHub Pages と nginx の両対応のため、すべてのリンクはルート相対パス（`/entries/xxx/`）ではなく相対パスで記述する（`../` 等）か、`config.yaml` に `base_url` を設けて切り替えられるようにする
