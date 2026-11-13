---
description: "Bezpieczeństwo Wi-Fi: słabości WEP, WPA2 i handshake, KRACK, WPA3 SAE i tryb przejściowy, ochrona ramek zarządzania, evil twin i deauth oraz audyt."
---

# Sieci bezprzewodowe

Sieć bezprzewodowa jest trudniejsza do zabezpieczenia niż przewodowa, bo medium (fale radiowe) jest dostępne dla każdego w zasięgu. Nie da się ograniczyć dostępu do medium kablem ani portem przełącznika, dlatego kluczowe są silne szyfrowanie warstwy łącza i kontrola dostępu.

## Standardy szyfrowania

| Standard | Stan | Uwagi |
|---|---|---|
| **WEP** | złamany | szyfr strumieniowy RC4 i krótkie, powtarzające się wektory inicjujące (IV); klucz można odtworzyć w ciągu kilku minut z przechwyconego ruchu. Nie wolno używać |
| **WPA/TKIP** | przestarzały | TKIP jako poprawka dla sprzętu z epoki WEP; znane ataki, wycofywany |
| **WPA2** | powszechny | AES-CCMP; silny szyfr, ale PSK jest podatny na atak słownikowy offline po przechwyceniu 4-way handshake lub PMKID |
| **WPA3** | zalecany | wymiana kluczy SAE (dragonfly) z forward secrecy; odporność na atak słownikowy offline i obowiązkowa ochrona ramek zarządzania |

!!! note "PSK a Enterprise"
    Tryb **Personal (PSK)** współdzieli jedno hasło dla całej sieci. Tryb **Enterprise (802.1X/EAP)** uwierzytelnia każdego użytkownika osobno wobec serwera RADIUS, co daje indywidualne poświadczenia, odwoływanie dostępu i lepsze logowanie. W środowisku firmowym preferuj Enterprise.

## WPA2: handshake i KRACK

Bezpieczeństwo WPA2-PSK opiera się na **4-way handshake** (czteroetapowym uzgadnianiu kluczy), który z hasła (PSK) wyprowadza klucze sesyjne między klientem a punktem dostępowym.

- **Atak słownikowy offline.** Przechwycenie uzgadniania (wystarczą ramki wymieniane przy dołączaniu klienta) pozwala **lokalnie** testować kandydatów na hasło bez kontaktu z siecią. Od 2018 znany jest też atak na **PMKID**: identyfikator wyliczany z hasła można pobrać z samego punktu dostępowego, bez żadnego podłączonego klienta i bez deauth. Słabe lub słownikowe PSK szybko padają. Obrona: długie, losowe hasło (frazy) oraz WPA3, gdzie taki atak offline jest niemożliwy.
- **KRACK (Key Reinstallation Attack).** Błąd w samym protokole handshake: napastnik zmusza stronę do **ponownej instalacji już używanego klucza**, co zeruje liczniki nonce/replay i umożliwia odtwarzanie oraz częściowe odszyfrowanie ramek. Nie wymaga znajomości hasła. Obrona: aktualizacje klientów i punktów dostępowych.

## WPA3: SAE i tryb przejściowy

WPA3 zastępuje wyprowadzanie klucza z PSK wymianą **SAE (Simultaneous Authentication of Equals)**, opartą na uzgadnianiu dragonfly.

- **Odporność na atak offline.** Każda próba zgadnięcia hasła wymaga interakcji z siecią, więc nie da się testować kandydatów na podstawie samego przechwyconego ruchu. Daje też **forward secrecy**: kompromitacja hasła nie odszyfrowuje wcześniej nagranych sesji.
- **Tryb przejściowy (transition mode).** Sieć ogłaszająca jednocześnie WPA3 i WPA2 dla zgodności ze starszymi klientami może zostać **zdegradowana**: napastnik nakłania klienta do połączenia w WPA2 i odtwarza klasyczny atak na uzgadnianie. W tym trybie PMF jest dla klientów WPA2 tylko opcjonalny. Gdy to możliwe, wymuszaj **WPA3-only** dla wrażliwych sieci.
- **Dragonblood.** Rodzina ataków (bocznokanałowych i downgrade) na wczesne implementacje SAE; łagodzona aktualizacjami oprogramowania układowego (firmware) i wariantem **SAE Hash-to-Element (H2E)**, obowiązkowym w paśmie 6 GHz (Wi-Fi 6E).

