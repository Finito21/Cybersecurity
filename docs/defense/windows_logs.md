---
description: "Analiza logów Windows w Podglądzie zdarzeń: dzienniki, struktura wpisu, kluczowe Event ID dla logowania, eskalacji uprawnień, trwałości i Sysmon."
---

# Logi Windows

Logi to rejestr zdarzeń systemu, aplikacji i usług. W analizie powłamaniowej pozwalają odtworzyć przebieg incydentu, wykryć nieautoryzowany dostęp i działania malware. Głównym narzędziem jest **Podgląd zdarzeń (Event Viewer)**.

## Dzienniki i format

- Dzienniki: **Aplikacja**, **Zabezpieczenia**, **System**, **Instalacja**, **Zdarzenia przesłane dalej** oraz **Dzienniki aplikacji i usług**.
- Od Windows Vista logi są w formacie binarnym `.evtx` (`%SystemRoot%\System32\winevt\Logs`), zarządzane przez usługę **Windows Event Log**.
- Dla bezpieczeństwa najważniejszy jest dziennik **Zabezpieczenia**, ale warto patrzeć też na System i Aplikację.
- Zdarzenie opisują m.in.: źródło, identyfikator (Event ID), poziom, użytkownik, czas, komputer i opis.
- Większość zdarzeń bezpieczeństwa (dostęp do obiektów, tworzenie procesów, zmiany polityki) rejestruje się dopiero po włączeniu odpowiedniej **polityki audytu** (`Advanced Audit Policy`).

## Kluczowe Event ID

### Logowanie i wylogowanie

| ID | Znaczenie |
|---|---|
| **4624** | pomyślne logowanie; pole typu logowania wskazuje wektor: 2 lokalne/interaktywne, 3 sieciowe, 10 RDP |
| **4625** | nieudane logowanie; seria wpisów to sygnał brute force lub password spraying. Kod stanu odróżnia błędne hasło (`0xC000006A`) od nieistniejącego konta (`0xC0000064`), czyli password spraying od enumeracji kont |
| **4634** | wylogowanie (zamknięcie sesji) |
| **4647** | wylogowanie zainicjowane przez użytkownika |
| **4648** | logowanie z jawnymi poświadczeniami („Uruchom jako”, bywa oznaką ruchu bocznego) |
| **4740** | zablokowanie konta (lockout) po wielu błędnych próbach; w domenie zapisywane na kontrolerze domeny (emulator PDC), nie na stacji roboczej |

!!! warning "RDP z NLA to typ logowania 3"
    Przy włączonym Network Level Authentication (domyślnie) nieudane logowanie przez RDP trafia do 4625 jako **typ 3**, a nie 10. Wyszukiwanie „4625 typ 10” przeoczy brute force na RDP.

### Kerberos i NTLM (kontroler domeny)

| ID | Znaczenie |
|---|---|
| **4768** | wydanie biletu TGT (logowanie do domeny) |
| **4769** | wydanie biletu usługi; szyfrowanie RC4 (`0x17`) przy kontach usług bywa śladem Kerberoastingu |
| **4771** | nieudane wstępne uwierzytelnienie Kerberos (błędne hasło) |
| **4776** | weryfikacja poświadczeń NTLM |

### Konta i grupy

| ID | Znaczenie |
|---|---|
| **4720** | utworzenie konta użytkownika |
| **4723** | użytkownik zmienił własne hasło |
| **4724** | próba zresetowania hasła konta (przez innego użytkownika, np. administratora) |
| **4728 / 4732 / 4756** | dodanie konta do grupy globalnej / lokalnej / uniwersalnej (np. Administratorzy) |

### Eskalacja uprawnień i dostęp

| ID | Znaczenie |
|---|---|
| **4672** | specjalne uprawnienia przy logowaniu (konto administracyjne lub SYSTEM) |
| **4663** | próba dostępu do obiektu (plik, katalog); wymaga ustawionego SACL na obiekcie |
| **5140** | dostęp do udziału sieciowego |
| **4660** | usunięcie obiektu |
| **4670** | zmiana uprawnień (ACL) obiektu |

