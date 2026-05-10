import json
import re
from pathlib import Path
from urllib.request import Request, urlopen

TOP_SONGS_PAGE = "https://charts.youtube.com/charts/TopSongs/vn/weekly"
TRENDING_VIDEOS_PAGE = "https://charts.youtube.com/charts/TrendingVideos/vn/RightNow"
INNERTUBE = "https://charts.youtube.com/youtubei/v1/browse?alt=json"

ROOT = Path(__file__).resolve().parents[1]
TOP_SONGS_HTML = ROOT / "top_songs.html"
TRENDING_HTML = ROOT / "trending.html"

STATIC_DATA_RE = re.compile(
    r"(?P<prefix>\s+const STATIC_CHART_DATA = )(?P<data>.*?)(?P<suffix>;\n\n\s+let songs = \[\];)",
    re.DOTALL,
)


def fetch_chart_home(referer):
    page_req = Request(referer, headers={"User-Agent": "Mozilla/5.0"})
    html = urlopen(page_req, timeout=20).read().decode("utf-8", "replace")
    match = re.search(r"ytcfg\.set\((\{.*?\})\);", html)
    if not match:
        raise RuntimeError("Cannot find YouTube Charts config")

    cfg = json.loads(match.group(1))
    payload = {
        "context": cfg["INNERTUBE_CONTEXT"],
        "browseId": "FEmusic_analytics_charts_home",
        "query": json.dumps({"region": "vn"}, separators=(",", ":")),
    }
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
        "Origin": "https://charts.youtube.com",
        "Referer": referer,
        "X-Goog-Visitor-Id": cfg["INNERTUBE_CONTEXT"]["client"].get("visitorData", ""),
    }
    req = Request(INNERTUBE, data=json.dumps(payload, separators=(",", ":")).encode(), headers=headers)
    return json.loads(urlopen(req, timeout=30).read().decode("utf-8", "replace"))


def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def best_thumbnail(thumbnail):
    thumbnails = (thumbnail or {}).get("thumbnails") or []
    if not thumbnails:
        return ""
    return max(thumbnails, key=lambda item: item.get("width", 0)).get("url", "")


def extract_top_songs(data):
    track_type = None
    for item in walk(data):
        if item.get("listType") == "TOP_VIEWS_CHART" and item.get("chartPeriodType") == "CHART_PERIOD_TYPE_WEEKLY" and item.get("trackViews"):
            track_type = item
            break
    if not track_type:
        raise RuntimeError("Cannot find weekly Top Songs list")

    songs = []
    for fallback_rank, item in enumerate(track_type.get("trackViews", []), start=1):
        meta = item.get("chartEntryMetadata") or {}
        video_id = item.get("encryptedVideoId") or item.get("id") or ""
        if not video_id:
            continue
        songs.append({
            "rank": meta.get("currentPosition") or fallback_rank,
            "title": item.get("name") or "Unknown song",
            "artists": ", ".join(artist.get("name", "") for artist in item.get("artists", []) if artist.get("name")) or "Unknown artist",
            "videoId": video_id,
            "thumbnail": best_thumbnail(item.get("thumbnail")),
            "views": int(item.get("viewCount", 0) or 0),
            "lastRank": meta.get("previousPosition"),
            "periodsOnChart": meta.get("periodsOnChart"),
        })

    return {"rangeEnd": track_type.get("endDate", ""), "songs": songs}


def extract_trending_videos(data):
    video_type = None
    for item in walk(data):
        if item.get("listType") == "TRENDING_CHART" and item.get("videoViews"):
            video_type = item
            break
    if not video_type:
        raise RuntimeError("Cannot find Trending Videos list")

    videos = []
    for fallback_rank, item in enumerate(video_type.get("videoViews", []), start=1):
        meta = item.get("chartEntryMetadata") or {}
        video_id = item.get("id") or ""
        if not video_id:
            continue
        videos.append({
            "rank": meta.get("currentPosition") or fallback_rank,
            "title": item.get("title") or "Unknown video",
            "artists": ", ".join(artist.get("name", "") for artist in item.get("artists", []) if artist.get("name")) or item.get("channelName") or "Unknown channel",
            "channelName": item.get("channelName") or "",
            "videoId": video_id,
            "thumbnail": best_thumbnail(item.get("thumbnail")),
            "views": int(item.get("viewCount", 0) or 0),
            "lastRank": meta.get("previousPosition"),
            "periodsOnChart": meta.get("periodsOnChart"),
        })

    return {"rangeLabel": "Right Now", "videos": videos}


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
    top_songs = extract_top_songs(fetch_chart_home(TOP_SONGS_PAGE))
    trending = extract_trending_videos(fetch_chart_home(TRENDING_VIDEOS_PAGE))

    update_static_data(TOP_SONGS_HTML, top_songs)
    update_static_data(TRENDING_HTML, trending)

    print(f"Updated {TOP_SONGS_HTML.name}: {len(top_songs['songs'])} songs, rangeEnd={top_songs.get('rangeEnd', '')}")
    print(f"Updated {TRENDING_HTML.name}: {len(trending['videos'])} videos, range={trending.get('rangeLabel', '')}")
    print("Next: commit and push top_songs.html and trending.html to update GitHub Pages.")


if __name__ == "__main__":
    main()
