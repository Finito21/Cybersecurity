---
description: "OSINT: biały wywiad w praktyce, higiena wyszukiwania, dorki, metadane, wycieki, geolokalizacja zdjęć, recon techniczny oraz etyka i prawo."
---

# OSINT

**OSINT (Open-Source Intelligence)** to zbieranie informacji z jawnych, publicznie dostępnych źródeł. W bezpieczeństwie służy do rozpoznania (recon) przed testem oraz do oceny, ile organizacja ujawnia o sobie na zewnątrz. Zasada przewodnia: najpierw hipoteza, potem najkrótsza ścieżka weryfikacji, a dowody (link, zrzut, data) zbiera się od razu.

!!! warning "Etyka i prawo"
    OSINT korzysta ze źródeł jawnych, ale „jawne” nie znaczy „wolno wszystko”. Pracuj w granicach zgody na test i uzgodnionego zakresu, z jasnym celem i zgodnie z przepisami (m.in. RODO, a przy uporczywym śledzeniu lub podszywaniu się pod kogoś art. 190a Kodeksu karnego). Celuj w powierzchnię organizacji, nie w prywatne osoby: profilowanie konkretnych ludzi, ustalanie ich miejsca pobytu, publiczne kamery czy dane wrażliwe z rejestrów szybko prowadzą do naruszenia prywatności i prawa. Tam kończy się recon.

## Higiena wyszukiwania (OPSEC)

- Nie loguj się do kont, jeśli nie trzeba; oddziel tożsamość roboczą (osobny profil, kontener, przeglądarka).
- Wyniki zależą od lokalizacji, sieci i VPN; porównuj je, aby sprawdzić ich spójność.
- Zapisuj źródła natychmiast: link, znacznik czasu, co dany dowód potwierdza.

## Dorki wyszukiwarki

Operatorów jest wiele, ale w praktyce liczy się kilka, używanych dobrze:

```text
site:example.com                          # zakres do domeny (razem z subdomenami)
site:example.com -site:www.example.com    # subdomeny inne niż www
site:example.com filetype:pdf (confidential OR internal)  # dokumenty, które nie powinny być publiczne
site:example.com intitle:"index of"       # otwarte katalogi
```

Jeden dork i „nic nie ma” to nie wynik: sprawdza się warianty (synonimy, języki, formaty, starsze wersje). Google wycofał operator `cache:` w 2024, więc starsze wersje stron sprawdza się w Wayback Machine lub archive.today.

## Metadane

Metadane to cicha warstwa, która zdradza za dużo: autor i organizacja (Office, PDF), nazwy użytkowników i ścieżki, wersje narzędzi, a w zdjęciach czasem współrzędne GPS. Narzędzia: **exiftool** (szybki podgląd metadanych), FOCA (masowo dla dokumentów organizacji), Maltego i Recon-ng (łączenie encji i wizualizacja relacji).

## Wycieki i hasła

Do oceny ryzyka (legalnie i defensywnie): **Have I Been Pwned** (czy e-mail pojawił się w wyciekach; wyszukiwanie dla całej domeny wymaga potwierdzenia, że się nią zarządza). Zasada: wyciek to artefakt do potwierdzenia innymi źródłami, a nie prawda sama w sobie. Nie pobiera się zrzutów baz z wycieków i nie testuje znalezionych haseł na żadnym systemie.

## Geolokalizacja obrazu (GEOINT)

Tylko dla zdjęć objętych zakresem testu (materiały organizacji) lub zadań szkoleniowych; nigdy w celu ustalenia, gdzie przebywa osoba prywatna.

1. **Wyszukiwanie obrazem (reverse image search)** w kilku silnikach (Google, Yandex, Bing, TinEye): różne radzą sobie z różnymi obrazami.
2. Wyszukaj „kotwice”: znaki, język, architektura, roślinność, numery, układ dróg.
3. Mapy i Street View / Mapillary do dopasowania detali.
4. Cień i słońce (SunCalc, ShadowMap) dają godzinę, archiwa pogody potwierdzają dzień.
5. Dokumentuj dowody (zrzuty, linki, daty). Zaczynaj od kotwic, nie od „zgaduję kraj”.

## Recon techniczny

Nadal chodzi o informacje jawne, ale techniczne. Warto rozdzielić dwa tryby:

- **Pasywny** (bez bezpośredniego kontaktu z celem): **Shodan** (usługi i urządzenia widoczne z internetu), **crt.sh** (subdomeny z Certificate Transparency), **VirusTotal** (reputacja domen i plików). **theHarvester** agreguje adresy e-mail, subdomeny i hosty głównie z takich źródeł.
- **Aktywny** (żądania trafiają do celu): enumeracja zasobów serwera WWW narzędziami **feroxbuster / ffuf**. To już bezpośrednie odpytywanie serwera, więc wymaga zgody i mieszczenia się w zakresie testu.

!!! tip "VirusTotal a poufność"
    Pliki wgrane do VirusTotal mogą pobrać płatni subskrybenci, a właściciel próbki widzi, że ją przesłano. Szukaj po skrócie (hash), adresie URL lub domenie; nigdy nie wgrywaj dokumentów klienta ani plików wewnętrznych.

## Rekomendacje (dla obrońcy)

- Sprawdź, co organizacja ujawnia: metadane w dokumentach, otwarte katalogi, subdomeny, wystawione usługi.
- Czyść metadane przed publikacją plików.
- Monitoruj wycieki powiązane z domeną i egzekwuj politykę haseł oraz MFA.
