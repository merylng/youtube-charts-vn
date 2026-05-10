import json
import re
from pathlib import Path

import youtube_charts_server as charts


ROOT = Path(__file__).resolve().parents[1]
TOP_SONGS_HTML = ROOT / "top_songs.html"
TRENDING_HTML = ROOT / "trending.html"
TRENDING_API_FALLBACK = ROOT / "api" / "trending-videos"


STATIC_DATA_RE = re.compile(
    r"(?P<prefix>\s+const STATIC_CHART_DATA = )(?P<data>.*?)(?P<suffix>;\n\n\s+let songs = \[\];)",
    re.DOTALL,
)


def update_static_data(file_path, payload):
    html = file_path.read_text(encoding="utf-8")
    serialized = json.dumps(payload, ensure_ascii=False)
    updated, count = STATIC_DATA_RE.subn(
        lambda match: f"{match.group('prefix')}{serialized}{match.group('suffix')}",
        html,
        count=1,
    )
    if count != 1:
        raise RuntimeError(f"Cannot find STATIC_CHART_DATA block in {file_path.name}")
    file_path.write_text(updated, encoding="utf-8")


def main():
    top_songs = charts.extract_top_songs(charts.fetch_json(charts.TOP_SONGS_PAGE))
    trending = charts.extract_trending_videos(charts.fetch_json(charts.TRENDING_VIDEOS_PAGE))

    update_static_data(TOP_SONGS_HTML, top_songs)
    update_static_data(TRENDING_HTML, trending)

    TRENDING_API_FALLBACK.parent.mkdir(exist_ok=True)
    TRENDING_API_FALLBACK.write_text(json.dumps(trending), encoding="utf-8")

    print(f"Updated {TOP_SONGS_HTML.name}: {len(top_songs['songs'])} songs, rangeEnd={top_songs.get('rangeEnd', '')}")
    print(f"Updated {TRENDING_HTML.name}: {len(trending['videos'])} videos, range={trending.get('rangeLabel', '')}")
    print("Upload/commit index.html, top_songs.html, trending.html to GitHub Pages after this.")


if __name__ == "__main__":
    main()
