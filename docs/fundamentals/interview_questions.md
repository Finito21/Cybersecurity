---
description: "Pytania rekrutacyjne na stanowisko pentestera aplikacji webowych z krótkimi odpowiedziami: HTTPS, HSTS, XSS, eskalacja uprawnień, cache i JWT."
---

# Pytania rekrutacyjne

Pytania zebrane podczas przygotowań do rozmów na stanowisko pentestera. Sprawdzają nie tylko znajomość ataków, ale też rozumienie działania przeglądarki i protokołów.

??? question "Co dzieje się technicznie, gdy otwierasz w przeglądarce adres https://…?"
    Przeglądarka rozwiązuje nazwę w DNS, nawiązuje połączenie TCP (lub QUIC przy HTTP/3), wykonuje handshake TLS (wymiana kluczy, weryfikacja certyfikatu i łańcucha zaufania), wysyła żądanie HTTP `GET`, odbiera odpowiedź, parsuje HTML, pobiera zasoby (CSS, JS, obrazy) i uruchamia skrypty z uwzględnieniem polityk (Same-Origin Policy, CSP).

??? question "Jak działa szyfrowanie w HTTPS i dlaczego wpisanie http:// otwiera wersję https://?"
    W handshake TLS kryptografia asymetryczna służy do uwierzytelnienia serwera i uzgodnienia klucza sesji, a dane szyfruje się szybkim szyfrem symetrycznym. Za przejście na HTTPS odpowiada przekierowanie serwera oraz nagłówek **HSTS** (`Strict-Transport-Security`): po pierwszej wizycie przeglądarka sama zamienia `http://` na `https://` przez zadany czas. Lista HSTS preload działa nawet przy pierwszej wizycie.

??? question "Czy DOM XSS to Stored XSS czy Reflected XSS?"
    Żaden z nich: to osobna kategoria. W DOM XSS złośliwe dane trafiają do niebezpiecznej funkcji (np. `innerHTML`) w skrypcie po stronie przeglądarki; serwer może ich w ogóle nie widzieć (np. fragment URL po `#`). Źródło danych może być przy tym trwałe lub odbite.

??? question "Czym różni się eskalacja pozioma od pionowej?"
    **Pozioma**: dostęp do danych lub funkcji innego użytkownika o tej samej roli (np. cudze zamówienia, IDOR). **Pionowa**: uzyskanie wyższej roli (np. zwykły użytkownik wykonuje akcje administratora).

??? question "Wstrzyknięty kod JavaScript wygląda poprawnie w źródle, ale się nie wykonuje. Dlaczego?"
    Najczęściej blokuje go **Content Security Policy**: polityka zabrania skryptów inline lub ze źródeł spoza listy. Inne przyczyny: `<script>` wstawiony przez `innerHTML` nigdy się nie wykonuje (tak stanowi specyfikacja HTML5), dane wstawione przez `textContent` zamiast HTML, kontekst, w którym kod nie jest interpretowany, sandbox ramki `iframe`.

??? question "Jak potwierdzić Blind SQL Injection?"
    Porównując odpowiedzi na warunek zawsze prawdziwy i zawsze fałszywy (różnica w treści lub długości: wariant boolean) albo mierząc czas odpowiedzi przy celowym opóźnieniu po stronie bazy (wariant time-based). Pomocne jest też wymuszenie połączenia wychodzącego do kontrolowanego serwera (out-of-band). Szczegóły: [SQL Injection](../web/sql_injection.md).

??? question "Na czym polega DNS Rebinding?"
    Atakujący kontroluje domenę, której rekord DNS ma bardzo krótki czas życia. Najpierw domena wskazuje na jego serwer, a po załadowaniu strony na adres wewnętrzny (np. `127.0.0.1` lub router w sieci ofiary). Przeglądarka uważa, że to wciąż to samo źródło, więc skrypt może komunikować się z usługą wewnętrzną. Obrona: sprawdzanie nagłówka `Host`, uwierzytelnianie usług lokalnych, blokowanie odpowiedzi DNS z adresami prywatnymi.

??? question "Jakie błędy można popełnić, wdrażając cache?"
    Zapisanie w cache odpowiedzi z danymi prywatnymi i podanie jej innym użytkownikom (**Web Cache Deception**) albo zapisanie odpowiedzi zmienionej przez atakującego przez nagłówek nieuwzględniany w kluczu cache (unkeyed header) (**Web Cache Poisoning**). Przyczyną są różnice w interpretacji ścieżek między cache a serwerem i brak nagłówków `Cache-Control: no-store, private`. Szczegóły: [Cache i nagłówki](../web/cache_and_headers.md).

??? question "Ciasteczko sesyjne jest tokenem JWT. Czego warto szukać?"
    Akceptowania algorytmu `none` lub braku weryfikacji podpisu, słabego sekretu HMAC, pomylenia algorytmów (RS256 i HS256), braku wygasania (`exp`) i unieważniania przy wylogowaniu, ról w payloadzie, którym serwer ufa bez sprawdzenia, danych wrażliwych w payloadzie (jest tylko zakodowany). Szczegóły: [Sesje i uwierzytelnianie](../web/sessions.md).

??? question "Masz self-XSS w trwałej postaci (widoczny tylko na własnym koncie). Jak ocenić jego realny wpływ?"
    Sprawdza się, czy da się go połączyć z **CSRF** (wymuszenie zapisania payloadu na koncie ofiary), z **login CSRF** lub wymuszeniem zalogowania ofiary na konto atakującego, z **Web Cache Poisoning** lub Deception (strona z payloadem trafia do cache dla innych) oraz z funkcją udostępniania lub podglądu profilu przez innych użytkowników.
