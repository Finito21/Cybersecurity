---
description: "Cross-Site Request Forgery: forcing actions as the victim, anti-CSRF tokens, SameSite nuances, GET and JSON CSRF, and double-submit pitfalls."
---

# CSRF

**Cross-Site Request Forgery (CSRF)** is an attack where a malicious page forces a logged-in victim's browser to perform an action in another application. The attacker does not steal data directly but "borrows" the victim's session (cookies attached automatically) to act on their behalf: changing a password, adding an administrator, making a transfer. To the server the request looks entirely legitimate. It is part of category **A01**.

## When it occurs

- A state-changing action relies on a predictable request (a known URL or form structure).
- The browser automatically attaches session cookies (ambient authority).
- The server does not verify that the request was made deliberately inside the application.

## When the application is safe

| Protection | How it works |
|---|---|
| **Anti-CSRF token** | a random, unpredictable token tied to the session, required for every state-changing action |
| **SameSite** | a cookie with the `Lax` or `Strict` attribute is not sent in cross-site requests |
| **Double submit cookie** | the same random value in a cookie and in a parameter; the server compares them |
| **Re-authentication** | a password or MFA code again for critical actions |
| **Origin/Referer check** | the server verifies the request comes from its own domain |
| **Fetch Metadata** | the server rejects state-changing requests with `Sec-Fetch-Site: cross-site` |
| **Custom header for APIs** | the API requires a header (e.g. `X-Requested-With`) that a cross-site form cannot set without a CORS preflight |

## SameSite, GET-based CSRF and JSON

SameSite and the content type change how exploitable an endpoint is, but each has gaps:

- **SameSite is a defence-in-depth measure, not a full defence.** It only governs the cookie, and "same-site" is broader than "same-origin": an open subdomain or an XSS on any same-site host can still issue a request with the cookie.
- **`Lax` still allows GET.** `Lax` (the default for cookies without SameSite in Chromium-based browsers; Firefox and Safari do not apply it) sends the cookie on top-level navigations with safe methods, so a state-changing `GET` (or an action that also accepts `GET`) stays exploitable through a link or redirect. Never let `GET` change state.
- **Lax+POST grace window.** For about 2 minutes after a cookie without SameSite is set, Chromium still sends it on a top-level cross-site `POST` — a window that defeats relying on `Lax` alone.
- **`Strict` breaks inbound links.** It blocks cross-site sending but logs the user out when they follow a link in, so apps often pair a `Strict` action cookie with a separate read cookie.
- **The JSON content type helps, if enforced.** A body with `Content-Type: application/json` forces a CORS preflight that an HTML form cannot send. But if the server also accepts form-encoded or `text/plain` bodies, a form can send a "simple request" with no preflight — forgeable. Enforce the content type and reject anything else.
- **CORS is a separate control.** A permissive CORS policy (reflecting `Origin` with credentials) enables cross-origin reads, not CSRF — do not confuse the two.

## Double submit pitfalls

Naive double-submit (the cookie value must equal the body token) assumes the attacker cannot set the cookie. That assumption fails if a sibling subdomain or a MITM on a non-HTTPS cookie can plant a chosen value into the cookie and send the matching token — the check passes. Harden it:

- bind the token to the session by signing it (HMAC / signed double-submit), not a bare random value,
- set the cookie with the `__Host-` prefix so sibling subdomains cannot overwrite it,
- prefer the stateful synchronizer token where you can keep server-side state.

## How to test

1. In the proxy history, filter state-changing requests (`POST`, `PUT`, `DELETE` and action `GET`s). Pick the critical ones: changing a password, data, permissions.
2. Check whether there is a token (`csrf`, `_token`, `authenticity_token`) and where: in the `POST` body (best), in a header, or in the URL (bad, it leaks into logs).
3. Check the `Set-Cookie` header: `SameSite=Strict` almost rules out CSRF, `Lax` reduces it (but see GET and the grace window), no attribute is the highest risk.
4. In Repeater, test the token:
    - remove the token parameter,
    - leave it empty (`csrf=`),
    - change one character,
    - substitute a token from another session (the most common flaw: the server checks validity but not binding to the session),
    - change the method from `POST` to `GET` (verb tampering),
    - change `Content-Type` to `text/plain` or form-encoding to see whether a non-preflighted body is accepted.
5. If any test passes, build a minimal PoC (`csrf.html` with an auto-submitting form) and open it in a browser logged in as the victim (your own test account).

!!! tip "XSS bypasses CSRF"
    XSS defeats every CSRF defence: the script runs in the same origin, so it can fetch the page with the form, read the token from the HTML or a response and send the request, and the browser attaches the session cookie itself. `HttpOnly` does not help here. That is why XSS and CSRF are considered together.

!!! warning "Login CSRF"
    CSRF also works on login forms: forcing the victim's browser to log in as the attacker, so the victim's later actions land in the attacker's account. Protect the login form with an anti-CSRF token too.

## Recommendations

- An anti-CSRF token tied to the session for every state-changing action.
- Session cookies with `SameSite=Lax` or `Strict` plus `HttpOnly` and `Secure`; treat SameSite as one layer, not the whole defence.
- Never change state on `GET`; enforce the JSON content type on APIs.
- Rejecting cross-site state-changing requests based on the Fetch Metadata headers (`Sec-Fetch-Site`).
- Extra identity confirmation for critical operations.
