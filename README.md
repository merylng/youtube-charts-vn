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

&nbsp;&nbsp;&nbsp;&nbsp;### 1. 🏠 `index.html`

&nbsp;&nbsp;&nbsp;&nbsp;Landing page for the GitHub Pages site.

&nbsp;&nbsp;&nbsp;&nbsp;Purpose:

&nbsp;&nbsp;&nbsp;&nbsp;- Redirects users to `top_songs.html`.
&nbsp;&nbsp;&nbsp;&nbsp;- Provides navigation links to the available chart pages.

&nbsp;&nbsp;&nbsp;&nbsp;Default GitHub Pages URL:

```text
https://<github-username>.github.io/<repository-name>/
```

&nbsp;&nbsp;&nbsp;&nbsp;---

&nbsp;&nbsp;&nbsp;&nbsp;### 2. 🎵 `top_songs.html`

&nbsp;&nbsp;&nbsp;&nbsp;Static page for **YouTube Charts VN Top Songs Weekly**.

&nbsp;&nbsp;&nbsp;&nbsp;This file contains:

&nbsp;&nbsp;&nbsp;&nbsp;- Page UI.
&nbsp;&nbsp;&nbsp;&nbsp;- Embedded Top Songs chart data.
&nbsp;&nbsp;&nbsp;&nbsp;- JavaScript logic to render the song list.
&nbsp;&nbsp;&nbsp;&nbsp;- YouTube iframe player logic for in-page playback.

&nbsp;&nbsp;&nbsp;&nbsp;The embedded data is stored in:

```js
const STATIC_CHART_DATA = ...
```

&nbsp;&nbsp;&nbsp;&nbsp;---

&nbsp;&nbsp;&nbsp;&nbsp;### 3. 🔥 `trending.html`

&nbsp;&nbsp;&nbsp;&nbsp;Static page for **YouTube Charts VN Trending Videos Right Now**.

&nbsp;&nbsp;&nbsp;&nbsp;This file contains:

&nbsp;&nbsp;&nbsp;&nbsp;- Page UI.
&nbsp;&nbsp;&nbsp;&nbsp;- Embedded Trending Videos chart data.
&nbsp;&nbsp;&nbsp;&nbsp;- JavaScript logic to render the trending list.
&nbsp;&nbsp;&nbsp;&nbsp;- YouTube iframe player logic for in-page playback.

&nbsp;&nbsp;&nbsp;&nbsp;The embedded data is also stored in:

```js
const STATIC_CHART_DATA = ...
```

&nbsp;&nbsp;&nbsp;&nbsp;---

&nbsp;&nbsp;&nbsp;&nbsp;### 4. 🐍 `scripts/update_static_pages.py`

&nbsp;&nbsp;&nbsp;&nbsp;Python script that refreshes the embedded chart data inside the HTML pages.

&nbsp;&nbsp;&nbsp;&nbsp;What it does:

&nbsp;&nbsp;&nbsp;&nbsp;1. Fetches YouTube Charts VN Top Songs Weekly data.
&nbsp;&nbsp;&nbsp;&nbsp;2. Fetches YouTube Charts VN Trending Videos Right Now data.
&nbsp;&nbsp;&nbsp;&nbsp;3. Extracts chart entries and video IDs.
&nbsp;&nbsp;&nbsp;&nbsp;4. Replaces the `STATIC_CHART_DATA` block inside:
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- `top_songs.html`
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- `trending.html`
&nbsp;&nbsp;&nbsp;&nbsp;5. Saves the updated HTML files.

&nbsp;&nbsp;&nbsp;&nbsp;Manual run:

```bash
python scripts/update_static_pages.py
```

&nbsp;&nbsp;&nbsp;&nbsp;---

&nbsp;&nbsp;&nbsp;&nbsp;### 5. ⚙️ `.github/workflows/update-charts.yml`

&nbsp;&nbsp;&nbsp;&nbsp;GitHub Actions workflow that automatically runs the update script.

&nbsp;&nbsp;&nbsp;&nbsp;It is triggered by:

&nbsp;&nbsp;&nbsp;&nbsp;#### a. ⏰ Schedule

```yaml
- cron: "0 */2 * * *"
```

&nbsp;&nbsp;&nbsp;&nbsp;This means the workflow runs every **2 hours**.

&nbsp;&nbsp;&nbsp;&nbsp;#### b. ▶️ Manual Trigger

```yaml
workflow_dispatch:
```