### Trwałość i ślady malware

| ID | Znaczenie |
|---|---|
| **4688** | utworzenie nowego procesu; z audytem wiersza poleceń rejestruje też pełne argumenty (np. `powershell.exe` do pobrania i uruchomienia) |
| **4697** | instalacja usługi odnotowana w dzienniku **Zabezpieczenia** (wymaga audytu) |
| **7045** | instalacja nowej usługi w dzienniku **System** (częste przy malware i narzędziach typu PsExec) |
| **4698** | utworzenie zadania Harmonogramu zadań (typowa metoda utrzymania trwałości) |
| **4719** | zmiana polityki audytu (próba ukrycia aktywności) |
| **1102** | wyczyszczenie dziennika **Zabezpieczenia** (zacieranie śladów); odpowiednik dla innych dzienników to zdarzenie **104** w dzienniku System |
| **4946–4948** | zmiany reguł zapory Windows (dodanie wyjątku przez backdoor); wymagają audytu „MPSSVC Rule-Level Policy Change”, a bez niego zmiany reguł widać w dzienniku zapory (zdarzenia 2004–2006) |
| **4104** | blok skryptu PowerShell (Script Block Logging, dziennik `Microsoft-Windows-PowerShell/Operational`); pokazuje kod po rozkodowaniu |
| **1100** | zatrzymanie usługi dziennika zdarzeń (możliwa próba wyłączenia rejestrowania) |

## Sysmon

**Sysmon** (System Monitor z pakietu Sysinternals) to sterownik i usługa, które rozszerzają natywne logowanie o bogatsze zdarzenia zapisywane w dzienniku `Microsoft-Windows-Sysmon/Operational`. Przydatne Event ID:

- **1** – utworzenie procesu (z sumą kontrolną pliku, wierszem polecenia i procesem nadrzędnym),
- **3** – połączenie sieciowe nawiązane przez proces,
- **7** – załadowanie obrazu/DLL (wykrywanie podmiany bibliotek),
- **8** – `CreateRemoteThread` (wstrzyknięcie kodu do innego procesu),
- **11** – utworzenie pliku,
- **13** – modyfikacja wartości rejestru (często wykorzystywana do trwałości).

Dobra konfiguracja (np. popularne szablony ograniczające szum) jest kluczowa. Sysmon nie zastępuje audytu Windows, lecz go uzupełnia o kontekst korelacji.

## Praca z logami

- **Widoki niestandardowe**: filtry po dzienniku, poziomie, Event ID, źródle, zakresie dat.
- **Zapis zdarzeń** jako dowód: format `.evtx` (zachowuje pełną strukturę) lub `.xml`/`.csv` do analizy poza Podglądem.
- **Zapora Windows**: nietypowe porty (np. TCP/4444) i protokoły mogą wskazywać na backdoor lub próbę obejścia zabezpieczeń.

!!! warning "Czyszczenie logów"
    Wyczyszczenie lub wyłączenie dziennika zabezpieczeń to typowy element zacierania śladów; zostawia ono zdarzenia 4719, 1102 (a dla innych dzienników 104) oraz 1100. Logi warto przesyłać na zewnątrz (np. do SIEM), zanim atakujący je usunie.

## Rekomendacje

- Włącz politykę audytu dla logowania, procesów (4688, najlepiej z audytem wiersza poleceń) i dostępu do obiektów.
- Centralizuj logi (przesyłanie zdarzeń, SIEM) i ustaw alerty na kluczowe Event ID, zwłaszcza 1102, 4720, 4698 i 7045.
- Rozważ wdrożenie Sysmon dla głębszej widoczności procesów, sieci i rejestru.
- Ustal poziom bazowy (baseline), by odróżnić normalną aktywność od anomalii.
