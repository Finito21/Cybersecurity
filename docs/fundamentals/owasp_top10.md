---
description: "OWASP Top 10 dla aplikacji webowych: kategorie ryzyka, przykłady błędów i odnośniki do szczegółowych notatek o poszczególnych podatnościach."
---

# OWASP Top 10

**OWASP Top 10** to ranking najważniejszych kategorii ryzyka w aplikacjach webowych, publikowany przez fundację OWASP na podstawie danych przekazanych przez organizacje oraz ankiety branżowej. Notatki opierają się na edycji 2025. Ranking nie jest pełną metodyką testów: do tego służą **OWASP ASVS** (lista wymagań) i **OWASP Web Security Testing Guide**.

| Kategoria (2025) | Na czym polega | Notatki |
|---|---|---|
| **A01 Broken Access Control** | użytkownik dostaje dane lub funkcje, do których nie ma uprawnień; od 2025 obejmuje też SSRF | [Kontrola dostępu i IDOR](../web/access_control.md), [CSRF](../web/csrf.md), [SSRF](../web/ssrf.md) |
| **A02 Security Misconfiguration** | domyślne ustawienia, tryb debugowania, zbędne usługi, ujawnianie wersji, XXE | [XXE](../web/xxe.md), [Cache i nagłówki](../web/cache_and_headers.md), [NGINX](../defense/nginx_hardening.md) |
| **A03 Software Supply Chain Failures** | podatne lub przejęte zależności, narzędzia budowania i potoki CI/CD | [Skanowanie podatności](../defense/vulnerability_scanning.md) |
| **A04 Cryptographic Failures** | dane wrażliwe bez szyfrowania lub ze słabą kryptografią | [Sesje i uwierzytelnianie](../web/sessions.md) |
| **A05 Injection** | dane od użytkownika są interpretowane jako kod (SQL, polecenia systemowe, HTML/JS) | [SQL Injection](../web/sql_injection.md), [XSS](../web/xss.md) |
| **A06 Insecure Design** | brak zabezpieczeń już na etapie projektu, np. brak limitu prób logowania | [Metodyka](pentest_methodology.md) |
| **A07 Authentication Failures** | słabe hasła, brak ochrony przed brute force, błędy sesji | [Sesje i uwierzytelnianie](../web/sessions.md) |
| **A08 Software or Data Integrity Failures** | brak kontroli integralności aktualizacji i danych, niebezpieczna deserializacja | [Pliki i ścieżki](../web/files_and_paths.md) |
| **A09 Security Logging and Alerting Failures** | atak nie zostawia śladów albo nikt nie dostaje alertu | [Logi Windows](../defense/windows_logs.md) |
| **A10 Mishandling of Exceptional Conditions** | błędna obsługa wyjątków: aplikacja przepuszcza żądanie po błędzie (fail open) lub ujawnia szczegóły w komunikacie | [Metodyka](pentest_methodology.md) |

## Inne klasyfikacje i pojęcia pokrewne

Starsze wydania rankingu i literatura wymieniają też osobno:

- **Sensitive Data Exposure**: ujawnianie danych wrażliwych (od 2021 część kategorii Cryptographic Failures),
- **XML External Entity**: osobna kategoria w 2017, od 2021 część Security Misconfiguration (w 2025 A02),
- **XSS**: osobna kategoria w 2017, od 2021 część Injection (w 2025 A05),
- **Server-Side Request Forgery**: osobna kategoria A10 w 2021, od 2025 część A01 Broken Access Control,
- **Vulnerable and Outdated Components**: A06 w 2021, w 2025 rozszerzona do A03 Software Supply Chain Failures,
- ataki na hasła: **credential stuffing** (wykradzione pary login–hasło z innych serwisów), **password spraying** (kilka popularnych haseł na wielu kontach), ataki słownikowe i tablice tęczowe.

!!! tip "OWASP API Security Top 10"
    Dla API istnieje osobny ranking (edycja 2023). Na pierwszym miejscu jest **BOLA** (Broken Object Level Authorization), czyli IDOR w API, a wśród kategorii jest też brak limitów zasobów (rate limiting).
