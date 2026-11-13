---
description: "Notatki z cyberbezpieczeństwa: podatności aplikacji webowych, metodyka pentestu, bezpieczeństwo sieci, analiza logów, hardening i narzędzia."
hide:
  - navigation
  - toc
---

<div class="cs-home" markdown>

<div class="cs-intro" markdown>

# Cybersecurity Notes { lang=en }

Notatki z nauki bezpieczeństwa IT: od podstawowych pojęć i OWASP Top 10, przez podatności aplikacji webowych i metodykę testu penetracyjnego, po bezpieczeństwo sieci, analizę logów i hardening serwerów.

<button type="button" class="cs-search" data-cs-search>Szukaj w notatkach <kbd>/</kbd></button>

</div>

<div class="cs-path" markdown>

## Ścieżka nauki

1. [Pojęcia bezpieczeństwa](fundamentals/security_basics.md) i [OWASP Top 10](fundamentals/owasp_top10.md): wspólny słownik i mapa najczęstszych błędów.
2. [Burp Suite](tools/burp_suite.md): narzędzie, w którym obserwuje się i modyfikuje ruch aplikacji.
3. [Kontrola dostępu](web/access_control.md), [SQL Injection](web/sql_injection.md) i [XSS](web/xss.md): trzy klasy błędów, od których zaczyna się każdy test.
4. [Metodyka testu](fundamentals/pentest_methodology.md) i [raport](fundamentals/pentest_report.md): jak prowadzić test i opisać wyniki.
5. [Bezpieczeństwo LAN](network/lan_security.md) i [logi Windows](defense/windows_logs.md): druga strona, czyli sieć i wykrywanie incydentów.

</div>

</div>

!!! warning "Tylko w ramach uprawnień"
    Techniki opisane w notatkach stosuje się wyłącznie na systemach, do których testowania ma się pisemną zgodę (umowa, zakres testów, program bug bounty), we własnym laboratorium lub na platformach szkoleniowych. Nieuprawniony dostęp do systemu, przechwytywanie danych, zakłócanie pracy systemów i udostępnianie narzędzi do tych celów są przestępstwami (w Polsce m.in. art. 267–269b Kodeksu karnego). Wyłączenie odpowiedzialności z art. 269c dotyczy wąskich przypadków i nie zastępuje zgody na test.

    Jeśli przypadkiem trafisz na podatność w cudzym systemie, nie wykorzystuj jej: zgłoś ją właścicielowi lub do [CERT Polska](https://cert.pl/). Notatki nie są poradą prawną.

## Działy i wszystkie strony { .cs-label }

<div class="cs-sections" markdown>

<div class="cs-section" markdown>
<div markdown>

### [Podstawy](fundamentals/index.md)

Triada CIA, uwierzytelnianie i autoryzacja, OWASP Top 10, metodyka i raport.

</div>

- [Pojęcia bezpieczeństwa](fundamentals/security_basics.md)
- [OWASP Top 10](fundamentals/owasp_top10.md)
- [Metodyka testu penetracyjnego](fundamentals/pentest_methodology.md)
- [Raport z testów](fundamentals/pentest_report.md)
- [Pytania rekrutacyjne](fundamentals/interview_questions.md)

</div>

<div class="cs-section" markdown>
<div markdown>

### [Aplikacje webowe](web/index.md)

Najczęstsze klasy podatności, każda z testem i obroną.

</div>

- [Kontrola dostępu i IDOR](web/access_control.md)
- [SQL Injection](web/sql_injection.md)
- [XSS](web/xss.md)
- [CSRF](web/csrf.md)
- [SSRF](web/ssrf.md)
- [XXE](web/xxe.md)
- [Pliki i ścieżki](web/files_and_paths.md)
- [Sesje i uwierzytelnianie](web/sessions.md)
- [Cache i nagłówki](web/cache_and_headers.md)

</div>

<div class="cs-section" markdown>
<div markdown>

### [Sieci](network/index.md)

Zagrożenia w LAN, 802.1X, listy ACL, Wi-Fi oraz ataki DoS i DDoS.

</div>

- [Bezpieczeństwo LAN](network/lan_security.md)
- [Listy ACL](network/acl.md)
- [Sieci bezprzewodowe](network/wireless.md)
- [Ataki DoS i DDoS](network/dos.md)

</div>

<div class="cs-section" markdown>
<div markdown>

### [Obrona](defense/index.md)

Logi, hardening serwerów, backup i skanowanie podatności.

</div>

- [Logi Windows](defense/windows_logs.md)
- [Linux](defense/linux_security.md)
- [NGINX](defense/nginx_hardening.md)
- [Backup i ransomware](defense/ransomware_backup.md)
- [Skanowanie podatności](defense/vulnerability_scanning.md)

</div>

<div class="cs-section" markdown>
<div markdown>

### [OSINT](osint/index.md)

Biały wywiad: wyszukiwanie, metadane, wycieki, geolokalizacja i rozpoznanie przed testem.

</div>

- [OSINT w praktyce](osint/index.md)

</div>

<div class="cs-section" markdown>
<div markdown>

### [Narzędzia](tools/index.md)

Proxy do testów aplikacji webowych.

</div>

- [Burp Suite](tools/burp_suite.md)
- [ZAP](tools/zap.md)

</div>

</div>

## O projekcie

Cybersecurity Notes to notatki z nauki bezpieczeństwa IT: kursów, szkoleń oraz własnych ćwiczeń praktycznych. Wykorzystane materiały są wymienione w zakładce **[Źródła](resources.md)**.

Narzędzia AI pomagają w porządkowaniu i redakcji tekstów, a każda strona jest sprawdzana przed publikacją. Notatki skupiają się na zrozumieniu mechanizmów i na obronie, a nie na gotowych exploitach.

Jeśli coś jest błędne lub niejasne, [zgłoś to w GitHub Issues](https://github.com/Finito21/Cybersecurity/issues).
