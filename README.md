# Cybersecurity Notes

[![Deploy docs](https://github.com/Finito21/Cybersecurity/actions/workflows/deploy.yml/badge.svg)](https://github.com/Finito21/Cybersecurity/actions/workflows/deploy.yml)
[![MkDocs Material](https://img.shields.io/badge/MkDocs-Material-526CFE?logo=materialformkdocs&logoColor=white)](https://squidfunk.github.io/mkdocs-material/)
[![OWASP Top 10](https://img.shields.io/badge/OWASP-Top%2010-000000)](https://owasp.org/Top10/)
[![Content: CC BY 4.0](https://img.shields.io/badge/content-CC%20BY%204.0-lightgrey)](LICENSE-CONTENT)
[![Code: MIT](https://img.shields.io/badge/code-MIT-green)](LICENSE)

A structured, bilingual (Polish / English) knowledge base on **cybersecurity**: web application penetration testing, network security, system defence and security tooling. Based on courses, training and hands-on practice.

**Website: https://finito21.github.io/Cybersecurity/**

> [!WARNING]
> These notes are for **authorised** security testing only: your own labs, training platforms, or engagements with written permission. They focus on understanding mechanisms and on defence. Unauthorised access to a computer system is a crime.

## Contents

| Section | Topics |
|---|---|
| **Fundamentals** | the CIA triad, authentication and authorisation, OWASP Top 10, pentest methodology, the report, interview questions |
| **Web applications** | access control / IDOR, SQL Injection, XSS, CSRF, SSRF, XXE, path traversal and file upload, sessions and JWT, cache and headers |
| **Networks** | LAN security (CAM, VLAN, DHCP, 802.1X), access control lists, wireless (WEP/WPA2/WPA3), DoS and DDoS |
| **Defence** | Windows log analysis, Linux security, NGINX hardening, backups against ransomware, vulnerability scanning |
| **OSINT** | open-source intelligence and reconnaissance: search operators, metadata, images, infrastructure |
| **Tools** | Burp Suite, ZAP |

Every page is available in Polish (default) and English. Use the language switcher in the site header.

## Repository structure

```
.
├── docs/                      site content
│   ├── fundamentals/          concepts, OWASP Top 10, methodology, report, interview questions
│   ├── web/                   web application vulnerabilities
│   ├── network/               LAN, ACLs, wireless, DoS/DDoS
│   ├── defense/               logs, Linux, NGINX, backups, vulnerability scanning
│   ├── osint/                 open-source intelligence
│   ├── tools/                 Burp Suite, ZAP
│   ├── assets/                images and extra.css
│   ├── *.md                   Polish pages
│   └── *.en.md                English pages
├── hooks/
│   ├── typography.py          Polish typesetting rules (non-breaking spaces)
│   └── search_per_language.py separate search index for each language
├── overrides/                 Material template overrides (head tags, header, 404)
├── includes/abbreviations.md  abbreviation tooltips appended to every page
├── scripts/                   check_translations.py (PL/EN consistency and content-rule check)
├── tests/                     unit tests for both hooks and the translation check
├── mkdocs.yml                 site configuration and navigation
├── requirements.in            direct Python dependencies
├── requirements.txt           hashed lock generated from requirements.in
├── .github/                   workflows (checks, deploy to Pages, link check), Dependabot, templates
├── .claude/                   Claude Code project settings, the /pr command and the site-design skill
└── CLAUDE.md                  guidance for Claude Code
```

## Running locally

The project uses Python 3.12 (pinned in `.python-version`, which CI reads too).

```bash
pip install -r requirements.txt
mkdocs serve
```

The site is available at `http://127.0.0.1:8000/Cybersecurity/`.

The `privacy` plugin, which self-hosts the Google Fonts, runs only in CI (it cannot create symlinks
on Windows), so a local preview loads the fonts from Google directly.

Before pushing, run the same checks as CI:

```bash
python -m unittest discover -s tests   # unit tests for the hooks and the translation check
python scripts/check_translations.py   # PL/EN pairs, nav, nav labels, one H1, no emoji
mkdocs build --strict                  # build without warnings
```

The same checks run automatically on every pull request (`.github/workflows/checks.yml`).
External links are checked once a week by `.github/workflows/links.yml` (lychee), outside the
pull request path so that a slow or rate-limiting site never blocks a merge.

## Dependencies

Direct dependencies are listed in `requirements.in`. `requirements.txt` is a lock file with every
transitive dependency pinned and hashed. After changing `requirements.in`, regenerate it with the
Python version from `.python-version` (another version can resolve a different lock):

```bash
pip install pip-tools
pip-compile --generate-hashes --strip-extras --allow-unsafe -o requirements.txt requirements.in
```

Dependabot updates both files once a month. GitHub Actions in `.github/workflows/` are pinned to
commit SHAs (with the version in a comment); Dependabot updates those pins as well.

### MkDocs status

MkDocs 1.x is no longer actively developed, and Material for MkDocs is in maintenance mode
(critical and security fixes only, announced until May 2027). MkDocs 2.0 drops plugin support and
cannot build this site, so Dependabot ignores MkDocs major updates. The planned successor is
[Zensical](https://zensical.org/) from the Material team; this site will move to it once Zensical
supports multilingual sites (mkdocs-static-i18n) and hooks, which `hooks/typography.py` and
`hooks/search_per_language.py` need.

## Adding or editing a page

1. Edit or create both versions: `page.md` (Polish) and `page.en.md` (English).
2. Add new pages to `nav` in `mkdocs.yml` and an English nav label under `nav_translations` (or `SAME_NAV_TITLES` in `scripts/check_translations.py` for terms identical in both languages).
3. Run the three checks above.

## Deployment

Every push to `main` runs the checks workflow, which builds the site and uploads it as an artifact.
`.github/workflows/deploy.yml` then publishes that artifact with `actions/deploy-pages`.

Repository settings that the deployment relies on: Settings > Pages > Source is **GitHub Actions**,
and the `github-pages` environment only accepts deployments from `main`.

## Contributing

Corrections and translation fixes are welcome: see [CONTRIBUTING.md](CONTRIBUTING.md) and the issue templates. Report security problems privately as described in [SECURITY.md](SECURITY.md). Everyone taking part follows the [Code of Conduct](CODE_OF_CONDUCT.md).

## Licence

- **Content** (`docs/`: text and images): [CC BY 4.0](LICENSE-CONTENT)
- **Code** (hooks, scripts, tests, styles, configuration): [MIT](LICENSE)
- `overrides/partials/header.html` is derived from [Material for MkDocs](https://github.com/squidfunk/mkdocs-material) (MIT, © Martin Donath)
