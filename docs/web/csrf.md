---
description: "Cross-Site Request Forgery: wymuszenie akcji w imieniu ofiary, tokeny anty-CSRF, niuanse SameSite, CSRF przez GET i JSON oraz pułapki double-submit."
---

# CSRF

**Cross-Site Request Forgery (CSRF)** to atak, w którym złośliwa strona zmusza przeglądarkę zalogowanej ofiary do wykonania akcji w innej aplikacji. Atakujący nie wykrada danych wprost, lecz „pożycza” sesję ofiary (ciasteczka dołączane automatycznie), aby wykonać akcję w jej imieniu: zmianę hasła, dodanie administratora, przelew. Dla serwera żądanie wygląda na w pełni prawidłowe. To część kategorii **A01**.

## Kiedy występuje

- Akcja zmieniająca stan opiera się na przewidywalnym żądaniu (znana struktura URL lub formularza).
- Przeglądarka automatycznie dołącza ciasteczka sesyjne (ambient authority).
- Serwer nie weryfikuje, czy żądanie powstało świadomie wewnątrz aplikacji.

## Kiedy aplikacja jest bezpieczna

| Zabezpieczenie | Jak działa |
|---|---|
| **Token anty-CSRF** | losowy, nieprzewidywalny token związany z sesją, wymagany przy każdej akcji zmieniającej stan |
| **SameSite** | ciasteczko z atrybutem `Lax` lub `Strict` nie jest wysyłane w żądaniach z innej witryny |
| **Double-submit cookie** | ta sama losowa wartość w ciasteczku i w parametrze; serwer porównuje zgodność |
| **Ponowne uwierzytelnienie** | przy akcjach krytycznych ponowne hasło lub kod MFA |
| **Weryfikacja Origin/Referer** | serwer sprawdza, czy żądanie pochodzi z własnej domeny |
| **Fetch Metadata** | serwer odrzuca żądania zmieniające stan z nagłówkiem `Sec-Fetch-Site: cross-site` |
| **Własny nagłówek w API** | API wymaga nagłówka (np. `X-Requested-With`), którego formularz z innej witryny nie ustawi bez preflightu CORS |

## SameSite, CSRF przez GET i JSON

SameSite i typ treści zmieniają podatność endpointu, ale każde ma luki:

- **SameSite to obrona w głąb, nie pełne zabezpieczenie.** Rządzi tylko ciasteczkiem, a „same-site” jest szersze niż „same-origin”: otwarta subdomena lub XSS na dowolnym hoście tej samej witryny wciąż może wysłać żądanie z ciasteczkiem.
- **`Lax` nadal przepuszcza GET.** `Lax` (w przeglądarkach opartych na Chromium domyślny dla ciasteczek bez atrybutu SameSite; Firefox i Safari tego nie robią) wysyła ciasteczko przy nawigacji najwyższego poziomu bezpieczną metodą, więc zmieniający stan `GET` (lub akcja przyjmująca też `GET`) pozostaje podatny przez link lub przekierowanie. Nigdy nie zmieniaj stanu metodą `GET`.
- **Okno ulgi Lax+POST.** Chromium przez około 2 minuty po ustawieniu ciasteczka bez atrybutu SameSite wysyła je przy międzywitrynowym `POST` najwyższego poziomu – to okno podważa poleganie na samym `Lax`.
- **`Strict` utrudnia korzystanie z linków przychodzących.** Blokuje wysyłkę międzywitrynową, ale wylogowuje użytkownika wchodzącego z linku, więc aplikacje często łączą ciasteczko akcji `Strict` z osobnym ciasteczkiem do odczytu.
- **Typ treści JSON pomaga, o ile jest wymuszony.** Treść z `Content-Type: application/json` wymusza preflight CORS, którego formularz HTML nie wyśle. Ale jeśli serwer przyjmuje też treści formularzowe lub `text/plain`, formularz wyśle „proste żądanie” bez preflightu – podatne. Wymuś typ treści i odrzucaj pozostałe.
- **CORS to osobna kontrola.** Zbyt luźna polityka CORS (odbijanie `Origin` z poświadczeniami) umożliwia odczyt międzydomenowy, a nie CSRF – to dwa różne mechanizmy.

## Pułapki double-submit

Naiwny double-submit (wartość ciasteczka musi równać się tokenowi z treści) zakłada, że atakujący nie ustawi ciasteczka. To założenie upada, gdy siostrzana subdomena lub MITM na ciasteczku bez HTTPS podstawi wybraną wartość do ciasteczka i wyśle pasujący token – kontrola przejdzie. Wzmocnienie:

- wiąż token z sesją przez podpis (HMAC / podpisany double-submit), a nie samą losową wartość,
- ustaw ciasteczko z prefiksem `__Host-`, aby siostrzane subdomeny nie mogły go nadpisać,
- tam, gdzie można trzymać stan po stronie serwera, wybieraj stanowy token synchronizujący.

## Jak testować

1. W historii proxy filtruj żądania zmieniające stan (`POST`, `PUT`, `DELETE` i `GET` wykonujące akcje). Wytypuj krytyczne: zmiana hasła, danych, uprawnień.
2. Sprawdź, czy jest token (`csrf`, `_token`, `authenticity_token`) i gdzie: w treści `POST` (najlepiej), w nagłówku, czy w URL (źle, wycieka w logach).
3. Sprawdź nagłówek `Set-Cookie`: `SameSite=Strict` niemal wyklucza CSRF, `Lax` ogranicza (ale patrz GET i okno ulgi), brak atrybutu to najwyższe ryzyko.
4. W Repeaterze testuj token:
    - usuń parametr z tokenem,
    - zostaw pusty (`csrf=`),
    - zmień jeden znak,
    - podstaw token z innej sesji (najczęstszy błąd: serwer sprawdza poprawność, ale nie przypisanie do sesji),
    - zmień metodę z `POST` na `GET` (verb tampering),
    - zmień `Content-Type` na `text/plain` lub formularzowy, aby sprawdzić, czy treść bez preflightu zostanie przyjęta.
5. Jeśli któryś test przeszedł, zbuduj minimalny PoC (`csrf.html` z formularzem wysyłanym automatycznie) i otwórz go w przeglądarce zalogowanej jako ofiara (własne konto testowe).

!!! tip "XSS omija CSRF"
    XSS pokonuje każdą ochronę przed CSRF: skrypt działa w tym samym originie, więc pobierze stronę z formularzem, odczyta token z HTML lub odpowiedzi i wyśle żądanie, a przeglądarka sama dołączy ciasteczko sesyjne. `HttpOnly` tu nie pomaga. Dlatego XSS i CSRF rozpatruje się razem.

!!! warning "Login CSRF"
    CSRF działa też na formularzu logowania: wymusza zalogowanie przeglądarki ofiary na konto atakującego, więc późniejsze działania ofiary trafiają na to konto. Chroń formularz logowania również tokenem anty-CSRF.

## Rekomendacje

- Token anty-CSRF związany z sesją dla każdej akcji zmieniającej stan.
- Ciasteczka sesyjne z `SameSite=Lax` lub `Strict` oraz `HttpOnly` i `Secure`; traktuj SameSite jako jedną warstwę, nie całość ochrony.
- Nigdy nie zmieniaj stanu metodą `GET`; w API wymuszaj typ treści JSON.
- Odrzucanie międzywitrynowych żądań zmieniających stan na podstawie nagłówków Fetch Metadata (`Sec-Fetch-Site`).
- Dla operacji krytycznych dodatkowe potwierdzenie tożsamości.
