---
description: "Server-Side Request Forgery: dostęp do sieci wewnętrznej i metadanych chmury, testowanie out-of-band, omijanie czarnych list i blind SSRF."
---

# SSRF

**Server-Side Request Forgery (SSRF)** to podatność, w której atakujący zmusza serwer do wykonania żądania pod wskazany adres. Serwer staje się pośrednikiem (proxy), co pozwala dotrzeć do zasobów wewnętrznych niedostępnych z internetu, skanować sieć wewnętrzną zza firewalla, odczytać metadane chmury (`169.254.169.254`) lub pliki lokalne (`file://`). W OWASP Top 10 2025 to część kategorii **A01 Broken Access Control** (w edycji 2021 osobna kategoria A10).

## Kiedy występuje

Wszędzie tam, gdzie aplikacja przyjmuje URL lub adres IP i pobiera z niego dane bez weryfikacji: import danych z URL, generatory PDF i zrzutów stron, ładowanie awatarów, podglądy linków, webhooki i integracje z API.

## Kiedy aplikacja jest bezpieczna (obrona w głąb)

- **Lista dozwolonych** domen i adresów (allowlist) zamiast listy blokowanych; walidację przeprowadzaj po rozwiązaniu nazwy na IP, a do połączenia przypnij dokładnie ten zweryfikowany adres (inaczej DNS rebinding podmienia IP między sprawdzeniem a żądaniem).
- Blokada całych zakresów, nie pojedynczych adresów: pętla zwrotna (loopback: `127.0.0.0/8`, `::1`), link-local wraz z metadanymi (`169.254.0.0/16`), prywatne (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), `0.0.0.0/8` (w Linuksie `0.0.0.0` trafia do localhosta), CGNAT (`100.64.0.0/10`), ULA (`fc00::/7`, w tym metadane AWS po IPv6 `fd00:ec2::254`) oraz adresy IPv4-mapped IPv6 (`::ffff:127.0.0.1`).
- Brak podążania za przekierowaniami albo ponowna walidacja celu przy każdym przekierowaniu.
- Walidacja odpowiedzi (czy to faktycznie oczekiwany typ zasobu).
- Izolacja sieciowa: serwer aplikacji nie ma dostępu do krytycznych usług wewnętrznych.

## Jak testować

Darmowy Burp nie ma modułu Collaborator, więc do nasłuchu potrzebny jest zewnętrzny serwer.

!!! warning "Granice testu SSRF"
    - W zleceniach używaj własnego serwera nasłuchowego (własny VPS lub samodzielnie hostowany interactsh); publiczne usługi typu webhook.site tylko w laboratoriach, bo zapisują dane klienta u stron trzecich.
    - Przy metadanych chmury poprzestań na potwierdzeniu dostępu; nie pobieraj poświadczeń roli (`iam/security-credentials`).
    - Usługi wewnętrzne (Redis, MySQL) tylko potwierdzaj jako osiągalne; nie wysyłaj do nich poleceń zmieniających stan.

1. Znajdź funkcję pobierającą dane z URL i wyślij żądanie do Repeatera.
2. Podmień podatny parametr (`url=`, `image=`, `src=`, `endpoint=`) na unikalny adres swojego serwera nasłuchowego. Pojawienie się żądania w logu potwierdza SSRF (serwer nawiązał połączenie wychodzące).
3. Testuj porty i protokoły: `http://listener.example:8080/id`, `file:///etc/passwd`, `gopher://`, `dict://`.
4. Celuj w zasoby wewnętrzne: `http://127.0.0.1`, `http://169.254.169.254/latest/meta-data/`, typowe porty usług (`:6379` Redis, `:3306` MySQL).
5. Sprawdź, czy walidacja jest odporna na typowe obejścia list blokowanych:

```text
http://2130706433        # 127.0.0.1 dziesiętnie
http://0x7f000001        # 127.0.0.1 szesnastkowo
http://127.0.0.1.        # kropka na końcu
http://localtest.me      # domena wskazująca na 127.0.0.1
http://[::1]/            # pętla zwrotna IPv6
http://[::ffff:7f00:1]   # 127.0.0.1 jako adres IPv4-mapped IPv6
```

6. **Blind SSRF** (serwer zwraca tylko „OK”): porównaj czasy odpowiedzi (`127.0.0.1` szybciej niż adres zewnętrzny) i sprawdź w logu serwera nasłuchowego nagłówki żądania (np. `User-Agent` zdradza bibliotekę i podpowiada dalsze kroki).

!!! warning "DNS rebinding i przekierowania obchodzą walidację"
    Sprawdzenie URL lub IP *przed* żądaniem nie wystarcza, jeśli serwer rozwiązuje nazwę drugi raz w chwili połączenia. W **DNS rebinding** atakujący kontroluje domenę z krótkim TTL: pierwsze zapytanie zwraca adres publiczny (przechodzi walidację), kolejne – adres wewnętrzny, którego serwer faktycznie użyje. Podobnie **przekierowanie 3xx** z zaufanej domeny może skierować klienta na `169.254.169.254` lub `127.0.0.1`, jeśli ten ślepo podąża za `Location`. Obrona: przypnij zweryfikowany adres do połączenia i nie ufaj przekierowaniom (albo sprawdzaj każdy krok przekierowania).

!!! example "Z laboratorium"
    Endpoint w aplikacji CRM przyjmował pełny adres (`endpoint=...&product_id=1`). To pozwalało kierować żądania serwera tam, gdzie chciał atakujący: klasyczny SSRF przez konfigurowalny endpoint.

## Rekomendacje

- Lista dozwolonych adresów docelowych, blokada zakresów prywatnych, link-local i metadanych, brak przekierowań, przypięcie zweryfikowanego IP do połączenia.
- Osobny, odizolowany komponent (proxy wychodzące) do pobierania zasobów zewnętrznych.
- W chmurze wymuś IMDSv2: metadane wymagają najpierw tokena (żądanie `PUT` z nagłówkiem TTL), który dopiero pozwala odczytać dane, więc prosty SSRF typu `GET` nie sięga po poświadczenia roli. W kontenerach ustaw też limit przeskoków odpowiedzi (hop limit) na 1, aby kontener nie dosięgał metadanych hosta. To utrudnienie, nie zamiennik segmentacji sieci.
