# Updating the tool

When scholist itself is updated, here is how to pull the changes into your repository.

## Concept

Your repository contains two types of files:

| Type | Files |
| --- | --- |
| **Tool files** (update from scholist) | `build.py`, `templates/`, `static/`, `tools/`, `docs/`, `requirements.txt`, `requirements-tools.txt`, `pyproject.toml`, `README.md`, `README.en.md`, `.github/workflows/build.yml` |
| **Your data** (never overwrite) | `data/`, `files/`, `CHANGELOG.md` |

`git merge` would mix both types, so instead use the approach of **selectively pulling only the tool files**.

## One-time setup: register upstream remote

```bash
git remote add upstream https://github.com/mar-tusita/scholist.git
```

## Syncing when scholist is updated

```bash
# 1. Fetch latest commits from scholist
git fetch upstream

# 2. Overwrite only tool files (leaves data/ and files/ untouched)
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

# 3. Commit and push
git commit -m "chore: sync tool files from scholist vX.Y.Z"
git push
```

To pin to a specific version tag, replace `upstream/main` with `upstream/v0.3.0`.

> **Note (manual sync):** After `git push`, you need to manually trigger a Build and Deploy run.
> Bot commits do not trigger the path-filtered push event in GitHub Actions.
> Go to **Actions → "Build and Deploy" → Run workflow** after pushing.
> If you use the sync workflow (see below), this step is handled automatically.

## Automate with GitHub Actions (optional)

**Method A (zip download):** `.github/workflows/sync-from-scholist.yml` is already included — no action needed.

**Method B (GitHub template):** `extras/sync-from-scholist.yml` is included in your repository.
Copy it to the correct location (same as the "About `extras/`" note in the README):

```bash
cp extras/sync-from-scholist.yml .github/workflows/
```

After that, run it from **Actions → "Sync tool files from scholist" → Run workflow**. Build and Deploy will start automatically when the sync completes.

> **Note:** The sync workflow cannot update workflow files themselves due to GitHub's security policy.
> If either file below changes, update it manually. Changes will always be noted in the release notes (CHANGELOG).
>
> **If `build.yml` has changed:**
> Run the manual sync command above, including `.github/workflows/build.yml` in the file list — manual pushes are allowed to write workflow files.
>
> **If `sync-from-scholist.yml` has changed:**
> In the scholist repository it lives under `extras/`, so the path differs. Run:
>
> ```bash
> git fetch upstream
> git show upstream/main:extras/sync-from-scholist.yml > .github/workflows/sync-from-scholist.yml
> git add .github/workflows/sync-from-scholist.yml
> git commit -m "chore: update sync-from-scholist.yml"
> git push
> ```
