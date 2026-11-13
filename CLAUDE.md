# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Project

**Cybersecurity Notes** is a bilingual (Polish / English) knowledge base about cybersecurity: web application penetration testing, network security, system defence and security tooling. It is built with [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) and published to GitHub Pages at <https://finito21.github.io/Cybersecurity/>.

Polish is the default language of the site. English is a full translation, not a subset.

The notes come from courses, training and hands-on practice (own labs, training platforms and CTF-style exercises). They focus on understanding mechanisms and on defence, not on ready-made exploits.

## Commands

```bash
pip install -r requirements.txt     # install locked dependencies (hashed)
mkdocs serve                        # local preview at http://127.0.0.1:8000/Cybersecurity/
python -m unittest discover -s tests   # tests for both hooks and the translation check
python scripts/check_translations.py   # PL/EN pages in sync, nav and nav labels, one H1, no emoji
mkdocs build --strict               # build check
```

Run all three checks before finishing any change. CI runs them too and blocks deployment on failure.

Never run `mkdocs gh-deploy` locally. Deployment happens only in CI (`.github/workflows/deploy.yml`) on every push to `main`: it calls `checks.yml` and publishes the uploaded build with `actions/deploy-pages`.

Direct dependencies go in `requirements.in`; `requirements.txt` is a hashed lock generated with `pip-compile` (see README). Never edit the lock by hand.

## Layout

```
docs/
  index.md / index.en.md        home page (intro, learning path, every section with all its pages)
  fundamentals/                 concepts, OWASP Top 10, pentest methodology and report, interview questions
  web/                          web vulnerabilities: access control, SQLi, XSS, CSRF, SSRF, XXE, files, sessions, cache
  network/                      LAN security, ACLs, wireless, DoS/DDoS
  defense/                      Windows logs, Linux, NGINX hardening, backup/ransomware, vulnerability scanning
  osint/                        OSINT (open-source intelligence, reconnaissance)
  tools/                        Burp Suite, ZAP
  resources.md                  sources
  assets/images/                images used by pages
  assets/stylesheets/extra.css  all custom styling (light + dark scheme)
overrides/404.html              bilingual 404 page (GitHub Pages serves one root 404)
overrides/main.html             head: fonts, Open Graph / Twitter tags, icons
overrides/partials/header.html  copy of Material's header (site name links home); re-copy on Material upgrade
hooks/typography.py             MkDocs hook: Polish non-breaking-space rules
hooks/search_per_language.py    MkDocs hook: splits the search index so each language searches only itself
scripts/check_translations.py   CI check: every page exists in PL and EN, is in nav, nav titles have EN labels,
                                EN has no Polish text, one H1 and a 120-160 char description per page, no emoji
tests/                          unit tests for both hooks and the translation check (stdlib unittest)
.github/ISSUE_TEMPLATE/         issue forms: content error, translation
.github/workflows/              checks (on PRs), deploy (to Pages), weekly external link check
mkdocs.yml                      site config, nav, i18n, markdown extensions
requirements.in / .txt          direct dependencies / hashed lock
```

## Rules for content

- **Every page exists in two languages.** `page.md` is Polish, `page.en.md` is English (mkdocs-static-i18n, `suffix` structure). Update both in the same change.
- **New pages must be added to `nav` in `mkdocs.yml`.** Add an English label for any new nav title under `plugins.i18n.languages[en].nav_translations`. Security terms that are the same in both languages (e.g. `SQL Injection`, `XSS`, `OSINT`) go in `SAME_NAV_TITLES` in `scripts/check_translations.py` instead.
- **Anchor links differ between languages.** Headings are translated, so fix `#anchor` links in both files when renaming a heading.
- **No emojis, no decorative icons, no header logo, no heading permalinks.** Use plain text.
- **Polish typography** is handled by `hooks/typography.py` at build time. Do not insert `&nbsp;` by hand; extend the hook's `RULES` instead and add a test.
- **One `#` (H1) per page.** Sections are `##`, subsections `###`.
- **Every page has a `description`** in its front matter (120-160 characters, in the page's language).
- **URLs are directory-style.** Link to other pages by their `.md` path.
- **Content is CC BY 4.0, code is MIT** (`LICENSE-CONTENT`, `LICENSE`).
- Keep pages concise and practical. Prefer tables, short lists, admonitions (`!!! tip`, `!!! warning`), content tabs and Mermaid diagrams over long prose.
- Translate comments, identifiers and strings inside code samples and Mermaid labels together with the prose.
- Polish quoted on purpose on an English page goes in `<span lang="pl">…</span>`.
- Give every Mermaid diagram an `accTitle:` line (and `accDescr:` when the surrounding text does not explain it).
- Abbreviation tooltips live in `includes/abbreviations.md`, appended to every page.

## Security and ethics

This repository teaches offensive and defensive security for **authorised** testing only (own labs, training platforms, engagements with written permission). Keep examples at the level of understanding and detection:

- payloads and PoCs are minimal and meant to confirm a vulnerability, not to maximise damage;
- do not add working exploit chains, malware, or step-by-step instructions aimed at a specific real target;
- pair each attack with its defence (detection, mitigation, secure configuration);
- the home page carries a legal/ethical warning; keep it.

## Rules for styling

- All custom CSS lives in `docs/assets/stylesheets/extra.css`.
- Define colours as variables for both schemes (`[data-md-color-scheme="default"]` and `[data-md-color-scheme="slate"]`) and check both light and dark mode.
- The dark scheme (`slate`) is the default; the light scheme (`default`) is the toggle. Style through the `--cs-*` tokens, which are mapped onto Material's `--md-*` variables.
- Keep the left section nav and the right table of contents visible on desktop; do not hide `.md-sidebar--primary` or `.md-sidebar--secondary`.
- Fonts (Archivo, JetBrains Mono) are linked in `overrides/main.html` and self-hosted by the `privacy` plugin, which runs in CI only (`enabled: !ENV [CI, false]`) because it cannot create symlinks on Windows.
- Check narrow screens (phone width) for the home page and the navigation drawer.
- Design rules and banned visual tropes: `.claude/skills/site-design/SKILL.md`.

## Repository conventions

- Repository-level files (README, CLAUDE.md, code comments, commit messages) are written in **English**.
- Commit messages: short imperative subject (`Add …`, `Fix …`), one logical change per commit.
- Work on a branch, never commit directly to `main`. Open pull requests with the `/pr` command.
- Do not commit the generated `site/` directory.
