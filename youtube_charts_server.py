import json
import re
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

TOP_SONGS_PAGE = "https://charts.youtube.com/charts/TopSongs/vn/weekly"
TRENDING_VIDEOS_PAGE = "https://charts.youtube.com/charts/TrendingVideos/vn/RightNow"
INNERTUBE = "https://charts.youtube.com/youtubei/v1/browse?alt=json"


def fetch_json(referer=TOP_SONGS_PAGE):
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
    thumbs = (thumbnail or {}).get("thumbnails") or []
    if not thumbs:
        return ""
    return max(thumbs, key=lambda item: item.get("width", 0)).get("url", "")


def extract_top_songs(data):
    track_type = None
    for item in walk(data):
        if item.get("listType") == "TOP_VIEWS_CHART" and item.get("chartPeriodType") == "CHART_PERIOD_TYPE_WEEKLY" and item.get("trackViews"):
            track_type = item
            break
    if not track_type:
        for item in walk(data):
            if item.get("listType") == "TOP_VIEWS_CHART" and item.get("trackViews"):
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
            "title": item.get("name") or "Không rõ tên bài hát",
            "artists": ", ".join(artist.get("name", "") for artist in item.get("artists", []) if artist.get("name")) or "Không rõ nghệ sĩ",
            "videoId": video_id,
            "thumbnail": best_thumbnail(item.get("thumbnail")),
            "views": int(item.get("viewCount", 0) or 0),
            "lastRank": meta.get("previousPosition"),
            "periodsOnChart": meta.get("periodsOnChart"),
        })

    latest = track_type.get("endDate", "")
    return {"rangeEnd": latest, "songs": songs}


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
            "title": item.get("title") or "Không rõ tên video",
            "artists": ", ".join(artist.get("name", "") for artist in item.get("artists", []) if artist.get("name")) or item.get("channelName") or "Không rõ kênh",
            "channelName": item.get("channelName") or "",
            "videoId": video_id,
            "thumbnail": best_thumbnail(item.get("thumbnail")),
            "views": int(item.get("viewCount", 0) or 0),
            "lastRank": meta.get("previousPosition"),
            "periodsOnChart": meta.get("periodsOnChart"),
        })

    return {"rangeLabel": "Right Now", "videos": videos}


def json_response(handler, status, payload):
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/top-songs":
            try:
                json_response(self, 200, extract_top_songs(fetch_json(TOP_SONGS_PAGE)))
            except (HTTPError, Exception) as error:
                json_response(self, 502, {"error": str(error)})
            return
        if path == "/api/trending-videos":
            try:
                json_response(self, 200, extract_trending_videos(fetch_json(TRENDING_VIDEOS_PAGE)))
            except (HTTPError, Exception) as error:
                json_response(self, 502, {"error": str(error)})
            return
        super().do_GET()


if __name__ == "__main__":
    port = 8000
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Open http://127.0.0.1:{port}/top_songs.html", flush=True)
    server.serve_forever()
