---
description: "Cross-Site Scripting: typy reflected, stored i DOM-based, kontekst wstrzyknięcia, testowanie odbicia i filtrów oraz obrona przez kodowanie wyjścia i CSP."
---

# XSS

**Cross-Site Scripting (XSS)** to podatność, w której do przeglądarki innego użytkownika trafia złośliwy kod (najczęściej JavaScript) przez podatną aplikację. To atak na klienta, nie na serwer. Służy do kradzieży ciasteczek sesyjnych, podmiany treści, phishingu w obrębie strony lub wykonywania akcji w imieniu ofiary. Należy do kategorii **A05 Injection** (OWASP Top 10 2025).

## Typy

| Typ | Gdzie jest kod | Zasięg |
|---|---|---|
| **Reflected (odbity)** | w parametrze żądania, odbijany w odpowiedzi | ofiara musi kliknąć spreparowany link |
| **Stored (trwały)** | zapisany na serwerze (komentarz, profil) | uruchamia się u każdego, kto otworzy stronę |
| **DOM-based** | w JavaScript strony (np. zapis do `innerHTML`) | dane z URL lub `#` nigdy nie muszą dotrzeć do serwera |

## Kiedy występuje

Aplikacja pobiera dane od użytkownika i wyświetla je bez odpowiedniego zakodowania znaków specjalnych HTML (`<`, `>`, `"`, `'`, `&`) w danym kontekście.

## Kiedy aplikacja jest bezpieczna

- **Kodowanie wyjścia zależne od kontekstu** (contextual output encoding): `<` zamieniane na `&lt;` itd., inaczej w treści HTML, w atrybucie, w JS i w URL.
- Nowoczesne frameworki (React, Angular) domyślnie kodują dane, ale mają furtki: `dangerouslySetInnerHTML` i `href="javascript:..."` w React, `bypassSecurityTrust*` w Angularze.
- **Trusted Types** (`Content-Security-Policy: require-trusted-types-for 'script'`): przeglądarka odrzuca przypisanie zwykłego tekstu do niebezpiecznych ujść DOM (`innerHTML`), co jest główną współczesną obroną przed DOM XSS.
- **Content Security Policy** jako druga warstwa: blokuje skrypty inline i z nieznanych źródeł.
- Flaga `HttpOnly` na ciasteczkach sesyjnych: JavaScript ich nie odczyta, więc XSS nie ukradnie sesji wprost.

## Jak testować

1. Wpisz w parametr unikalny znacznik (np. `PENTEST123`) i sprawdź, czy wraca w odpowiedzi (punkt wejścia).
2. Wyślij znaki specjalne `< > " ' ( ) ;` i zobacz, jak wracają: dosłownie (podatne) czy jako encje `&lt; &gt;` (bezpieczne). Część może być filtrowana, a część nie.
3. Dobierz payload do kontekstu i potwierdź w przeglądarce (Show response in browser):

```html
<script>alert(1)</script>          <!-- treść HTML -->
"><svg onload=alert(1)>            <!-- wyjście z atrybutu -->
" onerror="alert(1)                 <!-- wnętrze tagu img -->
```

4. Dla stored XSS wyślij payload w formularzu (komentarz, profil) i odśwież stronę jako inny użytkownik.

!!! tip "Obserwacja ważniejsza niż payload"
    Najpierw ustal, czy i gdzie dane wracają oraz w jakim kontekście. Payload jest tylko potwierdzeniem hipotezy. `<b>test</b>`, które renderuje się jako pogrubienie, to już sygnał braku kodowania (HTML injection).

## Źródła i ujścia (sinks) DOM

W DOM-based XSS dane płyną ze **źródła** kontrolowanego przez atakującego do niebezpiecznego **sinku**, często bez udziału serwera. Audyt polega na prześledzeniu tej ścieżki w kodzie JavaScript.

- Typowe źródła: `location` (w tym `location.hash` i `location.search`), `document.referrer`, `window.name`, `postMessage`, dane z `localStorage`.
- Sinki renderujące HTML: `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write`, jQuery `.html()`.
- Sinki wykonujące kod: `eval`, `Function`, `setTimeout`/`setInterval` z argumentem tekstowym, przypisanie `javascript:` do `location` lub `src`.

Bezpieczne odpowiedniki: `textContent` zamiast `innerHTML`, `setAttribute` dla atrybutów, a przy koniecznym renderowaniu HTML – sanityzacja zaufaną biblioteką.

!!! warning "Mutation XSS (mXSS)"
    Przeglądarka potrafi „naprawić” niepoprawny HTML przy wczytaniu do `innerHTML`, zmieniając pozornie nieszkodliwy ciąg w działający payload już po sanityzacji. Dlatego używaj aktualnej wersji sprawdzonej biblioteki i sanityzuj dokładnie w tej formie, w jakiej dane trafią do DOM.

## Rekomendacje

- Koduj dane na wyjściu zależnie od kontekstu; nie polegaj na filtrowaniu wejścia.
- Wdróż CSP i flagę `HttpOnly`. CSP działa tylko dobrze skonfigurowana: `unsafe-inline` i zbyt szerokie źródła ją unieważniają, dlatego preferuj nonce lub hash.
- Unikaj niebezpiecznych sinków DOM; przypisuj dane przez `textContent` i `setAttribute`.
- Do czyszczenia HTML od użytkownika używaj sprawdzonej biblioteki (np. DOMPurify), nie własnych reguł.
