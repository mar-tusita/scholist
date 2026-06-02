# scholist

個人（または小人数グループ）の研究業績データを YAML で管理し、静的 HTML として生成・公開する Web ツールです。

- データは `data/publications.yaml` に YAML テキストで記述
- `python build.py` で静的 HTML を生成
- GitHub Pages または nginx で配信

## 動作環境

- Python 3.10 以上
- PyYAML, Jinja2（`requirements.txt` に記載）

## セットアップ

```bash
git clone https://github.com/mar-tusita/scholist.git
cd scholist
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
| `misc` | 解説等 |
| `other` | その他 |

種別ごとの詳細フィールドは [CLAUDE.md](CLAUDE.md) のデータスキーマ節を参照してください。

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

# サイトの公開 URL（og:url / 将来の sitemap.xml 用）末尾スラッシュなし
# 例: https://username.github.io/publications
# 空文字または未設定の場合、og:url は出力しない
base_url: ""
```

`highlight_authors` に列挙した名前は一覧・詳細ページで強調表示されます。表記ゆれを複数列挙できます。

`base_url` を設定すると、詳細ページの OGP タグに `og:url` が追加され、SNS での URL プレビューが正確になります。GitHub Pages で運用する場合は `https://username.github.io/repository-name` を設定してください。

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

## ツールのアップデート

このリポジトリをテンプレートとして使い始めた場合、scholist 本体が更新されたときにその変更を取り込む手順を説明します。

### 基本的な考え方

自分のリポジトリの中身は2種類に分かれます。

| 種別 | ファイル |
| --- | --- |
| **ツールファイル**（更新を取り込む） | `build.py`, `templates/`, `static/`, `requirements.txt`, `pyproject.toml`, `.github/workflows/build.yml` |
| **自分のデータ**（絶対に上書きしない） | `data/`, `files/`, `README.md`, `CHANGELOG.md` |

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
  requirements.txt \
  pyproject.toml \
  .github/workflows/build.yml

# 3. 変更をコミット・プッシュ
git commit -m "chore: sync tool files from scholist vX.Y.Z"
git push
```

特定のバージョンタグに合わせたい場合は `upstream/main` の代わりに `upstream/v0.2.0` のように指定します。

> **注意：** sync 後は GitHub Pages の再ビルドを手動で起動する必要があります。
> `git push` によるコミットはツールファイルを更新しますが、
> GitHub Actions はボット以外のコミットでないとビルドワークフローを自動起動しません。
> push 後にリポジトリの **Actions → "Build and Deploy" → Run workflow** を実行してください。

### GitHub Actions で自動化する（任意）

手動でコマンドを打つ代わりに、GitHub の画面からボタン一つで同期することもできます。自分のリポジトリに以下のファイルを追加してください。

> **注意：** ワークフローは `.github/workflows/build.yml` を sync 対象に含みません。
> `GITHUB_TOKEN` は GitHub のセキュリティ制限によりワークフローファイルを書き込めないためです。
> `build.yml` に変更があった場合は、上記の手動 sync 手順でコピーしてください（手動実行なら書き込めます）。

**`.github/workflows/sync-from-scholist.yml`**

```yaml
name: Sync tool files from scholist

on:
  workflow_dispatch:
    inputs:
      ref:
        description: 'scholist のブランチ・タグ・SHA（例: main, v0.2.0）'
        default: 'main'
        required: false

permissions:
  contents: write

jobs:
  sync:
    runs-on: ubuntu-latest
    env:
      FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Fetch scholist
        run: |
          git remote add upstream https://github.com/mar-tusita/scholist.git
          git fetch upstream

      - name: Sync tool files
        run: |
          REF="${{ github.event.inputs.ref }}"
          REF="${REF:-main}"
          git checkout "upstream/${REF}" -- \
            build.py \
            templates/ \
            static/ \
            requirements.txt \
            pyproject.toml

      - name: Commit and push if changed
        run: |
          REF="${{ github.event.inputs.ref }}"
          REF="${REF:-main}"
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          if git diff --cached --quiet; then
            echo "No changes. Already up to date."
          else
            SCHOLIST_SHA=$(git rev-parse "upstream/${REF}")
            git commit -m "chore: sync tool files from scholist ${SCHOLIST_SHA:0:7}"
            git push
          fi
```

追加後は、リポジトリの **Actions → "Sync tool files from scholist" → Run workflow** で実行できます。

## 主な機能

- **フィルタ**：種別・年・国内/国際・査読有無・招待有無で絞り込み
- **インクリメンタル検索**：タイトル・著者・会議名・誌名を横断検索
- **エクスポート**：全件または1件を YAML / JSON / BibTeX でダウンロード
- **著者ハイライト**：設定した著者名を太字またはアンダーライン表示

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

## ライセンス

[LICENSE](LICENSE) を参照してください。
