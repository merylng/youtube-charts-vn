# Lyrics for Top Songs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fetch plain lyrics from LRCLIB during the Python chart update and display them open by default below the player in `top_songs.html`.

**Architecture:** Extend `scripts/update_static_pages.py` with an LRCLIB lookup loop (per-song, resilient, cached) that stores `lyrics` per song in the embedded `STATIC_CHART_DATA`. Add a lyrics panel to `top_songs.html` rendered from `song.lyrics` with a short fallback message. `trending.html` and the workflow stay untouched.

**Tech Stack:** Python 3.12 stdlib (`urllib`, `json`, `re`, `unicodedata`), static HTML/CSS/vanilla JS.

Spec: `docs/superpowers/specs/2026-08-05-lyrics-design.md`

---

## File Structure

- `scripts/update_static_pages.py` — add `LRCLIB` constant, `normalize_for_match()`, `fetch_lyrics()`, wire into `main()`, summary print.
- `tests/test_update_static_pages.py` — new `unittest` tests for the pure helpers (`normalize_for_match`, synced-to-plain stripping, cache behavior) using `unittest.mock` to avoid real network calls.
- `top_songs.html` — add `.lyrics` CSS, lyrics block after `#notice`, `els.lyrics`, and render logic in `loadSong()`.

---

## Task 1: `normalize_for_match()` helper

**Files:**
- Create: `tests/test_update_static_pages.py`
- Modify: `scripts/update_static_pages.py` (add import + helper)

- [ ] **Step 1: Write the failing test**

```python
import unittest

from update_static_pages import normalize_for_match


class NormalizeForMatchTest(unittest.TestCase):
    def test_lowercases_and_strips_diacritics(self):
        self.assertEqual(normalize_for_match("MỘNG DUYÊN"), "mong duyen")

    def test_strips_punctuation_and_spaces(self):
        self.assertEqual(normalize_for_match("  Tìm Em (feat. Bảo Anh )  "), "tim em feat bao anh")

    def test_keeps_ascii(self):
        self.assertEqual(normalize_for_match("Ariana Grande"), "ariana grande")

    def test_returns_empty_for_empty_input(self):
        self.assertEqual(normalize_for_match(""), "")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "D:/02_Clone git/01_github/youtube-charts-vn" && python -m unittest tests.test_update_static_pages -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'update_static_pages'` or `ImportError: cannot import name 'normalize_for_match'`

- [ ] **Step 3: Add the import and helper to `scripts/update_static_pages.py`**

Add `import unicodedata` to the imports at the top, then add this helper after `vietnam_timestamp()` (around line 127):

```python
def normalize_for_match(value):
    text = unicodedata.normalize("NFD", str(value or "").lower())
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", " ", text).strip()
```

Also add `import sys` + a path insert so the test can import the script module directly, at the top after the existing imports:

```python
sys.path.insert(0, str(ROOT / "scripts"))
```

Place `ROOT` definition before the `sys.path.insert` line.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd "D:/02_Clone git/01_github/youtube-charts-vn" && python -m unittest tests.test_update_static_pages -v`
Expected: PASS (4 tests)

- [ ] **Step 5: Commit**

```bash
cd "D:/02_Clone git/01_github/youtube-charts-vn"
git add scripts/update_static_pages.py tests/test_update_static_pages.py
git commit -m "feat: add title/artist normalizer for lyrics matching"
```

---

## Task 2: synced-to-plain lyric conversion

**Files:**
- Modify: `tests/test_update_static_pages.py`
- Modify: `scripts/update_static_pages.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_update_static_pages.py`:

```python
from update_static_pages import plain_from_synced


