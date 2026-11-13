"""Tests for hooks/search_per_language.py (run with: python -m unittest discover -s tests)."""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "hooks"))

import search_per_language as spl  # noqa: E402

INDEX = {
    "config": {"lang": ["en"]},
    "docs": [
        {"location": "", "title": "Start", "text": ""},
        {"location": "web/sql_injection/", "title": "SQL Injection", "text": ""},
        {"location": "en/", "title": "Home", "text": ""},
        {"location": "en/web/sql_injection/#when", "title": "When", "text": ""},
        {"location": "en/web/xss/", "title": "Cross-Site Scripting", "text": "zażółć"},
    ],
}

CONFIG_SCRIPT = '<script id="__config" type="application/json">{"annotate": null, "base": "%s", "features": []}</script>'


class SplitIndex(unittest.TestCase):
    def test_entries_go_to_their_language(self):
        default, other = spl.split_index(INDEX)
        self.assertEqual([d["location"] for d in default["docs"]], ["", "web/sql_injection/"])
        self.assertEqual([d["location"] for d in other["docs"]], ["", "web/sql_injection/#when", "web/xss/"])

    def test_config_is_kept(self):
        default, other = spl.split_index(INDEX)
        self.assertEqual(default["config"], INDEX["config"])
        self.assertEqual(other["config"], INDEX["config"])

    def test_input_is_not_modified(self):
        spl.split_index(INDEX)
        self.assertEqual(INDEX["docs"][2]["location"], "en/")


class PointBase(unittest.TestCase):
    def base(self, value):
        html, count = spl.point_base_to(CONFIG_SCRIPT % value)
        self.assertEqual(count, 1)
        return html

    def test_nested_page(self):
        self.assertIn('"base": "../../../en/"', self.base("../../.."))

    def test_home_page(self):
        self.assertIn('"base": "../en/"', self.base(".."))

    def test_root_base(self):
        self.assertIn('"base": "en/"', self.base("."))

    def test_absolute_base(self):
        self.assertIn('"base": "/Cybersecurity/en/"', self.base("/Cybersecurity/"))

    def test_base_without_space(self):
        html, count = spl.point_base_to(CONFIG_SCRIPT.replace('"base": ', '"base":') % "..")
        self.assertEqual(count, 1)
        self.assertIn('"base":"../en/"', html)

    def test_other_base_values_untouched(self):
        html = '<a data-base="..">x</a>' + CONFIG_SCRIPT % ".."
        out, _ = spl.point_base_to(html)
        self.assertIn('data-base=".."', out)

    def test_only_english_pages_change(self):
        html = CONFIG_SCRIPT % ".."
        self.assertEqual(spl.on_post_page(html, SimpleNamespace(url="web/xss/"), {}), html)
        self.assertIn("../en/", spl.on_post_page(html, SimpleNamespace(url="en/web/xss/"), {}))
        self.assertIn('"base": "en/"', spl.on_post_page(CONFIG_SCRIPT % ".", SimpleNamespace(url="en/"), {}))

    def test_missing_config_logs_warning(self):
        with self.assertLogs("mkdocs.hooks.search_per_language", level="WARNING"):
            out = spl.on_post_page("<p>no config</p>", SimpleNamespace(url="en/web/xss/"), {})
        self.assertEqual(out, "<p>no config</p>")

    def test_runs_after_i18n(self):
        self.assertLess(spl.on_post_build.mkdocs_priority, -100)


class PostBuild(unittest.TestCase):
    def test_writes_two_indexes(self):
        with tempfile.TemporaryDirectory() as tmp:
            site = Path(tmp)
            (site / "search").mkdir()
            (site / "search" / "search_index.json").write_text(json.dumps(INDEX), encoding="utf-8")
            spl.on_post_build({"site_dir": tmp})
            root = json.loads((site / "search" / "search_index.json").read_text(encoding="utf-8"))
            en = json.loads((site / "en" / "search" / "search_index.json").read_text(encoding="utf-8"))
            self.assertEqual(len(root["docs"]), 2)
            self.assertEqual(len(en["docs"]), 3)
            self.assertEqual(en["docs"][2]["text"], "zażółć")
            # running again on the already split index changes nothing
            spl.on_post_build({"site_dir": tmp})
            again = json.loads((site / "en" / "search" / "search_index.json").read_text(encoding="utf-8"))
            self.assertEqual(again, en)

    def test_missing_index_is_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            spl.on_post_build({"site_dir": tmp})
            self.assertFalse((Path(tmp) / "en").exists())


if __name__ == "__main__":
    unittest.main()
