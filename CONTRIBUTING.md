# Contributing to Cybersecurity Notes

Thank you for helping. Corrections of facts, terminology and translations are the most useful contributions.

## Reporting a problem

Open an issue and choose a template:

- **Content error**: a fact, definition, example or command is wrong or out of date.
- **Translation**: the Polish and English versions differ, or a translation reads badly.

Security problems go through private vulnerability reporting instead (see [SECURITY.md](SECURITY.md)).

## Scope and ethics

These notes teach security for **authorised** testing only. Keep contributions at the level of understanding and defence:

- payloads and proofs of concept are minimal and confirm a vulnerability rather than maximise damage;
- no working exploit chains, malware, or instructions aimed at a specific real target;
- pair each attack with its defence (detection, mitigation, secure configuration).

## Changing content

1. Fork the repository and create a branch.
2. Every page exists in two languages: `page.md` (Polish) and `page.en.md` (English). Change both in the same pull request. If you can only write one language, say so in the pull request and the maintainer will translate the other.
3. New pages go into `nav` in `mkdocs.yml`, with an English label under `nav_translations` (or in `SAME_NAV_TITLES` for terms identical in both languages). Every page needs a `description` in its front matter.
4. Use plain text: no emojis or decorative icons, one `#` heading per page. Terminology follows OWASP and common usage.
5. Run the checks:

   ```bash
   pip install -r requirements.txt
   python -m unittest discover -s tests
   python scripts/check_translations.py
   mkdocs build --strict
   ```

6. Open a pull request and fill in the template. Pull requests are squash-merged into `main`, which deploys the site.

## Licence

By contributing you agree that content (`docs/`) is published under [CC BY 4.0](LICENSE-CONTENT) and code under the [MIT licence](LICENSE).
