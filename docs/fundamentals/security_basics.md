---
description: "Podstawowe pojęcia bezpieczeństwa: triada CIA, uwierzytelnianie i autoryzacja, zagrożenie, podatność i ryzyko, szyfrowanie, hashowanie i kodowanie."
---

# Pojęcia bezpieczeństwa

## Triada CIA

| Cecha | Znaczenie | Przykład naruszenia |
|---|---|---|
| **Poufność** (confidentiality) | dane widzą tylko uprawnione osoby | wyciek bazy klientów, odczyt cudzej faktury przez IDOR |
| **Integralność** (integrity) | dane nie są zmieniane bez uprawnień | zmiana ceny w koszyku, podmiana treści strony |
| **Dostępność** (availability) | system działa, gdy jest potrzebny | atak DDoS, ransomware szyfrujący serwer |

Raport z testów ocenia każdą podatność właśnie przez jej wpływ na poufność, integralność i dostępność danych.

## Identyfikacja, uwierzytelnianie, autoryzacja

| Etap | Pytanie | Przykład |
|---|---|---|
| **Identyfikacja** | kim się deklarujesz? | podanie loginu |
| **Uwierzytelnianie** | czy to naprawdę ty? | hasło, klucz sprzętowy, kod MFA |
| **Autoryzacja** | co wolno ci zrobić? | rola `admin` może usuwać konta, rola `user` nie |
| **Rozliczalność** (accounting) | co faktycznie zrobiłeś? | wpisy w logach: kto, kiedy, jaka akcja |

Uwierzytelnianie, autoryzacja i rozliczalność bywają nazywane modelem **AAA** (authentication, authorization, accounting); identyfikacja je poprzedza. Uwaga: identyfikacja to tylko deklaracja tożsamości, a uwierzytelnianie dopiero ją potwierdza.

Większość krytycznych błędów webowych to błędy autoryzacji: aplikacja poprawnie sprawdza, *kto* wysłał żądanie, ale nie sprawdza, *czy wolno mu* to zrobić ([Kontrola dostępu i IDOR](../web/access_control.md)).

## Zagrożenie, podatność, ryzyko

- **Podatność** (vulnerability): słabość systemu, np. brak walidacji parametru.
- **Zagrożenie** (threat): ktoś lub coś, co może tę słabość wykorzystać, np. atakujący z internetu.
- **Exploit**: sposób wykorzystania podatności.
- **Ryzyko**: prawdopodobieństwo wykorzystania podatności w połączeniu ze skutkami.

Podatność bez realnego zagrożenia (np. wymagająca fizycznego dostępu do serwerowni) ma niskie ryzyko; łatwa do wykorzystania z internetu i dająca dostęp do danych ma ryzyko krytyczne.

## Szyfrowanie, hashowanie, kodowanie

Trzy często mylone operacje na danych:

| Operacja | Odwracalna? | Klucz | Do czego służy |
|---|---|---|---|
| **Kodowanie** (encoding) | tak, bez klucza | nie | zmiana reprezentacji danych (Base64, URL-encoding, hex); nie chroni poufności |
| **Hashowanie** (funkcja skrótu) | nie (jednokierunkowe) | nie (opcjonalnie sól) | integralność i przechowywanie haseł; skrót o stałej długości |
| **Szyfrowanie** (encryption) | tak, kluczem | tak | poufność danych |

Typowy błąd to „zabezpieczyłem hasło przez Base64” – to tylko kodowanie, każdy może je odwrócić. Hasła przechowuje się jako skrót z solą i wolną funkcją (bcrypt, scrypt, Argon2), a nie zwykłym SHA. Szyfrowanie wymaga klucza i daje się odwrócić; dobrego skrótu nie da się odwrócić.

Samo szyfrowanie dzieli się na:

- **Symetryczne**: ten sam klucz szyfruje i odszyfrowuje (np. AES). Szybkie, ale obie strony muszą najpierw bezpiecznie uzgodnić wspólny klucz.
- **Asymetryczne**: para kluczy – publiczny i prywatny (np. RSA, ECC). Wolniejsze; używane do uzgodnienia klucza sesji i do podpisów cyfrowych. To, co zaszyfruje klucz publiczny, odszyfruje tylko odpowiadający mu prywatny.

W HTTPS obie techniki się łączą: kryptografia asymetryczna uwierzytelnia serwer i pozwala uzgodnić klucz, a sam ruch szyfruje szybki szyfr symetryczny. W TLS 1.3 klucz uzgadnia się wyłącznie przez (EC)DHE, a RSA lub ECDSA służą już tylko do podpisu (uwierzytelnienia serwera).

## Zasady projektowania

- **Obrona w głąb** (defense in depth): kilka niezależnych warstw zabezpieczeń, np. walidacja wejścia, zapytania parametryzowane, WAF i minimalne uprawnienia konta bazy danych.
- **Najmniejsze uprawnienia** (least privilege): użytkownik, usługa i proces dostają tylko te prawa, których potrzebują.
- **Domyślna odmowa** (default deny): wszystko, co nie jest wprost dozwolone, jest zabronione (tak działają listy ACL i listy dozwolonych).
- **Brak zaufania do klienta**: wszystko, co przychodzi z przeglądarki (parametry, nagłówki, ciasteczka, ukryte pola), może zostać zmienione. Interfejs może coś blokować, ale decyduje serwer.
- **Bezpieczne ustawienia domyślne**: brak domyślnych haseł, wyłączone konta testowe, wyłączony tryb debugowania.

## Strony w bezpieczeństwie

| Zespół | Zadanie |
|---|---|
| **Red team, pentesterzy** | szukają i potwierdzają podatności, symulują atakującego w uzgodnionym zakresie |
| **Blue team, SOC** | monitorują, wykrywają i obsługują incydenty, utrzymują zabezpieczenia |
| **Purple team** | wspólne ćwiczenia: atak jest od razu porównywany z tym, co wykryła obrona |
