"""MkDocs hook: a separate search index for each language.

mkdocs-static-i18n merges the search entries of every language into one
``search/search_index.json`` and all pages read that file, so a search on a
Polish page also returns English pages and the other way round.

After the build this hook splits the file: the root index keeps the Polish
entries and ``en/search/search_index.json`` gets the English ones (with the
``en/`` prefix removed from their locations). English pages are pointed at
their own index by changing ``base`` in Material's ``__config`` script, which
Material uses to find the index and to resolve the links of the results.
Material resolves ``base`` with ``new URL(base, location)``, so the new value
must end with ``/``; otherwise ``search/search_index.json`` would resolve next
to ``en`` instead of inside it.

mkdocs-static-i18n runs a nested build for English and calls ``on_post_build``
there too; that run finds no English entries yet and leaves the files alone.
The outer run (after i18n has merged the indexes) does the split.
"""

import json
import logging
import re
from pathlib import Path

from mkdocs.plugins import event_priority

log = logging.getLogger("mkdocs.hooks.search_per_language")

PREFIX = "en/"
INDEX = Path("search") / "search_index.json"
CONFIG_BASE_RE = re.compile(r'(<script id="__config" type="application/json">\{[^<]*?"base":\s*")([^"]*)(")')


def split_index(index: dict, prefix: str = PREFIX) -> tuple[dict, dict]:
    """Return (default-language index, prefixed-language index)."""
    docs = index.get("docs", [])
    default = [d for d in docs if not d["location"].startswith(prefix)]
    other = [{**d, "location": d["location"][len(prefix):]} for d in docs if d["location"].startswith(prefix)]
    return {**index, "docs": default}, {**index, "docs": other}


def point_base_to(html: str, sub: str = PREFIX.rstrip("/")) -> tuple[str, int]:
    """Append `sub/` to the `base` value of Material's __config script.

    Returns the new HTML and the number of replacements (0 or 1).
    """

    def repl(match: re.Match) -> str:
        base = match.group(2).rstrip("/")
        new = f"{base}/{sub}/" if base and base != "." else f"{sub}/"
        return match.group(1) + new + match.group(3)

    return CONFIG_BASE_RE.subn(repl, html, count=1)


def on_post_page(output: str, page, config) -> str:
    if not page.url.startswith(PREFIX):
        return output
    html, count = point_base_to(output)
    if not count:
        log.warning("search_per_language: no __config base found on %s; it will use the Polish index", page.url)
    return html


@event_priority(-110)  # after mkdocs-static-i18n (-100) has written the merged index
def on_post_build(config) -> None:
    site = Path(config["site_dir"])
    path = site / INDEX
    if not path.is_file():
        return
    index = json.loads(path.read_text(encoding="utf-8"))
    default, other = split_index(index)
    if not other["docs"]:
        return
    path.write_text(json.dumps(default, ensure_ascii=False), encoding="utf-8")
    target = site / PREFIX / INDEX
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(other, ensure_ascii=False), encoding="utf-8")
