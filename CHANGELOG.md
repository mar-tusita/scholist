# Changelog

このファイルはプロジェクトのすべての変更を記録します。
フォーマットは [Keep a Changelog](https://keepachangelog.com/ja/1.1.0/) に基づいています。

## [Unreleased]

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
