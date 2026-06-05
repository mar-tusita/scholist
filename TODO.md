# TODO

実装予定の機能・改善項目。完了したエントリはここから削除し、CHANGELOG.md に移す。

優先度・難度の凡例：優先度 高／中／低、難度 小／中／大

---

## インポートツール

- **インポートツールの拡張フォーマット対応** ― 優先度: 低 / 難度: 中
  現在 `bibtex` / `hayagriva` / `ris` / `csl-json` に対応済み。`importers/` に新モジュールを追加するだけで拡張できる。

---

## デプロイ・運用

- **添付ファイルのアクセス制御（ドキュメント）** ― 優先度: 低 / 難度: 小
  `files/` 以下のファイルをパスワードや IP アドレスで保護する方法を README に記載する。
  コード変更は不要（`shutil.copytree` がサブディレクトリを再帰コピーするため、現状のまま動く）。

  **推奨パターン：`files/restricted/` サブディレクトリ規約**
  - 公開ファイルは `files/foo.pdf`、制限ファイルは `files/restricted/bar.pptx` に配置
  - YAML では `path: "files/restricted/bar.pptx"` と書くだけ（テンプレートの相対リンクも正しく解決される）
  - nginx 側で `location /files/restricted/` にだけアクセス制御をかける

  **nginx 設定例：**
  ```nginx
  # /files/ は公開（location ブロックなし、または明示的に allow all）
  location /files/restricted/ {
      auth_basic "Restricted";
      auth_basic_user_file /etc/nginx/.htpasswd;
      # IP 制限と組み合わせる場合：
      # satisfy any;   # OR 条件（IP が通れば認証不要）
      # allow 203.0.113.0/24;
      # deny all;
  }
  ```

  **GitHub Pages**：静的ホスティングのためサーバーサイド制御は不可。
  保護が必要なファイルは外部サービスに置き、YAML の `files[].url` に限定公開 URL を書く分離運用が現実解。

---

## 品質・堅牢性

- **ウォッチモード** ― 優先度: 低 / 難度: 中
  `data/` や `templates/` の変更を監視して自動再ビルドするオプション（`--watch`）を追加する。
  `watchdog` 等の追加ライブラリが必要。ローカル開発時の利便性向上。
