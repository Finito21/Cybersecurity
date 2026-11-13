---
description: "Path traversal, Local File Inclusion i upload plików: odczyt plików spoza katalogu, webshell, kodowanie ścieżek, bajt zerowy i walidacja po stronie serwera."
---

# Pliki i ścieżki

Trzy powiązane klasy błędów, w których aplikacja pracuje na ścieżkach lub plikach pochodzących od użytkownika: **path traversal**, **Local File Inclusion (LFI)** i niebezpieczny **upload plików**.

## Path traversal

Aplikacja skleja ścieżkę z parametrem bez normalizacji, więc sekwencją `../` można wyjść poza katalog bazowy i odczytać pliki systemowe.

```text
../../../etc/passwd                 # przejście względne
/etc/passwd                         # ścieżka bezwzględna
....//....//....//etc/passwd        # obejście filtra usuwającego ../
%2e%2e%2f  oraz  %252e%252e%252f    # kodowanie i podwójne kodowanie URL
..%c0%af  ..%ef%bc%8f               # nadmiarowe UTF-8 i ukośnik pełnej szerokości
filename=../../../etc/passwd%00.png # bajt zerowy, gdy wymagane jest rozszerzenie
```

Warto próbować różnych kodowań (Burp ma opcję automatycznego kodowania) i ścieżek Windows (`..\`, `C:\Windows\win.ini`).

!!! warning "Kolejność normalizacji ma znaczenie"
    Filtr, który usuwa `../` **raz** i przed zdekodowaniem wejścia, obchodzi się sekwencjami typu `....//` albo podwójnym kodowaniem (`%252e`) – po jego przejściu znów powstaje `../`. Bezpieczna kolejność jest zawsze ta sama: najpierw pełne zdekodowanie, potem kanonikalizacja ścieżki (rozwinięcie `.`, `..` i dowiązań symbolicznych), a dopiero na końcu sprawdzenie, że wynik mieści się w katalogu bazowym. Walidacja przed normalizacją nie daje żadnej gwarancji.

!!! note "Bajt zerowy to technika w większości historyczna"
    `%00` ucinał ścieżkę przed wymaganym rozszerzeniem na starszych środowiskach (np. PHP < 5.3.4 czy API plikowe oparte na łańcuchach C). Współczesne wersje języków odrzucają osadzony bajt zerowy lub obsługują go poprawnie, więc traktuj go jako wektor istotny tylko przy starych systemach, a nie jako pierwszy wybór.

## Local File Inclusion

Gdy aplikacja **dołącza** plik na podstawie parametru (`?module=network_tester.php`), atakujący może wskazać inny plik, a przy sprzyjających warunkach doprowadzić do wykonania kodu. Przykład z laboratorium: `include($_GET['module'])` w panelu routera pozwalał dołączyć dowolny plik.

## Upload plików

Niebezpieczny upload pozwala wgrać plik wykonywalny (webshell) lub plik prowadzący do stored XSS. Testowanie w Repeaterze: modyfikacja `filename`, `Content-Type` i zawartości żądania `multipart/form-data`.

Czerwone flagi: serwer akceptuje „dziwne” rozszerzenia, plik ląduje pod przewidywalnym URL, jedyną walidacją jest `Content-Type` (łatwy do podmiany).

### Walidacja typu: Content-Type kontra magic bytes

- **`Content-Type` z żądania** pochodzi od klienta i łatwo go podmienić – nie jest dowodem na rzeczywisty typ pliku.
- **Magic bytes (sygnatura)** to pierwsze bajty pliku (`FF D8 FF` JPEG, `89 50 4E 47` PNG, `25 50 44 46` PDF). Sprawdzenie ich jest mocniejsze niż `Content-Type`, ale wciąż nierozstrzygające: plik może mieć poprawną sygnaturę i mimo to zawierać kod.
- **Polyglot** to plik poprawny w dwóch formatach naraz – np. z poprawnym nagłówkiem obrazu, który jednocześnie jest poprawnym skryptem PHP. Sama kontrola sygnatury go przepuści.

!!! tip "O bezpieczeństwie decyduje sposób serwowania, nie samo rozpoznanie typu"
    Ponieważ zawartość da się sfałszować, kluczowe jest to, że katalog uploadu **nie wykonuje kodu** i serwuje pliki z wymuszonym, bezpiecznym typem oraz `X-Content-Type-Options: nosniff`. Walidacja typu to warstwa dodatkowa, a nie główna linia obrony.

## Kiedy aplikacja jest bezpieczna

- Dane użytkownika nie trafiają wprost do API systemu plików.
- Porównanie z listą dozwolonych wartości albo sprawdzenie, że wartość zawiera tylko dozwolone znaki, a potem doklejenie do katalogu bazowego, normalizacja i upewnienie się, że wynik wciąż zaczyna się od katalogu bazowego.
- Upload: walidacja typu po stronie serwera (nie tylko `Content-Type`), losowa nazwa, katalog bez prawa wykonywania, osobna domena na pliki użytkowników.

## Rekomendacje

- Unikaj przekazywania wejścia użytkownika do ścieżek; używaj identyfikatorów mapowanych na pliki po stronie serwera.
- Normalizuj i weryfikuj ścieżkę po złożeniu, nie tylko przed.
- Pliki od użytkowników trzymaj poza katalogiem aplikacji i serwuj bez interpretacji.
