# TODO

実装予定の機能・改善項目。完了したエントリはここから削除し、CHANGELOG.md に移す。

優先度・難度の凡例：優先度 高／中／低、難度 小／中／大

---

## 多言語対応

- **UI 多言語対応（日本語 / 英語）** ― 優先度: 中 / 難度: 中
  ページ閲覧者がヘッダーの JA / EN ボタンで表示言語を切り替えられるようにする。
  `localStorage` に保存し、ページをまたいで維持する。設定ファイル（config.yaml）は変更しない。

  ### 作業項目

  #### 1. `static/i18n.js` を新規作成

  - 翻訳辞書オブジェクト（`ja` / `en`）を定義する
  - 翻訳が必要な文字列（下記「辞書に含める文字列」参照）をすべて収録する
  - `applyLanguage(lang)` 関数：`[data-i18n]` 属性を持つ要素のテキストを書き換える
  - `applyPlaceholder(lang)` 関数：`[data-i18n-placeholder]` 属性を持つ input の placeholder を書き換える
  - カウント表示・サマリーなど数値を含む文字列はテンプレート関数形式（例: `` n => `${n} 件表示` ``）で定義する
  - ページロード時に `localStorage` から言語を読み込み適用する

  #### 2. `templates/index.html.j2` の変更

  - ヘッダーに言語切り替えボタン（JA / EN）を追加する
  - フィルターのラベル（種別・年・国内/国際・査読・招待）に `data-i18n` 属性を付与する
  - フィルター選択肢（すべて・国内・国際・査読あり/なし・招待あり/なし）に `data-i18n` 属性を付与する
  - 種別フィルター選択肢（会議・論文誌・講演・特許・受賞・書籍・解説等・その他・学位論文・技術レポート）に `data-i18n` 属性を付与する
  - テーブルヘッダー（年・種別・タイトル・著者・掲載先/会議）に `data-i18n` 属性を付与する
  - 検索ボックスの `placeholder` に `data-i18n-placeholder` 属性を付与する
  - エクスポートボタン（全件 YAML / JSON / BibTeX / Hayagriva）に `data-i18n` 属性を付与する
  - 種別バッジに `data-type` 属性を持たせ、JS でテキストを書き換えられるようにする
  - 招待・査読・国内・国際バッジに `data-i18n` 属性を付与する
  - カウント表示（N 件表示）の更新ロジックを i18n 対応にする
  - サマリー（全 N 件 · 年範囲）の生成ロジックを i18n 対応にする

  #### 3. `templates/entry.html.j2` の変更

  - ヘッダーに言語切り替えボタン（JA / EN）を追加する（または共通パーツ化を検討）
  - 詳細テーブルの行ラベル（著者・日付・登壇者・組織/学会・会議名・開催地・論文集・ページ・誌名・巻/号・DOI・賞名・授与機関・出版社・ISBN・編者・章・出典・URL/DOI・備考・特許番号・国・状態・機関・番号）に `data-i18n` 属性を付与する
  - バッジラベル（招待講演・査読あり・国際・国内）に `data-i18n` 属性を付与する
  - 特許の状態表示（登録/出願）・学位の表示（博士/修士/学士）に `data-i18n` 属性を付与する
  - セクションタイトル（添付ファイル・このエントリをエクスポート）に `data-i18n` 属性を付与する
  - エクスポートボタン（YAML / JSON / BibTeX / Hayagriva）に `data-i18n` 属性を付与する

  #### 4. `static/style.css` の変更

  - 言語切り替えボタンのスタイルを追加する

  #### 5. 両テンプレートで `i18n.js` を読み込む

  - `export.js` と同様に `<script src="...i18n.js">` を追加する

  #### 6. `README.en.md` を新規作成

  - `README.md`（日本語）はそのまま残す
  - 英訳版を `README.en.md` として作成する

  #### 7. テストの更新

  - Python 側（`build.py`）は変更なしなので既存テストへの影響なし
  - 手動での動作確認（言語切り替え・localStorage 永続化・ページをまたいだ維持）を実施する

  ### 辞書に含める文字列（一覧）

  | キー例 | ja | en |
  | --- | --- | --- |
  | `type.conference` | 会議 | Conference |
  | `type.journal` | 論文誌 | Journal |
  | `type.talk` | 講演 | Talk |
  | `type.patent` | 特許 | Patent |
  | `type.award` | 受賞 | Award |
  | `type.book` | 書籍 | Book |
  | `type.misc` | 解説等 | Article/Misc |
  | `type.other` | その他 | Other |
  | `type.thesis` | 学位論文 | Thesis |
  | `type.report` | 技術レポート | Tech Report |
  | `badge.invited` | 招待 | Invited |
  | `badge.reviewed` | 査読 | Reviewed |
  | `badge.domestic` | 国内 | Domestic |
  | `badge.international` | 国際 | International |
  | `col.year` | 年 | Year |
  | `col.type` | 種別 | Type |
  | `col.title` | タイトル | Title |
  | `col.authors` | 著者 | Authors |
  | `col.venue` | 掲載先・会議 | Venue |
  | `filter.all` | すべて | All |
  | `filter.reviewed.yes` | 査読あり | Reviewed |
  | `filter.reviewed.no` | 査読なし | Not reviewed |
  | `filter.invited.yes` | 招待あり | Invited |
  | `filter.invited.no` | 招待なし | Not invited |
  | `btn.exportAll.yaml` | 全件 YAML | All YAML |
  | `detail.authors` | 著者 | Authors |
  | `detail.date` | 日付 | Date |
  | `detail.venue` | 会場・会議 | Venue |
  | `detail.pages` | ページ | Pages |
  | … | … | … |

---

## 配布・セットアップ

- **README 方法 B の削除ファイルリストを追記** ― 優先度: 低 / 難度: 小
  「Use this template」から始めた場合に削除できるファイルの一覧（`tests/`・`requirements-dev.txt`・
  `.github/workflows/test.yml`・`CLAUDE.md` 等）を README 方法 B の説明に追記する。

---

## 機能追加

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
