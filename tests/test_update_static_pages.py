import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

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
