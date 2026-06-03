# TODO

実装予定の機能・改善項目。完了したエントリはここから削除し、CHANGELOG.md に移す。

優先度・難度の凡例：優先度 高／中／低、難度 小／中／大

---

## インポートツール

- **`publications.yaml` インポートツール（プラグイン方式）** ― 優先度: 中 / 難度: 中
  既存の文献データを scholist 形式（`publications.yaml`）に変換するツール。
  他ツールから移行するユーザーの参入障壁を下げることが目的。

  **アーキテクチャ：**
  ```text
  tools/
    import.py          # メイン CLI（共通インターフェース）
    importers/
      bibtex.py        # BibTeX → scholist
      hayagriva.py     # Hayagriva → scholist
  ```

  使い方：
  ```bash
  python tools/import.py --format bibtex refs.bib >> data/publications.yaml
  python tools/import.py --format hayagriva refs.yml >> data/publications.yaml
  ```

  **初期サポート形式：**
  - `bibtex`：`bibtexparser` ライブラリを使用（`requirements-tools.txt` に分離）
  - `hayagriva`：PyYAML のみで対応（既存依存）

  **変換方針：**
  - ID：BibTeX の cite key / Hayagriva のキーをそのまま使用
  - 著者名：変換せずそのまま出力し、警告を表示
  - 型マッピングが曖昧な場合（`@misc` 等）は `misc` に落とし `note` にヒントを残す
  - scholist 固有フィールド（`scope`, `invited`, `reviewed` 等）は空欄で出力

  **将来の拡張候補：**
  - `ris`：RIS 形式（Zotero・Mendeley 等からのエクスポート）
  - `csl-json`：CSL-JSON 形式（Pandoc・Zotero の汎用形式）
  - プラグイン構造により追加が容易

---

## 品質・堅牢性

- **ウォッチモード** ― 優先度: 低 / 難度: 中
  `data/` や `templates/` の変更を監視して自動再ビルドするオプション（`--watch`）を追加する。
  `watchdog` 等の追加ライブラリが必要。ローカル開発時の利便性向上。
