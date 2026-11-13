# Security Policy

Cybersecurity Notes is a static documentation site (MkDocs Material) with no backend, user accounts or stored user data. The relevant attack surface is the build and deployment pipeline (GitHub Actions, Python dependencies) and the content of the published pages.

## Reporting a vulnerability

Please do not open a public issue for security problems. Use GitHub's private vulnerability reporting:
**Security > Report a vulnerability** in this repository.

Include a description, the affected file or workflow, and steps to reproduce. You can expect an initial response within 7 days.

Please give the maintainer a reasonable time to fix the problem before disclosing it publicly (coordinated disclosure). A typical timeline is a fix within 30 days of the first response.

## Scope

- Workflows in `.github/workflows/` (injection, excessive permissions, unpinned actions).
- Dependencies in `requirements.txt` with known vulnerabilities.
- Secrets or personal data accidentally committed to the repository.
- Documentation that teaches insecure practices, or that crosses from education into operational attack instructions against a specific real target.

## Out of scope

- Vulnerabilities in third-party sites and tools that the documentation links to; report those to their owners.
- Issues in GitHub Pages or GitHub itself.
- Missing security headers on `github.io`, which this project does not control.

## Supported versions

Only the current `main` branch and the published site are supported.
