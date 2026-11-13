---
description: "OSINT: open-source intelligence in practice, search hygiene, dorks, metadata, breaches, image geolocation, technical recon, and ethics and law."
---

# OSINT

**OSINT (Open-Source Intelligence)** is gathering information from open, publicly available sources. In security it is used for reconnaissance before a test and to assess how much an organisation reveals about itself. The guiding principle: a hypothesis first, then the shortest path to verification, with evidence (a link, a screenshot, a date) collected immediately.

!!! warning "Ethics and law"
    OSINT uses open sources, but "open" does not mean "anything goes". Work within permission to test and the agreed scope, with a clear purpose and in line with the law (including the GDPR and, for stalking or impersonation, Article 190a of the Polish Criminal Code, <span lang="pl">Kodeks karny</span>). Aim at an organisation's attack surface, not at private individuals: profiling specific people, working out where they are, public cameras or sensitive registry data quickly cross the line into a privacy violation and break the law. That is where recon ends.

## Search hygiene (OPSEC)

- Do not log in to accounts unless you have to; separate your working identity (a separate profile, container, browser).
- Results are personalised by location, network and VPN; compare them for consistency.
- Save sources at once: the link, a timestamp, what the evidence proves.

## Search dorks

There are many operators, but in practice a few, used well, matter:

```text
site:example.com                          # scope to a domain (subdomains included)
site:example.com -site:www.example.com    # subdomains other than www
site:example.com filetype:pdf (confidential OR internal)  # documents that were not meant to be public
site:example.com intitle:"index of"       # open directories
```

One dork and "nothing there" is not a result: you try variants (synonyms, languages, formats, older versions). Google retired the `cache:` operator in 2024, so older versions of pages are found in the Wayback Machine or archive.today.

## Metadata

Metadata is a quiet layer that reveals too much: the author and organisation (Office, PDF), usernames and paths, tool versions, and in photos sometimes GPS coordinates. Tools: **exiftool** (a quick look at what a file reveals), FOCA (in bulk for an organisation's documents), Maltego and Recon-ng (linking entities and visualising relationships).

## Breaches and passwords

For risk assessment (legally and defensively): **Have I Been Pwned** (whether an email appeared in breaches; a search for a whole domain requires proving you manage it). The principle: a breach is an artefact to confirm with other sources, not a truth in itself. Do not download breach dumps, and do not try passwords you find on any system.

## Image geolocation (GEOINT)

Only for photos within the test scope (the organisation's own material) or training tasks; never to find out where a private person is.

1. **Reverse image search** in several engines (Google, Yandex, Bing, TinEye): different ones handle different images.
2. Catch the "anchors": signs, language, architecture, vegetation, numbers, the road layout.
3. Maps and Street View / Mapillary to match details.
4. Shadow and sun (SunCalc, ShadowMap) give the time, weather archives confirm the day.
5. Document the evidence (screenshots, links, dates). Start from anchors, not from "I guess the country".

## Technical recon

This is still open information, but technical. There are two modes:

- **Passive** (no direct contact with the target): **Shodan** (services and devices visible from the internet), **crt.sh** (subdomains from Certificate Transparency), **VirusTotal** (reputation of domains and files). **theHarvester** aggregates emails, subdomains and hosts mostly from such sources.
- **Active** (requests reach the target): enumerating web resources with **feroxbuster / ffuf**. This directly queries the server, so it needs permission and must stay within the test scope.

!!! tip "VirusTotal and confidentiality"
    Files uploaded to VirusTotal can be downloaded by paying subscribers, and the owner of a sample can see that it was submitted. Search by hash, URL or domain; never upload client documents or internal files.

## Recommendations (for the defender)

- Check what your organisation reveals: metadata in documents, open directories, subdomains, exposed services.
- Strip metadata before publishing files.
- Monitor breaches linked to your domain and enforce a password policy and MFA.
