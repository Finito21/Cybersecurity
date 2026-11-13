"""Check that the Polish and English versions of the site stay in sync.

Fails (exit code 1) when:
  1. a Polish page `page.md` has no English `page.en.md`, or the other way round,
  2. a Polish page is missing from `nav` in mkdocs.yml, or `nav` points to a missing
     file or lists a page twice,
  3. a nav title has no entry in `nav_translations` for English and is not listed
     in SAME_NAV_TITLES (names such as "Docker" that are the same in both languages),
     or a `nav_translations` key is not used in `nav`,
  4. an English page contains Polish words, also inside code samples, Mermaid
     diagrams and front matter (a sign of an untranslated fragment); Polish quoted
     on purpose is marked with lang="pl",
  5. a page does not have exactly one H1, has no `description` of 120-160 characters
     in its front matter, or contains emoji / icon shortcodes / hand-written `&nbsp;`
     (front matter included; rules from CLAUDE.md).

Usage:  python scripts/check_translations.py
"""

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
MKDOCS = ROOT / "mkdocs.yml"

POLISH_CHARS = "ąćęłńóśźżĄĆĘŁŃÓŚŹŻ"

# Proper names that may legitimately appear in English pages.
ALLOWED_WORDS = {"Zięba", "Rzeszów", "Kraków", "Łódź", "Gdańsk", "Poznań"}

# Nav titles that are identical in English (product and technology names). Every
# other title needs an English label, so a Polish word such as "Testowanie" cannot slip through.
SAME_NAV_TITLES = {
    "Burp Suite", "Docker", "GitHub", "NGINX", "OSINT", "ZAP", "OWASP Top 10", "Linux",
    "SSRF", "XSS", "CSRF", "XXE", "SQL Injection", "IDOR", "Path Traversal",
}

# A closing fence may be longer than the opening one (CommonMark).
FENCE_RE = re.compile(r"^([ \t]*)(`{3,}|~{3,}).*?^\1\2[`~]*[ \t]*$", re.M | re.S)
INLINE_CODE_RE = re.compile(r"(`+)(?!`)(.+?)(?<!`)\1(?!`)")
# Only the link target is skipped; a link title ("...") stays in the scanned text.
URL_RE = re.compile(r"\]\(\s*(?:<[^>]*>|[^\s)]*)|https?://\S+")
FRONT_MATTER_RE = re.compile(r"\A---\n(.*?)\n---[ \t]*(?:\n|\Z)", re.S)
NBSP_RE = re.compile(r"&nbsp;|&#160;|&#x0*a0;| ", re.I)
# Polish deliberately quoted on an English page (e.g. the glossary) is marked with
# lang="pl", which screen readers also need, and is not reported.
LANG_PL_RE = re.compile(r"<(\w+)\b[^>]*\blang=([\"'])pl\2[^>]*>.*?</\1>", re.S)
POLISH_WORD_RE = re.compile(rf"\w*[{POLISH_CHARS}]\w*")
# Common Polish words without diacritics; in lowercase they never occur in English
# prose, so they catch untranslated sentences that POLISH_WORD_RE misses
# (case-sensitive, so names such as "Jest" the test framework are not flagged).
POLISH_STOP_WORDS = {"jest", "nie", "oraz", "dla", "przez", "jak", "aby", "lub", "czy", "jako", "przy", "tylko"}
STOP_WORD_RE = re.compile(rf"\b({'|'.join(sorted(POLISH_STOP_WORDS))})\b")
H1_RE = re.compile(r"^# \S", re.M)
# Emoji and pictograph blocks, misc symbols and dingbats, and the emoji variation
# selector, and a few emoji-style punctuation marks and arrows; the plain check and
# cross marks used in decision tables and the keyboard symbols used in shortcut
# tables are allowed.
EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF⌀-⏿■-◿ℹ⃣☀-➿⬀-⯿️‼⁉↩↪⤴⤵]")
ALLOWED_SYMBOLS = {"✓", "✔", "✗", "✘", "⌘", "⌥", "⌃", "⌫", "⏎"}
# Meta description length recommended for search result snippets (CLAUDE.md).
DESCRIPTION_MIN, DESCRIPTION_MAX = 120, 160
ICON_RE = re.compile(r":(?:material|fontawesome|octicons|simple)-[\w-]+:")


class _Loader(yaml.SafeLoader):
    """SafeLoader that accepts the `!!python/name:` and `!ENV` tags used in mkdocs.yml."""


_Loader.add_multi_constructor("tag:yaml.org,2002:python/", lambda loader, suffix, node: None)
_Loader.add_constructor("!ENV", lambda loader, node: None)


def rel(path: Path, docs: Path = DOCS) -> str:
    return path.relative_to(docs).as_posix()


def strip_code(text: str) -> str:
    text = FENCE_RE.sub("", text)
    text = INLINE_CODE_RE.sub("", text)
    return URL_RE.sub("", text)


def read_source(path: Path) -> str:
    """Page source without a BOM, with Unix line endings."""
    return path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")


def read_page(path: Path) -> str:
    """Page source without YAML front matter."""
    return FRONT_MATTER_RE.sub("", read_source(path))


def front_matter(path: Path) -> dict:
    match = FRONT_MATTER_RE.match(read_source(path))
    try:
        data = yaml.safe_load(match.group(1)) if match else None
    except yaml.YAMLError:
        data = None
    return data if isinstance(data, dict) else {}


def has_emoji(text: str) -> bool:
    return any(ch not in ALLOWED_SYMBOLS for ch in EMOJI_RE.findall(text))


