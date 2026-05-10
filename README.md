# YouTube Charts VN

This repository publishes static YouTube Charts pages with GitHub Pages.

It includes:

- Top Songs Vietnam Weekly
- Trending Videos Vietnam Right Now

The website is static. Data is embedded directly inside the HTML files and refreshed by a Python update script, either manually or through GitHub Actions.

## Active files

```text
index.html
top_songs.html
trending.html
scripts/update_static_pages.py
.github/workflows/update-charts.yml
```

## File purpose

### `index.html`

Landing page for the GitHub Pages site.

It redirects users to `top_songs.html` and provides navigation links to the available chart pages.

Default GitHub Pages URL:

```text
https://<github-username>.github.io/<repository-name>/
```

### `top_songs.html`

Static page for **YouTube Charts VN Top Songs Weekly**.

It contains:

- the page UI,
- the embedded Top Songs chart data,
- JavaScript logic to render the list,
- YouTube iframe player logic for in-page playback.

The embedded data is stored in the JavaScript variable:

```js
const STATIC_CHART_DATA = ...
```

### `trending.html`

Static page for **YouTube Charts VN Trending Videos Right Now**.

It contains:

- the page UI,
- the embedded Trending Videos chart data,
- JavaScript logic to render the list,
- YouTube iframe player logic for in-page playback.

The embedded data is also stored in:

```js
const STATIC_CHART_DATA = ...
```

### `scripts/update_static_pages.py`

Python script that refreshes the embedded chart data inside the HTML pages.

It does the following:

1. Fetches YouTube Charts VN Top Songs Weekly data.
2. Fetches YouTube Charts VN Trending Videos Right Now data.
3. Extracts chart entries and video IDs.
4. Replaces the `STATIC_CHART_DATA` block inside:
   - `top_songs.html`
   - `trending.html`
5. Saves the updated HTML files.

Manual run:

```bash
python scripts/update_static_pages.py
```

### `.github/workflows/update-charts.yml`

GitHub Actions workflow that automatically runs the update script.

It is triggered by:

1. Schedule:

```yaml
- cron: "0 */2 * * *"
```

This means the workflow runs every 2 hours.

2. Manual trigger:

```yaml
workflow_dispatch:
```

This allows running it from the GitHub Actions UI with **Run workflow**.

## Update flow

### Scheduled or manual GitHub Actions run

```text
GitHub Actions trigger
        ↓
Checkout repository
        ↓
Set up Python 3.12
        ↓
Run scripts/update_static_pages.py
        ↓
Update embedded data in top_songs.html and trending.html
        ↓
Git checks whether those files changed
        ↓
If changed: commit and push to main
        ↓
GitHub Pages rebuilds and publishes the updated site
```

## Commit behavior

The workflow only creates a commit if either of these files changes:

```text
top_songs.html
trending.html
```

If YouTube Charts returns the same data as the previous run, there is no file diff, so the workflow exits successfully without creating a new commit.

Commit message format:

```text
update lasted data - yyyy/mm/dd
```

Example:

```text
update lasted data - 2026/05/11
```

## GitHub Pages behavior

GitHub Pages serves the static HTML files from the repository.

It does not run Python.

That is why `scripts/update_static_pages.py` must run before the public website can show updated chart data.

After GitHub Actions commits updated HTML files, GitHub Pages usually refreshes the public URL within a few minutes.

## Public URLs

Landing page:

```text
https://<github-username>.github.io/<repository-name>/
```

Top Songs:

```text
https://<github-username>.github.io/<repository-name>/top_songs.html
```

Trending:

```text
https://<github-username>.github.io/<repository-name>/trending.html
```

## Playback notes

The pages use the YouTube iframe player.

Some videos may not play inside the page if:

- embedding is disabled by the video owner,
- the video has region restrictions,
- YouTube applies copyright or playback limitations.

The chart list can still render even if some individual videos cannot be played in the embedded player.
