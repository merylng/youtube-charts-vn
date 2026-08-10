import json
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from update_static_pages import fetch_lyrics
from update_static_pages import normalize_for_match
from update_static_pages import plain_from_synced
from update_static_pages import is_music_video


class NormalizeForMatchTest(unittest.TestCase):
    def test_lowercases_and_strips_diacritics(self):
        self.assertEqual(normalize_for_match("MỘNG DUYÊN"), "mong duyen")

    def test_strips_punctuation_and_spaces(self):
        self.assertEqual(normalize_for_match("  Tìm Em (feat. Bảo Anh )  "), "tim em feat bao anh")

    def test_keeps_ascii(self):
        self.assertEqual(normalize_for_match("Ariana Grande"), "ariana grande")

    def test_returns_empty_for_empty_input(self):
        self.assertEqual(normalize_for_match(""), "")


class PlainFromSyncedTest(unittest.TestCase):
    def test_keeps_plain_text(self):
        self.assertEqual(plain_from_synced("Line one\nLine two"), "Line one\nLine two")

    def test_strips_timestamp_prefixes(self):
        synced = "[00:12.34]Line one\n[00:15.00]Line two"
        self.assertEqual(plain_from_synced(synced), "Line one\nLine two")

    def test_handles_empty(self):
        self.assertEqual(plain_from_synced(""), "")


class FetchLyricsTest(unittest.TestCase):
    def make_response(self, payload):
        response = mock.MagicMock()
        response.__enter__.return_value = response
        response.status = 200
        response.read.return_value = json.dumps(payload).encode()
        return response

    def setUp(self):
        fetch_lyrics.cache = {}

    def test_returns_plain_lyrics(self):
        payload = {
            "trackName": "Tìm Em",
            "artistName": "Hngle",
            "plainLyrics": "Lời bài hát",
            "syncedLyrics": None,
            "instrumental": False,
        }
        with mock.patch("update_static_pages.urlopen", return_value=self.make_response(payload)):
            self.assertEqual(fetch_lyrics("Tìm Em", "Hngle"), {"synced": "", "plain": "Lời bài hát"})

    def test_uses_synced_when_plain_missing(self):
        payload = {
            "trackName": "Tìm Em",
            "artistName": "Hngle",
            "plainLyrics": None,
            "syncedLyrics": "[00:12.34]Line",
            "instrumental": False,
        }
        with mock.patch("update_static_pages.urlopen", return_value=self.make_response(payload)):
            self.assertEqual(fetch_lyrics("Tìm Em", "Hngle"), {"synced": "[00:12.34]Line", "plain": "Line"})

    def test_returns_both_synced_and_plain(self):
        payload = {
            "trackName": "Tìm Em",
            "artistName": "Hngle",
            "plainLyrics": "Line A",
            "syncedLyrics": "[00:10.00]Line A",
            "instrumental": False,
        }
        with mock.patch("update_static_pages.urlopen", return_value=self.make_response(payload)):
            self.assertEqual(fetch_lyrics("Tìm Em", "Hngle"), {"synced": "[00:10.00]Line A", "plain": "Line A"})

    def test_skips_instrumental(self):
        payload = {
            "trackName": "Tìm Em",
            "artistName": "Hngle",
            "plainLyrics": "Lời bài hát",
            "syncedLyrics": "[00:12.34]Line",
            "instrumental": True,
        }
        with mock.patch("update_static_pages.urlopen", return_value=self.make_response(payload)):
            self.assertEqual(fetch_lyrics("Tìm Em", "Hngle"), {"synced": "", "plain": ""})

    def test_rejects_wrong_version_subtitle(self):
        payload = {
            "trackName": "Em Đồng Ý",
            "artistName": "Hngle",
            "plainLyrics": "Lời bài hát",
            "syncedLyrics": None,
            "instrumental": False,
        }
        with mock.patch("update_static_pages.urlopen", return_value=self.make_response(payload)):
            self.assertEqual(fetch_lyrics("Em Đồng Ý (Live)", "Hngle"), {"synced": "", "plain": ""})

    def test_accepts_feat_suffix_title(self):
        payload = {
            "trackName": "Tìm Em (feat. Bảo Anh)",
            "artistName": "Hngle",
            "plainLyrics": "Lời bài hát",
            "syncedLyrics": None,
            "instrumental": False,
        }
        with mock.patch("update_static_pages.urlopen", return_value=self.make_response(payload)):
            self.assertEqual(fetch_lyrics("Tìm Em (feat. Bảo Anh)", "Hngle"), {"synced": "", "plain": "Lời bài hát"})

    def test_rejects_mismatched_artist(self):
        payload = {
            "trackName": "Tìm Em",
            "artistName": "Someone Else",
            "plainLyrics": "Lời bài hát",
            "syncedLyrics": None,
            "instrumental": False,
        }
        with mock.patch("update_static_pages.urlopen", return_value=self.make_response(payload)):
            self.assertEqual(fetch_lyrics("Tìm Em", "Hngle"), {"synced": "", "plain": ""})

    def test_returns_empty_on_http_error(self):
        with mock.patch("update_static_pages.urlopen", side_effect=Exception("boom")):
            self.assertEqual(fetch_lyrics("Tìm Em", "Hngle"), {"synced": "", "plain": ""})

    def test_caches_by_title_artist(self):
        payload = {
            "trackName": "Tìm Em",
            "artistName": "Hngle",
            "plainLyrics": "Lời bài hát",
            "syncedLyrics": None,
            "instrumental": False,
        }
        expected = {"synced": "", "plain": "Lời bài hát"}
        with mock.patch("update_static_pages.urlopen", return_value=self.make_response(payload)) as mocked:
            self.assertEqual(fetch_lyrics("Tìm Em", "Hngle"), expected)
            self.assertEqual(fetch_lyrics("Tìm Em", "Hngle"), expected)
            self.assertEqual(mocked.call_count, 1)