## Ochrona ramek zarządzania (PMF / 802.11w)

W klasycznym Wi-Fi ramki zarządzania (m.in. **deauthentication** i disassociation) nie są uwierzytelniane, więc każdy w zasięgu może je sfałszować. Stąd ataki **deauth**: podrobione ramki wyrzucają klientów z sieci, co służy do zakłócania usługi (DoS) albo do wymuszenia ponownego połączenia i przechwycenia uzgadniania.

**802.11w (Protected Management Frames, PMF)** kryptograficznie chroni krytyczne ramki zarządzania i blokuje sfałszowane deauth. PMF jest **obowiązkowy w WPA3** i opcjonalny w WPA2: włącz go wszędzie, gdzie sprzęt na to pozwala.

## Zagrożenia

- **Podsłuch (eavesdropping)**: przy słabym szyfrowaniu lub jego braku ruch można biernie przechwycić z powietrza.
- **Rogue AP a evil twin**: *rogue AP* to nieautoryzowany punkt dostępowy podpięty do sieci (np. przyniesiony przez pracownika), omijający kontrolę brzegu. *Evil twin* to AP podszywający się pod zaufany SSID, by skłonić ofiary do połączenia i prowadzić MITM lub phishing (fałszywy portal logowania).
- **Deauth / zakłócanie**: nadużycie ramek zarządzania do wyrzucania klientów (patrz PMF powyżej). Nawet we własnym audycie ogranicza się deauth do własnych klientów testowych; zakłócanie cudzych urządzeń w zasięgu jest niezgodne z prawem.
- **Ataki na AP i router**: domyślne hasła administracyjne, nieaktualne oprogramowanie, odsłonięty panel zarządzania, WPS (PIN można odgadnąć metodą siłową lub atakiem Pixie Dust).
- **Phishing i spoofing**: fałszywe portale i brak świadomości użytkowników.

## Audyt sieci bezprzewodowej

Audyt prowadzi się wyłącznie na własnej sieci lub za pisemną zgodą właściciela. Typowy przebieg:

1. **Inwentaryzacja**: punkty dostępowe, standardy szyfrowania i tryby (PSK/Enterprise, PMF), router, przełączniki, urządzenia końcowe.
2. **Identyfikacja słabości**: WEP/WPA-TKIP, tryb przejściowy WPA3, brak PMF, domyślne hasła, włączony WPS, brak segmentacji (VLAN), brak firewalla, nieaktualne oprogramowanie, brak polityk.
3. **Zagrożenia**: zewnętrzne (podsłuch, evil twin, MITM, deauth) i wewnętrzne (rogue AP, nieautoryzowany dostęp, malware, utrata danych).
4. **Rekomendacje modernizacji** z priorytetami.

## Rekomendacje

- Migracja z WEP/WPA-TKIP na **WPA3** (lub co najmniej WPA2-AES z długim, losowym hasłem); dla wrażliwych sieci WPA3-only, bez trybu przejściowego.
- Włącz **PMF (802.11w)** i wyłącz WPS.
- W firmie stosuj **WPA2/WPA3-Enterprise (802.1X)** zamiast współdzielonego PSK.
- Zmiana domyślnych haseł i regularne aktualizacje oprogramowania urządzeń.
- Osobne sieci dla pracowników, gości i systemów krytycznych (VLAN, osobne SSID); dla gości zamiast otwartej sieci **OWE (Wi-Fi Enhanced Open)**, które szyfruje ruch bez hasła.
- Silne uwierzytelnianie (MFA), dostęp na podstawie roli, firewall i IDS/IPS z wykrywaniem rogue AP.
- Szkolenia użytkowników i polityka korzystania z urządzeń mobilnych (BYOD).
