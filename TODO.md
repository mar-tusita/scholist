# TODO

実装予定の機能・改善項目。完了したエントリはここから削除し、CHANGELOG.md に移す。

優先度・難度の凡例：優先度 高／中／低、難度 小／中／大

---

## CI / リリース

- **release-asset.yml：Release 作成と zip アップロードを一体化** ― 優先度: 中 / 難度: 小
  現状、タグ push で `release-asset.yml` が自動起動するが、Release がまだ存在しないため
  `gh release upload` が "release not found" で失敗する。毎回手動で workflow_dispatch を再実行している。
  ワークフロー内で `gh release create --notes-file <file> "${TAG}"` を先に実行し、その後 zip をアップロードする
  形に変更することで、タグ push 一発でリリースが完結するようにする。

---

## 品質・堅牢性

- **ウォッチモード** ― 優先度: 低 / 難度: 中
  `data/` や `templates/` の変更を監視して自動再ビルドするオプション（`--watch`）を追加する。
  `watchdog` 等の追加ライブラリが必要。ローカル開発時の利便性向上。
