# YouTube Charts VN Pages

This repository contains static HTML pages for showing YouTube Charts Vietnam data:

- Top Songs Vietnam Weekly
- Trending Videos Vietnam Right Now

The pages are designed for **GitHub Pages**. Other people can view them through a public GitHub Pages URL.

## Current repository structure

```text
youtube-charts-vn/
│
├─ index.html
├─ top_songs.html
├─ trending.html
│
└─ scripts/
   └─ update_static_pages.py
```

## File meanings

### `index.html`

Main landing page.

It redirects users to the Top Songs page and provides navigation links to:

- `top_songs.html`
- `trending.html`

When GitHub Pages is enabled, this is the default page opened at:

```text
https://<github-username>.github.io/<repository-name>/
```

### `top_songs.html`

Static page for **YouTube Charts VN Top Songs Weekly**.

It shows the Top Songs list and includes a YouTube iframe player so users can play songs inside the page.

This file contains embedded chart data, so it can work on GitHub Pages without a backend server.

Direct URL after publishing:

```text
https://<github-username>.github.io/<repository-name>/top_songs.html
```

### `trending.html`

Static page for **YouTube Charts VN Trending Videos Right Now**.

It shows the Trending Videos list and includes a YouTube iframe player so users can play videos inside the page.

This file also contains embedded chart data, so it can work on GitHub Pages without a backend server.

Direct URL after publishing:

```text
https://<github-username>.github.io/<repository-name>/trending.html
```

### `scripts/update_static_pages.py`

Helper script for refreshing the embedded chart data inside the static HTML pages.

Run this script locally before uploading or committing updated pages to GitHub:

```bash
python scripts/update_static_pages.py
```

It updates the embedded data inside:

```text
top_songs.html
trending.html
```

After running it, commit or upload the updated HTML files to GitHub so GitHub Pages shows the latest data.

## How the website works

GitHub Pages can only host static files such as:

- HTML
- CSS
- JavaScript

It does **not** run Python scripts.

Because of that, the chart data is embedded directly inside:

```text
top_songs.html
trending.html
```

The flow is:

```text
Run scripts/update_static_pages.py locally
        ↓
Fetch latest YouTube Charts data
        ↓
Embed the data into top_songs.html and trending.html
        ↓
Commit or upload the updated HTML files to GitHub
        ↓
GitHub Pages publishes the static website
        ↓
Users open the public URL and view the chart lists
```

The website stores chart metadata and YouTube video IDs. Actual playback is handled by the YouTube iframe player.

## Local usage

You can open these files directly in a browser:

```text
top_songs.html
trending.html
```

The lists will appear because the chart data is already embedded in the HTML files.

However, YouTube iframe playback may not always work correctly when opened with `file://`. Playback usually works better after publishing to GitHub Pages because the page is served over HTTPS.

## Updating chart data

To refresh the chart data:

```bash
python scripts/update_static_pages.py
```

Then commit or upload the updated files:

```text
index.html
top_songs.html
trending.html
scripts/update_static_pages.py
```

Usually only these files change after an update:

```text
top_songs.html
trending.html
```

## Publishing with GitHub Pages

### 1. Create or open the GitHub repository

Example repository name:

```text
youtube-charts-vn
```

### 2. Upload the files

Make sure the repository contains:

```text
index.html
top_songs.html
trending.html
scripts/update_static_pages.py
```

### 3. Enable GitHub Pages

In the GitHub repository:

1. Open **Settings**.
2. Open **Pages**.
3. Under **Build and deployment**, choose:
   - Source: **Deploy from a branch**
   - Branch: **main**
   - Folder: **/ root**
4. Click **Save**.

### 4. Get the public URL

After GitHub Pages finishes deploying, GitHub will show a message like:

```text
Your site is live at https://<github-username>.github.io/<repository-name>/
```

Example:

```text
https://merylng1010.github.io/youtube-charts-vn/
```

Share that URL with other people.

## Page URLs

Default page:

```text
https://<github-username>.github.io/<repository-name>/
```

Top Songs page:

```text
https://<github-username>.github.io/<repository-name>/top_songs.html
```

Trending page:

```text
https://<github-username>.github.io/<repository-name>/trending.html
```

## Important notes

- GitHub Pages does not run Python.
- The Python script is only for updating the static HTML files locally.
- The public website will not automatically update by itself.
- To refresh public data, run `python scripts/update_static_pages.py`, then commit or upload the updated HTML files.
- Some YouTube videos may not play inside the iframe if embedding is disabled or if there are region/copyright restrictions.