class PlainFromSyncedTest(unittest.TestCase):
    def test_keeps_plain_text(self):
        self.assertEqual(plain_from_synced("Line one\nLine two"), "Line one\nLine two")

    def test_strips_timestamp_prefixes(self):
        synced = "[00:12.34]Line one\n[00:15.00]Line two"
        self.assertEqual(plain_from_synced(synced), "Line one\nLine two")

    def test_handles_empty(self):
        self.assertEqual(plain_from_synced(""), "")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "D:/02_Clone git/01_github/youtube-charts-vn" && python -m unittest tests.test_update_static_pages -v`
Expected: FAIL with `ImportError: cannot import name 'plain_from_synced'`

- [ ] **Step 3: Add the helper**

Add after `normalize_for_match()` in `scripts/update_static_pages.py`:

```python
TIMESTAMP_RE = re.compile(r"^\[[^\]]*\]\s*")

def plain_from_synced(lyrics):
    lines = []
    for line in (lyrics or "").splitlines():
        line = TIMESTAMP_RE.sub("", line).strip()
        if line:
            lines.append(line)
    return "\n".join(lines)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd "D:/02_Clone git/01_github/youtube-charts-vn" && python -m unittest tests.test_update_static_pages -v`
Expected: PASS (7 tests)

- [ ] **Step 5: Commit**

```bash
cd "D:/02_Clone git/01_github/youtube-charts-vn"
git add scripts/update_static_pages.py tests/test_update_static_pages.py
git commit -m "feat: convert synced lyrics to plain text"
```

---

## Task 3: `fetch_lyrics()` with LRCLIB + cache

**Files:**
- Modify: `tests/test_update_static_pages.py`
- Modify: `scripts/update_static_pages.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_update_static_pages.py`:

```python
import json
from unittest import mock

from update_static_pages import fetch_lyrics


