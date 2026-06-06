# ツールのアップデート

scholist 本体が更新されたとき、その変更をあなたのリポジトリに取り込む手順です。

## 基本的な考え方

リポジトリ内のファイルは2種類に分かれます。

| 種別 | ファイル |
| --- | --- |
| **ツールファイル**（更新を取り込む） | `build.py`, `templates/`, `static/`, `tools/`, `docs/`, `requirements.txt`, `requirements-tools.txt`, `pyproject.toml`, `README.md`, `README.en.md`, `.github/workflows/build.yml` |
| **自分のデータ**（絶対に上書きしない） | `data/`, `files/`, `CHANGELOG.md` |

`git merge` を使うと両方が混ざってしまうため、**ツールファイルだけを選んで取り込む**方法を使います。

## 初回のみ：upstream リモートを登録する

```bash
git remote add upstream https://github.com/mar-tusita/scholist.git
```

## scholist が更新されたときの手順

```bash
# 1. scholist の最新コミットを取得
git fetch upstream

# 2. ツールファイルだけを上書き（data/ と files/ は触れない）
git checkout upstream/main -- \
  build.py \
  templates/ \
  static/ \
  tools/ \
  docs/ \
  requirements.txt \
  requirements-tools.txt \
  pyproject.toml \
  README.md \
  README.en.md \
  .github/workflows/build.yml

# 3. 変更をコミット・プッシュ
git commit -m "chore: sync tool files from scholist vX.Y.Z"
git push
```

特定のバージョンタグに合わせたい場合は `upstream/main` の代わりに `upstream/v0.2.0` のように指定します。

> **注意（手動 sync の場合）：** `git push` 後は GitHub Pages の再ビルドを手動で起動する必要があります。
> push によるコミットはツールファイルを更新しますが、
> GitHub Actions はボット以外のコミットでないとビルドワークフローを自動起動しません。
> push 後にリポジトリの **Actions → "Build and Deploy" → Run workflow** を実行してください。
> ワークフローを使って sync する場合はこの手順は不要です（自動でビルドが起動します）。

## GitHub Actions で自動化する（任意）

手動でコマンドを打つ代わりに、GitHub の画面からボタン一つで同期することもできます。

**方法 A（zip ダウンロード）：** `.github/workflows/sync-from-scholist.yml` が既に含まれているため、追加作業は不要です。

**方法 B（GitHub テンプレート）：** `extras/sync-from-scholist.yml` が同梱されています。
以下でコピーしてください（方法 B の「`extras/` について」で案内している手順と同じです）。

```bash
cp extras/sync-from-scholist.yml .github/workflows/
```

追加後は、リポジトリの **Actions → "Sync tool files from scholist" → Run workflow** で実行できます。sync が完了すると自動で Build and Deploy が起動します。

> **注意：** ワークフローは `.github/workflows/build.yml` を sync 対象に含みません。
> `GITHUB_TOKEN` は GitHub のセキュリティ制限によりワークフローファイルを書き込めないためです。
> `build.yml` に変更があった場合は、上記の手動 sync 手順でコピーしてください（手動実行なら書き込めます）。
