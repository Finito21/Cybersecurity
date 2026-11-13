---
description: "ZAP (Zed Attack Proxy): a free proxy tool for web application security testing, active and passive scanning, the Spider and Fuzzer, and a comparison with Burp."
---

# ZAP

**ZAP (Zed Attack Proxy)** is a free, open-source, multi-purpose web application security testing tool. It works as a **man-in-the-middle proxy**: it sits between the browser and the application, so it can intercept, analyse and, if needed, modify the messages exchanged. If another proxy is already in use, ZAP can be chained to it.

!!! note "Formerly OWASP ZAP"
    Until 2023 ZAP was an OWASP project. It then moved to the Software Security Project (Linux Foundation), and since 2024 it has been developed as "ZAP by Checkmarx". It is still free and open source (Apache 2.0 licence).

## Active and passive scanning

| Mode | What it is |
|---|---|
| **Passive** | analysing the messages between the browser and the application for known problems, without interfering with the traffic |
| **Active** | trying to detect flaws by directly attacking the application (sending test requests) |

!!! warning "Active scan only within scope"
    Active scanning sends real requests and can change data or load the server. Run it only on systems covered by permission, preferably in a test environment.

## Main features

- **Spider**: automatically discovering the structure, links and resources of the application (a crawler builds a site map). It parses static HTML.
- **AJAX Spider**: explores JavaScript-heavy applications (SPAs) by driving a real browser; it reaches content and actions generated dynamically that the traditional Spider cannot see. It is slower, so use it where the plain Spider maps too little.
- **Fuzzer**: sending a large amount of data (random or from a list) to find input-handling errors.
- **Automation**: the Automation Framework (YAML plans), headless mode, an API and Docker images (baseline and full scan) let you run ZAP in a CI/CD pipeline.
- Intercepting and modifying requests, browsing the history, reporting findings.

## ZAP versus Burp Suite

| Feature | ZAP | Burp Suite Community |
|---|---|---|
| Licence | free, open-source | free (Community), paid (Pro) |
| Active scanner | built in | not in Community |
| Automation | good, CI/CD friendly | limited in Community |
| Ecosystem | community add-ons | a rich ecosystem (mostly Pro) |

In practice the two tools complement each other: ZAP works well for automation and when a free scanner helps, Burp for precise manual work ([Burp Suite](burp_suite.md)).

## Recommendations

- Start with passive scanning and mapping the application with the Spider; for SPAs add the AJAX Spider.
- Run an active scan deliberately, with the scope set correctly.
- Verify scanner results manually: the tool also reports false positives.
