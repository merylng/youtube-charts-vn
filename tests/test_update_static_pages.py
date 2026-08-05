import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from update_static_pages import normalize_for_match
from update_static_pages import plain_from_synced


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


if __name__ == "__main__":
    unittest.main()
