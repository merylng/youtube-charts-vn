# YouTube Charts VN

A static GitHub Pages website for browsing and playing YouTube Charts Vietnam data.

The site currently includes:

- 🎵 **Top Songs Vietnam Weekly**
- 🔥 **Trending Videos Vietnam Right Now**

The UI is static HTML. Chart data is fetched by a Python script, embedded into the HTML files, then published through GitHub Pages.

---

## 📚 Table of Contents

- [I. 🎯 Project Goal](#i--project-goal)
- [II. 🧩 High-Level Architecture](#ii--high-level-architecture)
- [III. 📁 Repository Files](#iii--repository-files)
  - [1. `index.html`](#1-indexhtml)
  - [2. `top_songs.html`](#2-top_songshtml)
  - [3. `trending.html`](#3-trendinghtml)
  - [4. `scripts/update_static_pages.py`](#4-scriptsupdate_static_pagespy)
  - [5. `.github/workflows/update-charts.yml`](#5-githubworkflowsupdate-chartsyml)
- [IV. 📥 Data Source and Fetch Method](#iv--data-source-and-fetch-method)
- [V. 🖥️ UI Behavior](#v-️-ui-behavior)
- [VI. 🔄 Update Flow](#vi--update-flow)
  - [1. Automatic GitHub Actions flow](#1-automatic-github-actions-flow)
  - [2. Manual local update flow](#2-manual-local-update-flow)
- [VII. 🚀 GitHub Pages Setup](#vii--github-pages-setup)
  - [1. Required repository structure](#1-required-repository-structure)
  - [2. Enable GitHub Pages](#2-enable-github-pages)
  - [3. Enable workflow write permission](#3-enable-workflow-write-permission)
  - [4. Run the workflow manually](#4-run-the-workflow-manually)
- [VIII. 📝 Commit Behavior](#viii--commit-behavior)
- [IX. 🔗 Public URLs](#ix--public-urls)
- [X. ▶️ Playback Notes](#x-️-playback-notes)

---

## I. 🎯 Project Goal

This project creates a simple public website where users can:

- View Vietnam YouTube chart lists.
- Switch between **Top Songs** and **Trending** tabs.
- Play videos directly inside the page using the YouTube iframe player.
- See when the data was last updated.

The website is hosted with **GitHub Pages**, so no custom server is required for visitors.

---

## II. 🧩 High-Level Architecture

```text
GitHub Actions schedule/manual trigger
        ↓
Run scripts/update_static_pages.py
        ↓
Fetch Vietnam chart data from YouTube Charts
        ↓
Embed fetched data into HTML as STATIC_CHART_DATA
        ↓
Commit and push updated HTML files
        ↓
GitHub Pages publishes the static UI
        ↓
Users open the public URL and interact with the chart player
```

Important architecture notes:

- GitHub Pages only serves static files.
- GitHub Pages does **not** run Python.
- The Python script runs before publishing and writes the latest data into the HTML files.
- The browser reads embedded `STATIC_CHART_DATA`; it does not fetch live data from YouTube Charts.

---

## III. 📁 Repository Files

Current active files:

```text
index.html
top_songs.html
trending.html
scripts/update_static_pages.py
.github/workflows/update-charts.yml
```

### 1. `index.html`

Purpose:

- Acts as the landing page.
- Redirects users to `top_songs.html`.
- Provides a safe default page for the root GitHub Pages URL.

Root URL:

```text
https://<github-username>.github.io/<repository-name>/
```

### 2. `top_songs.html`

Purpose:

- Displays **YouTube Charts VN Top Songs Weekly**.
- Renders the Top Songs list from embedded static data.
- Shows the selected song title, artist, view count, and last updated time.
- Plays the selected song through the YouTube iframe player.

Main embedded data variable:

```js
const STATIC_CHART_DATA = ...
```

Top Songs data includes:

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

### 3. `trending.html`

Purpose:

- Displays **YouTube Charts VN Trending Videos Right Now**.
- Renders the Trending list from embedded static data.
- Shows the selected video title, artist/channel, and last updated time.
- Plays the selected video through the YouTube iframe player.

Main embedded data variable:

```js
const STATIC_CHART_DATA = ...
```

Trending data includes:

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

Note: YouTube Charts does not currently expose reliable view counts for the Trending response used here, so the Trending tab does not display views.

### 4. `scripts/update_static_pages.py`

Purpose:

- Fetches the latest chart data.
- Forces the request context to Vietnam.
- Extracts useful fields from the YouTube Charts response.
- Replaces the `STATIC_CHART_DATA` block inside:
  - `top_songs.html`
  - `trending.html`

Manual run:

```bash
python scripts/update_static_pages.py
```

### 5. `.github/workflows/update-charts.yml`

Purpose:

- Runs the Python updater automatically on GitHub Actions.
- Commits updated HTML files when chart data changes.
- Pushes changes to `main`, allowing GitHub Pages to republish the site.

Triggers:

```yaml
schedule:
  - cron: "0 */2 * * *"
workflow_dispatch:
```

Meaning:

- Runs every **2 hours**.
- Can also be started manually from the GitHub Actions UI.

---

## IV. 📥 Data Source and Fetch Method

The source pages are:

```text
https://charts.youtube.com/charts/TopSongs/vn/weekly
https://charts.youtube.com/charts/TrendingVideos/vn/RightNow
```

The script loads those pages, extracts YouTube chart configuration, then calls the internal YouTube Charts endpoint:

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

This is important because GitHub Actions runners may run outside Vietnam. Without forcing the context, the fetched chart can accidentally become US/global data.

---

## V. 🖥️ UI Behavior

Both HTML pages use client-side JavaScript to:

1. Read `STATIC_CHART_DATA` from the HTML file.
2. Render the chart list.
3. Load the selected `videoId` into the YouTube iframe player.
4. Show the currently selected title and artist/channel.
5. Support playback controls:
   - Play / Pause
   - Previous
   - Next
   - Repeat
   - Shuffle

Top Songs additionally shows:

- View count for the selected song.

Both pages show:

- Last updated time.
- Chart range/status badge.
- YouTube iframe playback area.

The actual playback is handled by YouTube:

```text
https://www.youtube.com/iframe_api
```

GitHub Pages hosts the UI and embedded data only. YouTube streams the media.

---

## VI. 🔄 Update Flow

### 1. Automatic GitHub Actions flow

```text
Workflow trigger runs every 2 hours
        ↓
Checkout repository
        ↓
Set up Python 3.12
        ↓
Run scripts/update_static_pages.py
        ↓
Fetch Top Songs VN and Trending VN data
        ↓
Rewrite STATIC_CHART_DATA in both HTML files
        ↓
Check git diff
        ↓
If HTML changed: commit and push to main
        ↓
GitHub Pages deploys the updated website
```

### 2. Manual local update flow

```text
Run python scripts/update_static_pages.py locally
        ↓
HTML files are updated on local machine
        ↓
Commit and push the changed files
        ↓
GitHub Pages deploys the updated website
```

Manual commands:

```bash
python scripts/update_static_pages.py
git add top_songs.html trending.html scripts/update_static_pages.py
git commit -m "update lasted data - yyyy/mm/dd"
git push
```

---

## VII. 🚀 GitHub Pages Setup

### 1. Required repository structure

Root files:

```text
index.html
top_songs.html
trending.html
```

Updater and workflow files:

```text
scripts/update_static_pages.py
.github/workflows/update-charts.yml
```

### 2. Enable GitHub Pages

In the GitHub repository:

1. Open **Settings**.
2. Open **Pages**.
3. Under **Build and deployment**, choose:
   - Source: **Deploy from a branch**
   - Branch: **main**
   - Folder: **/ root**
4. Click **Save**.

GitHub will provide a public URL like:

```text
https://<github-username>.github.io/<repository-name>/
```

### 3. Enable workflow write permission

The workflow must be able to commit updated HTML files.

In the GitHub repository:

1. Open **Settings**.
2. Open **Actions** → **General**.
3. Find **Workflow permissions**.
4. Select **Read and write permissions**.
5. Click **Save**.

### 4. Run the workflow manually

In the GitHub repository:

1. Open the **Actions** tab.
2. Select **Update YouTube Charts Data**.
3. Click **Run workflow**.
4. Select branch **main**.
5. Click **Run workflow** again.

If chart data changes, the workflow commits and pushes updated HTML files automatically.

---

## VIII. 📝 Commit Behavior

The workflow stages and checks these files:

```text
top_songs.html
trending.html
```

If there is no data change, there is no commit.

If there is a data change, the workflow commits with this format:

```text
update lasted data - yyyy/mm/dd
```

Example:

```text
update lasted data - 2026/05/11
```

---

## IX. 🔗 Public URLs

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

## X. ▶️ Playback Notes

Some videos may not play inside the page if:

- Embedding is disabled by the video owner.
- The video has region restrictions.
- YouTube applies copyright or playback limitations.

The chart list can still render even if some individual videos cannot be played in the embedded player.

Playback through the embedded YouTube iframe may contribute views to the original YouTube video, but YouTube decides whether each playback is counted as a valid view.

Mobile background playback is not guaranteed because YouTube iframe playback is controlled by mobile browser and YouTube policies.
