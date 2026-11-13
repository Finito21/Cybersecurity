---
description: "Ochrona przed ransomware: zasada backupu 3-2-1, strategie kopii plików, obrazu dysku i maszyn wirtualnych, szyfrowanie kopii i odtwarzanie po ataku."
---

# Backup i ransomware

**Ransomware** blokuje dostęp do systemu lub szyfruje dane i żąda okupu. Jedyną pewną drogą wyjścia po udanym ataku jest **odtworzenie z kopii zapasowej**, dlatego backup jest podstawą obrony. Notatka opiera się na projekcie łączącym backup i szyfrowanie.

## Zasada 3-2-1 (i 3-2-1-1-0)

- **3** kopie danych,
- na **2** różnych typach nośników,
- **1** kopia poza lokalizacją (offsite).

Rozszerzenie **3-2-1-1-0** dodaje:

- **1** kopię offline, odseparowana (air-gap) lub niemodyfikowalna (immutable),
- **0** błędów przy odtwarzaniu – kopie są regularnie testowane i weryfikowane.

Kopia offline lub niemodyfikowalna jest kluczowa: ransomware często szyfruje także podłączone dyski, udziały sieciowe i dostępne z hosta kopie. Niemodyfikowalność zapewnia np. **Object Lock / WORM**: kopii nie da się nadpisać ani usunąć przez zadany czas. Chroni to także przed skradzionym kontem administratora tylko w trybie **compliance**; w trybie governance użytkownik z odpowiednim uprawnieniem może blokadę zdjąć. Poświadczenia do magazynu kopii trzymaj osobno od produkcji (osobne konto lub dzierżawa, MFA).

## RPO i RTO

Dwa parametry wyznaczają harmonogram i architekturę backupu; wynikają z wymagań biznesowych:

- **RPO** (Recovery Point Objective) – ile danych organizacja może stracić, czyli maksymalny odstęp między kopiami. Krótszy RPO oznacza częstsze kopie.
- **RTO** (Recovery Time Objective) – jak szybko trzeba przywrócić działanie. Krótszy RTO oznacza szybsze (często lokalne) ścieżki odtwarzania.

## Strategie kopii (z laboratorium)

| Strategia | Narzędzie | Zalety | Wady |
|---|---|---|---|
| **Kopia wybranych plików** | Duplicity (szyfrowanie GPG, kopie przyrostowe, FTP/SFTP) | mały rozmiar, można automatyzować skryptem z datą | trzeba wiedzieć, co kopiować |
| **Klon całego dysku** | Clonezilla (tryb device-device lub obraz) | pełne odtworzenie systemu i konfiguracji | większy rozmiar, dłuższy proces |
| **Backup maszyn wirtualnych** | Proxmox + magazyn na TrueNAS | automatyzacja, elastyczne zarządzanie | wymaga infrastruktury wirtualnej |

W projekcie magazynem był **TrueNAS** (pula dyskowa, udział), a kopie dodatkowo szyfrowano, aby chronić je przed odczytem.

## Odtwarzanie po ataku

1. Odizoluj zainfekowany system od sieci, ale go nie wyłączaj: pamięć operacyjna zawiera ślady ataku.
2. Zabezpiecz dowody (obraz pamięci i dysków, logi), zanim cokolwiek zostanie przeinstalowane.
3. Ustal wektor wejścia i moment pierwszego włamania (logi, [analiza powłamaniowa](windows_logs.md)). Atakujący często czekają tygodniami przed szyfrowaniem, więc najnowsze kopie mogą już zawierać ich narzędzia.
4. Zresetuj poświadczenia, zwłaszcza kont administratorów domeny i konta `krbtgt` (dwukrotnie), i zamknij lukę.
5. Odtwórz czysty system (reinstalacja lub klon sprzed włamania), przywróć dane z kopii sprzed pierwszego włamania i zweryfikuj integralność.

## Wykrywanie

Ransomware zwykle zdradza się, zanim zaszyfruje dane:

- polecenia usuwające kopie zapasowe i punkty przywracania: `vssadmin delete shadows`, `wmic shadowcopy delete`, `wbadmin delete catalog`, `bcdedit /set {default} recoveryenabled no` (widoczne jako zdarzenie 4688 lub Sysmon 1, zob. [Logi Windows](windows_logs.md)),
- masowa zmiana nazw lub zapis wielu plików w krótkim czasie; pliki-pułapki (canary) wykrywają to najwcześniej,
- nieudane zadania kopii zapasowej, zmiany retencji lub wyłączenie agenta backupu.

!!! warning "Nie licz na okup"
    Zapłata nie gwarantuje odzyskania danych ani usunięcia kopii wykradzionych przez atakującego i finansuje kolejne ataki. Zabezpiecz dowody (obrazy dysków, logi), rozważ zgłoszenie do CERT lub organów ścigania. Jedyną pewną drogą pozostają działające, przetestowane kopie.

!!! warning "Testuj odtwarzanie"
    Kopia, której nigdy nie przywrócono, bywa bezużyteczna (uszkodzony plik, brakujący klucz szyfrujący, niekompletny zakres). Regularne próbne odtworzenie jest częścią strategii.

## Rekomendacje

- Wdróż 3-2-1 z co najmniej jedną kopią offline lub niemodyfikowalną.
- Szyfruj kopie i bezpiecznie przechowuj klucze (nie razem z kopią).
- Automatyzuj backup i monitoruj jego powodzenie; okresowo testuj odtwarzanie.
- Backup to warstwa ostatnia: nie zastępuje aktualizacji, segmentacji i ograniczania uprawnień.
