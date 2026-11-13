"""Tests for scripts/check_translations.py (run with: python -m unittest discover -s tests)."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import check_translations as ct  # noqa: E402

MKDOCS = """\
nav:
  - Start: index.md
  - Podstawy:
      - Podstawy QA: a.md
plugins:
  - privacy:
      enabled: !ENV [CI, false]
  - i18n:
      languages:
        - locale: pl
          default: true
        - locale: en
          nav_translations:
            Start: Home
            Podstawy: Fundamentals
            Podstawy QA: QA fundamentals
markdown_extensions:
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
"""

DESCRIPTION = (
    "A short summary of the page used as the meta description in search results, "
    "long enough to pass the length check of the script."
)
PAGE = f"---\ndescription: {DESCRIPTION}\n---\n# Title\n\nText.\n"


class CheckTranslations(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        self.docs = self.root / "docs"
        self.docs.mkdir()
        self.mkdocs = self.root / "mkdocs.yml"
        self.mkdocs.write_text(MKDOCS, encoding="utf-8")
        for name in ("index", "a"):
            self.write(f"{name}.md", PAGE)
            self.write(f"{name}.en.md", PAGE)

    def write(self, name, text):
        (self.docs / name).write_text(text, encoding="utf-8")

    def errors(self):
        return ct.check(self.docs, self.mkdocs)

    def assertError(self, fragment):
        errors = self.errors()
        self.assertTrue(any(fragment in e for e in errors), errors)

    def test_clean_tree_passes(self):
        self.assertEqual(self.errors(), [])

    def test_missing_english_page(self):
        (self.docs / "a.en.md").unlink()
        self.assertError("missing English version: a.en.md")

    def test_english_page_without_polish(self):
        self.write("b.en.md", PAGE)
        self.assertError("without a Polish version: b.en.md")

    def test_page_not_in_nav(self):
        self.write("b.md", PAGE)
        self.write("b.en.md", PAGE)
        self.assertError("not in mkdocs.yml nav: b.md")

    def test_nav_points_to_missing_file(self):
        self.mkdocs.write_text(MKDOCS.replace("a.md", "gone.md"), encoding="utf-8")
        self.assertError("missing file: gone.md")

    def test_duplicate_nav_entry(self):
        self.mkdocs.write_text(MKDOCS.replace("index.md", "a.md"), encoding="utf-8")
        self.assertError("more than once in nav: a.md")

    def test_missing_nav_translation(self):
        self.mkdocs.write_text(MKDOCS.replace("            Podstawy QA: QA fundamentals\n", ""), encoding="utf-8")
        self.assertError("without English label in nav_translations: Podstawy QA")

    def test_unused_nav_translation(self):
        text = MKDOCS.replace("Start: Home", "Start: Home\n            Stary: Old")
        self.mkdocs.write_text(text, encoding="utf-8")
        self.assertError("key not used in nav: Stary")

    def test_polish_text_in_english_page(self):
        self.write("a.en.md", PAGE + "Zażółć gęślą jaźń\n")
        self.assertError("Polish words in a.en.md")

    def test_polish_text_in_code_is_reported(self):
        self.write("a.en.md", PAGE + "```bash\n# zażółć komentarz\n```\n")
        self.assertError("Polish words in a.en.md: zażółć")

    def test_polish_text_in_mermaid_is_reported(self):
        self.write("a.en.md", PAGE + "```mermaid\nflowchart LR\n  A[Błąd] --> B\n```\n")
        self.assertError("Polish words in a.en.md: Błąd")

    def test_polish_sentence_without_diacritics(self):
        self.write("a.en.md", PAGE + "Dodaj nowy przypadek testowy, jest to proste.\n")
        self.assertError("Polish words in a.en.md: jest")

    def test_polish_marked_with_lang_is_allowed(self):
        self.write("a.en.md", PAGE + '| **Failure** | <span lang="pl">awaria, błąd</span> |\n')
        self.assertEqual(self.errors(), [])

    def test_unmarked_polish_next_to_marked_is_reported(self):
        self.write("a.en.md", PAGE + '<span lang="pl">błąd</span> and gęślą\n')
        self.assertError("Polish words in a.en.md: gęślą")

    def test_stop_words_in_code_and_names_are_ignored(self):
        self.write("a.en.md", PAGE + "Use Jest or `nie` here.\n")
        self.assertEqual(self.errors(), [])

    def test_longer_closing_fence(self):
        self.write("a.md", PAGE + "\n```\n# comment\n````\n")
        self.assertEqual(self.errors(), [])

    def test_bom_and_front_matter(self):
        (self.docs / "a.md").write_text(f"﻿---\ntitle: x\ndescription: {DESCRIPTION}\n# not a heading\n---\n# Title\n", encoding="utf-8")
        self.assertEqual(self.errors(), [])

    def test_external_nav_entry(self):
        text = MKDOCS.replace("      - Podstawy QA: a.md", "      - Podstawy QA: a.md\n      - GitHub: https://github.com")
        self.mkdocs.write_text(text, encoding="utf-8")
        self.assertEqual(self.errors(), [])

    def test_h1_in_code_fence_is_not_counted(self):
        self.write("a.md", PAGE + "\n```bash\n# comment\n```\n")
        self.assertEqual(self.errors(), [])

    def test_two_h1_headings(self):
        self.write("a.md", PAGE + "\n# Second\n")
        self.assertError("a.md: expected exactly one H1, found 2")

    def test_no_h1_heading(self):
        self.write("a.md", "## Only a section\n")
        self.assertError("a.md: expected exactly one H1, found 0")

    def test_emoji_and_icon_shortcodes(self):
        self.write("a.md", PAGE + "Done \U0001F680\n")
        self.assertError("a.md: emoji")
        self.write("a.md", PAGE + ":material-check: ok\n")
        self.assertError("a.md: emoji")

    def test_check_mark_symbol_is_allowed(self):
        self.write("a.md", PAGE + "| x | ✔ | ✓ |\n")
        self.assertEqual(self.errors(), [])

    def test_symbol_emoji_without_variation_selector(self):
        for symbol in ("⚡", "✨", "⚠", "❗", "➡", "⬆"):
            with self.subTest(symbol=symbol):
                self.write("a.md", PAGE + f"Note {symbol}\n")
                self.assertError("a.md: emoji")

    def test_variation_selector(self):
        self.write("a.md", PAGE + "Done ✔️\n")
        self.assertError("a.md: emoji")

    def test_missing_description(self):
        self.write("a.md", "# Title\n")
        self.assertError("a.md: no description in front matter")
        self.write("a.md", "---\ndescription: ''\n---\n# Title\n")
        self.assertError("a.md: no description in front matter")

    def test_front_matter_at_end_of_file(self):
        self.write("a.md", f"# Title\n")
        self.write("a.md", f"---\ndescription: {DESCRIPTION}\n---")
        errors = self.errors()
        self.assertFalse(any("a.md: no description" in e for e in errors), errors)

    def test_polish_in_english_mkdocs_settings(self):
        self.mkdocs.write_text(
            MKDOCS.replace("            Start: Home", "            Start: Strona główna"), encoding="utf-8"
        )
        self.assertError("Polish words in the English settings of mkdocs.yml: główna")

    def test_description_length(self):
        for length in (119, 161):
            with self.subTest(length=length):
                self.write("a.md", f"---\ndescription: {'x' * length}\n---\n# Title\n")
                self.assertError(f"a.md: description has {length} characters, expected 120-160")
        for length in (120, 160):
            with self.subTest(length=length):
                self.write("a.md", f"---\ndescription: {'x' * length}\n---\n# Title\n")
                self.assertEqual(self.errors(), [])

    def test_emoji_and_nbsp_in_front_matter(self):
        self.write("a.md", PAGE.replace("summary", "summary \U0001F680"))
        self.assertError("a.md: emoji")
        self.write("a.md", PAGE.replace("A short", "A&nbsp;short"))
        self.assertError("hand-written &nbsp;")

    def test_nbsp_entity_in_inline_code_is_allowed(self):
        self.write("a.md", PAGE + "Do not write `&nbsp;` by hand.\n")
        self.assertEqual(self.errors(), [])

    def test_polish_in_link_title_is_reported(self):
        self.write("a.en.md", PAGE + '[Docs](https://example.com/zażółć "Opis zażółć")\n')
        self.assertError("Polish words in a.en.md: zażółć")

    def test_polish_in_link_target_is_ignored(self):
        self.write("a.en.md", PAGE + "[Docs](https://example.com/zażółć) and [page](strona_główna.md)\n")
        self.assertEqual(self.errors(), [])

    def test_lang_pl_with_single_quotes(self):
        self.write("a.en.md", PAGE + "<span lang='pl'>zażółć</span>\n")
        self.assertEqual(self.errors(), [])

    def test_keyboard_symbols_are_allowed(self):
        self.write("a.md", PAGE + "| ⌘ + ⌥ + I | DevTools |\n")
        self.assertEqual(self.errors(), [])

    def test_emoji_style_punctuation(self):
        for symbol in ("‼", "⁉", "↪"):
            with self.subTest(symbol=symbol):
                self.write("a.md", PAGE + f"Note {symbol}\n")
                self.assertError("a.md: emoji")

    def test_polish_in_english_front_matter(self):
        self.write("a.en.md", "---\ndescription: Opis strony z błędami\n---\n# Title\n")
        self.assertError("Polish words in a.en.md: błędami")

    def test_single_word_polish_nav_title_needs_label(self):
        text = MKDOCS.replace("      - Podstawy QA: a.md", "      - Testowanie: a.md")
        self.mkdocs.write_text(text, encoding="utf-8")
        self.assertError("without English label in nav_translations: Testowanie")

    def test_product_name_nav_title_needs_no_label(self):
        text = MKDOCS.replace("      - Podstawy QA: a.md", "      - Podstawy QA: a.md\n      - Docker: https://docker.com")
        self.mkdocs.write_text(text, encoding="utf-8")
        self.assertEqual(self.errors(), [])

    def test_more_symbol_emoji(self):
        for symbol in ("⏱", "▶", "ℹ", "1⃣"):
            with self.subTest(symbol=symbol):
                self.write("a.md", PAGE + f"Note {symbol}\n")
                self.assertError("a.md: emoji")

    def test_html_nbsp_entities(self):
        for entity in ("&#160;", "&#xA0;"):
            with self.subTest(entity=entity):
                self.write("a.md", PAGE + f"a{entity}b\n")
                self.assertError("hand-written &nbsp;")

    def test_hand_written_nbsp(self):
        self.write("a.md", PAGE + "a&nbsp;b\n")
        self.assertError("hand-written &nbsp;")
        self.write("a.md", PAGE + "a b\n")
        self.assertError("hand-written &nbsp;")


class NavEntries(unittest.TestCase):
    def test_flattens_nested_nav(self):
        nav = [{"A": "a.md"}, {"B": [{"C": "b/c.md"}, "d.md"]}]
        self.assertEqual(ct.nav_entries(nav), (["A", "B", "C"], ["a.md", "b/c.md", "d.md"]))


if __name__ == "__main__":
    unittest.main()