&nbsp;&nbsp;&nbsp;&nbsp;This allows running it manually from the GitHub Actions UI with **Run workflow**.

---

## III. 🧠 How the UI Works

&nbsp;&nbsp;&nbsp;&nbsp;### 1. 📍 Data source

&nbsp;&nbsp;&nbsp;&nbsp;The chart data comes from YouTube Charts:

```text
https://charts.youtube.com/charts/TopSongs/vn/weekly
https://charts.youtube.com/charts/TrendingVideos/vn/RightNow
```

&nbsp;&nbsp;&nbsp;&nbsp;The updater script reads the YouTube Charts page config, then calls YouTube's internal chart endpoint:

```text
https://charts.youtube.com/youtubei/v1/browse?alt=json
```

&nbsp;&nbsp;&nbsp;&nbsp;The request is forced to Vietnam context:

```text
region = vn
gl = VN
hl = vi
Accept-Language = vi-VN
```

&nbsp;&nbsp;&nbsp;&nbsp;This prevents GitHub Actions runners from accidentally fetching US/global chart data.

&nbsp;&nbsp;&nbsp;&nbsp;---

&nbsp;&nbsp;&nbsp;&nbsp;### 2. 📥 Fetch/update method

&nbsp;&nbsp;&nbsp;&nbsp;The Python script:

```text
scripts/update_static_pages.py
```

&nbsp;&nbsp;&nbsp;&nbsp;uses HTTP requests to:

&nbsp;&nbsp;&nbsp;&nbsp;1. Load the YouTube Charts page.
&nbsp;&nbsp;&nbsp;&nbsp;2. Extract the `ytcfg` / InnerTube context.
&nbsp;&nbsp;&nbsp;&nbsp;3. Send a JSON request to the YouTube Charts internal endpoint.
&nbsp;&nbsp;&nbsp;&nbsp;4. Parse the JSON response.
&nbsp;&nbsp;&nbsp;&nbsp;5. Extract the relevant chart entries.

&nbsp;&nbsp;&nbsp;&nbsp;For **Top Songs**, the script extracts:

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

&nbsp;&nbsp;&nbsp;&nbsp;For **Trending Videos**, the script extracts:

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

&nbsp;&nbsp;&nbsp;&nbsp;Note: Trending Videos currently does not expose reliable view counts in the YouTube Charts response, so views are not displayed for the Trending tab.

&nbsp;&nbsp;&nbsp;&nbsp;---

&nbsp;&nbsp;&nbsp;&nbsp;### 3. 📦 Static output method

&nbsp;&nbsp;&nbsp;&nbsp;GitHub Pages cannot run Python.

&nbsp;&nbsp;&nbsp;&nbsp;Because of that, the script writes the fetched data directly into the HTML files as embedded JavaScript:

```js
const STATIC_CHART_DATA = {...}
```

&nbsp;&nbsp;&nbsp;&nbsp;The updated files are:

```text
top_songs.html
trending.html
```

&nbsp;&nbsp;&nbsp;&nbsp;When a user opens the website, the browser does **not** call YouTube Charts directly. Instead, it reads the already embedded `STATIC_CHART_DATA` from the HTML file and renders the UI.

&nbsp;&nbsp;&nbsp;&nbsp;---

&nbsp;&nbsp;&nbsp;&nbsp;### 4. 🖥️ UI rendering method

&nbsp;&nbsp;&nbsp;&nbsp;The HTML pages use client-side JavaScript to:

&nbsp;&nbsp;&nbsp;&nbsp;1. Read `STATIC_CHART_DATA`.
&nbsp;&nbsp;&nbsp;&nbsp;2. Render the chart list.
&nbsp;&nbsp;&nbsp;&nbsp;3. Show the current selected song/video.
&nbsp;&nbsp;&nbsp;&nbsp;4. Load the selected `videoId` into the YouTube iframe player.
&nbsp;&nbsp;&nbsp;&nbsp;5. Handle playback controls:
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- Play / Pause
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- Previous
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- Next
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- Repeat
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- Shuffle

&nbsp;&nbsp;&nbsp;&nbsp;The actual video/audio playback is handled by YouTube through the iframe player:

```text
https://www.youtube.com/iframe_api
```

&nbsp;&nbsp;&nbsp;&nbsp;GitHub Pages only hosts the UI and embedded chart data. YouTube streams the actual media.

&nbsp;&nbsp;&nbsp;&nbsp;---

&nbsp;&nbsp;&nbsp;&nbsp;### 5. 📤 Output shown on the website

