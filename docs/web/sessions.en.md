---
description: "Sessions and authentication: hijacking and fixation, secure cookies, JWT flaws, algorithm confusion and kid, refresh tokens and login protection."
---

# Sessions and authentication

Because HTTP is stateless, the application recognises a logged-in user by a **session**: an identifier in a cookie or a token. Flaws here lead to account takeover. It is category **A07 Authentication Failures** of the OWASP Top 10.

## Session attacks

| Attack | Description |
|---|---|
| **Session hijacking** | capturing the session identifier (e.g. through XSS or sniffing) and impersonating the user |
| **Session fixation** | forcing a known session identifier on the victim; the server does not change it after login |
| **Session sniffing** | intercepting the identifier from unencrypted traffic |
| **Brute force** | guessing a weak identifier or password |

## A safe session

- A new session identifier after login (protection against fixation).
- Cookies with the `HttpOnly` (not readable by JS), `Secure` (HTTPS only) and `SameSite` flags.
- Invalidating the session on logout and a reasonable expiry time.
- High entropy of the identifier (the Sequencer module in Burp helps assess randomness).

## Authentication

- Brute-force protection: attempt limits, lockouts, delays, CAPTCHA, MFA.
- Passwords stored as a hash with a strong function (bcrypt, argon2) and a salt. A hash in the HTML or an API response is a leak: when changing a password you sometimes see `$2y$12$...` (bcrypt), which should not be there.
- Consistent messages: the login form should not reveal whether a given username exists (account enumeration).
- A password policy and no default credentials.

## JWT

A **JWT (JSON Web Token)** is three Base64URL parts: header, data (payload), signature. The content can be read but not changed without invalidating the signature. A JWT is signed, not encrypted, so it hides nothing.

### Verification flaws

- acceptance of the `none` algorithm, or the signature is not verified at all,
- a weak HMAC secret (crackable offline with a wordlist),
- algorithm confusion (RS256→HS256): the server verifies with HS256 using the RSA **public** key as the HMAC secret, so an attacker signs a forged token with that public key — pin the expected algorithm per key,
- `kid` header abuse: `kid` selects the signing key; if it feeds a file path or SQL query, an attacker can point it at a predictable file or inject SQL to choose a known key — treat `kid` as untrusted and use an allowlist,
- `jku` / `x5u` header abuse: these point to a JWKS or certificate URL; if the server fetches keys from an attacker-controlled URL it will trust attacker-signed tokens — allowlist the host or ignore these headers,
- no `exp`, or no revocation on logout / password change,
- a role or scope in the payload that the server trusts without a check,
- sensitive data in the payload (it is only encoded, not encrypted).

### Refresh tokens

- Pair a short-lived access token with a longer-lived refresh token, so a leaked access token expires quickly.
- Store the refresh token in an `HttpOnly`, `Secure` cookie (not `localStorage`); keep only its hash on the server.
- Rotate on every use: each refresh issues a new refresh token and invalidates the previous one.
- Reuse detection: a refresh token presented after it was already rotated signals theft — revoke the whole token family.
- Keep revocation possible (logout, password change, admin action) via a server-side session or denylist; stateless access tokens alone cannot be revoked before `exp`.

!!! warning "302 at login"
    A common lead is a `302` after login: the browser follows the redirect, but the response body may already contain data or set a session. View the full response in Burp before the redirect happens.

## Recommendations

- Regenerate the session identifier after login, set the cookie flags, invalidate on logout.
- Enforce MFA and limit login attempts.
- Verify the JWT signature and pin the algorithm on the server; never trust `kid`, `jku` or roles from the token without validation.
- Keep access tokens short-lived and rotate refresh tokens with reuse detection.
