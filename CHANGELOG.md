# Changelog

このファイルはプロジェクトのすべての変更を記録します。
フォーマットは [Keep a Changelog](https://keepachangelog.com/ja/1.1.0/) に基づいています。

## [Unreleased]

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

### 変更

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
