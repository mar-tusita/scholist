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

# サイトの公開 URL（og:url / sitemap.xml / feed.xml 用）末尾スラッシュなし
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

`show_entry_id: true` にすると詳細ページのバッジ右端にエントリ ID が表示されます。YAML ファイルの手動編集時や `import.py --append` 時の確認に便利です。デフォルトは `false`（非表示）です。

`base_url` を設定すると以下が有効になります。GitHub Pages で運用する場合は `https://username.github.io/repository-name` を設定してください。

- 詳細ページの OGP タグに `og:url` を追加（SNS での URL プレビューが正確になる）
- `public/sitemap.xml` の自動生成
- `public/feed.xml`（Atom フィード）の自動生成

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

## 既存データのインポート

BibTeX・Hayagriva・RIS・CSL-JSON 形式のデータを `publications.yaml` に変換できます。

詳細は **[docs/import.md](docs/import.md)** を参照してください（使い方・対応フォーマット・カスタムインポーターの追加）。

## デプロイ

GitHub Pages または nginx でサイトを公開できます。

詳細は **[docs/deployment.md](docs/deployment.md)** を参照してください（GitHub Pages・nginx 設定例・添付ファイルのアクセス制御）。

## ツールのアップデート

scholist 本体が更新されたとき、ツールファイルのみを取り込む手順です。

詳細は **[docs/update.md](docs/update.md)** を参照してください（手動 sync・GitHub Actions 自動化）。

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
- **エクスポート**：全件または1件を YAML / JSON / BibTeX / Hayagriva / RIS / CSL-JSON / 参考文献テキスト でダウンロード
- **インポート**：BibTeX・Hayagriva・RIS・CSL-JSON 形式から `publications.yaml` に変換（`tools/import.py`）
- **著者ハイライト**：設定した著者名を太字またはアンダーライン表示
- **言語切り替え**：ページ上の JA / EN ボタンで日本語と英語を切り替え（`localStorage` で保持）
- **OGP 対応**：詳細ページを SNS で共有するとタイトル・著者・会議名のプレビューを表示
- **sitemap.xml 生成**：`base_url` を設定すると検索エンジン向け sitemap を自動生成
- **Atom フィード生成**：`base_url` を設定すると `feed.xml` を自動生成（日付のあるエントリを bibliography 形式で収録）

## 開発者向け

テスト実行・ローカルビルド確認・リリース手順など。

詳細は **[docs/development.md](docs/development.md)** を参照してください。

## 謝辞

このツールの開発にあたり、以下のプロジェクト・サービスを利用しました。

- **[Jinja2](https://jinja.palletsprojects.com/)・[PyYAML](https://pyyaml.org/)** ― Python による HTML 生成とデータ読み込み
- **[js-yaml](https://github.com/nodeca/js-yaml)** ― クライアントサイドの YAML エクスポート
- **[peaceiris/actions-gh-pages](https://github.com/peaceiris/actions-gh-pages)** ― GitHub Pages への自動デプロイ
- **[GitHub Actions](https://github.com/features/actions)** ― CI/CD 基盤
- **[Claude Code](https://claude.ai/code) (Anthropic)** 本ツールの開発全般にわたって利用しました。 ツール作成にあたり、「どこまで機械がプログラムを書けるのか、人間が機械をどのように活用できるのか」を模索する実験的な試みとして、コード生成からドキュメント作成まで幅広く活用しています。

## ライセンス

[LICENSE](LICENSE) を参照してください。