class FetchLyricsTest(unittest.TestCase):
    def make_response(self, payload):
        response = mock.Mock()
        response.status = 200
        response.read.return_value = json.dumps(payload).encode()
        return response

    def test_returns_plain_lyrics(self):
        payload = {
            "trackName": "Tìm Em",
            "artistName": "Hngle",
            "plainLyrics": "Lời bài hát",
            "syncedLyrics": None,
            "instrumental": False,
        }
        with mock.patch("update_static_pages.urlopen", return_value=self.make_response(payload)):
            self.assertEqual(fetch_lyrics("Tìm Em", "Hngle"), "Lời bài hát")

    def test_uses_synced_when_plain_missing(self):
        payload = {
            "trackName": "Tìm Em",
            "artistName": "Hngle",
            "plainLyrics": None,
            "syncedLyrics": "[00:12.34]Line",
            "instrumental": False,
        }
        with mock.patch("update_static_pages.urlopen", return_value=self.make_response(payload)):
            self.assertEqual(fetch_lyrics("Tìm Em", "Hngle"), "Line")

    def test_rejects_mismatched_artist(self):
        payload = {
            "trackName": "Tìm Em",
            "artistName": "Someone Else",
            "plainLyrics": "Lời bài hát",
            "syncedLyrics": None,
            "instrumental": False,
        }
        with mock.patch("update_static_pages.urlopen", return_value=self.make_response(payload)):
            self.assertEqual(fetch_lyrics("Tìm Em", "Hngle"), "")

    def test_returns_empty_on_http_error(self):
        with mock.patch("update_static_pages.urlopen", side_effect=Exception("boom")):
            self.assertEqual(fetch_lyrics("Tìm Em", "Hngle"), "")

    def test_caches_by_title_artist(self):
        payload = {
            "trackName": "Tìm Em",
            "artistName": "Hngle",
            "plainLyrics": "Lời bài hát",
            "syncedLyrics": None,
            "instrumental": False,
        }
        with mock.patch("update_static_pages.urlopen", return_value=self.make_response(payload)) as mocked:
            self.assertEqual(fetch_lyrics("Tìm Em", "Hngle"), "Lời bài hát")
            self.assertEqual(fetch_lyrics("Tìm Em", "Hngle"), "Lời bài hát")
            self.assertEqual(mocked.call_count, 1)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "D:/02_Clone git/01_github/youtube-charts-vn" && python -m unittest tests.test_update_static_pages -v`
Expected: FAIL with `ImportError: cannot import name 'fetch_lyrics'`

- [ ] **Step 3: Add the constant and function**

Add `LRCLIB = "https://lrclib.net/api/get"` near the other constants (around line 10). Then add after `plain_from_synced()`:

```python
def fetch_lyrics(title, artists):
    key = normalize_for_match(f"{title}|{artists}")
    if key in fetch_lyrics.cache:
        return fetch_lyrics.cache[key]

    lyrics = ""
    try:
        params = urllib.parse.urlencode({
            "track_name": title,
            "artist_name": artists,
        })
        request = Request(
            f"{LRCLIB}?{params}",
            headers={"User-Agent": "youtube-charts-vn-updater/1.0 (static site updater)"},
        )
        with urlopen(request, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8", "replace"))
        if not payload.get("instrumental"):
            track_name = normalize_for_match(payload.get("trackName", ""))
            artist_name = normalize_for_match(payload.get("artistName", ""))
            if track_name and (track_name == normalize_for_match(title) or track_name in normalize_for_match(title)):
                if artist_name and artist_name == normalize_for_match(artists):
                    plain = payload.get("plainLyrics") or ""
                    synced = payload.get("syncedLyrics") or ""
                    if plain.strip():
                        lyrics = plain.strip()
                    elif synced.strip():
                        lyrics = plain_from_synced(synced)
    except Exception:
        lyrics = ""

    fetch_lyrics.cache[key] = lyrics
    return lyrics


fetch_lyrics.cache = {}
```

Also add `import urllib.parse` to the imports.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd "D:/02_Clone git/01_github/youtube-charts-vn" && python -m unittest tests.test_update_static_pages -v`
Expected: PASS (12 tests)

- [ ] **Step 5: Commit**

```bash
cd "D:/02_Clone git/01_github/youtube-charts-vn"
git add scripts/update_static_pages.py tests/test_update_static_pages.py
git commit -m "feat: fetch lyrics from LRCLIB with cache"
```

---

## Task 4: Wire lyrics into `main()` + summary print

**Files:**
- Modify: `scripts/update_static_pages.py`

- [ ] **Step 1: Modify `main()`**

Replace the body of `main()` (currently lines 144–156) with:

```python
def main():
    updated_at = vietnam_timestamp()
    top_songs = extract_top_songs(fetch_chart_home(TOP_SONGS_PAGE))
    trending = extract_trending_videos(fetch_chart_home(TRENDING_VIDEOS_PAGE))
    top_songs["updatedAt"] = updated_at
    trending["updatedAt"] = updated_at

    with_lyrics = 0
    for song in top_songs["songs"]:
        song["lyrics"] = fetch_lyrics(song["title"], song["artists"])
        if song["lyrics"]:
            with_lyrics += 1

    update_static_data(TOP_SONGS_HTML, top_songs)
    update_static_data(TRENDING_HTML, trending)

    print(f"Updated {TOP_SONGS_HTML.name}: {len(top_songs['songs'])} songs, rangeEnd={top_songs.get('rangeEnd', '')}")
    print(f"Lyrics: {with_lyrics}/{len(top_songs['songs'])} songs")
    print(f"Updated {TRENDING_HTML.name}: {len(trending['videos'])} videos, range={trending.get('rangeLabel', '')}")
    print("Next: commit and push top_songs.html and trending.html to update GitHub Pages.")
```

- [ ] **Step 2: Run the full test suite**

Run: `cd "D:/02_Clone git/01_github/youtube-charts-vn" && python -m unittest discover -s tests -v`
Expected: PASS (all tests)

- [ ] **Step 3: Commit**

```bash
cd "D:/02_Clone git/01_github/youtube-charts-vn"
git add scripts/update_static_pages.py
git commit -m "feat: embed lyrics into top_songs.html during update"
```

---

## Task 5: UI — lyrics panel in `top_songs.html`

**Files:**
- Modify: `top_songs.html`

- [ ] **Step 1: Add `.lyrics` CSS**

After the `.notice` rule (around line 213), add:

```css
.lyrics {
  margin-top: 14px;
  padding: 14px 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.05);
  color: var(--text);
  font-size: 15px;
  line-height: 1.7;
  white-space: pre-line;
  max-height: 320px;
  overflow: auto;
}

.lyrics h3 {
  margin: 0 0 8px;
  color: var(--muted);
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.lyrics .no-lyrics {
  color: var(--muted);
}
```

- [ ] **Step 2: Add the lyrics HTML block**

After the `#notice` div (line 282, before the closing `</div>` of `.now-playing`), add:

```html
          <div class="lyrics" id="lyrics">
            <h3>Lyrics</h3>
            <div id="lyricsText"></div>
          </div>
```

- [ ] **Step 3: Add `lyrics` to `els` map**

In the `els` object (after `notice:` entry, around line 318), add:

```js
      lyrics: document.getElementById('lyricsText'),
```

- [ ] **Step 4: Render lyrics in `loadSong()`**

In `loadSong()` (after `els.nowViews.textContent = formatViews(song.views);`, around line 431), add:

```js
      if (song.lyrics) {
        els.lyrics.innerHTML = escapeHtml(song.lyrics);
      } else {
        els.lyrics.innerHTML = '<div class="no-lyrics">Không có lời bài hát cho bài này.</div>';
      }
```

Note: `els.lyrics` is the `#lyricsText` container, so the `<h3>Lyrics</h3>` heading stays static in the HTML.

- [ ] **Step 5: Verify UI manually**

Run: open `D:\02_Clone git\01_github\youtube-charts-vn\top_songs.html` in a browser via `file://`.
Expected:
- Lyrics panel shows below the notice with heading "Lyrics".
- Selecting a song with `lyrics` shows the lyrics text, open by default.
- Selecting a song with empty `lyrics` shows "Không có lời bài hát cho bài này."

- [ ] **Step 6: Commit**

```bash
cd "D:/02_Clone git/01_github/youtube-charts-vn"
git add top_songs.html
git commit -m "feat: display lyrics panel in top songs page"
```

---

## Task 6: End-to-end verification

**Files:**
- Run: `scripts/update_static_pages.py`

- [ ] **Step 1: Run the updater locally**

Run: `cd "D:/02_Clone git/01_github/youtube-charts-vn" && python scripts/update_static_pages.py`
Expected: prints `Lyrics: <n>/100 songs`, no crash. This hits the live LRCLIB API; allow ~1–2 min for 100 sequential requests.

- [ ] **Step 2: Check generated data**

Run: `grep -o '"lyrics":' top_songs.html | wc -l`
Expected: number equal to 100 (every song has the `lyrics` key, possibly `""`).

Run: `git diff --stat trending.html`
Expected: `trending.html` has no changes (byte-identical).

- [ ] **Step 3: Spot-check 2–3 songs**

Open `https://lrclib.net/api/get?track_name=<title>&artist_name=<artist>` for 2–3 songs that have non-empty lyrics in the generated HTML. Confirm the lyrics match the embedded `song.lyrics`.

- [ ] **Step 4: Commit the regenerated HTML**

```bash
cd "D:/02_Clone git/01_github/youtube-charts-vn"
git add top_songs.html
git commit -m "update lasted data - 2026/08/05"
```

---

## Self-Review Notes

- Spec coverage: all spec points map to Tasks 1–6 (normalizer, fetch/matching, data shape via `lyrics` key, UI open-by-default, fallback message, trending untouched, verification).
- Placeholders: none — every step has concrete code/commands.
- Type consistency: `fetch_lyrics(title, artists)` returns `str`; `song["lyrics"]` is always a string; `els.lyrics` is the `#lyricsText` div.
