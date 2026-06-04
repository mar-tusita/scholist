# scholist

個人（または小人数グループ）の研究業績データを YAML で管理し、静的 HTML として生成・公開する Web ツールです。

- データは `data/publications.yaml` に YAML テキストで記述
- `python build.py` で静的 HTML を生成
- GitHub Pages または nginx で配信
- ページ上の **JA / EN** ボタンで日本語・英語を切り替え可能

## 動作環境

- Python 3.10 以上
- PyYAML, Jinja2（`requirements.txt` に記載）

## セットアップ

### 方法 A：テンプレート zip をダウンロードする（推奨）

[Releases](https://github.com/mar-tusita/scholist/releases/latest) から
`scholist-vX.Y.Z-template.zip` をダウンロードして展開します。
テスト・開発用ファイルを含まない最小構成で、**sync ワークフロー（`sync-from-scholist.yml`）も同梱**されています。

```bash
unzip scholist-vX.Y.Z-template.zip -d my-publications
cd my-publications
pip install -r requirements.txt
```

その後、GitHub にリポジトリを作成して push してください。

```bash
git init
git add -A
git commit -m "Initial commit"
git remote add origin https://github.com/your-username/your-repo.git
git push -u origin main
```

### 方法 B：GitHub テンプレートから始める

[リポジトリページ](https://github.com/mar-tusita/scholist) の
「Use this template」ボタンから自分のリポジトリを作成します。
テスト・開発用ファイルも含まれます。業績の記録にしか使わない場合は以下を削除できます。

```text
tests/
requirements-dev.txt
.github/workflows/test.yml
.markdownlint.json
CLAUDE.md
TODO.md
extras/
```

> **`extras/` について：** ツール更新の自動同期ワークフロー（`sync-from-scholist.yml`）が入っています。
> 使う場合はコピーしてから削除してください。
>
> ```bash
> cp extras/sync-from-scholist.yml .github/workflows/
> ```
>
> 使わない場合はそのまま削除できます。

### 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

## 業績データの編集

`data/publications.yaml` を編集します。すべてのエントリは `entries:` キーの下にリストで記述します。

```yaml
entries:
  - id: "yamada-2024-ipsj-example"
    type: conference
    title: "論文タイトル"
    title_en: "Paper Title"
    authors:
      - "山田 太郎"
      - "鈴木 花子"
    date: "2024-03-15"
    organization: "情報処理学会"
    presenter: "山田 太郎"
    scope: domestic        # domestic / international
    invited: false
    reviewed: false
    venue: "情報処理学会 第86回全国大会"
    source:
      proceedings: "情報処理学会第86回全国大会講演論文集"
      pages: "1-1 -- 1-2"
    url: "https://doi.org/xxxx"
```

### 種別（`type`）

| 値 | 意味 |
| --- | --- |
| `conference` | 国内・国際会議 |
| `journal` | 国内・国際論文誌 |
| `talk` | 講演 |
| `patent` | 特許 |
| `award` | 受賞 |
| `book` | 書籍 |
| `thesis` | 学位論文（学士・修士・博士） |
| `report` | 技術レポート |
| `misc` | 解説等 |
| `other` | その他 |

種別ごとの詳細フィールドは [CLAUDE.md](CLAUDE.md) のデータスキーマ節を参照してください。

全種別で使える主な任意フィールド：

| フィールド | 説明 |
| --- | --- |
| `abstract` | アブストラクト。詳細ページに表示、BibTeX/Hayagriva エクスポートにも含まれる |
| `language` | 言語コード（`ja`、`en` 等）。`title` と `title_en` 両方ある場合に Hayagriva エクスポートで使用 |

### 添付ファイルの配置

PDF・スライド等は `files/` ディレクトリに置き、`publications.yaml` で参照します。

```yaml
files:
  - label: "発表スライド"
    path: "files/2024-conf-001-slides.pdf"
  - label: "論文PDF"
    url: "https://example.com/paper.pdf"   # 外部URLも可
```

## サイト設定

`data/config.yaml` を編集します。

```yaml
highlight_authors:
  - "山田 太郎"
  - "Taro Yamada"
  - "T. Yamada"
highlight_style: underline   # bold または underline

site_title: "研究業績一覧"

# 初回訪問者（localStorage 未設定）に表示する言語
# auto: ブラウザ言語を検出（ja → 日本語、それ以外 → 英語）
# ja:   常に日本語で開始  / en: 常に英語で開始
default_language: auto

# 一覧ページの初期表示件数（「さらに表示」で同数ずつ追加）
# 0 または未設定の場合は全件表示
entries_per_page: 30

# サイトの公開 URL（og:url / 将来の sitemap.xml 用）末尾スラッシュなし
# 例: https://username.github.io/publications
# 空文字または未設定の場合、og:url は出力しない
base_url: ""
```

`highlight_authors` に列挙した名前は一覧・詳細ページで強調表示されます。各エントリは**正規表現**として評価されます。

```yaml
highlight_authors:
  - "山田 ?太郎"   # 「山田太郎」「山田 太郎」どちらもマッチ（. より安全）
  - "Taro Yamada"
  - "T\\. Yamada"  # ピリオドを文字通りに使うには \. と書く
```

`base_url` を設定すると以下が有効になります。GitHub Pages で運用する場合は `https://username.github.io/repository-name` を設定してください。

- 詳細ページの OGP タグに `og:url` を追加（SNS での URL プレビューが正確になる）
- `public/sitemap.xml` の自動生成
- `public/feed.xml`（Atom フィード）の自動生成

## 既存データのインポート

BibTeX や Hayagriva 形式で管理していた文献データを `publications.yaml` に変換できます。

### セットアップ

```bash
pip install -r requirements-tools.txt
```

`bibtexparser` が追加でインストールされます（BibTeX のみ必要、Hayagriva は不要）。

### 使い方

```bash
# BibTeX から変換して標準出力に出力
python tools/import.py --format bibtex refs.bib

# ファイルに書き出す
python tools/import.py --format bibtex refs.bib --output data/publications.yaml

# 既存の publications.yaml に追記（ID 重複をチェックしてスキップ）
python tools/import.py --format bibtex refs.bib --append data/publications.yaml

# Hayagriva から変換
python tools/import.py --format hayagriva refs.yml --append data/publications.yaml
```

変換できなかったフィールドは `note` に `[import: field=value]` 形式で記録されます。
著者名フォーマット（BibTeX: 「姓, 名」形式）や月なし日付など、確認が必要な点は
stderr に警告として出力されます。

## ビルド

```bash
python build.py
```

`public/` ディレクトリに HTML が生成されます。

```text
public/
├── index.html            # 一覧ページ
├── entries/
│   └── <id>/
│       └── index.html   # 詳細ページ
├── static/              # CSS, JS
└── files/               # 添付ファイル（コピー）
```

出力先を変更する場合：

```bash
python build.py --output /var/www/html
```

## デプロイ

### GitHub Pages

`.github/workflows/build.yml` が含まれています。`data/` または `files/` への push 時に
自動でビルドし、`gh-pages` ブランチにデプロイします。

リポジトリの Settings → Pages → Branch を `gh-pages` に設定してください。

### nginx

```bash
python build.py --output /var/www/scholist
```

nginx 設定例：

```nginx
server {
    listen 80;
    server_name your-domain.example.com;
    root /var/www/scholist;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

### カスタムインポーターの追加

独自フォーマットのインポーターを追加できます。`tools/importers/` に以下の形式でファイルを作成するだけで、`import.py` が自動的に検出します。**`import.py` 本体の修正は不要です。**

```python
# tools/importers/my_format.py
from . import BaseImporter

class MyFormatImporter(BaseImporter):
    format_name = 'my_format'  # --format に渡す名前

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

## ツールのアップデート

このリポジトリをテンプレートとして使い始めた場合、scholist 本体が更新されたときにその変更を取り込む手順を説明します。

### 基本的な考え方

自分のリポジトリの中身は2種類に分かれます。

| 種別 | ファイル |
| --- | --- |
| **ツールファイル**（更新を取り込む） | `build.py`, `templates/`, `static/`, `tools/`, `requirements.txt`, `requirements-tools.txt`, `pyproject.toml`, `README.md`, `README.en.md`, `.github/workflows/build.yml` |
| **自分のデータ**（絶対に上書きしない） | `data/`, `files/`, `CHANGELOG.md` |

`git merge` を使うと両方が混ざってしまうため、**ツールファイルだけを選んで取り込む**方法を使います。

### 初回のみ：upstream リモートを登録する

```bash
git remote add upstream https://github.com/mar-tusita/scholist.git
```

### scholist が更新されたときの手順

```bash
# 1. scholist の最新コミットを取得
git fetch upstream

# 2. ツールファイルだけを上書き（data/ と files/ は触れない）
git checkout upstream/main -- \
  build.py \
  templates/ \
  static/ \
  tools/ \
  requirements.txt \
  requirements-tools.txt \
  pyproject.toml \
  README.md \
  README.en.md \
  .github/workflows/build.yml

# 3. 変更をコミット・プッシュ
git commit -m "chore: sync tool files from scholist vX.Y.Z"
git push
```

特定のバージョンタグに合わせたい場合は `upstream/main` の代わりに `upstream/v0.2.0` のように指定します。

> **注意（手動 sync の場合）：** `git push` 後は GitHub Pages の再ビルドを手動で起動する必要があります。
> push によるコミットはツールファイルを更新しますが、
> GitHub Actions はボット以外のコミットでないとビルドワークフローを自動起動しません。
> push 後にリポジトリの **Actions → "Build and Deploy" → Run workflow** を実行してください。
> ワークフローを使って sync する場合はこの手順は不要です（自動でビルドが起動します）。

### GitHub Actions で自動化する（任意）

手動でコマンドを打つ代わりに、GitHub の画面からボタン一つで同期することもできます。

**方法 A（zip ダウンロード）：** `.github/workflows/sync-from-scholist.yml` が既に含まれているため、追加作業は不要です。

**方法 B（GitHub テンプレート）：** `extras/sync-from-scholist.yml` が同梱されています。
以下でコピーしてください（方法 B の「`extras/` について」で案内している手順と同じです）。

```bash
cp extras/sync-from-scholist.yml .github/workflows/
```

追加後は、リポジトリの **Actions → "Sync tool files from scholist" → Run workflow** で実行できます。sync が完了すると自動で Build and Deploy が起動します。

> **注意：** ワークフローは `.github/workflows/build.yml` を sync 対象に含みません。
> `GITHUB_TOKEN` は GitHub のセキュリティ制限によりワークフローファイルを書き込めないためです。
> `build.yml` に変更があった場合は、上記の手動 sync 手順でコピーしてください（手動実行なら書き込めます）。

## 主な機能

- **統計サマリー**：一覧ページ上部に総件数・年範囲・種別ごとの件数チップを表示
- **フィルタ**：種別・年・国内/国際・査読有無・招待有無で絞り込み（条件は URL に保持・共有可能）
  フィルタ条件は以下のクエリパラメータで直接指定できます：

  | パラメータ | 値の例 | 説明 |
  | --- | --- | --- |
  | `type` | `journal` | 種別（`conference` / `journal` / `talk` / `patent` / `award` / `book` / `thesis` / `report` / `misc` / `other`） |
  | `year` | `2024` | 年（4桁） |
  | `scope` | `domestic` | 国内/国際（`domestic` / `international`） |
  | `reviewed` | `true` | 査読（`true` / `false`） |
  | `invited` | `true` | 招待（`true` / `false`） |
  | `q` | `yamada` | 検索語（タイトル・著者・abstract 等の全文） |

  例：`https://example.github.io/publications/?type=journal&year=2023`

- **インクリメンタル検索**：タイトル・著者・会議名・誌名・アブストラクトを横断検索
- **ページネーション**：`entries_per_page` 件ずつ表示し「さらに表示」「全件表示」で読み込む
- **前後ナビゲーション**：詳細ページ下部に「← 前の業績」「次の業績 →」リンクを表示
- **エクスポート**：全件または1件を YAML / JSON / BibTeX / Hayagriva でダウンロード
- **インポート**：BibTeX・Hayagriva 形式から `publications.yaml` に変換（`tools/import.py`）
- **著者ハイライト**：設定した著者名を太字またはアンダーライン表示
- **言語切り替え**：ページ上の JA / EN ボタンで日本語と英語を切り替え（`localStorage` で保持）
- **OGP 対応**：詳細ページを SNS で共有するとタイトル・著者・会議名のプレビューを表示
- **sitemap.xml 生成**：`base_url` を設定すると検索エンジン向け sitemap を自動生成
- **Atom フィード生成**：`base_url` を設定すると `feed.xml` を自動生成（日付のあるエントリを bibliography 形式で収録）

## 開発者向け

### 開発環境のセットアップ

```bash
pip install -r requirements-dev.txt
```

`requirements.txt`（本番依存）に加えて `pytest` がインストールされます。

### テストの実行

```bash
pytest -v
```

`tests/test_build.py` に `build.py` のロジック関数（`validate`・`sort_entries`・`highlight_authors`・`read_version`）のユニットテストが含まれています。

`build.py` を変更するときは、テストが引き続き通ることを確認してください。

### ローカルビルドの確認

```bash
python build.py
```

`public/` に HTML が生成されます。ブラウザで `public/index.html` を開いて動作を確認できます。

### ファイル構成（ツール側）

| ファイル | 役割 |
| --- | --- |
| `build.py` | 静的サイト生成スクリプト本体 |
| `templates/` | Jinja2 テンプレート |
| `static/` | CSS・JavaScript |
| `data/` | サンプルデータ（テスト兼ドキュメント） |
| `tests/` | pytest テストスイート |
| `pyproject.toml` | バージョン・pytest 設定 |
| `requirements.txt` | 本番依存（PyYAML, Jinja2） |
| `requirements-dev.txt` | 開発依存（pytest） |

### リリース手順

1. `pyproject.toml` のバージョンを更新する
2. `CHANGELOG.md` の `[Unreleased]` を `[vX.Y.Z] - YYYY-MM-DD` に確定する
3. コミット・push する

   ```bash
   git add pyproject.toml CHANGELOG.md
   git commit -m "chore: release X.Y.Z"
   git push origin main
   ```

4. タグを作成・push する（これだけで Release 作成と template zip の配布まで自動完結）

   ```bash
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```

> **リリースノートを手書きする場合：** 手順 4 の前に `gh release create vX.Y.Z --title "..." --notes "..."` を実行しておくと、ワークフローは Release 作成をスキップして zip のアップロードだけ行います。

## 謝辞

このツールの開発にあたり、以下のプロジェクト・サービスを利用しました。

- **[Jinja2](https://jinja.palletsprojects.com/)・[PyYAML](https://pyyaml.org/)** ― Python による HTML 生成とデータ読み込み
- **[js-yaml](https://github.com/nodeca/js-yaml)** ― クライアントサイドの YAML エクスポート
- **[peaceiris/actions-gh-pages](https://github.com/peaceiris/actions-gh-pages)** ― GitHub Pages への自動デプロイ
- **[GitHub Actions](https://github.com/features/actions)** ― CI/CD 基盤
- **[Claude Code](https://claude.ai/code) (Anthropic)** 本ツールの開発全般にわたって利用しました。 ツール作成にあたり、「どこまで機械がプログラムを書けるのか、人間が機械をどのように活用できるのか」を模索する実験的な試みとして、コード生成からドキュメント作成まで幅広く活用しています。

## ライセンス

[LICENSE](LICENSE) を参照してください。
