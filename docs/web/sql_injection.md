---
description: "SQL Injection: na czym polega, warianty union, error, boolean i time-based, testowanie w Burpie oraz obrona przez zapytania parametryzowane."
---

# SQL Injection

**SQL Injection (SQLi)** to podatność, w której dane od użytkownika trafiają do zapytania SQL i są interpretowane jako część polecenia, a nie jako zwykły tekst. Atakujący może odczytać lub zmienić dane, ominąć logowanie, a czasem wykonać polecenia systemowe. To część kategorii **A05 Injection** (OWASP Top 10 2025).

## Kiedy występuje

Wszędzie tam, gdzie dane od użytkownika (parametry URL, pola formularzy, nagłówki, ciasteczka, JSON/XML) są wstawiane do zapytania przez sklejanie tekstu zamiast parametryzacji. Dotyczy to też klauzul `ORDER BY`, `LIMIT` i nazw kolumn, które bywają budowane dynamicznie. Obrona oparta na escapowaniu (np. `addslashes`) bywa obchodzona przy niezgodności kodowania znaków między aplikacją a bazą (znaki wielobajtowe, np. GBK); zapytań parametryzowanych to nie dotyczy.

## Kiedy aplikacja jest bezpieczna

- **Zapytania parametryzowane** (prepared statements): zapytanie jest zdefiniowane z góry, a dane idą osobno i nigdy nie są wykonywane jako kod. To podstawowa i najważniejsza obrona.
- Silne typowanie: pole oczekujące liczby odrzuca wszystko inne.
- Minimalne uprawnienia konta bazy (osobne konto tylko do odczytu tam, gdzie wystarczy).
- Poprawna i spójna obsługa kodowania znaków.

## Warianty i jak testować

Najpierw sprawdź, czy parametr wpływa na zapytanie: dopisz pojedynczy apostrof (`'`) i obserwuj błąd składni, kod 500 lub zmianę treści. Dla parametru liczbowego porównaj `id=10` z `id=11-1`: ta sama odpowiedź sugeruje SQLi.

| Wariant | Kiedy | Jak potwierdzić |
|---|---|---|
| **Union-based** | wynik zapytania widać na stronie | `ORDER BY n` ustala liczbę kolumn, `UNION SELECT` dokłada własne dane |
| **Error-based** | aplikacja pokazuje błędy bazy | funkcja wymuszająca błąd zawierający wynik podzapytania |
| **Boolean-based (blind)** | brak błędów i danych, ale strona reaguje inaczej | porównanie `AND 1=1` i `AND 1=2` |
| **Time-based (blind)** | brak widocznej różnicy | opóźnienie po stronie bazy i pomiar czasu odpowiedzi |

```text
' ORDER BY 3-- -           # ustalenie liczby kolumn
' UNION SELECT NULL,version(),NULL-- -   # test ekstrakcji
1' AND 1=1-- -   vs   1' AND 1=2-- -     # boolean-based
```

!!! note "Składnia zależy od bazy"
    W MySQL `--` zaczyna komentarz tylko wtedy, gdy po nim jest spacja, stąd `-- -` (albo `#`, w URL `%23`). Wersję bazy zwraca `version()` w MySQL i PostgreSQL, `@@version` w MSSQL, a w Oracle `SELECT banner FROM v$version`; tam każde `UNION SELECT` wymaga też `FROM dual`.

W Burpie warianty testuje się w Repeaterze (jedna zmiana na raz) albo w Intruderze z listą payloadów. Do automatyzacji służy **sqlmap**, ale warto rozumieć, co robi.

!!! warning "Kod stanu i blind"
    Kod 500 po samym apostrofie to mocny sygnał. Przy blind SQLi liczy się różnica w długości lub czasie odpowiedzi, a nie sam kod stanu.

!!! warning "Czego nie da się sparametryzować"
    Parametry wiążą tylko wartości, nie nazwy obiektów. Nazwy tabel, kolumn czy kierunek `ORDER BY` nie mogą być przekazane jako parametry. Jeśli muszą pochodzić z wejścia, mapuj je przez listę dozwolonych wartości (allowlist), nigdy nie sklejaj z tekstem.

## SQLi drugiego rzędu (second-order)

W SQLi drugiego rzędu dane są bezpiecznie zapisywane w jednym miejscu, a wstrzyknięcie uruchamia się później, gdy inna funkcja wczytuje je z bazy i skleja z nowym zapytaniem bez parametryzacji. Przykład: nazwa użytkownika z apostrofem zapisana przy rejestracji, a później użyta dosłownie w zapytaniu przy zmianie hasła. Dlatego parametryzować trzeba każde zapytanie, także te operujące na danych już znajdujących się w bazie, a nie tylko na świeżym wejściu.

!!! note "Filtry i WAF to nie naprawa"
    Blokowanie słów kluczowych czy znaków bywa obchodzone (inne kodowanie, komentarze, warianty składni), dlatego WAF traktuj jako warstwę dodatkową, a nie jako właściwą obronę. Jedynym niezawodnym rozwiązaniem jest parametryzacja po stronie kodu.

## Rekomendacje

- Zapytania parametryzowane wszędzie, także w zapytaniach dynamicznych i raportach.
- ORM i konstruktory zapytań (query builders) pomagają, ale surowe zapytania (`raw`) i ręczna interpolacja w nich nadal są podatne.
- Procedury składowane nie chronią, jeśli wewnątrz budują dynamiczny SQL przez konkatenację.
- Walidacja typu i formatu danych wejściowych (lista dozwolonych wartości), zwłaszcza dla fragmentów, których nie da się przekazać jako parametr.
- Komunikaty błędów bez szczegółów bazy; szczegóły tylko do logów.
- Konto bazy z minimalnymi uprawnieniami.
