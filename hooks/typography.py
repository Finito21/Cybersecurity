"""Polish typesetting: non-breaking spaces where a line must not break.

MkDocs hook that runs for every page after Markdown -> HTML conversion.
It only changes text outside of tags and outside of code blocks,
and only on Polish pages (English pages are left as they are).

Rules:
  1. one-letter words (a, i, o, u, w, z) never stay at the end of a line,
  2. abbreviations (np., tj., tzw., wg, tys. ...) stick to the next word,
  3. a number is not separated from its unit, from the next word or from the next
     group of digits ("10 000"),
  4. a relation sign (<, >, =, ≤, ≥, ±, ~) or § is not separated from the number,
  5. a dash never starts a line (non-breaking space before – and —).

Elements marked with a language other than Polish (lang="en") are left alone,
and the content of raw-text elements (<script>, <style>, <textarea>) is copied
as it is, even when it contains "<".
"""

import re

POLISH = "pl"

NBSP = "\u00a0"  # written as an escape so it stays visible in editors and diffs

# Tags whose content is left untouched.
SKIP_TAGS = {"pre", "code", "kbd", "samp", "script", "style", "svg", "textarea", "math", "option", "noscript"}

# Inline tags: text that ends right before one of these continues inside it,
# so "np. <code>200</code>" must still be glued.
INLINE_TAGS = {
    "a", "abbr", "b", "cite", "code", "del", "dfn", "em", "i", "img", "ins", "kbd", "mark", "q",
    "s", "samp", "small", "span", "strong", "sub", "sup", "time", "u", "var",
}

# Raw-text elements: their content is not HTML, so it is copied up to the closing tag.
RAW_RE = re.compile(r"(<(script|style|textarea)\b(?:[^>\"']|\"[^\"]*\"|'[^']*')*>.*?</\2\s*>)", re.S | re.I)
LANG_RE = re.compile(r"""\blang\s*=\s*["']?([A-Za-z-]+)""")
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}

# A tag is "<...>" where ">" inside a quoted attribute value does not end it;
# a comment is matched as a whole so its content is never treated as text.
TAG_RE = re.compile(r"(<!--.*?-->|<(?:[^>\"']|\"[^\"]*\"|'[^']*')*>)", re.S)
TAG_NAME_RE = re.compile(r"<\s*(/)?\s*([a-zA-Z0-9]+)")

LETTER = r"A-Za-zÀ-ÖØ-öø-ÿĀ-žЀ-ӿ"
SPACE = r"[ \t\r\n]+"
# Stands in for the inline tag that follows a text chunk while the rules run.
NEXT = "\ue000"

RULES = [
    # 1. one-letter conjunctions and prepositions
    (re.compile(rf"(?<![{LETTER}0-9])([aiouwzAIOUWZ]){SPACE}(?=\S)"), rf"\1{NBSP}"),
    # 2. abbreviations with a full stop
    (re.compile(
        rf"(?<![{LETTER}])"
        rf"(np|Np|tj|Tj|tzn|Tzn|tzw|Tzw|ul|Ul|nr|Nr|godz|ang|ds|im|św|dr|Dr|prof|Prof|inż|mgr"
        rf"|m\.in|M\.in|rys|Rys|zob|Zob|por|Por|pkt|Pkt|wg|Wg|tys|al|ust|Ust)\.{SPACE}(?=\S)"
    ), rf"\1.{NBSP}"),
    # 2a. abbreviations that also end sentences ("w 2025 r. Potem", "jest ok. Dalej"):
    #     glued only before a lowercase word, a number or an inline tag
    (re.compile(
        rf"(?<![{LETTER}])(ok|r|s|str|pt|tab|Tab|art|lit)\.{SPACE}(?=[a-ząćęłńóśźż0-9{NEXT}])"
    ), rf"\1.{NBSP}"),
    # 2b. abbreviations written without a full stop
    (re.compile(rf"(?<![{LETTER}])(wg|Wg|mln|mld|tys|zł|nr|Nr|pkt|Pkt){SPACE}(?=\S)"), rf"\1{NBSP}"),
    # 3. number + unit / word
    (re.compile(rf"(?<=\d){SPACE}(?=[{LETTER}%°§{NEXT}])"), NBSP),
    # 3a. thousands separator: "10 000", "1 500 000" (the first group has 1-3 digits,
    #     so "rok 2024 123" is not glued)
    (re.compile(r"(?<!\d)(?<!\d )\d{1,3}(?: \d{3})+(?!\d)"), lambda m: m.group(0).replace(" ", NBSP)),
    # 4. relation sign or section sign + number
    (re.compile(rf"(&lt;|&gt;|[=≤≥±~×§]){SPACE}(?=[\d{NEXT}])"), rf"\1{NBSP}"),
    # 5. a dash never starts a line
    (re.compile(rf"{SPACE}(?=[–—][ \t\r\n])"), NBSP),
]


def _fix_text(text: str, before_inline: bool = False) -> str:
    if before_inline:
        text += NEXT
    for pattern, repl in RULES:
        text = pattern.sub(repl, text)
    return text.removesuffix(NEXT)


def _opens_inline(part: str) -> bool:
    m = TAG_NAME_RE.match(part)
    return bool(m) and not m.group(1) and m.group(2).lower() in INLINE_TAGS


def _tokens(html: str):
    """Yield (kind, text): "raw" for a whole raw-text element, "tag" or "text"."""
    for i, chunk in enumerate(RAW_RE.split(html)):
        if i % 3 == 1:
            yield "raw", chunk
        elif i % 3 == 0 and chunk:
            for part in TAG_RE.split(chunk):
                if part:
                    yield ("tag" if part.startswith("<") else "text"), part


def fix_typography(html: str) -> str:
    out = []
    skip_depth = 0
    # Elements with a lang attribute: [tag name, is Polish, nesting depth of that name].
    lang_stack: list[list] = []
    tokens = list(_tokens(html))
    for i, (kind, part) in enumerate(tokens):
        if kind == "raw":
            out.append(part)
            continue
        if kind == "tag":
            m = TAG_NAME_RE.match(part)
            if m:
                closing, name = m.group(1), m.group(2).lower()
                self_closing = part.endswith("/>") or name in VOID_TAGS
                if name in SKIP_TAGS and not self_closing:
                    skip_depth = max(skip_depth + (-1 if closing else 1), 0)
                if not self_closing:
                    top = lang_stack[-1] if lang_stack else None
                    if closing:
                        if top and top[0] == name:
                            top[2] -= 1
                            if not top[2]:
                                lang_stack.pop()
                    else:
                        lang = LANG_RE.search(part)
                        if lang:
                            lang_stack.append([name, lang.group(1).lower().split("-")[0] == POLISH, 1])
                        elif top and top[0] == name:
                            top[2] += 1
            out.append(part)
        elif skip_depth or (lang_stack and not lang_stack[-1][1]):
            out.append(part)
        else:
            nxt = tokens[i + 1] if i + 1 < len(tokens) else None
            before_inline = bool(nxt) and nxt[0] == "tag" and _opens_inline(nxt[1])
            out.append(_fix_text(part, before_inline))
    return "".join(out)


def page_language(page, config) -> str:
    """Locale of the page source: set by mkdocs-static-i18n, else the site language."""
    return getattr(page.file, "locale", None) or config["theme"]["language"]


def on_page_content(html, page, config, files):
    if page_language(page, config) != POLISH:
        return html
    return fix_typography(html)
