---
description: "Ataki w warstwie 2: zalewanie CAM, VLAN hopping, ochrona STP, DHCP snooping, DAI, IP Source Guard, port security oraz dostęp 802.1X i EAP."
---

# Bezpieczeństwo LAN

Ataki w warstwie 2 (przełączniki) są groźne, bo działają poniżej firewalli i routingu: host w tym samym segmencie może podsłuchiwać lub przekierowywać ruch, zanim dotrze on do zapory. Punktem wyjścia obrony jest kontrola, kto i jak podłącza się do sieci.

## Ataki na przełączniki

| Atak | Mechanizm | Obrona |
|---|---|---|
| **Zalewanie CAM (MAC flooding)** | zalanie tablicy adresów fałszywymi MAC; po przepełnieniu przełącznik działa jak koncentrator i rozsyła ramki na wszystkie porty (podsłuch) | **port security**: limit adresów MAC na porcie |
| **VLAN hopping (fałszywy trunk)** | atakujący udaje przełącznik i przez DTP negocjuje łącze trunk, uzyskując dostęp do wszystkich VLAN-ów | wyłączyć DTP (tryb access, `switchport nonegotiate`) |
| **VLAN hopping (double tagging)** | ramka z dwiema etykietami 802.1Q; pierwszą (równą natywnemu VLAN) przełącznik zdejmuje i przekazuje ramkę do innego VLAN | native VLAN jako nieużywany VLAN, nieprzypisany do portów dostępowych; tagowanie native VLAN (`vlan dot1q tag native`) |
| **Manipulacja STP** | fałszywe ramki BPDU czynią hosta atakującego mostem głównym, przez który przechodzi ruch (MITM) | **BPDU guard** i **root guard** |
| **ARP spoofing** | fałszywe odpowiedzi ARP wiążą adres IP bramy z MAC atakującego (MITM) | **Dynamic ARP Inspection (DAI)** |
| **DHCP spoofing** | fałszywy serwer DHCP podaje własną bramę i DNS (MITM) | **DHCP snooping**, zaufane porty |
| **DHCP starvation** | wyczerpanie puli adresów fałszywymi żądaniami | port security, ograniczenie tempa DHCP snooping |

### Port security

- Ogranicza liczbę dozwolonych adresów MAC na porcie; tylko autoryzowane MAC mają dostęp. Chroni przed MAC flooding i (pośrednio) przed DHCP starvation.
- Adresy: statyczne (skonfigurowane ręcznie), dynamiczne (uczone, ulotne) i „przyklejone” (sticky – uczone, ale zapisane w konfiguracji).
- Reakcja na naruszenie:
    - `protect` – odrzuca nadmiarowe ramki po cichu,
    - `restrict` – odrzuca i loguje (licznik, SNMP),
    - `shutdown` – przełącza port w stan error-disabled (domyślna i najbezpieczniejsza).

### VLAN hopping

- **Fałszywy trunk (switch spoofing)** wykorzystuje automatyczną negocjację DTP: host podszywa się pod przełącznik, zestawia trunk i widzi ruch wszystkich VLAN-ów. Obrona: statyczny tryb access na portach użytkowników i wyłączone DTP; trunking tylko na wyznaczonych, ręcznie skonfigurowanych portach.
- **Double tagging** działa, bo przełącznik zdejmuje tylko zewnętrzną etykietę. Atakujący nadaje ramkę z dwiema etykietami: zewnętrzną równą natywnemu VLAN trunku (który jest przesyłany bez znacznika) i wewnętrzną wskazującą VLAN ofiary. Atak jest jednokierunkowy (brak odpowiedzi). Obrona: native VLAN ustawiony na osobny, nieużywany identyfikator i niewykorzystywany do ruchu użytkowników, tagowanie native VLAN na trunkach (`vlan dot1q tag native`) oraz przepuszczanie przez trunk tylko potrzebnych VLAN-ów (`switchport trunk allowed vlan`).

### Ochrona STP

Oba mechanizmy bronią drzewa rozpinającego, ale w innych miejscach:

- **BPDU guard** zakłada się na porty dostępowe (z PortFast). Każda odebrana ramka BPDU jest sygnałem nieoczekiwanego przełącznika – port natychmiast wchodzi w stan error-disabled.
- **Root guard** zakłada się na porty prowadzące do innych przełączników. Jeśli port odbierze „lepszą” (superior) BPDU próbującą przejąć rolę mostu głównego, zostaje zablokowany (root-inconsistent), aż atak ustanie. Chroni stabilną pozycję mostu głównego.

