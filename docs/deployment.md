# デプロイ

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

## GitHub Pages

`.github/workflows/build.yml` が含まれています。`data/` または `files/` への push 時に
自動でビルドし、`gh-pages` ブランチにデプロイします。

リポジトリの Settings → Pages → Branch を `gh-pages` に設定してください。

## nginx

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

## 添付ファイルのアクセス制御（nginx）

`files/` 以下のファイルをパスワードや IP アドレスで保護したい場合は、`files/restricted/` サブディレクトリを使うパターンを推奨します。

- 公開ファイルは `files/foo.pdf`、制限ファイルは `files/restricted/bar.pptx` に配置
- YAML では `path: "files/restricted/bar.pptx"` と書くだけ（テンプレートの相対リンクも正しく解決される）
- `build.py` は `files/` を `public/files/` にそのまま再帰コピーするため、コード変更は不要
- nginx 側で `location /files/restricted/` にだけアクセス制御をかける

```nginx
# /files/ は公開（location ブロックなし）
location /files/restricted/ {
    auth_basic "Restricted";
    auth_basic_user_file /etc/nginx/.htpasswd;
    # IP 制限と組み合わせる場合：
    # satisfy any;   # OR 条件（IP が通れば認証不要）
    # allow 203.0.113.0/24;
    # deny all;
}
```

> **GitHub Pages：** 静的ホスティングのためサーバーサイド制御は不可。
> 保護が必要なファイルは外部サービスに置き、YAML の `files[].url` に限定公開 URL を書く分離運用が現実解です。
