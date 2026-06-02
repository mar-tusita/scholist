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
│   └── export.js                    # YAML/JSON/BibTeX書き出し処理
├── build.py                         # 静的サイト生成スクリプト
├── public/                          # 生成物（nginxまたはGitHub Pagesで配信）
│   ├── index.html
│   ├── entries/
│   │   └── <id>/
│   │       └── index.html
│   └── files/                       # files/ をそのままコピー
└── .github/
    └── workflows/
        └── build.yml                # push時に自動生成・デプロイ
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
| `type` | enum | ✅ | 種別（下記8種） |
| `title` | string | △ | 日本語タイトル（`title_en` と少なくとも一方必須） |
| `title_en` | string | △ | 英語タイトル（`title` と少なくとも一方必須） |
| `authors` | list[string] | ✅ | 著者リスト（順序を保持） |
| `date` | string | | 発表日・公開日（`YYYY-MM-DD` または `YYYY-MM`） |
| `registered_at` | string | | エントリ登録日（`YYYY-MM-DD`） |
| `organization` | string | | 学会名・組織名 |
| `presenter` | string | | 登壇者（会議・講演の場合） |
| `files` | list | | 添付ファイルリスト（下記参照） |
| `url` | string | | DOI または外部URL |
| `abstract` | string | | アブストラクト（詳細ページに表示、BibTeX にも出力） |
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

- 1行1エントリで表示
- デフォルト表示順：上記ソート規則に従う
- フィルタ機能（JavaScript）：
  - 種別（type）
  - 年（date の年部分）
  - 国内/国際（scope）
  - 査読有無（reviewed）
  - 招待有無（invited）
- インクリメンタル検索（JavaScript）：タイトル・著者名・会議名・誌名を対象
- 全件エクスポートボタン：YAML / JSON / BibTeX
- 各行には詳細ページへのリンクを含む

### 詳細ページ（`public/entries/<id>/index.html`）

- 全フィールドを整形して表示
- 添付ファイルへのリンク（`files/` 内のパスは相対パスで解決）
- 外部URL（DOI等）へのリンク
- 著者ハイライト：`config.yaml` の `highlight_authors` リストと照合し、一致する著者名に `highlight_style` を適用
- 「このエントリをエクスポート」ボタン：YAML / JSON / BibTeX（1件）

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
| `organization` | `organization` |
| `url` | `url` |

---

## `build.py` の仕様

```text
使い方: python build.py [--output public/]

処理手順:
1. data/config.yaml を読み込む
2. data/publications.yaml を読み込む
3. バリデーション：
   - id の重複チェック
   - title / title_en の少なくとも一方が存在するか
   - type が定義済み8種のいずれかか
4. ソート（date降順、同日はYAML記述順、null は末尾）
5. Jinja2でテンプレートをレンダリング
   - public/index.html（一覧ページ）
   - public/entries/<id>/index.html（詳細ページ、全エントリ分）
6. static/ を public/static/ にコピー
7. files/ を public/files/ にコピー

依存パッケージ（requirements.txt に記載）:
  PyYAML
  Jinja2
```

---

## GitHub Actions（`.github/workflows/build.yml`）

- トリガー：`data/` または `files/` への push
- 処理：
  1. Python 環境セットアップ
  2. `pip install -r requirements.txt`
  3. `python build.py`
  4. `public/` を GitHub Pages にデプロイ（`peaceiris/actions-gh-pages` 等を使用）

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

## 実装上の注意事項

- `public/` ディレクトリは生成物なので `.gitignore` に含めるか、GitHub Pages デプロイ専用ブランチ（`gh-pages`）に出力する
- エクスポート機能（YAML/JSON/BibTeX）はすべてクライアントサイドJavaScriptで実装し、サーバサイド処理を不要にする
- BibTeXの `author` フィールドは `山田 太郎 and 鈴木 花子` のように ` and ` で結合する（姓名の順序はデータそのままを使用）
- GitHub Pages と nginx の両対応のため、すべてのリンクはルート相対パス（`/entries/xxx/`）ではなく相対パスで記述する（`../` 等）か、`config.yaml` に `base_url` を設けて切り替えられるようにする
