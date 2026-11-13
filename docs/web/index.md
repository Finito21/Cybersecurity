---
description: "Podatności aplikacji webowych: kontrola dostępu, SQL Injection, XSS, CSRF, SSRF, XXE, path traversal, upload plików, sesje oraz cache i nagłówki."
---

# Aplikacje webowe

Najczęstsze klasy podatności w aplikacjach webowych, każda według tego samego schematu: na czym polega, kiedy występuje, kiedy aplikacja jest bezpieczna i jak to sprawdzić w [Burp Suite](../tools/burp_suite.md).

| Podatność | OWASP 2025 | Główny skutek |
|---|---|---|
| [Kontrola dostępu i IDOR](access_control.md) | A01 | dostęp do cudzych danych i funkcji |
| [SQL Injection](sql_injection.md) | A05 | odczyt i modyfikacja bazy danych |
| [XSS](xss.md) | A05 | wykonanie JavaScriptu u innych użytkowników |
| [CSRF](csrf.md) | A01 | akcja w imieniu zalogowanej ofiary |
| [SSRF](ssrf.md) | A01 | żądania serwera do sieci wewnętrznej |
| [XXE](xxe.md) | A02 / A05 | odczyt plików i SSRF przez parser XML |
| [Pliki i ścieżki](files_and_paths.md) | A01 / A08 | odczyt plików, wgranie webshella |
| [Sesje i uwierzytelnianie](sessions.md) | A07 | przejęcie konta |
| [Cache i nagłówki](cache_and_headers.md) | A02 | wyciek danych, brak warstw ochrony |

!!! warning "Tylko w ramach uprawnień"
    Przykłady służą do nauki i do testów na własnych lub autoryzowanych systemach. Payloady są minimalne i mają potwierdzać podatność, a nie wyrządzać szkody.
