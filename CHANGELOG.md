# Changelog

このファイルはプロジェクトのすべての変更を記録します。
フォーマットは [Keep a Changelog](https://keepachangelog.com/ja/1.1.0/) に基づいています。

## [Unreleased]

### 追加

- エクスポート機能（`static/export.js`）に RIS・CSL-JSON 形式を追加
  - 一覧ページ：「全件 RIS」「全件 CSL-JSON」ボタン
  - 詳細ページ：「RIS」「CSL-JSON」ボタン
  - RIS：TY タグによる種別マッピング、日付は `YYYY/MM/DD/` 形式、SP/EP でページ範囲分割
  - CSL-JSON：著者名は `{"literal": "..."}` 形式（family/given 分割なし）、`issued.date-parts` 形式の日付

- `tools/importers/csl_json.py`：CSL-JSON 形式インポーターを追加（`--format csl-json`）
  - Zotero・Pandoc・Mendeley 等が出力する CSL-JSON（`.json`）を `publications.yaml` に変換
  - 標準ライブラリのみ使用（追加依存なし）
  - `type` フィールドによる種別マッピング：`article-journal` → `journal`、`paper-conference` → `conference`、`book`/`chapter` → `book`、`thesis` → `thesis`、`report` → `report`、`patent` → `patent`、`speech` → `talk`
  - `author` の `family`/`given` を `family given` 形式（スペース区切り）に結合
  - `language: ja` のエントリはタイトルを `title`（日本語）として格納
  - `issued.date-parts` の `[年, 月, 日]` 形式を解析
  - `tests/test_import.py` に 28 件のテストを追加（計201件）

- `tools/importers/ris.py`：RIS 形式インポーターを追加
  - Zotero・Mendeley・EndNote 等からのエクスポートファイル（`.ris`）を `publications.yaml` に変換
  - 標準ライブラリのみ使用（追加依存なし）
  - `TY` タグによる種別マッピング：`JOUR/EJOU/MGZN` → `journal`、`CONF/CPAPER` → `conference`、`BOOK/CHAP` → `book`、`THES` → `thesis`、`RPRT` → `report`、`PAT` → `patent`
  - 日付形式 `YYYY/MM/DD/`・`YYYY/MM/`・`YYYY` をすべて解析
  - ID タグ不在時の自動 ID 付与、ID 使用不可文字の自動置換
  - 変換不能フィールドは `note` に `[import: ...]` 形式で記録
  - `tests/test_import.py` に 25 件のテストを追加（計173件）

- 詳細ページ：エントリ ID の表示機能（`config.yaml` の `show_entry_id: true` で有効化）
  - バッジ行の右端にモノスペースで `ID: entry-id-value` を表示
  - デフォルト `false`（公開サイトでは非表示、管理・開発時にオンにする想定）
  - 印刷時は非表示、i18n 対応

### 修正

- `static/export.js`：YAML・BibTeX・Hayagriva エクスポート時の文字化けを修正
  - `download()` 関数で `text/` 系 MIME タイプに `; charset=utf-8` を自動付与
  - JSON は `application/json`（RFC で UTF-8 必須）のため影響なし

### 変更

- `build.py`：`highlight_authors` の照合を完全一致から `re.fullmatch()` による正規表現マッチに変更
  - `"山田.?太郎"` のように書くと「山田太郎」「山田 太郎」どちらもハイライト可能
  - 無効な正規表現はリテラル文字列にフォールバック（後方互換）
  - `"T. Yamada"` の `.` は正規表現では任意の1文字を意味する点に注意（厳密には `"T\. Yamada"`）
- `data/config.yaml`：`highlight_authors` のサンプルを `"山田 ?太郎"` 形式に更新（`.?` より安全：「山田一太郎」等への誤マッチを防ぐ）
- `tests/test_build.py`：`TestHighlightAuthors` に正規表現テスト3件を追加（計148件）

## [0.6.0] - 2026-06-03

### 追加

- `tools/` ディレクトリ：既存データから `publications.yaml` へのインポート CLI
  - `tools/import.py`：`--format`・`--output`・`--append` オプション
    - 変換できなかったフィールドは `note` に `[import: field=value]` 形式で記録
    - 著者名フォーマット・月なし日付等の問題点は警告として stderr に出力
  - `tools/importers/__init__.py`：`BaseImporter` 基底クラス
  - `tools/importers/bibtex.py`：BibTeX インポーター（`bibtexparser` v1.x 使用）
    - `@article`（journal / conference）・`@inproceedings`・`@book`・`@incollection`・`@phdthesis`・`@mastersthesis`・`@techreport` 対応
  - `tools/importers/hayagriva.py`：Hayagriva インポーター（PyYAML のみで対応）
    - `parent` 構造から `journal` / `conference` を判定
  - `requirements-tools.txt`：ツール用追加依存（`bibtexparser>=1.3,<2.0`）
  - `tests/test_import.py`：インポーターのユニットテスト（33件）

### 変更

- `tools/import.py`：インポーター検出をプラグイン方式に変更
  - `importers/` を `pkgutil` で自動スキャンし `IMPORTER_CLASS`・`format_name` を持つモジュールを動的に登録
  - 新フォーマット追加時に `import.py` 本体の修正が不要になった
  - 依存パッケージが未インストールのインポーターは自動的に非表示
- `build.py`：`build_searchtext()` を追加し、検索対象をエントリの全文字列値に拡大
  - `source` 内の誌名・論文集名・機関名・賞名・説明文・出版社など全て対象
  - `id`・`type`・`date`・`scope` 等の構造フィールドと内部フィールド（`_`）は除外
- `templates/index.html.j2`：`data-searchtext` を `{{ e._searchtext }}` の1行に簡略化
- `tests/test_build.py`：`TestBuildSearchtext` クラスを追加（13件、計112件）
- `tools/`・`README.md`・`README.en.md`・`requirements-tools.txt` を配布 zip・sync 対象に追加
  - ツールファイル／ユーザーデータの分類表を更新（`CHANGELOG.md` は sync しない）

### 修正

- `tools/import.py`：`main()` 冒頭で stdout・stderr を UTF-8 に統一
  - `sys.stdout.reconfigure(encoding='utf-8')` と `sys.stderr.reconfigure(encoding='utf-8')` を追加
  - Windows 等の非 UTF-8 ロケールでの文字化けを防止

### ドキュメント

- `CLAUDE.md`：「配布パッケージ・sync の対象ファイル」セクションを追加（zip と sync は常に一致させるルールを明文化）
- `CLAUDE.md`：`tools/import.py` 仕様にプラグインアーキテクチャの説明・追加手順を追記
- `CLAUDE.md`：機能仕様・build.py 仕様・ディレクトリ構成の記載漏れを全件修正
- `README.md`・`README.en.md`：「既存データのインポート」節・「カスタムインポーターの追加」節を追加
- `README.md`・`README.en.md`：フィルタの URL クエリパラメータ一覧表を追加

## [0.5.2] - 2026-06-03

### 変更

- `.github/workflows/release-asset.yml`：CHANGELOG.md から該当バージョンのセクションを抽出して Release Notes として使用（`--generate-notes` を廃止）

## [0.5.1] - 2026-06-03

### 変更

- `.github/workflows/release-asset.yml`：タグ push 一発でリリースが完結するよう修正
  - Release が未作成の場合は `gh release create` で作成して zip をアップロード
  - Release が既に存在する場合は `gh release upload` で zip だけ追加
  - これまでの「タグ push → 失敗 → 手動で Release 作成 → 手動で workflow_dispatch 再実行」の手順が不要になる

### ドキュメント

- `README.md`・`README.en.md`：謝辞セクションを追加
- `README.md`：リリース手順を開発者向けセクションに追記
- `.github/workflows/release-asset.yml`：リリース手順のコメントを追加

## [0.5.0] - 2026-06-02

### ドキュメント

- `README.md`・`README.en.md`：ページネーション・前後ナビゲーション・Atom フィードを主な機能一覧に追記
- `README.md`・`README.en.md`：`base_url` の説明に `feed.xml` 生成の記述を追加

### 追加

- `build.py`：Atom フィード（`public/feed.xml`）の生成
  - `base_url` が設定されている場合のみ出力（未設定時はスキップ）
  - 日付優先順：`registered_at` → `date`、どちらもないエントリは除外
  - `<content>` は bibliography 形式（著者. タイトル. 誌名, 巻・号, pp., 年.）
  - ElementTree で生成（XML エスケープを標準ライブラリに委譲）
- `tests/test_build.py`：`TestGenerateFeed` クラスを追加（13件）
- `templates/index.html.j2`・`templates/entry.html.j2`：`base_url` 設定時に `<link rel="alternate" type="application/atom+xml">` を `<head>` に追加（ブラウザ自動検出対応）
- 詳細ページ（`entry.html.j2`）：前後ナビゲーション「← 前の業績」「次の業績 →」を記事下部に追加
  - 一覧と同じソート順（左が新しい・右が古い）、端のページは該当方向を非表示
  - `build.py`：詳細ページ生成時に `prev_entry`・`next_entry` をテンプレートに渡すよう変更
  - `static/i18n.js`：`nav.prev`・`nav.next` キーを追加（日英対応）
  - `static/style.css`：`.entry-nav` スタイルを追加（印刷時は非表示）
- `static/style.css`：印刷用スタイル（`@media print`）を追加
  - ヘッダーの背景・ボタン類・エクスポートセクション・フッターを非表示
  - バッジの色付き背景を除去（枠線のみ）
  - `detail-table` の行が途中でページをまたがないよう設定
  - `http(s)` リンクの URL をテキストとして本文に追記
- 一覧ページ：「さらに表示」「全件表示」ボタンによるページネーション
  - `config.yaml` の `entries_per_page`（デフォルト 30）で初期表示件数を設定
  - `0` または未設定で全件表示（従来動作）
  - フィルタ変更時に表示件数をリセット
  - カウント表示を「30 / 150 件表示」形式に変更（絞り込み時は全件数も表示）
  - `static/style.css`：`.pagination-controls` スタイルを追加
  - `static/i18n.js`：`btn.show.more`・`btn.show.all` キーを追加、`count` 関数を2引数対応に変更
- `static/i18n.js`：UI 多言語対応（日本語 / 英語）
  - ヘッダーの JA / EN ボタンで言語を切り替え（`localStorage` で永続化）
  - 翻訳辞書：種別・バッジ・フィルター・テーブルヘッダー・詳細ラベル・エクスポートボタン等
  - `applyLanguage(lang)`・`initLang()` 関数
- `templates/index.html.j2`・`templates/entry.html.j2`：JA/EN トグルボタンをヘッダーに追加、全 UI 要素に `data-i18n` 属性付与
- `static/style.css`：`.lang-toggle`・`.lang-btn`・`.lang-btn-active` スタイルを追加
- `README.md`・`README.en.md`：方法 B（GitHub テンプレート）で始めた場合に削除できるファイルの一覧を追記
- `README.en.md`：README の英訳版を追加
- `README.md`：言語切り替え機能の記述を追加（導入説明・主な機能一覧）
- `.github/workflows/release-asset.yml`：配布 zip に `README.en.md` を追加
- `data/config.yaml`：`default_language` フィールドを追加（`auto` / `ja` / `en`）
  - `auto`（デフォルト）：ブラウザ言語を検出し `ja` なら日本語、それ以外は英語
  - `ja` / `en`：初回訪問者の言語を固定（`localStorage` 既存設定は常に優先）
- `static/i18n.js`：`initLang()` を `SCHOLIST_DEFAULT_LANG` 参照に更新
- `templates/index.html.j2`・`templates/entry.html.j2`：`SCHOLIST_DEFAULT_LANG` 変数を埋め込み

## [0.3.0] - 2026-06-02

### 修正

- `extras/sync-from-scholist.yml`・`README.md`：`gh workflow run build.yml` に `--repo "${GITHUB_REPOSITORY}"` を追加
  - `git remote add upstream` 後に `gh` CLI が scholist を誤認識して 403 エラーになる問題を解消

### 追加

- `extras/sync-from-scholist.yml`：template zip に同梱する sync ワークフローのマスターファイルを追加
- `.github/workflows/release-asset.yml`：zip に `sync-from-scholist.yml` を自動同梱するよう更新
  - `extras/sync-from-scholist.yml` を `.github/workflows/sync-from-scholist.yml` として含める
  - zip 内のファイル構成を tmpdir 方式で管理

- Hayagriva 形式のエクスポート対応（`export.js`）
  - 全件・1件エクスポートボタンに「Hayagriva」を追加
  - 種別ごとに Hayagriva 型と `parent:` 構造に変換
  - `language` フィールドによるタイトル選択（`en` → `title_en`、それ以外 → `title`）
  - DOI URL は `serial-number.doi` に自動変換
- `language` フィールドを共通フィールドに追加（省略可、ISO 639-1 コード）
  - Hayagriva エクスポートのタイトル選択と `language` フィールドに使用

- `thesis`・`report` 種別を追加（合計10種別に）
  - `thesis`：`source.institution`（機関名）・`source.degree`（`bachelor`/`master`/`doctoral`）
    BibTeX: `doctoral`→`@phdthesis`、`master`→`@mastersthesis`、`bachelor`→`@misc`
  - `report`：`source.institution`（発行機関）・`source.number`（レポート番号）、BibTeX: `@techreport`
  - `validate()` に `source.degree` の列挙値チェックを追加
  - テンプレートの種別フィルタ・バッジ・サマリーチップ・会場表示に対応
  - `tests/test_build.py`：`TestValidateDegree` クラスを追加（6件、計87件）
- `abstract` フィールドのサポート（全種別・省略可）
  - 詳細ページ（`entry.html.j2`）の URL / DOI 行の直後に表示
  - OGP `og:description` を abstract 優先に変更（未設定時は従来の著者名・会議名から生成）
  - BibTeX エクスポートの `abstract` フィールドに出力
  - インクリメンタル検索の対象に追加（`data-searchtext` に含める）
  - `data/publications.yaml` のサンプル journal エントリに例を追加
- `.github/workflows/release-asset.yml`：タグ push 時に開発ファイルを除いた配布用 zip を生成し Release にアタッチ
  - `workflow_dispatch` でタグを指定して手動実行も可能

### 変更

- `.markdownlint.json`：MD031（コードブロック前後の空行）を無効化

### ドキュメント

- `README.md`：方法 A の説明に sync ワークフローが同梱される旨を追記
- `README.md`：「GitHub Actions で自動化する」節に方法 A ユーザーは追加不要である旨を追記
- `README.md`：`abstract`・`language` フィールドを任意フィールド表として追加
- `README.md`：「主な機能」に統計サマリー・フィルタ URL 保持・OGP・sitemap.xml を追記
- `CLAUDE.md`：`build.py` バリデーション項目を現状に合わせて更新（10種別・全バリデーション項目・sitemap 生成ステップ）
- `CLAUDE.md`：`abstract` フィールドの説明に OGP 優先使用を明記
- `README.md`：種別表に `thesis`・`report` を追加
- `CLAUDE.md`：`thesis`・`report` の種別定義・固有フィールドスキーマ・BibTeX マッピングを追加
- `README.md`：セットアップ方法を「方法 A（template zip）」「方法 B（GitHub テンプレート）」の2択に整理

## [0.2.0] - 2026-06-02

### 追加

- 一覧ページ（`templates/index.html.j2`）：フィルタ状態を URL クエリパラメータに保持
  - フィルタ・検索変更時に `history.replaceState` で URL を更新（ブラウザ履歴には残さない）
  - ページロード時に URL パラメータを読み込みフィルタを復元（`URLSearchParams`）
  - パラメータ: `type`, `year`, `scope`, `reviewed`, `invited`, `q`（検索語）
  - フィルタなし時は URL をクリーンに保つ（クエリ文字列なし）
- 一覧ページ（`templates/index.html.j2`）：統計サマリーをヘッダー直下に表示
  - 総件数・年範囲（最古 – 最新）を表示
  - 種別ごとの件数をカラーチップで表示（件数が0の種別は非表示）
  - JavaScript のみで完結（`ALL_ENTRIES` から集計）
- `static/style.css`：`.summary`・`.summary-chip` スタイルを追加
- `build.py`：GitHub Actions `::error::` アノテーション対応
  - `GITHUB_ACTIONS=true` 環境下では `::error file=data/publications.yaml::` 形式で出力
  - ローカル実行時は従来通り `ERROR:` を stderr に出力
- `tests/test_build.py`：`TestErrorOutput` クラスを追加（3件）
- `build.py`：追加フィールドバリデーション
  - `id` 文字種・`authors` 必須・`scope` 列挙値・`registered_at` 形式
  - `files` 各要素の `path`/`url`・`paper_type`・`source.status`
- `tests/test_build.py`：バリデーション追加分テスト 44件追加（計72件）
- `build.py`：`date` フォーマットの厳密バリデーションを追加
- `build.py`：`generate_sitemap()` 関数を追加し、`public/sitemap.xml` を生成
  - `config.base_url` が設定されている場合のみ出力（空・未設定時はスキップ）
  - 一覧ページと全詳細ページの URL を列挙
  - `registered_at` → `date` の優先順で `<lastmod>` を設定
  - `YYYY-MM` 形式の日付は `YYYY-MM-01` に変換
- `tests/test_build.py`：`TestGenerateSitemap` クラスを追加（9件）
- `data/config.yaml`：`base_url` フィールドを追加（og:url・将来の sitemap.xml 用）
  - 設定時は詳細ページに `og:url` を追加、未設定（空）なら出力しない
  - `CLAUDE.md`・`README.md` のスキーマ説明に追記
- `templates/entry.html.j2`：OGP / Twitter Card メタタグを追加
  - `og:type`（article）・`og:title`・`og:description`・`og:site_name`・`twitter:card`
  - description は「著者 — 会議/誌名 (年)」形式で自動生成（種別により venue を選択）
- `templates/index.html.j2`：一覧ページに基本 OGP タグを追加（`og:type: website`）

### 変更

- `README.md`：sync ワークフローサンプルに `actions: write` 権限と Build and Deploy 自動起動ステップを追加
  - sync 後の手動ビルドが不要になる
  - 手動 sync（`git checkout`）の場合は引き続き手動起動が必要である旨を注記

- `static/export.js`：YAML エクスポートを簡易シリアライザから js-yaml（CDN 経由）に切り替え
  - 長い文字列・ネストの深いオブジェクト・特殊文字などエッジケースを正確に処理
  - `templates/index.html.j2`・`templates/entry.html.j2` に CDN スクリプトタグを追加
- `.github/workflows/build.yml`：`workflow_dispatch` トリガーを追加（手動実行を可能に）
- `.markdownlint.json`：MD013（行長制限）を無効化

### ドキュメント

- `README.md`：sync 後に手動ビルドが必要な旨の注意書きを追加
- `README.md`：sync-from-scholist.yml サンプルから無効な `workflows: write` を削除、制限の説明を追加
- `README.md`：markdownlint 警告を修正（テーブル区切り・コードブロック言語指定）

## [0.1.1] - 2026-06-02

### 追加

- `tests/test_build.py`：pytest によるユニットテスト（25件）
  - `validate()`：ID重複・title/title_en欠落・不明type・複数エラー
  - `sort_entries()`：date降順・同日YAML記述順保持・null末尾・YYYY-MM形式
  - `highlight_authors()`：完全一致・大文字小文字区別・複数表記ゆれ・スタイル・順序保持
  - `read_version()`：正常読み込み・ファイルなしフォールバック・プレリリース形式
- `tests/conftest.py`：テスト用パス設定
- `requirements-dev.txt`：開発依存（pytest）
- `.github/workflows/test.yml`：push / PR 時に自動テストを実行する CI ワークフロー
- `.markdownlint.json`：CHANGELOG の重複見出し警告を抑制

### 変更

- `pyproject.toml`：バージョンを 0.1.1 に更新、`[tool.pytest.ini_options]` 設定を追加
- `data/publications.yaml`：全8種別・エッジケース（同日2件・dateなし・title/title_en の組み合わせ）を網羅するサンプルデータに再設計
- `data/config.yaml`・`CLAUDE.md`・`README.md`：サンプル中の著者名をすべて架空名（山田 太郎 / Taro Yamada）に統一

### ドキュメント

- `README.md`：「開発者向け」節を追加（開発環境セットアップ・テスト実行・ローカルビルド確認・ファイル構成）
- `README.md`：upstream からのアップデート手順（リモート登録・ファイル単位の取り込み・GitHub Actions による自動化）を追加

### その他

- git 履歴を1コミットにスカッシュ（旧コミットに含まれていた実名を除去）

## [0.1.0] - 2026-06-02

### 追加

- `pyproject.toml`：バージョン管理と配布メタデータ
- `build.py`：静的サイト生成スクリプト
  - YAML 読み込み・バリデーション（ID重複、title/title_en の存在確認、type 検証）
  - date 降順ソート（同日はYAML記述順、date なしは末尾）
  - 著者ハイライト処理（`config.yaml` の `highlight_authors` と照合）
  - Jinja2 テンプレートからの HTML 生成（一覧・詳細ページ）
  - `static/` および `files/` の `public/` へのコピー
  - `pyproject.toml` からバージョンを読み込み、フッターに表示
- `templates/index.html.j2`：一覧ページテンプレート
  - 種別・年・国内/国際・査読・招待 によるフィルタ機能（JavaScript）
  - タイトル・著者・会議名のインクリメンタル検索
  - 表示件数カウンタ
  - 全件エクスポートボタン（YAML / JSON / BibTeX）
- `templates/entry.html.j2`：詳細ページテンプレート
  - 全フィールドの整形表示（種別ごとの出典フィールド対応）
  - 添付ファイルへのリンク
  - 1件エクスポートボタン（YAML / JSON / BibTeX）
- `static/style.css`：レスポンシブ対応のスタイルシート
- `static/export.js`：クライアントサイドエクスポート機能（YAML / JSON / BibTeX）
- `data/config.yaml`：著者ハイライト設定・サイトタイトルの設定ファイル
- `data/publications.yaml`：業績データファイル（サンプルエントリ付き）
- `requirements.txt`：依存パッケージ（PyYAML, Jinja2）
- `.github/workflows/build.yml`：GitHub Actions による自動ビルド・GitHub Pages デプロイ
- `.gitignore`：`public/`（生成物）の除外設定

### 変更

- `.github/workflows/build.yml`：Node.js 24 へのオプトイン（`FORCE_JAVASCRIPT_ACTIONS_TO_NODE24`）を追加
