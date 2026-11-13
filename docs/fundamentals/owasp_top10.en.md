---
description: "The OWASP Top 10 for web applications: risk categories, examples of flaws and links to the detailed notes on each vulnerability class."
---

# OWASP Top 10

The **OWASP Top 10** is a ranking of the most important risk categories in web applications, published by the OWASP Foundation from data contributed by organisations together with an industry survey. These notes use the 2025 edition. The ranking is not a complete test methodology: that is what **OWASP ASVS** (a list of requirements) and the **OWASP Web Security Testing Guide** are for.

| Category (2025) | What it is | Notes |
|---|---|---|
| **A01 Broken Access Control** | a user gets data or functions they have no rights to; since 2025 it also covers SSRF | [Access control and IDOR](../web/access_control.md), [CSRF](../web/csrf.md), [SSRF](../web/ssrf.md) |
| **A02 Security Misconfiguration** | default settings, debug mode, unnecessary services, version disclosure, XXE | [XXE](../web/xxe.md), [Cache and headers](../web/cache_and_headers.md), [NGINX](../defense/nginx_hardening.md) |
| **A03 Software Supply Chain Failures** | vulnerable or compromised dependencies, build tools and CI/CD pipelines | [Vulnerability scanning](../defense/vulnerability_scanning.md) |
| **A04 Cryptographic Failures** | sensitive data without encryption or with weak cryptography | [Sessions and authentication](../web/sessions.md) |
| **A05 Injection** | user data is interpreted as code (SQL, system commands, HTML/JS) | [SQL Injection](../web/sql_injection.md), [XSS](../web/xss.md) |
| **A06 Insecure Design** | protections missing at the design stage, e.g. no limit on login attempts | [Methodology](pentest_methodology.md) |
| **A07 Authentication Failures** | weak passwords, no brute-force protection, session flaws | [Sessions and authentication](../web/sessions.md) |
| **A08 Software or Data Integrity Failures** | no integrity checks on updates and data, insecure deserialisation | [Files and paths](../web/files_and_paths.md) |
| **A09 Security Logging and Alerting Failures** | an attack leaves no trace, or nobody gets an alert | [Windows logs](../defense/windows_logs.md) |
| **A10 Mishandling of Exceptional Conditions** | errors handled badly: the application lets a request through after an error (fail open) or leaks details in the message | [Methodology](pentest_methodology.md) |

## Other classifications and related terms

Older editions of the ranking and the literature also list separately:

- **Sensitive Data Exposure**: exposing sensitive data (part of Cryptographic Failures since 2021),
- **XML External Entity**: its own category in 2017, part of Security Misconfiguration since 2021 (A02 in 2025),
- **XSS**: its own category in 2017, part of Injection since 2021 (A05 in 2025),
- **Server-Side Request Forgery**: its own category A10 in 2021, part of A01 Broken Access Control since 2025,
- **Vulnerable and Outdated Components**: A06 in 2021, broadened to A03 Software Supply Chain Failures in 2025,
- password attacks: **credential stuffing** (username and password pairs stolen from other services), **password spraying** (a few common passwords against many accounts), dictionary attacks and rainbow tables.

!!! tip "OWASP API Security Top 10"
    APIs have a separate ranking (2023 edition). First place goes to **BOLA** (Broken Object Level Authorization), which is IDOR in an API, and the categories also include missing resource limits (rate limiting).