def nav_entries(nav, titles=None, paths=None):
    """Flatten the nav tree into ([titles], [paths]); a bare string entry has no title."""
    titles = [] if titles is None else titles
    paths = [] if paths is None else paths
    for item in nav or []:
        if isinstance(item, str):
            paths.append(item)
        elif isinstance(item, dict):
            for title, value in item.items():
                titles.append(title)
                if isinstance(value, list):
                    nav_entries(value, titles, paths)
                else:
                    paths.append(value)
    return titles, paths


def english_language(config) -> dict:
    """The `en` entry of the i18n plugin's languages (empty when missing)."""
    for plugin in config.get("plugins") or []:
        if isinstance(plugin, dict) and "i18n" in plugin:
            for lang in plugin["i18n"].get("languages") or []:
                if lang.get("locale") == "en":
                    return lang
    return {}


def english_translations(config) -> dict:
    return english_language(config).get("nav_translations") or {}


def strings(value):
    """Every string value inside a nested YAML structure."""
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from strings(item)


def polish_words(text: str) -> set:
    return (set(POLISH_WORD_RE.findall(text)) - ALLOWED_WORDS) | set(STOP_WORD_RE.findall(text))


def check(docs: Path = DOCS, mkdocs: Path = MKDOCS) -> list:
    """Return a list of error messages (empty when everything is in sync)."""
    errors = []
    all_md = sorted(docs.rglob("*.md"))
    pl_pages = [p for p in all_md if not p.name.endswith(".en.md")]
    en_pages = [p for p in all_md if p.name.endswith(".en.md")]

    # 1. every page exists in both languages
    for pl in pl_pages:
        en = pl.with_name(pl.stem + ".en.md")
        if not en.exists():
            errors.append(f"missing English version: {rel(en, docs)}")
    for en in en_pages:
        pl = en.with_name(en.name[: -len(".en.md")] + ".md")
        if not pl.exists():
            errors.append(f"English page without a Polish version: {rel(en, docs)}")

    # 2. every page is in the navigation; the navigation has no dead or duplicate entries
    config = yaml.load(mkdocs.read_text(encoding="utf-8"), Loader=_Loader)
    titles, nav_paths = nav_entries(config.get("nav"))
    nav_set = set(nav_paths)
    for pl in pl_pages:
        if rel(pl, docs) not in nav_set:
            errors.append(f"page not in mkdocs.yml nav: {rel(pl, docs)}")
    for path in sorted(nav_set):
        if "://" not in path and not (docs / path).exists():
            errors.append(f"nav entry points to a missing file: {path}")
    for path in sorted({p for p in nav_paths if nav_paths.count(p) > 1}):
        errors.append(f"page listed more than once in nav: {path}")

    # 3. nav titles have an English label
    translations = english_translations(config)
    for title in dict.fromkeys(titles):
        if title not in SAME_NAV_TITLES and title not in translations:
            errors.append(f"nav title without English label in nav_translations: {title}")
    for title in sorted(set(translations) - set(titles)):
        errors.append(f"nav_translations key not used in nav: {title}")

    # 4. no untranslated Polish text in English pages; code samples (comments,
    #    strings, Mermaid labels) and front matter (title, description) must be
    #    translated too, so only URLs and text marked lang="pl" are skipped
    for en in en_pages:
        raw = LANG_PL_RE.sub("", read_source(en))
        words = set(POLISH_WORD_RE.findall(URL_RE.sub("", raw))) - ALLOWED_WORDS
        words |= set(STOP_WORD_RE.findall(strip_code(raw)))
        if words:
            errors.append(f"Polish words in {rel(en, docs)}: {', '.join(sorted(words)[:10])}")

    # 4a. English strings in mkdocs.yml (site_description, copyright, palette toggles,
    #     nav labels) must not contain Polish either
    english = {k: v for k, v in english_language(config).items() if k not in ("locale", "name")}
    words = set()
    for text in strings(english):
        words |= polish_words(text)
    if words:
        errors.append(f"Polish words in the English settings of mkdocs.yml: {', '.join(sorted(words)[:10])}")

    # 5. content rules from CLAUDE.md
    for page in all_md:
        source = read_source(page)
        body = FENCE_RE.sub("", read_page(page))
        h1 = len(H1_RE.findall(body))
        if h1 != 1:
            errors.append(f"{rel(page, docs)}: expected exactly one H1, found {h1}")
        if has_emoji(source) or ICON_RE.search(source):
            errors.append(f"{rel(page, docs)}: emoji or icon shortcode (not allowed)")
        description = str(front_matter(page).get("description") or "").strip()
        if not description:
            errors.append(f"{rel(page, docs)}: no description in front matter (used for search snippets)")
        elif not DESCRIPTION_MIN <= len(description) <= DESCRIPTION_MAX:
            errors.append(
                f"{rel(page, docs)}: description has {len(description)} characters, "
                f"expected {DESCRIPTION_MIN}-{DESCRIPTION_MAX}"
            )
        # Inline code may show the entity itself (e.g. a page explaining `&nbsp;`).
        if NBSP_RE.search(INLINE_CODE_RE.sub("", FENCE_RE.sub("", source))):
            errors.append(f"{rel(page, docs)}: hand-written &nbsp; (handled by hooks/typography.py)")

    return errors


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    errors = check()
    if errors:
        print("Translation check failed:")
        for e in errors:
            print(f"  - {e}")
        return 1

    pages = [p for p in DOCS.rglob("*.md") if not p.name.endswith(".en.md")]
    print(f"Translation check passed: {len(pages)} pages in Polish and English.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
