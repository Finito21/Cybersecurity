---
description: "XML External Entity: podatność parserów XML, odczyt plików i SSRF przez encje zewnętrzne, DoS przez rozwijanie encji, testy in-band i blind, wyłączanie DTD."
---

# XXE

**XML External Entity (XXE)** to podatność parserów XML skonfigurowanych tak, że przetwarzają **encje zewnętrzne** zdefiniowane w DTD (Document Type Definition). Atakujący może odczytać lokalne pliki serwera, wykonać atak SSRF (skan sieci wewnętrznej), spowodować DoS (atak Billion Laughs, oparty na rozwijaniu encji wewnętrznych), a rzadziej doprowadzić do RCE. W OWASP Top 10 2025 to część kategorii **A02 Security Misconfiguration**; w edycji z 2017 XXE miało własną kategorię.

## Kiedy występuje

- Aplikacja przyjmuje dane XML (bezpośrednio lub w formatach, które „pod spodem” są XML: SVG, DOCX/XLSX/PPTX, ODT, RSS/Atom, SAML, SOAP).
- Parser ma włączoną obsługę DTD i encji zewnętrznych, a programista tego nie wyłączył.
- Częste w uploadzie plików i w API typu SOAP.

## Kiedy aplikacja jest bezpieczna

- Całkowicie wyłączona obsługa DTD w parserze.
- Wyłączone encje zewnętrzne i zewnętrzne encje parametryczne.
- Serwer zwraca błąd „DTD is prohibited” przy każdym dokumencie z `DOCTYPE`.

## Jak testować

1. W historii proxy znajdź żądania z `Content-Type: application/xml` lub `text/xml`. Czasem aplikacja przyjmie XML, mimo że domyślnie wysyła JSON: spróbuj zmienić `Content-Type` i przerobić treść.
2. Wyślij żądanie do Repeatera.
3. Test podstawowy (czy encje działają): zdefiniuj encję i użyj jej w polu widocznym w odpowiedzi.

```xml
<?xml version="1.0"?>
<!DOCTYPE foo [ <!ENTITY test "PENTEST_VALUE"> ]>
<data><field>&test;</field></data>
```

4. Odczyt pliku (in-band): encja wskazująca na plik systemowy.

```xml
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>
<data><field>&xxe;</field></data>
```

5. **Blind XXE** (brak wyniku w odpowiedzi): encja zewnętrzna wskazująca na własny serwer nasłuchowy (VPS lub samodzielnie hostowany interactsh; publiczne usługi typu webhook.site tylko w laboratoriach). Żądanie przychodzące z IP serwera potwierdza podatność (SSRF przez XXE).
6. **Error-based**: wymuszenie błędu zawierającego treść pliku, gdy nie ma wyjścia ani połączeń wychodzących.

!!! danger "Billion Laughs"
    Zagnieżdżone encje mnożące się wykładniczo potrafią wyczerpać pamięć serwera (DoS). Tego wariantu nie testuje się w środowisku produkcyjnym. Wyłączenie samych encji zewnętrznych go nie blokuje, bo Billion Laughs używa encji wewnętrznych; pomaga wyłączenie DTD lub limity rozwijania encji.

## Encje parametryczne i OOB

Gdy w odpowiedzi nie ma żadnego odbicia, atakujący sięga po **encje parametryczne** (`%nazwa;`), używane wewnątrz samego DTD. Pozwalają one zbudować zewnętrzny DTD, który wczytuje plik i odsyła jego treść w żądaniu do serwera kontrolowanego przez testera (kanał out-of-band). To ten sam mechanizm co blind XXE, tylko realizowany w całości po stronie definicji DTD. Obrona jest identyczna: wyłączenie zewnętrznych encji parametrycznych zamyka również ten wariant.

## Wyłączanie w popularnych parserach

Konfiguracja różni się między bibliotekami, dlatego warto sprawdzić dokładny sposób dla używanego parsera.

| Platforma / parser | Jak utwardzić |
|---|---|
| Java (`DocumentBuilderFactory`, SAX, StAX) | ustaw `disallow-doctype-decl` na `true`; wyłącz `external-general-entities` i `external-parameter-entities` |
| Python (`lxml`, `ElementTree`) | używaj biblioteki `defusedxml` zamiast domyślnych parserów |
| .NET (`XmlReader`) | ustaw `DtdProcessing` na `Prohibit` i `XmlResolver` na `null` (domyślne w nowszych wersjach) |
| PHP (libxml) | w nowszych wersjach encje zewnętrzne są domyślnie wyłączone; nie włączaj `LIBXML_NOENT` |

## Rekomendacje

- Wyłącz DTD i encje zewnętrzne (także parametryczne) w konfiguracji parsera, dla każdej biblioteki osobno.
- Preferuj prostsze formaty (JSON) tam, gdzie XML nie jest konieczny.
- Waliduj i ograniczaj rozmiar oraz zagnieżdżenie dokumentów XML.
- Ogranicz ruch wychodzący z serwera, aby utrudnić kanały blind i OOB.
