---
description: "Ataki DoS i DDoS: taksonomia wolumetryczna, protokolarna i aplikacyjna, amplifikacja i reflekcja, mechanika SYN flood, SYN cookies oraz obrona."
---

# Ataki DoS i DDoS

**DoS (Denial of Service)** to atak blokujący dostępność usługi. **DDoS (Distributed DoS)** używa wielu maszyn jednocześnie (często botnetu), przez co trudniej go odfiltrować i zablokować u źródła. Celem jest trzeci filar triady CIA: dostępność.

## Taksonomia ataków

| Kategoria | Cel | Przykłady |
|---|---|---|
| **Wolumetryczne** | wysycenie przepustowości łącza | UDP flood, ICMP flood, amplifikacja (DNS, NTP, memcached) |
| **Protokolarne (warstwa 3–4)** | wyczerpanie stanu (tablice połączeń, zapory, równoważniki obciążenia) | SYN flood, ping of death (zbyt duże pakiety), fragmentacja |
| **Aplikacyjne (warstwa 7)** | wyczerpanie zasobów serwera małym ruchem | HTTP flood, wolne żądania (Slowloris), kosztowne zapytania |

Ataki wolumetryczne mierzy się w bitach na sekundę (Gb/s) i wysycają łącze „od zewnątrz”, protokolarne w pakietach na sekundę, a aplikacyjne w żądaniach na sekundę. Ataki aplikacyjne bywają mało widoczne: niewielki, ale pozornie prawidłowy ruch (np. drogie zapytania do bazy lub wyszukiwarki) wyczerpuje CPU, pamięć albo pulę połączeń.

## Amplifikacja i reflekcja

Atak **reflekcyjny** wykorzystuje serwery pośredniczące: napastnik wysyła zapytania ze **sfałszowanym adresem źródłowym ofiary**, więc odpowiedzi trafiają do ofiary, a nie do niego. Gdy odpowiedź jest znacznie większa od zapytania, jest to **amplifikacja**: niewielki ruch napastnika zamienia się w ogromny strumień kierowany na ofiarę.

- Nadaje się do tego UDP, bo nie wymaga uzgodnienia połączenia (łatwo podrobić adres źródłowy).
- Nadużywane są **otwarte** usługi: resolwery DNS, serwery NTP (monlist), memcached. Współczynnik wzmocnienia wynosi od kilkudziesięciu (DNS) przez około 550 (NTP monlist) do dziesiątek tysięcy razy (memcached).
- Obrona systemowa: **nie wystawiaj otwartych resolwerów**, filtruj adresy źródłowe na brzegu (**BCP 38 / anti-spoofing**), aby nie dało się podszyć pod ofiarę.

## SYN flood i SYN cookies

SYN flood to klasyczny atak protokolarny na uzgadnianie TCP (three-way handshake).

1. Napastnik wysyła strumień pakietów **SYN** (zwykle ze sfałszowanym adresem źródłowym).
2. Serwer odpowiada **SYN-ACK** i rezerwuje stan dla **półotwartego** połączenia w kolejce (backlog), czekając na **ACK**.
3. ACK nigdy nie nadchodzi. Kolejka półotwartych połączeń zapełnia się, a serwer **odrzuca nowe, prawidłowe połączenia**.

**SYN cookies** neutralizują ten atak: zamiast rezerwować pamięć dla każdego SYN, serwer koduje stan połączenia w numerze sekwencyjnym wysyłanym w SYN-ACK. Dopiero gdy wróci poprawny ACK (z odtworzonym „ciasteczkiem”), stan jest tworzony. Dzięki temu backlog się nie przepełnia. W Linuksie włącza je `net.ipv4.tcp_syncookies = 1` (zwykle domyślnie), a kolejkę ustawia `net.ipv4.tcp_max_syn_backlog`. Uzupełniająco pomagają krótsze limity czasu (timeouty) półotwartych połączeń i filtrowanie na brzegu. Atak widać jako gwałtowny wzrost liczby połączeń w stanie `SYN-RECV` (`ss -s`, `ss -tan state syn-recv`).

!!! warning "Tylko w autoryzowanym środowisku"
    Mechanika ataków i narzędzia generujące ruch (np. `hping3`) opisano wyłącznie dla zrozumienia działania i testów we **własnym, odizolowanym** środowisku lub za pisemną zgodą. Przeprowadzenie ataku DoS na cudzy system jest przestępstwem (w Polsce m.in. art. 268a i 269a Kodeksu karnego).

## Ograniczanie skutków (obrona)

Obrona działa warstwowo: inne środki na zalew wolumetryczny, inne na warstwę aplikacji.

- **Rate limiting** i ograniczanie liczby połączeń na klienta (patrz [NGINX](../defense/nginx_hardening.md)); dla warstwy 7 także limity na kosztowne endpointy i wczesne odrzucanie wolnych żądań.
- **Ochrona u dostawcy / scrubbing**: ruch wolumetryczny trzeba pochłonąć **powyżej** własnego łącza: u dostawcy łączności, w centrum czyszczenia (scrubbing) lub w CDN z anycastem. Lokalna zapora nie pomoże, gdy wysycone jest samo łącze.
- **SYN cookies** i utwardzenie (hardening) stosu sieciowego przeciw atakom typu flood na protokoły.
- **Anti-spoofing (BCP 38)** i brak otwartych resolwerów DNS i serwerów NTP, aby nie zasilać ataków amplifikacyjnych.
- **Skalowanie i nadmiarowość** (redundancja, klastry), aby pochłonąć skoki ruchu; pojedyncza instancja pada szybciej niż klaster.
- **Monitoring i alerty**: nagły wzrost ruchu, nietypowe wzorce, wyczerpanie zasobów i pul połączeń.

## Rekomendacje

- Wdróż limity żądań i połączeń oraz ochronę anty-DDoS odpowiednią do ekspozycji usługi (upstream/CDN dla ruchu wolumetrycznego).
- Włącz SYN cookies i anti-spoofing; zamknij otwarte resolwery.
- Przygotuj plan reakcji na incydent (kontakt z dostawcą, procedury przekierowania i czyszczenia ruchu).
- Testuj wydajność i progi alarmowe, zanim zrobi to atakujący.
