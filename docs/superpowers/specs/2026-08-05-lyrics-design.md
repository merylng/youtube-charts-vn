# Lyrics for Top Songs — Design Spec

Date: 2026-08-05
Status: Approved

## Goal

Add plain lyrics for each Top Songs result in the static YouTube Charts VN site. During the Python chart update, query LRCLIB by song title and artist, select the best match, embed the lyrics into `top_songs.html`, and display them open by default below the player/notice area. Trending stays untouched for now (can be added later after review).

## Scope

- Only Top Songs (`top_songs.html`).
- Plain lyrics only. Synced lyrics are kept in data if LRCLIB provides them, but the initial UI shows plain text.
- No browser-side fetch; site remains fully static.

## Data source

- LRCLIB public API, no auth: `GET https://lrclib.net/api/get?track_name=<urlencoded title>&artist_name=<urlencoded artists>`
- Returns one best match (or 404 if none).
- Fields used: `trackName`, `artistName`, `plainLyrics`, `syncedLyrics`, `instrumental`.

## Data shape

Each Top Songs entry gains one key:

```json
{
  "rank": 1,
  "title": "Tìm Em (feat. Bảo Anh )",
  "artists": "Hngle",
  "videoId": "gJAbDSse5WM",
  "thumbnail": "...",
  "views": 5744933,
  "lastRank": 1,
  "periodsOnChart": 6,
  "lyrics": "plain text or empty string"
}
```

`lyrics` is always a string; `""` means absent.

## Python changes (`scripts/update_static_pages.py`)

- Add module constant `LRCLIB = "https://lrclib.net/api/get"`.
- Add helpers `normalize_for_match(s)` (lowercase, strip diacritics via NFD, strip punctuation) and `fetch_lyrics(title, artists)`.
- In `main()`, after `extract_top_songs(...)`, loop over `top_songs["songs"]` and set `song["lyrics"] = fetch_lyrics(song["title"], song["artists"])` before `update_static_data(TOP_SONGS_HTML, top_songs)`.
- Matching: accept the `/api/get` result; sanity-check normalized title/artist. Skip titles clearly unlikely to match (live/cover/remix/intro...).
- Plain lyrics preferred; if only synced exists, strip `[mm:ss.xx]` timestamp lines.
- Robustness: short timeout (~5s), per-song try/except (failure → `""`, never abort), valid `User-Agent` header, small per-request spacing (~0.1–0.2s), in-run cache keyed by normalized title+artist to avoid duplicate fetches.
- Print a summary count of songs with lyrics.

## UI changes (`top_songs.html` only)

- HTML: add a lyrics block below `#notice` inside `.now-playing`:
  - `<div class="lyrics" id="lyrics">` with a heading and empty container.
- CSS: style `.lyrics` like `.notice` (panel card, rounded), `white-space: pre-line`.
- JS:
  - Add `lyrics` to the `els` map.
  - In `loadSong()`, render `song.lyrics` via `escapeHtml()` (existing helper), open by default.
  - If `lyrics` is empty, show a short message: "Không có lời bài hát cho bài này."

## Unchanged

- `trending.html`
- `.github/workflows/update-charts.yml`
- `update_static_data()` / `STATIC_DATA_RE`
- `renderList()` (no lyrics indicator in list in this version)

## Verification

1. Run `python scripts/update_static_pages.py` locally; confirm no crash, lyrics counts in output, `trending.html` byte-identical.
2. Grep generated `STATIC_CHART_DATA` for `"lyrics":` entries; spot-check 2–3 songs against lrclib.net manually.
3. Open `top_songs.html` via `file://` — lyrics panel renders below the notice, switches per song, shows fallback message when absent.
4. Sanity: lyrics with quotes/`<` render safely (escapeHtml).

## Caveats

- LRCLIB has community-enforced rate limits (429s); sequential pass with spacing is fine for on-demand runs.
- Matching quality varies, especially for Vietnamese titles, remixes, and "(Live)" variants; the normalized-title check and skip list reduce wrong matches.
- Lyrics are a snapshot at update time; no auto-refresh.
