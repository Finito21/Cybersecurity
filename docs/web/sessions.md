---
description: "Sesje i uwierzytelnianie: hijacking i fixation, bezpieczne ciasteczka, błędy JWT, pomylenie algorytmów i kid, tokeny odświeżające oraz ochrona logowania."
---

# Sesje i uwierzytelnianie

Ponieważ HTTP jest bezstanowy, aplikacja rozpoznaje zalogowanego użytkownika po **sesji**: identyfikatorze w ciasteczku lub tokenie. Błędy w tym miejscu prowadzą do przejęcia konta. To kategoria **A07 Authentication Failures** OWASP Top 10.

## Ataki na sesję

| Atak | Opis |
|---|---|
| **Session hijacking** | przejęcie identyfikatora sesji (np. przez XSS lub podsłuch) i podszycie się |
| **Session fixation** | narzucenie ofierze znanego identyfikatora sesji; serwer nie zmienia go po zalogowaniu |
| **Session sniffing** | przechwycenie identyfikatora z nieszyfrowanego ruchu |
| **Brute force** | zgadywanie słabego identyfikatora lub hasła |

## Bezpieczna sesja

- Nowy identyfikator sesji po zalogowaniu (ochrona przed fixation).
- Ciasteczka z flagami `HttpOnly` (niedostępne dla JS), `Secure` (tylko HTTPS) i `SameSite`.
- Unieważnianie sesji po wylogowaniu i rozsądny czas wygaśnięcia.
- Wysoka entropia identyfikatora (moduł Sequencer w Burpie pozwala ocenić losowość).

## Uwierzytelnianie

- Ochrona przed brute force: limit prób, blokady, opóźnienia, CAPTCHA, MFA.
- Hasła przechowywane jako skrót z silną funkcją (bcrypt, Argon2) i solą. Skrót hasła w HTML lub w odpowiedzi API to wyciek: przy zmianie hasła widać czasem `$2y$12$...` (bcrypt), czego być nie powinno.
- Spójne komunikaty: formularz logowania nie powinien zdradzać, czy istnieje dany login (enumeracja kont).
- Polityka haseł i brak domyślnych poświadczeń.

## JWT

**JWT (JSON Web Token)** to trzy części w Base64URL: nagłówek, dane (payload), podpis. Treść można odczytać, ale nie zmienić bez unieważnienia podpisu. JWT jest podpisany, a nie zaszyfrowany, więc niczego nie ukrywa.

### Błędy weryfikacji

- akceptacja algorytmu `none` albo całkowity brak weryfikacji podpisu,
- słaby sekret HMAC (możliwy do złamania offline listą słów),
- pomylenie algorytmów (RS256→HS256): serwer weryfikuje jako HS256, używając jako sekretu HMAC **publicznego** klucza RSA, więc atakujący podpisuje tym kluczem sfałszowany token – wymuś oczekiwany algorytm dla danego klucza,
- nadużycie nagłówka `kid`: `kid` wskazuje klucz podpisu; jeśli trafia do ścieżki pliku lub zapytania SQL, atakujący może wskazać przewidywalny plik lub wstrzyknąć SQL, by wybrać znany klucz – traktuj `kid` jako niezaufany i stosuj listę dozwolonych,
- nadużycie nagłówków `jku` / `x5u`: wskazują URL z JWKS lub certyfikatem; jeśli serwer pobiera klucze spod adresu kontrolowanego przez atakującego, zaufa tokenom podpisanym przez niego – ogranicz host listą dozwolonych lub ignoruj te nagłówki,
- brak `exp` albo brak unieważniania przy wylogowaniu / zmianie hasła,
- rola lub zakres w payloadzie, którym serwer ufa bez sprawdzenia,
- dane wrażliwe w payloadzie (jest tylko zakodowany, nie zaszyfrowany).

### Tokeny odświeżające

- Łącz token dostępu o krótkim czasie życia z dłużej żyjącym tokenem odświeżającym, aby wyciekły token dostępu szybko wygasał.
- Przechowuj token odświeżający w ciasteczku `HttpOnly`, `Secure` (nie w `localStorage`); po stronie serwera trzymaj tylko jego skrót.
- Rotuj przy każdym użyciu: każde odświeżenie wydaje nowy token odświeżający i unieważnia poprzedni.
- Wykrywanie ponownego użycia: token odświeżający użyty po rotacji oznacza kradzież – unieważnij całą „rodzinę” tokenów.
- Zapewnij możliwość unieważnienia (wylogowanie, zmiana hasła, akcja administratora) przez serwerową sesję lub listę odrzuceń; samych bezstanowych tokenów dostępu nie da się unieważnić przed `exp`.

!!! warning "302 w logowaniu"
    Częstym tropem jest kod `302` po logowaniu: przeglądarka podąża za przekierowaniem, ale w treści odpowiedzi mogą już być dane lub ustawiona sesja. Warto obejrzeć pełną odpowiedź w Burpie, zanim nastąpi przekierowanie.

## Rekomendacje

- Regeneruj identyfikator sesji po zalogowaniu, ustaw flagi ciasteczek, unieważniaj przy wylogowaniu.
- Wymuszaj MFA i ograniczaj próby logowania.
- Weryfikuj podpis JWT i wymuszaj algorytm po stronie serwera; nigdy nie ufaj `kid`, `jku` ani rolom z tokena bez walidacji.
- Utrzymuj krótki czas życia tokenów dostępu i rotuj tokeny odświeżające z wykrywaniem ponownego użycia.
