---
description: "Bezpieczeństwo Linuksa: uprawnienia, SUID i capabilities, typowe drogi eskalacji (sudo, cron, timery), zapora, hardening oraz monitoring auditd i journald."
---

# Linux

Podstawy bezpieczeństwa systemu Linux z perspektywy obrońcy: uprawnienia, typowe drogi eskalacji i utwardzanie. Techniki ofensywne opisano po to, by wiedzieć, co utwardzać i czego szukać przy audycie.

## Uprawnienia

- Uprawnienia pliku: odczyt, zapis, wykonanie, osobno dla właściciela, grupy i pozostałych (`ls -la`).
- Zapis ósemkowy: `chmod 640` to odczyt i zapis dla właściciela, odczyt dla grupy, nic dla reszty.
- **Bit SUID** pozwala uruchomić plik z uprawnieniami właściciela (litera `s` w polu właściciela). Analogiczny **SGID** działa dla grupy, a **sticky bit** chroni pliki w katalogach współdzielonych (np. `/tmp`).
- Źle dobrany SUID na programie, który potrafi uruchomić powłokę lub czytać dowolne pliki, to droga do eskalacji. Inwentaryzacja: `find / -perm -4000 -type f 2>/dev/null`.
- **Capabilities** (POSIX capabilities) rozbijają przywileje roota na mniejsze uprawnienia nadawane pojedynczym plikom wykonywalnym (`getcap -r / 2>/dev/null`). Zdolności takie jak `cap_setuid` czy `cap_dac_read_search` bywają równie niebezpieczne jak SUID.

!!! note "GTFOBins"
    **GTFOBins** to katalog uniksowych programów wykorzystywanych w technice „living off the land”, które przy ustawionym SUID, dozwolonym `sudo` lub nadanej capability pozwalają wyjść z ograniczeń powłoki, odczytać lub zapisać dowolne pliki albo uzyskać roota. Wyniki audytu SUID i reguł `sudo` warto zestawić z tą listą, aby ocenić realne ryzyko.

## Typowe drogi eskalacji uprawnień


- **Exploity jądra**: wykorzystanie luki w podatnej wersji jądra (sprawdzenie `uname -a`, bazy exploitów).
- **Błędna konfiguracja sudo**: polecenia dozwolone bez hasła (`sudo -l`) lub programy pozwalające uruchomić powłokę.
- **Niebezpieczne capabilities**: pliki wykonywalne z nadanym `cap_setuid+ep` i podobnymi zdolnościami.
- **Zapisywalny `/etc/passwd` lub `/etc/shadow`**: dodanie konta z uprawnieniami roota. Groźny jest też sam *odczyt* `/etc/shadow`, bo skróty haseł można łamać offline.
- **Zadania cron i timery systemd**: skrypt uruchamiany z wysokimi uprawnieniami, do którego zwykły użytkownik ma prawo zapisu; dotyczy też zapisywalnych jednostek `.service` i `.timer`.
- **Usługi z uprawnieniami roota**: np. źle skonfigurowany Docker. Członkostwo w grupie `docker` (dostęp do gniazda) jest równoważne uprawnieniom roota.

!!! note "Kontekst"
    Te techniki opisano, by rozumieć, co utwardzać i czego szukać przy audycie. Stosuje się je wyłącznie na własnych lub autoryzowanych systemach.

## Zapora i porty

- Zamykanie nieużywanych portów i blokowanie zbędnych protokołów ogranicza powierzchnię ataku.
- Zasada domyślnej odmowy: zezwalaj tylko na potrzebny ruch (np. SSH z wybranych adresów), resztę blokuj.
- Narzędzia: `iptables`/`nftables`, `ufw`, a do automatycznego blokowania adresów po powtarzających się nieudanych próbach `fail2ban`.

Minimalny zestaw reguł nftables z domyślną odmową (SSH tylko z sieci administracyjnej):

```text
table inet filter {
  chain input {
    type filter hook input priority 0; policy drop;
    ct state established,related accept
    iif "lo" accept
    ip saddr 192.168.50.0/24 tcp dport 22 accept
  }
}
```

## Hardening i monitoring

- Aktualizacje systemu i pakietów (łatanie znanych CVE).
- Najmniejsze uprawnienia: osobne konta usług, brak zbędnego dostępu do roota, przemyślane `sudo`.
- Wyłączenie zbędnych usług i kont, zmiana domyślnych haseł, utwardzenie SSH w `sshd_config`: `PermitRootLogin no`, `PasswordAuthentication no`, `KbdInteractiveAuthentication no`, `AllowGroups` z wybraną grupą i `MaxAuthTries`.
- **Logi i monitoring**:
    - `/var/log` (`auth.log`, `syslog`) oraz `journalctl` do przeglądu zdarzeń (np. `journalctl -u ssh` w Debianie i Ubuntu, `journalctl -u sshd` w RHEL i Fedorze); wpisy `Failed password` i `Invalid user` to próby zgadywania haseł i kont. Warto włączyć trwałe przechowywanie dziennika journald.
    - **auditd** rejestruje wywołania systemowe i dostęp do plików według reguł (`auditctl`, przegląd przez `ausearch`/`aureport`) i uzupełnia logi uwierzytelniania o kontekst „kto, co, kiedy”; przykład reguły: `-w /etc/passwd -p wa -k identity`.
    - **Kontrola integralności plików**: AIDE lub Tripwire porównują stan systemu z bazą odniesienia; pomocne są też `dpkg --verify` i `rpm -Va`.
    - Alerty na nietypowe procesy, nowe konta oraz nasłuchujące połączenia.

## Rekomendacje

- Regularnie przeglądaj pliki z bitem SUID/SGID, nadane capabilities i konfigurację `sudo`.
- Regularnie aktualizuj jądro i pakiety; usuwaj zbędne usługi.
- Włącz auditd i kontrolę integralności plików; centralizuj logi uwierzytelniania oraz monitoruj tworzenie nowych kont i usług.
