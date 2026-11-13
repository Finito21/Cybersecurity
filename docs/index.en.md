---
description: "Cybersecurity notes: web application vulnerabilities, penetration test methodology, network security, log analysis, hardening and tools."
hide:
  - navigation
  - toc
---

<div class="cs-home" markdown>

<div class="cs-intro" markdown>

# Cybersecurity Notes

Notes made while learning IT security: from core concepts and the OWASP Top 10, through web application vulnerabilities and penetration test methodology, to network security, log analysis and server hardening.

<button type="button" class="cs-search" data-cs-search>Search the notes <kbd>/</kbd></button>

</div>

<div class="cs-path" markdown>

## Learning path

1. [Security concepts](fundamentals/security_basics.md) and the [OWASP Top 10](fundamentals/owasp_top10.md): a shared vocabulary and a map of the most common flaws.
2. [Burp Suite](tools/burp_suite.md): the tool used to observe and modify application traffic.
3. [Access control](web/access_control.md), [SQL Injection](web/sql_injection.md) and [XSS](web/xss.md): the three classes of bugs every test starts with.
4. [Penetration test methodology](fundamentals/pentest_methodology.md) and the [report](fundamentals/pentest_report.md): how to run a test and describe the results.
5. [LAN security](network/lan_security.md) and [Windows logs](defense/windows_logs.md): the other side: networks and incident detection.

</div>

</div>

!!! warning "Only with permission"
    The techniques in these notes are used only on systems you have written permission to test (a contract, an agreed scope, a bug bounty programme), in your own lab or on training platforms. Unauthorised access to a system, intercepting data, disrupting systems and sharing tools for these purposes are crimes: in Poland under Articles 267–269b of the Criminal Code (<span lang="pl">Kodeks karny</span>), and elsewhere under laws such as the UK Computer Misuse Act or the US CFAA. The exemption in Article 269c covers narrow cases and does not replace permission to test.

    If you come across a vulnerability in someone else's system by accident, do not exploit it: report it to the owner or to a national CERT (in Poland, [CERT Polska](https://cert.pl/)). These notes are not legal advice.

## Sections and all pages { .cs-label }

<div class="cs-sections" markdown>

<div class="cs-section" markdown>
<div markdown>

### [Fundamentals](fundamentals/index.md)

The CIA triad, authentication and authorisation, the OWASP Top 10, methodology and the report.

</div>

- [Security concepts](fundamentals/security_basics.md)
- [OWASP Top 10](fundamentals/owasp_top10.md)
- [Penetration test methodology](fundamentals/pentest_methodology.md)
- [Test report](fundamentals/pentest_report.md)
- [Interview questions](fundamentals/interview_questions.md)

</div>

<div class="cs-section" markdown>
<div markdown>

### [Web applications](web/index.md)

The most common classes of vulnerabilities, each with testing and defence.

</div>

- [Access control and IDOR](web/access_control.md)
- [SQL Injection](web/sql_injection.md)
- [XSS](web/xss.md)
- [CSRF](web/csrf.md)
- [SSRF](web/ssrf.md)
- [XXE](web/xxe.md)
- [Files and paths](web/files_and_paths.md)
- [Sessions and authentication](web/sessions.md)
- [Cache and headers](web/cache_and_headers.md)

</div>

<div class="cs-section" markdown>
<div markdown>

### [Networks](network/index.md)

LAN threats, 802.1X, access control lists, Wi-Fi, and DoS and DDoS attacks.

</div>

- [LAN security](network/lan_security.md)
- [Access control lists](network/acl.md)
- [Wireless networks](network/wireless.md)
- [DoS and DDoS attacks](network/dos.md)

</div>

<div class="cs-section" markdown>
<div markdown>

### [Defence](defense/index.md)

Logs, server hardening, backups and vulnerability scanning.

</div>

- [Windows logs](defense/windows_logs.md)
- [Linux](defense/linux_security.md)
- [NGINX](defense/nginx_hardening.md)
- [Backup and ransomware](defense/ransomware_backup.md)
- [Vulnerability scanning](defense/vulnerability_scanning.md)

</div>

<div class="cs-section" markdown>
<div markdown>

### [OSINT](osint/index.md)

Open-source intelligence: search, metadata, leaks, geolocation and reconnaissance before a test.

</div>

- [OSINT in practice](osint/index.md)

</div>

<div class="cs-section" markdown>
<div markdown>

### [Tools](tools/index.md)

Proxies for web application testing.

</div>

- [Burp Suite](tools/burp_suite.md)
- [ZAP](tools/zap.md)

</div>

</div>

## About

This site collects notes from learning IT security: courses, training and hands-on practice. The materials used are listed in **[Resources](resources.md)**.

AI tools help with organising and editing the texts, and every page is reviewed before publication. The notes focus on understanding the mechanisms and on defence, not on ready-made exploits.

Found a mistake or something unclear? [Report it in GitHub Issues](https://github.com/Finito21/Cybersecurity/issues).
