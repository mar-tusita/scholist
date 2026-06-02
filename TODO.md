# TODO

実装予定の機能・改善項目。完了したエントリはここから削除し、CHANGELOG.md に移す。

優先度・難度の凡例：優先度 高／中／低、難度 小／中／大

---

## 配布・セットアップ

- **template zip に sync-from-scholist.yml を同梱** ― 優先度: 中 / 難度: 小
  現状、zip をダウンロードして始めたユーザーは sync ワークフローを README を見ながら手動で作成する必要がある。
  `release-asset.yml` で zip を作成する際に、README のサンプルと同内容の
  `.github/workflows/sync-from-scholist.yml` を動的生成して含めることで解消できる。

- **README 方法 B の削除ファイルリストを追記** ― 優先度: 低 / 難度: 小
  「Use this template」から始めた場合に削除できるファイルの一覧（`tests/`・`requirements-dev.txt`・
  `.github/workflows/test.yml`・`CLAUDE.md` 等）を README 方法 B の説明に追記する。

---

## 機能追加

- **`thesis`・`report` 種別の追加** ― 優先度: 中 / 難度: 小
  Hayagriva 調査により、学術 CV で頻出の種別が欠けていることが判明。

  **`thesis`（学位論文）**
  - `source` フィールド：`institution`（大学名）、`degree`（学位種別）
  - `degree` は enum：`bachelor`（学士）/ `master`（修士）/ `doctoral`（博士）
  - BibTeX マッピング：`doctoral` → `@phdthesis`、`master` → `@mastersthesis`、`bachelor` → `@misc`
  - `reviewed` フィールドは不要（論文審査は査読とは別概念）

  **`report`（技術レポート）**
  - `journal` の「査読なし版」ではなく、発行体・識別子の構造が根本的に異なる独立した型
  - `source` フィールド：`institution`（発行機関）、`number`（レポート番号）
  - BibTeX マッピング：`@techreport`
  - 例：IETF RFC、大学技術報告書、NIST 文書など

  共通作業：CLAUDE.md スキーマ定義、`validate()` の `VALID_TYPES`、
  テンプレートの種別フィルタ select・バッジ CSS、テスト追加。

- **`abstract` フィールドの追加** ― 優先度: 中 / 難度: 小
  論文アブストラクトを格納するフィールド。
  - `data/publications.yaml` の共通フィールドに追加（省略可）
  - 詳細ページ（`entry.html.j2`）に表示
  - OGP の `og:description` の補完候補として使用（現在は著者名・会議名から生成）
  - BibTeX エクスポートの `abstract` フィールドに出力
  - インクリメンタル検索の対象に追加

- **Hayagriva 形式のエクスポート対応** ― 優先度: 低 / 難度: 中
  [Hayagriva](https://github.com/typst/hayagriva) は Typst（現代的な組版システム）用の YAML 文献形式。
  Typst で論文を書くユーザーが scholist のデータを使い回せるよう、
  YAML / JSON / BibTeX に並ぶエクスポート形式として追加する。
  スキーマのマッピング（型名・著者形式・日付形式など）の調査が必要。

- **RSS / Atom フィード生成** ― 優先度: 低 / 難度: 中
  `registered_at` フィールドを利用した新着フィード（`feed.xml`）を生成する。
  XML 生成ロジックと `registered_at` の扱いがやや複雑。

- **ページネーション** ― 優先度: 低 / 難度: 大
  エントリ数が多くなった場合の一覧ページの分割表示。
  またはスクロール遅延読み込み（Intersection Observer）による対応。
  フィルタ・検索との組み合わせが複雑になるため規模が大きい。

---

## 品質・堅牢性

- **ウォッチモード** ― 優先度: 低 / 難度: 中
  `data/` や `templates/` の変更を監視して自動再ビルドするオプション（`--watch`）を追加する。
  `watchdog` 等の追加ライブラリが必要。ローカル開発時の利便性向上。

---

## 表示・UX

- **詳細ページ内の前後ナビゲーション** ― 優先度: 低 / 難度: 中
  詳細ページに「前の業績」「次の業績」リンクを追加する（一覧と同じソート順）。
  `build.py` でソート済みリストから前後エントリを取り出してテンプレートに渡す必要がある。

- **印刷用 CSS** ― 優先度: 低 / 難度: 小
  `@media print` スタイルを追加し、詳細ページの印刷出力を整える。
  CSS のみで完結。
