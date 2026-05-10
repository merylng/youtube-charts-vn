# YouTube Charts VN

This repository publishes static YouTube Charts pages with GitHub Pages.

It includes:

- 🎵 **Top Songs Vietnam Weekly**
- 🔥 **Trending Videos Vietnam Right Now**

The website is static. Data is embedded directly inside the HTML files and refreshed by a Python update script, either manually or through GitHub Actions.

---

## I. 📁 Active Files

```text
index.html
top_songs.html
trending.html
scripts/update_static_pages.py
.github/workflows/update-charts.yml
```

---

## II. 📌 File Purposes

### 1. 🏠 `index.html`

Landing page for the GitHub Pages site.

Purpose:

- Redirects users to `top_songs.html`.
- Provides navigation links to the available chart pages.

Default GitHub Pages URL:

```text
https://<github-username>.github.io/<repository-name>/
```

---

### 2. 🎵 `top_songs.html`

Static page for **YouTube Charts VN Top Songs Weekly**.

This file contains:

- Page UI.
- Embedded Top Songs chart data.
- JavaScript logic to render the song list.
- YouTube iframe player logic for in-page playback.

The embedded data is stored in:

```js
const STATIC_CHART_DATA = ...
```

---

### 3. 🔥 `trending.html`

Static page for **YouTube Charts VN Trending Videos Right Now**.

This file contains:

- Page UI.
- Embedded Trending Videos chart data.
- JavaScript logic to render the trending list.
- YouTube iframe player logic for in-page playback.

The embedded data is also stored in:

```js
const STATIC_CHART_DATA = ...
```

---

### 4. 🐍 `scripts/update_static_pages.py`

Python script that refreshes the embedded chart data inside the HTML pages.

What it does:

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

---

### 5. ⚙️ `.github/workflows/update-charts.yml`

GitHub Actions workflow that automatically runs the update script.

It is triggered by:

#### a. ⏰ Schedule

```yaml
- cron: "0 */2 * * *"
```

This means the workflow runs every **2 hours**.

#### b. ▶️ Manual Trigger

```yaml
workflow_dispatch:
```

This allows running it manually from the GitHub Actions UI with **Run workflow**.

---

## III. 🔄 Update Flow

### 1. GitHub Actions run flow

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

### 2. Manual local update flow

```text
Run python scripts/update_static_pages.py locally
        ↓
HTML files are updated on local machine
        ↓
Commit and push changes to GitHub
        ↓
GitHub Pages rebuilds and publishes the updated site
```

---

## IV. 📝 Commit Behavior

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

---

## V. 🌐 GitHub Pages Behavior

GitHub Pages serves the static HTML files from the repository.

Important notes:

- GitHub Pages does **not** run Python.
- `scripts/update_static_pages.py` must run before the public website can show updated chart data.
- After GitHub Actions commits updated HTML files, GitHub Pages usually refreshes the public URL within a few minutes.

---

## VI. 🔗 Public URLs

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

---

## VII. ▶️ Playback Notes

The pages use the YouTube iframe player.

Some videos may not play inside the page if:

- Embedding is disabled by the video owner.
- The video has region restrictions.
- YouTube applies copyright or playback limitations.

The chart list can still render even if some individual videos cannot be played in the embedded player.
