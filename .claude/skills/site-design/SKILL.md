---
name: site-design
description: Visual and UX design rules for the Cybersecurity Notes site (MkDocs Material, PL/EN). Load before changing extra.css, overrides/, mkdocs.yml theme/palette, the home page, section landing pages, or before making any mockup of the site. Also load when the user says the site "looks generic" or "looks AI-made".
---

# Site design: Cybersecurity Notes

The owner has rejected designs that "look AI-made". The look must come from
the subject (application, network and system security), its real artefacts
and the site's real content, not from a generic "tech" or "editorial" template.

## 1. Start from content, never from decoration

- Before designing, read the real pages you are styling (`docs/index.md`,
  one vulnerability page such as `docs/web/sql_injection.md`, a section index
  such as `docs/web/index.md`). Mockups use their real headings, sentences and tables.
- Never invent numbers: no reading times, page counts, "rules", "alerts" or
  progress bars unless they are computed from the repo. Missing facts are
  marked `[DO UZUPEŁNIENIA]`.
- No slogans or taglines. The H1 is the site name or the page subject; the
  lead is the page's real first paragraph.
- Each view carries at least one detail only this subject has, as content:
  a raw HTTP request/response, a real config directive, an Event ID, a
  CWE/OWASP 2025 ID, an `art. 267 k.k.` reference. Not as ornament.

## 2. Banned tropes (each one has already been rejected here)

- Warm cream paper (#F4F1EA-like) + serif display + terracotta/vermilion accent.
- Near-black page with a single neon cyan/green/red accent and glow.
- Fake terminal windows (traffic-light dots, `$ _` cursor, `alerts.log`).
- Chips/pills on everything; `CRIT/WARN/INFO` badges used as decoration.
- `01 / 02 / 03` numbering where order is not real information.
  (RFC-style section numbers are fine when they are the page's real structure.)
- Big-number stat tiles, four identical cards in a row, rounded cards with a
  coloured left border, gradients, emoji, shield/padlock logos.
- Uppercase mono micro-labels above every block.
- Everything centred, `100vh` hero.

## 3. Structure rules (from the 10-specialist review, 2026-11-13)

- Desktop keeps a section nav (left) and an in-page TOC; never hide
  `.md-sidebar--primary` / `--secondary` with CSS.
- Vulnerability pages follow one template: lead → Kiedy występuje →
  Kiedy aplikacja jest bezpieczna → Jak testować → Wykrywanie → Rekomendacje → Zobacz też.
- Attack and defence are linked both ways ("Zobacz też").
- Admonition types must look different (`warning`, `danger`, `tip`, `note`);
  never one colour for all via `!important`.

## 4. Tokens and implementation

- All colours as tokens in `extra.css` mapped onto Material's `--md-*`
  variables for both `[data-md-color-scheme="default"]` and `"slate"`.
  Avoid selectors that depend on Material's internal DOM.
- 1 accent at most plus semantic colours; semantic colours that must be told
  apart also differ in lightness (attack vs defence must work in greyscale).
- Fonts: 2 families (text + mono), self-hosted through the Material `privacy`
  plugin, never a CSS `@import` from Google.
- Contrast ≥ 4.5:1 for text (incl. small grey labels), links underlined in
  body text, visible focus, `prefers-reduced-motion` respected.
- Running text ≈ 65–72ch; tables and code scroll in their own container.

## 5. Before you finish

1. Compare the result against section 2; remove every banned trope.
2. Ask: could this exact layout be a SaaS landing page or a recipe blog? If
   yes, it is not grounded enough in the subject; redo the weakest part.
3. Run `python -m unittest discover -s tests`, `python scripts/check_translations.py`,
   `mkdocs build --strict` (build into a temp dir, not `site/`, when only previewing).