&nbsp;&nbsp;&nbsp;&nbsp;The website outputs:

&nbsp;&nbsp;&nbsp;&nbsp;#### Top Songs page

&nbsp;&nbsp;&nbsp;&nbsp;- Weekly Top Songs list for Vietnam.
&nbsp;&nbsp;&nbsp;&nbsp;- Current song title.
&nbsp;&nbsp;&nbsp;&nbsp;- Artist/singer name.
&nbsp;&nbsp;&nbsp;&nbsp;- View count for the selected song.
&nbsp;&nbsp;&nbsp;&nbsp;- Last updated time.
&nbsp;&nbsp;&nbsp;&nbsp;- YouTube iframe playback.

&nbsp;&nbsp;&nbsp;&nbsp;#### Trending page

&nbsp;&nbsp;&nbsp;&nbsp;- Trending Videos list for Vietnam.
&nbsp;&nbsp;&nbsp;&nbsp;- Current video title.
&nbsp;&nbsp;&nbsp;&nbsp;- Artist/channel name.
&nbsp;&nbsp;&nbsp;&nbsp;- Last updated time.
&nbsp;&nbsp;&nbsp;&nbsp;- YouTube iframe playback.

---

## IV. 🚀 GitHub Pages Setup

&nbsp;&nbsp;&nbsp;&nbsp;### 1. 📂 Required repository structure

&nbsp;&nbsp;&nbsp;&nbsp;The repository should keep these files at the root level:

```text
index.html
top_songs.html
trending.html
```

&nbsp;&nbsp;&nbsp;&nbsp;The update script and workflow should stay here:

```text
scripts/update_static_pages.py
.github/workflows/update-charts.yml
```

&nbsp;&nbsp;&nbsp;&nbsp;---

&nbsp;&nbsp;&nbsp;&nbsp;### 2. ⚙️ Enable GitHub Pages

&nbsp;&nbsp;&nbsp;&nbsp;In the GitHub repository:

&nbsp;&nbsp;&nbsp;&nbsp;1. Open **Settings**.
&nbsp;&nbsp;&nbsp;&nbsp;2. Open **Pages**.
&nbsp;&nbsp;&nbsp;&nbsp;3. Under **Build and deployment**, choose:
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- Source: **Deploy from a branch**
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- Branch: **main**
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- Folder: **/ root**
&nbsp;&nbsp;&nbsp;&nbsp;4. Click **Save**.

&nbsp;&nbsp;&nbsp;&nbsp;After deployment, GitHub will provide a public URL like:

```text
https://<github-username>.github.io/<repository-name>/
```

&nbsp;&nbsp;&nbsp;&nbsp;---

&nbsp;&nbsp;&nbsp;&nbsp;### 3. 🔐 Enable workflow write permission

&nbsp;&nbsp;&nbsp;&nbsp;The workflow needs permission to commit updated HTML files back to the repository.

&nbsp;&nbsp;&nbsp;&nbsp;In the GitHub repository:

&nbsp;&nbsp;&nbsp;&nbsp;1. Open **Settings**.
&nbsp;&nbsp;&nbsp;&nbsp;2. Open **Actions** → **General**.
&nbsp;&nbsp;&nbsp;&nbsp;3. Find **Workflow permissions**.
&nbsp;&nbsp;&nbsp;&nbsp;4. Select **Read and write permissions**.
&nbsp;&nbsp;&nbsp;&nbsp;5. Click **Save**.

&nbsp;&nbsp;&nbsp;&nbsp;---

&nbsp;&nbsp;&nbsp;&nbsp;### 4. ▶️ Run the workflow manually

&nbsp;&nbsp;&nbsp;&nbsp;In the GitHub repository:

&nbsp;&nbsp;&nbsp;&nbsp;1. Open the **Actions** tab.
&nbsp;&nbsp;&nbsp;&nbsp;2. Select **Update YouTube Charts Data**.
&nbsp;&nbsp;&nbsp;&nbsp;3. Click **Run workflow**.
&nbsp;&nbsp;&nbsp;&nbsp;4. Select branch **main**.
&nbsp;&nbsp;&nbsp;&nbsp;5. Click **Run workflow** again.

&nbsp;&nbsp;&nbsp;&nbsp;If chart data changes, the workflow commits and pushes updated HTML files automatically.

---

## V. 🔄 Update Flow

&nbsp;&nbsp;&nbsp;&nbsp;### 1. GitHub Actions run flow

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

&nbsp;&nbsp;&nbsp;&nbsp;### 2. Manual local update flow

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
