---
description: "XML External Entity: a flaw in XML parsers, reading files and SSRF through external entities, DoS by entity expansion, in-band and blind tests, disabling DTDs."
---

# XXE

**XML External Entity (XXE)** is a flaw in XML parsers configured to process **external entities** defined in a DTD (Document Type Definition). An attacker can read local server files, perform SSRF (scanning the internal network), cause DoS (the Billion Laughs attack, which expands internal entities) and, less often, reach RCE. In the OWASP Top 10 2025 it is part of **A02 Security Misconfiguration**; in the 2017 edition XXE had its own category.

## When it occurs

- The application accepts XML data (directly or in formats that are XML underneath: SVG, DOCX/XLSX/PPTX, ODT, RSS/Atom, SAML, SOAP).
- The parser has DTD and external entity support enabled, and the developer did not disable it.
- Common in file upload and SOAP APIs.

## When the application is safe

- DTD support fully disabled in the parser.
- External entities and external parameter entities disabled.
- The server returns a "DTD is prohibited" error for every document with a `DOCTYPE`.

## How to test

1. In the proxy history, find requests with `Content-Type: application/xml` or `text/xml`. Sometimes the application accepts XML even though it sends JSON by default: try changing the `Content-Type` and reshaping the body.
2. Send the request to Repeater.
3. Basic test (do entities work): define an entity and use it in a field shown in the response.

```xml
<?xml version="1.0"?>
<!DOCTYPE foo [ <!ENTITY test "PENTEST_VALUE"> ]>
<data><field>&test;</field></data>
```

4. Reading a file (in-band): an entity pointing to a system file.

```xml
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>
<data><field>&xxe;</field></data>
```

5. **Blind XXE** (no result in the response): an external entity pointing to your own listener (a VPS or a self-hosted interactsh; public services such as webhook.site only in labs). A request arriving from the server's IP confirms the vulnerability (SSRF through XXE).
6. **Error-based**: forcing an error that contains the file content, when there is no output and no outbound connections.

!!! danger "Billion Laughs"
    Nested entities that multiply exponentially can exhaust the server's memory (DoS). This variant is not tested in production. Disabling only external entities does not stop it, because Billion Laughs uses internal entities; disabling DTDs or limiting entity expansion does.

## Parameter entities and OOB

When there is no reflection in the response, an attacker reaches for **parameter entities** (`%name;`), used inside the DTD itself. They make it possible to build an external DTD that reads a file and sends its content in a request to a server the tester controls (an out-of-band channel). This is the same mechanism as blind XXE, only carried out entirely on the DTD-definition side. The defence is identical: disabling external parameter entities also closes this variant.

## Disabling it in common parsers

Configuration differs between libraries, so check the exact method for the parser in use.

| Platform / parser | How to harden |
|---|---|
| Java (`DocumentBuilderFactory`, SAX, StAX) | set `disallow-doctype-decl` to `true`; disable `external-general-entities` and `external-parameter-entities` |
| Python (`lxml`, `ElementTree`) | use the `defusedxml` library instead of the default parsers |
| .NET (`XmlReader`) | set `DtdProcessing` to `Prohibit` and `XmlResolver` to `null` (the default in newer versions) |
| PHP (libxml) | in newer versions external entities are disabled by default; do not enable `LIBXML_NOENT` |

## Recommendations

- Disable DTDs and external entities (including parameter entities) in the parser configuration, separately for each library.
- Prefer simpler formats (JSON) where XML is not necessary.
- Validate and limit the size and nesting depth of XML documents.
- Restrict outbound traffic from the server to hamper blind and OOB channels.
