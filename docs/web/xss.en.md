---
description: "Cross-Site Scripting: the reflected, stored and DOM-based types, injection context, testing reflection and filters, and defence with encoding and CSP."
---

# XSS

**Cross-Site Scripting (XSS)** is a vulnerability where malicious code (usually JavaScript) reaches another user's browser through a vulnerable application. It is an attack on the client, not the server. It is used to steal session cookies, deface content, phish within the page or perform actions on behalf of the victim. It belongs to the **A05 Injection** category (OWASP Top 10 2025).

## Types

| Type | Where the code is | Who is affected |
|---|---|---|
| **Reflected** | in a request parameter, reflected in the response | the victim must click a crafted link |
| **Stored** | saved on the server (a comment, a profile) | runs for everyone who opens the page |
| **DOM-based** | in the page's own JavaScript (e.g. a write to `innerHTML`) | data from the URL or `#` need never reach the server |

## When it occurs

The application takes user data and displays it without properly encoding HTML special characters (`<`, `>`, `"`, `'`, `&`) for the given context.

## When the application is safe

- **Contextual output encoding**: `<` becomes `&lt;` and so on, differently in HTML content, in an attribute, in JS and in a URL.
- Modern frameworks (React, Angular) encode data by default, but they have escape hatches: `dangerouslySetInnerHTML` and `href="javascript:..."` in React, `bypassSecurityTrust*` in Angular.
- **Trusted Types** (`Content-Security-Policy: require-trusted-types-for 'script'`): the browser rejects plain strings assigned to dangerous DOM sinks (`innerHTML`), the main modern defence against DOM XSS.
- **Content Security Policy** as a second layer: it blocks inline scripts and scripts from unknown sources.
- The `HttpOnly` flag on session cookies: JavaScript cannot read them, so XSS cannot steal the session directly.

## How to test

1. Put a unique marker (e.g. `PENTEST123`) in the parameter and check whether it comes back in the response (the entry point).
2. Send the special characters `< > " ' ( ) ;` and see how they come back: literally (vulnerable) or as entities `&lt; &gt;` (safe). Some may be filtered and some not.
3. Pick a payload for the context and confirm it in the browser (Show response in browser):

```html
<script>alert(1)</script>          <!-- HTML content -->
"><svg onload=alert(1)>            <!-- breaking out of an attribute -->
" onerror="alert(1)                 <!-- inside an img tag -->
```

4. For stored XSS, submit the payload in a form (comment, profile) and refresh the page as another user.

!!! tip "Observation matters more than the payload"
    First establish whether and where the data comes back and in what context. The payload only confirms the hypothesis. A `<b>test</b>` that renders as bold is already a sign of missing encoding (HTML injection).

## DOM sources and sinks

In DOM-based XSS the data flows from an attacker-controlled **source** to a dangerous **sink**, often without the server being involved. Auditing means tracing that path through the JavaScript.

- Common sources: `location` (including `location.hash` and `location.search`), `document.referrer`, `window.name`, `postMessage`, data from `localStorage`.
- HTML-rendering sinks: `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write`, jQuery `.html()`.
- Code-executing sinks: `eval`, `Function`, `setTimeout`/`setInterval` with a string argument, assigning a `javascript:` value to `location` or `src`.

Safe equivalents: `textContent` instead of `innerHTML`, `setAttribute` for attributes, and, where rendering HTML is unavoidable, sanitisation with a trusted library.

!!! warning "Mutation XSS (mXSS)"
    The browser can "fix" invalid HTML when it is loaded into `innerHTML`, turning a seemingly harmless string into a working payload after sanitisation has run. Use an up-to-date, proven library and sanitise in exactly the form the data will take in the DOM.

## Recommendations

- Encode data on output according to the context; do not rely on input filtering.
- Deploy a CSP and the `HttpOnly` flag. A CSP only works when well configured: `unsafe-inline` and overly broad sources void it, so prefer a nonce or a hash.
- Avoid dangerous DOM sinks; assign data through `textContent` and `setAttribute`.
- To clean user HTML, use a proven library (e.g. DOMPurify), not your own rules.
