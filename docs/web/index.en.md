---
description: "Web application vulnerabilities: access control, SQL Injection, XSS, CSRF, SSRF, XXE, path traversal, file upload, sessions, and cache and headers."
---

# Web applications

The most common classes of web application vulnerability, each with the same structure: what it is, when it occurs, when the application is safe and how to check it in [Burp Suite](../tools/burp_suite.md).

| Vulnerability | OWASP 2025 | Main impact |
|---|---|---|
| [Access control and IDOR](access_control.md) | A01 | access to other people's data and functions |
| [SQL Injection](sql_injection.md) | A05 | reading and modifying the database |
| [XSS](xss.md) | A05 | running JavaScript in other users' browsers |
| [CSRF](csrf.md) | A01 | an action on behalf of a logged-in victim |
| [SSRF](ssrf.md) | A01 | server requests into the internal network |
| [XXE](xxe.md) | A02 / A05 | reading files and SSRF through the XML parser |
| [Files and paths](files_and_paths.md) | A01 / A08 | reading files, uploading a web shell |
| [Sessions and authentication](sessions.md) | A07 | account takeover |
| [Cache and headers](cache_and_headers.md) | A02 | data leaks, missing layers of protection |

!!! warning "Only with permission"
    The examples are for learning and for testing on your own or authorised systems. The payloads are minimal and meant to confirm a vulnerability, not to cause damage.
