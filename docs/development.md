# 開発者向け

## 開発環境のセットアップ

```bash
pip install -r requirements-dev.txt
```

`requirements.txt`（本番依存）に加えて `pytest` がインストールされます。

## テストの実行

```bash
pytest -v
```

`tests/test_build.py` に `build.py` のロジック関数（`validate`・`sort_entries`・`highlight_authors`・`read_version`）のユニットテストが含まれています。

`build.py` を変更するときは、テストが引き続き通ることを確認してください。

## ローカルビルドの確認

```bash
python build.py
```

`public/` に HTML が生成されます。ブラウザで `public/index.html` を開いて動作を確認できます。

## ファイル構成（ツール側）

| ファイル | 役割 |
| --- | --- |
| `build.py` | 静的サイト生成スクリプト本体 |
| `templates/` | Jinja2 テンプレート |
| `static/` | CSS・JavaScript |
| `data/` | サンプルデータ（テスト兼ドキュメント） |
| `tests/` | pytest テストスイート |
| `pyproject.toml` | バージョン・pytest 設定 |
| `requirements.txt` | 本番依存（PyYAML, Jinja2） |
| `requirements-dev.txt` | 開発依存（pytest） |

## リリース手順

1. `pyproject.toml` のバージョンを更新する
2. `CHANGELOG.md` の `[Unreleased]` を `[vX.Y.Z] - YYYY-MM-DD` に確定する
3. コミット・push する

   ```bash
   git add pyproject.toml CHANGELOG.md
   git commit -m "chore: release X.Y.Z"
   git push origin main
   ```

4. タグを作成・push する（これだけで Release 作成と template zip の配布まで自動完結）

   ```bash
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```

> **リリースノートを手書きする場合：** 手順 4 の前に `gh release create vX.Y.Z --title "..." --notes "..."` を実行しておくと、ワークフローは Release 作成をスキップして zip のアップロードだけ行います。

### CHANGELOG の書き方：ワークフローファイルを変更した場合

`build.yml` または `extras/sync-from-scholist.yml` を変更したときは、CHANGELOG にユーザーへの手動更新通知を必ず明記する。

```markdown
- `.github/workflows/build.yml` を更新 — **手動更新が必要**：[docs/update.md](docs/update.md)
- `extras/sync-from-scholist.yml` を更新 — **手動更新が必要**：[docs/update.md](docs/update.md)
```

これらのファイルは sync ワークフローで自動配布されないため、ユーザーが気づかずに古いバージョンのまま使い続けるリスクがある。リリースノート（= CHANGELOG の該当バージョン節）に書いておくことで、GitHub Release 上でも周知できる。
