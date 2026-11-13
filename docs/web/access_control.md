---
description: "Broken Access Control i IDOR: eskalacja pozioma i pionowa, BOLA i BFLA, mass assignment i testowanie uprawnień do obiektów oraz zabezpieczenia serwerowe."
---

# Kontrola dostępu i IDOR

**Broken Access Control (BAC)** to błąd, w którym aplikacja pozwala użytkownikowi na dostęp do danych lub funkcji, do których nie ma uprawnień. **IDOR (Insecure Direct Object Reference)** to szczególny przypadek: obiekt jest wskazywany identyfikatorem (np. `id=124`), a serwer wydaje go bez sprawdzenia, czy należy do zalogowanego użytkownika. To kategoria **A01** OWASP Top 10, a ta sama klasa błędów otwiera OWASP API Security Top 10 jako **BOLA**.

## Rodzaje

| Rodzaj | Opis | Przykład |
|---|---|---|
| **Eskalacja pozioma** | dostęp do zasobu innego użytkownika o tej samej roli | `GET /invoice/124` zwraca cudzą fakturę |
| **Eskalacja pionowa** | uzyskanie wyższych uprawnień | zwykły użytkownik wywołuje `POST /admin/deleteUser` |
| **Manipulacja parametrem** | zmiana wartości biznesowej przyjmowanej na zaufanie od klienta | `price=1`, `role=admin`, `isAdmin=true` |

## BOLA, BFLA i mass assignment

W testach API te same błędy mają precyzyjniejsze nazwy. Wiedza, na której warstwie brakuje kontroli, wskazuje, gdzie ją naprawić.

| Termin | Warstwa | Odpowiednik | Przykład |
|---|---|---|---|
| **BOLA** (Broken Object Level Authorization) | instancja obiektu | IDOR (eskalacja pozioma) | `GET /api/orders/1001` zwraca zamówienie innego najemcy (tenanta) |
| **BFLA** (Broken Function Level Authorization) | funkcja / endpoint | eskalacja pionowa | użytkownik wywołuje `DELETE /api/admin/users/5` |
| **Mass assignment** (część BOPLA, obok nadmiernej ekspozycji danych) | właściwość obiektu | manipulacja parametrem | treść żądania ustawia `"role":"admin"` na własnym koncie |

**Mass assignment** występuje, gdy serwer wiąże treść żądania wprost z modelem danych, więc klient może ustawić właściwości, których nie powinien kontrolować:

```
PATCH /api/users/me
{ "displayName": "Alice", "role": "admin", "emailVerified": true }
```

Jeśli `role` i `emailVerified` są wiązane automatycznie, użytkownik podnosi uprawnienia własnego konta. Obrona: wiązać tylko jawną listę dozwolonych pól (DTO / schemat wejścia), nigdy całego obiektu żądania, a pola uprzywilejowane ustawiać po stronie serwera.

## Kiedy występuje

- Identyfikator obiektu pochodzi wprost od klienta i nie jest wiązany z sesją.
- Funkcja administracyjna jest ukryta tylko w interfejsie, ale endpoint działa dla każdego (BFLA).
- Serwer ufa polom przesłanym przez przeglądarkę (`role`, `price`, `discount`), zamiast liczyć je samodzielnie.
- Treść żądania jest wiązana z modelem bez listy dozwolonych pól, więc przyjmowane są dodatkowe właściwości (mass assignment).
- API przyjmuje akcję (`action=delete&id=10`) bez sprawdzenia uprawnień.

## Kiedy aplikacja jest bezpieczna

- Dla każdego żądania serwer sprawdza, czy zalogowany użytkownik ma prawo do **konkretnego** obiektu, a nie tylko czy jest zalogowany.
- Wartości biznesowe (ceny, rabaty, role) są liczone i pobierane po stronie serwera.
- Treść żądania wiąże tylko dozwolone pola; właściwości uprzywilejowane przesłane przez klienta są ignorowane.
- Domyślna odmowa: brak reguły zezwalającej oznacza brak dostępu.
- Identyfikatory trudne do zgadnięcia (UUID) utrudniają atak, ale **nie zastępują** kontroli uprawnień.

## Jak testować

1. Zaloguj się jako użytkownik A i znajdź żądanie do zasobu (np. `GET /api/orders/1001`).
2. Wyślij je do Repeatera i zmień tylko identyfikator na sąsiedni lub należący do użytkownika B (BOLA / pozioma).
3. Porównaj odpowiedzi (moduł Comparer). Czerwone flagi:
    - `200 OK` z cudzymi danymi,
    - `302` do logowania, ale w treści odpowiedzi wciąż są dane,
    - stały `200` z „miękkim” błędem (`{"error":"not allowed"}`), który interfejs ukrywa.
4. Dla eskalacji pionowej / BFLA weź żądanie administratora i powtórz je z sesją zwykłego użytkownika oraz przetestuj zmianę metody (np. `GET`→`POST`). Akcje niszczące (usuwanie, zmiana danych) testuj wyłącznie na obiektach utworzonych przez siebie.
5. Dla manipulacji parametrem zmień jedno pole (`price`, `role`); dla mass assignment dodaj pole, którego formularz nigdy nie wysyła (`"role":"admin"`), i sprawdź, czy serwer je przyjął (wraca w odpowiedzi lub zmienia stan).

!!! example "Z laboratorium"
    W aplikacji CRM żądanie `POST /products` z `action=delete&id=10` usuwało produkt, choć interfejs zwykłego użytkownika nie miał takiej opcji. Backend nie sprawdzał roli: naraz brak kontroli uprawnień na poziomie funkcji i zaufanie do parametru.

## Rekomendacje

- Sprawdzaj uprawnienia do obiektu na serwerze, przy każdym żądaniu, w jednym wspólnym mechanizmie (centralna warstwa autoryzacji).
- Nie ufaj żadnej wartości z klienta, która wpływa na uprawnienia lub cenę.
- Wiąż tylko dozwolone pola wejścia; właściwości uprzywilejowane pozostają pod kontrolą serwera.
- Stosuj zasadę najmniejszych uprawnień: każda rola i konto dostaje tylko dostęp niezbędny do swoich zadań.
- Testy automatyczne: ten sam zestaw żądań dla różnych ról powinien dawać różne wyniki.
