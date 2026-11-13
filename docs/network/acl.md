---
description: "Listy kontroli dostępu ACL: filtrowanie pakietów, niejawna odmowa, kolejność reguł, kierunek, maski blankietowe, listy standardowe i rozszerzone."
---

# Listy ACL

**Lista kontroli dostępu (ACL)** to uporządkowana lista reguł zezwalających lub blokujących ruch na podstawie kryteriów pakietu. Rolę filtra pełni router (lub przełącznik warstwy 3), a każda reguła to wpis kontroli dostępu (**ACE**). ACL to praktyczna realizacja zasady domyślnej odmowy.

## Zasady działania

- Reguły są przetwarzane **sekwencyjnie**, od góry; **pierwsza pasująca decyduje**, a pozostałe są pomijane.
- Na końcu każdej listy jest **niejawna odmowa** (implicit deny): ruch bez pasującej reguły jest odrzucany. Dlatego lista bez żadnej reguły zezwalającej blokuje cały ruch.
- Kolejność reguł ma znaczenie: regułę bardziej szczegółową umieszcza się przed ogólną (inaczej ogólna „przykryje” szczegółową i ta nigdy nie zadziała).
- Na jeden interfejs przypada jedna lista na protokół i kierunek (np. jedna dla IPv4 wejściowa i jedna wyjściowa).

## Kierunek zastosowania

Lista działa dopiero po przypisaniu do interfejsu wraz z kierunkiem – z perspektywy routera:

- **wejściowy (in)**: filtruje pakiety, gdy wchodzą na interfejs, zanim router je przetworzy i skieruje; to tańszy wariant, bo odrzucony ruch nie obciąża routingu;
- **wyjściowy (out)**: filtruje pakiety już skierowane, tuż przed wysłaniem z interfejsu.

## Maski blankietowe

Maska blankietowa (wildcard) określa, które bity adresu są dopasowywane. Jest odwrotnością maski podsieci:

- bit **0** maski: dopasuj odpowiadający bit adresu,
- bit **1** maski: zignoruj odpowiadający bit.

Przykłady:

- `192.168.1.0 0.0.0.255` – cała podsieć `192.168.1.0/24`;
- `0.0.0.0 0.0.0.0` (słowo kluczowe `host`) – pojedynczy adres;
- `0.0.0.0 255.255.255.255` (słowo kluczowe `any`) – dowolny adres.

## Rodzaje list

| Rodzaj | Kryteria | Zastosowanie |
|---|---|---|
| **Standardowe** | tylko źródłowy adres IP | prosty filtr blisko celu ruchu |
| **Rozszerzone** | źródło i cel, protokół, porty, flagi | precyzyjny filtr blisko źródła ruchu |

Listy mogą być **numerowane** lub **nazwane**; te drugie są czytelniejsze i łatwiejsze w edycji. W Cisco IOS numeracja to przykładowo 1–99 i 1300–1999 (standardowe) oraz 100–199 i 2000–2699 (rozszerzone) – szczegóły zależą od producenta.

Przykład nazwanej listy rozszerzonej w Cisco IOS: dopuszcza HTTPS do serwera WWW, a resztę ruchu z podsieci loguje i odrzuca.

```text
ip access-list extended WEB-IN
 remark HTTPS do serwera WWW
 permit tcp 192.168.10.0 0.0.0.255 host 10.0.0.80 eq 443
 deny   ip any any log
!
interface GigabitEthernet0/1
 ip access-group WEB-IN in
```

## Dobre praktyki

- **Standardowe ACL** umieszcza się blisko miejsca docelowego (filtrują tylko po źródle, więc zbyt wcześnie odcięłyby za dużo). **Rozszerzone** umieszcza się blisko źródła i stosuje wejściowo, by odrzucić niechciany ruch, zanim przejdzie przez sieć.
- Dokumentuj reguły (komentarze/`remark`); nazwane ACL są czytelniejsze niż numerowane.
- Testuj po wdrożeniu: niejawna odmowa potrafi zablokować ruch, o którym się zapomniało (np. DNS, DHCP, zwrotny ruch sesji).
- Podstawowa ACL to filtr bezstanowy, nie pełna zapora; do filtrowania stanowego (dopuszczanie odpowiedzi tylko dla sesji zainicjowanych wewnątrz) potrzebna jest zapora z inspekcją stanu. Cisco IOS ma też półśrodki: słowo kluczowe `established`, listy refleksyjne i zaporę strefową (ZBF).

## Rekomendacje

- Stosuj zasadę najmniejszych uprawnień: zezwalaj tylko na potrzebny ruch, resztę pozostaw niejawnej odmowie.
- Porządkuj reguły od szczegółowych do ogólnych i pilnuj kierunku przypisania do interfejsu.
- Regularnie przeglądaj reguły i usuwaj nieaktualne.
- Loguj odrzucenia na krytycznych listach (jawna reguła `deny ... log` przed końcem), aby wykrywać próby dostępu.
