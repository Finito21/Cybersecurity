---
description: "Obrona systemów: analiza logów Windows, bezpieczeństwo Linuksa, hardening serwera NGINX, backup przeciw ransomware i skanowanie podatności."
---

# Obrona

Strona obrońcy (blue team): wykrywanie incydentów, utwardzanie systemów i przygotowanie na atak.

| Strona | Co zawiera |
|---|---|
| [Logi Windows](windows_logs.md) | Podgląd zdarzeń, kluczowe Event ID, Sysmon, wykrywanie ataków w logach |
| [Linux](linux_security.md) | uprawnienia, SUID i capabilities, eskalacja, utwardzanie i monitoring |
| [NGINX](nginx_hardening.md) | ukrycie wersji, limity żądań, nagłówki i TLS |
| [Backup i ransomware](ransomware_backup.md) | strategie kopii zapasowych i odtwarzanie po ataku |
| [Skanowanie podatności](vulnerability_scanning.md) | Nessus, OpenVAS, InsightVM i miejsce skanerów w procesie |

!!! tip "Atak i obrona razem"
    Każda podatność z działu [Aplikacje webowe](../web/index.md) ma odpowiednik po stronie obrony: wykrycie w logach, utwardzenie konfiguracji, ograniczenie skutków. Warto czytać oba działy równolegle.

!!! warning "Tylko w ramach uprawnień"
    Opisane techniki stosuje się wyłącznie na własnych systemach, w laboratorium lub za pisemną zgodą właściciela, w uzgodnionym zakresie.
