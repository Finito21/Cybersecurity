---
description: "ZAP: darmowe narzędzie proxy do testów bezpieczeństwa aplikacji webowych, skanowanie aktywne i pasywne, Spider i Fuzzer oraz porównanie z Burpem."
---

# ZAP

**ZAP (Zed Attack Proxy)** to darmowe, otwarte i wielofunkcyjne narzędzie do testowania bezpieczeństwa aplikacji webowych. Działa jako **proxy typu man-in-the-middle**: pośredniczy między przeglądarką a aplikacją, dzięki czemu może przechwytywać, analizować i w razie potrzeby modyfikować przesyłane komunikaty. Jeśli używany jest już inny serwer proxy, ZAP można z nim połączyć kaskadowo.

!!! note "Dawniej OWASP ZAP"
    Do 2023 ZAP był projektem OWASP. Później przeszedł do Software Security Project (Linux Foundation), a od 2024 jest rozwijany jako „ZAP by Checkmarx”. Nadal jest darmowy i otwarty (licencja Apache 2.0).

## Skanowanie aktywne i pasywne

| Tryb | Na czym polega |
|---|---|
| **Pasywne** | analiza komunikatów między przeglądarką a aplikacją w poszukiwaniu znanych problemów, bez ingerencji w ruch |
| **Aktywne** | próby wykrycia luk przez bezpośrednie ataki na aplikację (wysyłanie testowych żądań) |

!!! warning "Skan aktywny tylko w zakresie"
    Skanowanie aktywne wysyła realne żądania i może zmieniać dane lub obciążać serwer. Uruchamia się je wyłącznie na systemach objętych zgodą, najlepiej w środowisku testowym.

## Główne funkcje

- **Spider**: automatyczne odkrywanie struktury, linków i zasobów aplikacji (robot indeksujący buduje mapę serwisu). Analizuje statyczny HTML.
- **AJAX Spider**: eksploruje aplikacje intensywnie korzystające z JavaScriptu (SPA), sterując prawdziwą przeglądarką; dociera do treści i akcji generowanych dynamicznie, których klasyczny Spider nie zobaczy. Jest wolniejszy, więc używa się go tam, gdzie zwykły Spider mapuje za mało.
- **Fuzzer**: wysyłanie dużej ilości danych (losowych lub z listy) w celu znalezienia błędów obsługi wejścia.
- **Automatyzacja**: Automation Framework (plany w YAML), tryb headless, API oraz obrazy Docker (skan baseline i pełny) pozwalają uruchamiać ZAP w potokach CI/CD.
- Przechwytywanie i modyfikacja żądań, przeglądanie historii, raportowanie znalezisk.

## ZAP a Burp Suite

| Cecha | ZAP | Burp Suite Community |
|---|---|---|
| Licencja | darmowa, open source | darmowa (Community), płatna (Pro) |
| Skaner aktywny | wbudowany | brak w Community |
| Automatyzacja | dobra, przyjazna CI/CD | ograniczona w Community |
| Ekosystem | dodatki społeczności | bogaty ekosystem (głównie Pro) |

W praktyce oba narzędzia się uzupełniają: ZAP dobrze sprawdza się w automatyzacji i gdy przydaje się darmowy skaner, Burp w ręcznej, precyzyjnej pracy ([Burp Suite](burp_suite.md)).

## Rekomendacje

- Zacznij od skanowania pasywnego i mapowania aplikacji Spiderem; przy aplikacjach SPA dołóż AJAX Spider.
- Skan aktywny uruchamiaj świadomie, z poprawnie ustawionym zakresem.
- Wyniki skanera weryfikuj ręcznie: automat zgłasza też fałszywe alarmy.
