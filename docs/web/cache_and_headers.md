---
description: "Bezpieczeństwo cache i nagłówki HTTP: Web Cache Deception i Poisoning, nagłówki bezpieczeństwa HSTS, CSP, X-Frame-Options oraz ujawnianie wersji."
---

# Cache i nagłówki

## Web Cache Deception i Poisoning

Cache (pamięć podręczna CDN lub serwera) przyspiesza działanie, ale błędna konfiguracja prowadzi do dwóch podatności:

- **Web Cache Deception**: atakujący skłania cache do zapisania odpowiedzi z danymi prywatnymi ofiary, a potem odczytuje ją ze współdzielonego cache.
- **Web Cache Poisoning**: atakujący zatruwa cache odpowiedzią zmienioną przez nagłówek nieuwzględniany w kluczu cache (unkeyed header), którą dostają inni użytkownicy.

Oba błędy wynikają z tego, co wchodzi (lub nie wchodzi) do **klucza cache**: zwykle metody, hosta i ścieżki, czasem wybranych parametrów. Deception wykorzystuje rozbieżność w interpretacji ścieżki, poisoning – wejścia pomijane w kluczu, które mimo to zmieniają odpowiedź.

### Jak testować Web Cache Deception

1. Sprawdź nagłówki cache w odpowiedziach: `X-Cache`, `CF-Cache-Status`, `Age`, `Via`.
2. Znajdź endpoint z danymi prywatnymi (`/my-account`, `/profile`, `/orders`).
3. Dodaj na końcu rozszerzenie statyczne (`/my-account.js`) i sprawdź, czy odpowiedź jest cache'owana (hit) i czy widać w niej dane.
4. Testuj separatory i znaki kodowane (Intruder) oraz normalizację ścieżek:

```text
/static/..%2fmy-account
/my-account%2f%2e%2e%2fstatic
```

Sednem jest **rozbieżność interpretacji ścieżki**: cache widzi statyczne rozszerzenie (`.css`, `.js`) i zapisuje odpowiedź jako publiczny zasób, podczas gdy serwer źródłowy ignoruje dopisany sufiks (np. mapuje `/my-account/dowolne` na tę samą stronę) i zwraca treść zalogowanego użytkownika.

### Jak testować Web Cache Poisoning

Cel to nagłówek nieuwzględniany w kluczu cache, który mimo to trafia do odpowiedzi (do bezwzględnego URL, linku do skryptu, przekierowania).

!!! warning "Zawsze z cache busterem"
    Podczas testu dodawaj do każdego żądania unikalny parametr (np. `?cb=8317`), aby zatruć wyłącznie własny klucz cache. Bez niego zatruta odpowiedź trafi do prawdziwych użytkowników. Parametr usuwa się dopiero wtedy, gdy wpływ jest potwierdzony, a klient wyraził na to zgodę. To samo dotyczy testów Web Cache Deception.

1. Wyślij żądanie z podejrzanym nagłówkiem, np. `X-Forwarded-Host`, `X-Forwarded-Scheme` czy `X-Forwarded-For`, i sprawdź, czy jego wartość odbija się w treści odpowiedzi.
2. Potwierdź, że odpowiedź jest cache'owalna (`Cache-Control`, `X-Cache: hit/miss`, `Age`).
3. Powtórz żądanie **bez** zatrutego nagłówka, ale z tym samym cache busterem: jeśli wraca zatruta odpowiedź z cache, każdy użytkownik pod tym kluczem dostałby ją także.

### Przeciwdziałanie

- `Cache-Control: no-store, private` dla treści dynamicznych i spersonalizowanych.
- Spójna interpretacja ścieżek między CDN a serwerem źródłowym; nie cache'uj po samym rozszerzeniu.
- Włącz do klucza cache każdy nagłówek, który wpływa na odpowiedź, albo w ogóle takie nagłówki ignoruj.
- Mechanizmy typu Cloudflare Cache Deception Armor.

## Nagłówki bezpieczeństwa

| Nagłówek | Rola |
|---|---|
| `Strict-Transport-Security` (HSTS) | wymusza HTTPS; po pierwszej wizycie przeglądarka sama zamienia `http` na `https` |
| `Content-Security-Policy` (CSP) | ogranicza źródła skryptów i zasobów; druga warstwa przeciw XSS |
| `X-Content-Type-Options: nosniff` | zakazuje zgadywania typu MIME |
| `X-Frame-Options` | starsza ochrona przed clickjackingiem; tylko `DENY` lub `SAMEORIGIN` |
| `Content-Security-Policy: frame-ancestors` | nowsza, elastyczniejsza ochrona przed osadzaniem w ramce |
| `Set-Cookie: HttpOnly; Secure; SameSite` | zabezpiecza ciasteczka sesyjne |
| `Referrer-Policy` | ogranicza wyciek adresów w nagłówku Referer |
| `Permissions-Policy` | wyłącza niepotrzebne funkcje przeglądarki (kamera, mikrofon, geolokalizacja) |
| `Cross-Origin-Opener-Policy` | odcina stronę od okien otwartych z innych originów |

!!! note "frame-ancestors zastępuje X-Frame-Options"
    `CSP: frame-ancestors` to nowszy mechanizm i pozwala wskazać wiele źródeł, podczas gdy przestarzałe `X-Frame-Options: ALLOW-FROM` jest ignorowane przez współczesne przeglądarki. Aby zezwolić na ramkę z konkretnych źródeł, użyj `frame-ancestors`. Można wysyłać oba naraz (XFO dla starszych przeglądarek), ale przy konflikcie liczy się `frame-ancestors`. HSTS działa w pełni już po pierwszej wizycie; wpis na liście `preload` (wymaga `includeSubDomains`, `max-age` co najmniej roku i tokenu `preload`) usuwa tylko lukę przy pierwszym połączeniu.

!!! warning "X-XSS-Protection jest przestarzały"
    Nagłówka `X-XSS-Protection` nie włącza się: współczesne przeglądarki go ignorują, a stary filtr XSS sam wprowadzał podatności. Zalecane jest `X-XSS-Protection: 0` albo pominięcie nagłówka i poleganie na CSP. Skanery wciąż go zgłaszają, więc warto znać tę odpowiedź.

## Ujawnianie informacji

Nagłówki `Server`, `X-Powered-By` czy `Via` zdradzają wersje oprogramowania (np. `Apache/2.4.66`, `PHP/8.4`), co ułatwia dobranie exploita. Również pełne komunikaty błędów z bezwzględnymi ścieżkami skryptów to ujawnianie informacji (zwykle poziom LOW w raporcie, ale warto zgłosić).

## Rekomendacje

- Ustaw komplet nagłówków bezpieczeństwa (można zweryfikować skanerem lub w DevTools).
- Ukryj wersje w nagłówkach (`server_tokens off` w [NGINX](../defense/nginx_hardening.md)).
- Wyłącz szczegółowe błędy w odpowiedziach; loguj je po stronie serwera.