### DHCP snooping, DAI i IP Source Guard

Trzy warstwy budowane na jednej tablicy powiązań (MAC–IP–port–VLAN), tworzonej przez DHCP snooping:

- **DHCP snooping** dzieli porty na zaufane (w stronę prawidłowego serwera DHCP) i niezaufane (użytkownicy); odpowiedzi serwera (OFFER/ACK) z portu niezaufanego są odrzucane. Blokuje DHCP spoofing i ogranicza tempo żądań (starvation).
- **Dynamic ARP Inspection (DAI)** sprawdza pakiety ARP na portach niezaufanych względem tablicy powiązań; odpowiedzi ze sfałszowaną parą IP–MAC są odrzucane. Blokuje ARP spoofing. Hosty ze statycznym IP nie trafiają do tablicy DHCP snooping, więc wymagają list ARP ACL, a porty w stronę innych przełączników muszą być oznaczone jako zaufane; inaczej DAI odrzuci prawidłowy ruch.
- **IP Source Guard** filtruje ruch na porcie według tablicy powiązań – przepuszcza tylko pakiety z przypisanym adresem źródłowym IP (i MAC). Blokuje podszywanie się pod adres IP.

## 802.1X i EAP

**802.1X** to standard kontroli dostępu do sieci na poziomie portu: urządzenie musi się uwierzytelnić, zanim port przepuści ruch inny niż samo uwierzytelnianie.

| Rola | Opis |
|---|---|
| **Suplikant** | urządzenie (klient), które chce się uwierzytelnić |
| **Authenticator** (strona uwierzytelniająca) | przełącznik lub punkt dostępowy egzekwujący kontrolę na porcie |
| **Serwer uwierzytelniający** | zwykle RADIUS, sprawdza poświadczenia i zwraca decyzję (oraz atrybuty, np. VLAN) |

**EAP (Extensible Authentication Protocol)** to rama dla różnych metod uwierzytelniania negocjowanych między suplikantem a serwerem:

| Metoda | Poświadczenia | Kompromis |
|---|---|---|
| **EAP-TLS** | certyfikaty po obu stronach | najsilniejsza, wzajemne uwierzytelnianie; wymaga PKI i zarządzania certyfikatami klienta |
| **PEAP** / **EAP-TTLS** | certyfikat serwera + hasło w tunelu TLS (np. MS-CHAPv2) | łatwiejsze wdrożenie; wymaga walidacji certyfikatu serwera, inaczej grozi podszycie i przechwycenie poświadczeń |
| **EAP-MD5** | skrót hasła, bez tunelu | przestarzała: brak wzajemnego uwierzytelniania i szyfrowania, podatna na atak słownikowy; nieprzydatna w Wi-Fi |

!!! warning "Walidacja certyfikatu serwera"
    W PEAP i EAP-TTLS cała ochrona poświadczeń opiera się na tunelu TLS. Jeśli suplikant nie sprawdza certyfikatu serwera (i nazwy CA), atakujący może uruchomić fałszywy punkt dostępowy i przechwycić uwierzytelnianie MS-CHAPv2.

## Monitorowanie i kontrola dostępu

- **Monitorowanie aktywne** (generowanie i analiza ruchu testowego) i **pasywne** (obserwacja ruchu bez zakłócania).
- Rozwiązania klasy **NAC (Network Access Control)** łączą uwierzytelnianie (802.1X, autoryzacja po MAC, Captive Portal dla gości), sprawdzanie zgodności urządzenia przed wpuszczeniem (poziom łatek, antywirus) i przypisanie polityki dostępu (VLAN, ACL, QoS) zależnie od tożsamości.

## Rekomendacje

- Włącz port security; wyłącz DTP i ustaw porty użytkowników w trybie access.
- Zbuduj obronę DHCP/ARP warstwowo: DHCP snooping, a na nim DAI i IP Source Guard.
- Chroń STP: BPDU guard na portach dostępowych, root guard na portach między przełącznikami.
- Segmentuj sieć na VLAN-y (osobno pracownicy, goście, systemy krytyczne); native VLAN ustaw na nieużywany identyfikator.
- Uwierzytelniaj dostęp do sieci (802.1X z EAP-TLS tam, gdzie to możliwe; w PEAP/EAP-TTLS wymuś walidację certyfikatu serwera).