class IsMusicVideoTest(unittest.TestCase):
    def test_flags_when_video_is_much_longer_than_track(self):
        self.assertTrue(is_music_video(371, 232))

    def test_does_not_flag_when_video_matches_track(self):
        self.assertFalse(is_music_video(272, 274))

    def test_does_not_flag_when_video_is_shorter(self):
        self.assertFalse(is_music_video(300, 420))

    def test_returns_false_when_track_duration_missing(self):
        self.assertFalse(is_music_video(416, None))

    def test_returns_false_when_video_duration_missing(self):
        self.assertFalse(is_music_video(None, 420))


class MainTest(unittest.TestCase):
    def test_wires_lyrics_into_top_songs(self):
        songs = [
            {"title": "Tìm Em", "artists": "Hngle", "videoId": "abc123"},
            {"title": "Mưa", "artists": "Ai đó", "videoId": "def456"},
        ]
        top_songs = {"songs": songs, "updatedAt": "old"}
        trending = {"videos": [], "updatedAt": "old"}

        def fake_lyrics(title, artists):
            if title == "Tìm Em":
                return {"synced": "", "plain": "Lời bài hát"}
            return {"synced": "", "plain": ""}

        def fake_lrc_duration(title, artists):
            return 200.0 if title == "Tìm Em" else None

        with mock.patch("update_static_pages.fetch_chart_home", return_value={}), \
             mock.patch("update_static_pages.fetch_lyrics", side_effect=fake_lyrics), \
             mock.patch("update_static_pages.lrc_duration", side_effect=fake_lrc_duration), \
             mock.patch("update_static_pages.get_video_duration", return_value=300), \
             mock.patch("update_static_pages.extract_top_songs", return_value=top_songs), \
             mock.patch("update_static_pages.extract_trending_videos", return_value=trending), \
             mock.patch("update_static_pages.update_static_data") as mocked_update:
            from update_static_pages import main
            main()

        self.assertEqual(top_songs["songs"][0]["lyrics"], {"synced": "", "plain": "Lời bài hát"})
        self.assertEqual(top_songs["songs"][0]["lyrics"]["plain"], "Lời bài hát")
        self.assertEqual(top_songs["songs"][0]["lyrics"]["synced"], "")
        self.assertEqual(top_songs["songs"][1]["lyrics"], {"synced": "", "plain": ""})
        self.assertEqual(top_songs["songs"][1]["lyrics"]["plain"], "")
        self.assertEqual(top_songs["songs"][1]["lyrics"]["synced"], "")
        self.assertEqual(top_songs["songs"][0]["isMv"], True)
        self.assertNotIn("isMv", top_songs["songs"][1])
        self.assertEqual(top_songs["updatedAt"], trending["updatedAt"])
        self.assertEqual(mocked_update.call_count, 2)


if __name__ == "__main__":
    unittest.main()
