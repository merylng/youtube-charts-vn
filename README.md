# YouTube Charts VN

This repository publishes static YouTube Charts pages with GitHub Pages.

It includes:

- 🎵 **Top Songs Vietnam Weekly**
- 🔥 **Trending Videos Vietnam Right Now**

The website is static. Data is embedded directly inside the HTML files and refreshed by a Python update script, either manually or through GitHub Actions.

---

## 📚 Table of Contents

- [I. 📁 Active Files](#i--active-files)
- [II. 📌 File Purposes](#ii--file-purposes)
  - [1. 🏠 `index.html`](#1--indexhtml)
  - [2. 🎵 `top_songs.html`](#2--top_songshtml)
  - [3. 🔥 `trending.html`](#3--trendinghtml)
  - [4. 🐍 `scripts/update_static_pages.py`](#4--scriptsupdate_static_pagespy)
  - [5. ⚙️ `.github/workflows/update-charts.yml`](#5-️-githubworkflowsupdate-chartsyml)
- [III. 🧠 How the UI Works](#iii--how-the-ui-works)
  - [1. 📍 Data source](#1--data-source)
  - [2. 📥 Fetch/update method](#2--fetchupdate-method)
  - [3. 📦 Static output method](#3--static-output-method)
  - [4. 🖥️ UI rendering method](#4-️-ui-rendering-method)
  - [5. 📤 Output shown on the website](#5--output-shown-on-the-website)
- [IV. 🚀 GitHub Pages Setup](#iv--github-pages-setup)
  - [1. 📂 Required repository structure](#1--required-repository-structure)
  - [2. ⚙️ Enable GitHub Pages](#2-️-enable-github-pages)
  - [3. 🔐 Enable workflow write permission](#3--enable-workflow-write-permission)
  - [4. ▶️ Run the workflow manually](#4-️-run-the-workflow-manually)
- [V. 🔄 Update Flow](#v--update-flow)
  - [1. GitHub Actions run flow](#1-github-actions-run-flow)
  - [2. Manual local update flow](#2-manual-local-update-flow)
- [VI. 📝 Commit Behavior](#vi--commit-behavior)
- [VII. 🌐 GitHub Pages Behavior](#vii--github-pages-behavior)
- [VIII. 🔗 Public URLs](#viii--public-urls)
- [IX. ▶️ Playback Notes](#ix-️-playback-notes)

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

## III. 🧠 How the UI Works

### 1. 📍 Data source

The chart data comes from YouTube Charts:

```text
https://charts.youtube.com/charts/TopSongs/vn/weekly
https://charts.youtube.com/charts/TrendingVideos/vn/RightNow
```

The updater script reads the YouTube Charts page config, then calls YouTube's internal chart endpoint:

```text
https://charts.youtube.com/youtubei/v1/browse?alt=json
```

The request is forced to Vietnam context:

```text
region = vn
gl = VN
hl = vi
Accept-Language = vi-VN
```

This prevents GitHub Actions runners from accidentally fetching US/global chart data.

---

### 2. 📥 Fetch/update method

The Python script:

```text
scripts/update_static_pages.py
```

uses HTTP requests to:

  1. Load the YouTube Charts page.
  2. Extract the `ytcfg` / InnerTube context.
  3. Send a JSON request to the YouTube Charts internal endpoint.
  4. Parse the JSON response.
  5. Extract the relevant chart entries.

For **Top Songs**, the script extracts:

```text
rank
title
artists
videoId
thumbnail
views
lastRank
periodsOnChart
rangeEnd
updatedAt
```

For **Trending Videos**, the script extracts:

```text
rank
title
artists
channelName
videoId
thumbnail
lastRank
periodsOnChart
rangeLabel
updatedAt
```

Note: Trending Videos currently does not expose reliable view counts in the YouTube Charts response, so views are not displayed for the Trending tab.

---

### 3. 📦 Static output method

GitHub Pages cannot run Python.

Because of that, the script writes the fetched data directly into the HTML files as embedded JavaScript:

```js
const STATIC_CHART_DATA = {...}
```

The updated files are:

```text
top_songs.html
trending.html
```

When a user opens the website, the browser does **not** call YouTube Charts directly. Instead, it reads the already embedded `STATIC_CHART_DATA` from the HTML file and renders the UI.

---

### 4. 🖥️ UI rendering method

The HTML pages use client-side JavaScript to:

  1. Read `STATIC_CHART_DATA`.
  2. Render the chart list.
  3. Show the current selected song/video.
  4. Load the selected `videoId` into the YouTube iframe player.
  5. Handle playback controls:
  - Play / Pause
  - Previous
  - Next
  - Repeat
  - Shuffle

The actual video/audio playback is handled by YouTube through the iframe player:

```text
https://www.youtube.com/iframe_api
```

GitHub Pages only hosts the UI and embedded chart data. YouTube streams the actual media.

---

### 5. 📤 Output shown on the website

The website outputs:

#### Top Songs page

  - Weekly Top Songs list for Vietnam.
  - Current song title.
  - Artist/singer name.
  - View count for the selected song.
  - Last updated time.
  - YouTube iframe playback.

#### Trending page

  - Trending Videos list for Vietnam.
  - Current video title.
  - Artist/channel name.
  - Last updated time.
  - YouTube iframe playback.

---

## IV. 🚀 GitHub Pages Setup

### 1. 📂 Required repository structure

The repository should keep these files at the root level:

```text
index.html
top_songs.html
trending.html
```

The update script and workflow should stay here:

```text
scripts/update_static_pages.py
.github/workflows/update-charts.yml
```

---

### 2. ⚙️ Enable GitHub Pages

In the GitHub repository:

  1. Open **Settings**.
  2. Open **Pages**.
  3. Under **Build and deployment**, choose:
  - Source: **Deploy from a branch**
  - Branch: **main**
  - Folder: **/ root**
  4. Click **Save**.

After deployment, GitHub will provide a public URL like:

```text
https://<github-username>.github.io/<repository-name>/
```

---

### 3. 🔐 Enable workflow write permission

The workflow needs permission to commit updated HTML files back to the repository.

In the GitHub repository:

  1. Open **Settings**.
  2. Open **Actions** → **General**.
  3. Find **Workflow permissions**.
  4. Select **Read and write permissions**.
  5. Click **Save**.

---

### 4. ▶️ Run the workflow manually

In the GitHub repository:

  1. Open the **Actions** tab.
  2. Select **Update YouTube Charts Data**.
  3. Click **Run workflow**.
  4. Select branch **main**.
  5. Click **Run workflow** again.

If chart data changes, the workflow commits and pushes updated HTML files automatically.

---

## V. 🔄 Update Flow

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
Fetch Vietnam YouTube Charts data
        ↓
Embed data into top_songs.html and trending.html
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

## VI. 📝 Commit Behavior

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

## VII. 🌐 GitHub Pages Behavior

GitHub Pages serves the static HTML files from the repository.

Important notes:

- GitHub Pages does **not** run Python.
- `scripts/update_static_pages.py` must run before the public website can show updated chart data.
- After GitHub Actions commits updated HTML files, GitHub Pages usually refreshes the public URL within a few minutes.

---

## VIII. 🔗 Public URLs

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

## IX. ▶️ Playback Notes

The pages use the YouTube iframe player.

Some videos may not play inside the page if:

- Embedding is disabled by the video owner.
- The video has region restrictions.
- YouTube applies copyright or playback limitations.

The chart list can still render even if some individual videos cannot be played in the embedded player.

Playback through the embedded YouTube iframe may contribute views to the original YouTube video, but YouTube decides whether each playback is counted as a valid view.
