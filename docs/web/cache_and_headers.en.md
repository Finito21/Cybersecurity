---
description: "Cache security and HTTP headers: web cache deception and poisoning, the HSTS, CSP and X-Frame-Options security headers, and version disclosure."
---

# Cache and headers

## Web Cache Deception and Poisoning

A cache (a CDN or server cache) speeds things up, but a misconfiguration leads to two vulnerabilities:

- **Web Cache Deception**: the attacker makes the cache store a response with the victim's private data, then reads it from the shared cache.
- **Web Cache Poisoning**: the attacker poisons the cache with a response altered through an unkeyed header, which other users then receive.

Both flaws come down to what does (or does not) go into the **cache key**: usually the method, host and path, sometimes selected parameters. Deception exploits a mismatch in how the path is interpreted; poisoning exploits inputs left out of the key that still change the response.

### How to test Web Cache Deception

1. Check the cache headers in responses: `X-Cache`, `CF-Cache-Status`, `Age`, `Via`.
2. Find an endpoint with private data (`/my-account`, `/profile`, `/orders`).
3. Append a static extension (`/my-account.js`) and check whether the response is cached (hit) and whether it shows the data.
4. Test separators and encoded characters (Intruder) and path normalisation:

```text
/static/..%2fmy-account
/my-account%2f%2e%2e%2fstatic
```

The core of it is a **path-interpretation mismatch**: the cache sees a static extension (`.css`, `.js`) and stores the response as a public asset, while the origin server ignores the appended suffix (e.g. it maps `/my-account/anything` to the same page) and returns the logged-in user's content.

### How to test Web Cache Poisoning

The target is an unkeyed header that still reaches the response (an absolute URL, a script link, a redirect).

!!! warning "Always use a cache buster"
    During the test, add a unique parameter to every request (e.g. `?cb=8317`) so that you poison only your own cache key. Without it the poisoned response reaches real users. Drop the parameter only once the impact is confirmed and the client has agreed. The same applies to Web Cache Deception tests.

1. Send a request with a suspect header, e.g. `X-Forwarded-Host`, `X-Forwarded-Scheme` or `X-Forwarded-For`, and check whether its value is reflected in the response body.
2. Confirm the response is cacheable (`Cache-Control`, `X-Cache: hit/miss`, `Age`).
3. Repeat the request **without** the poisoned header but with the same cache buster: if the poisoned response comes back from the cache, every user under that key would receive it.

### Mitigation

- `Cache-Control: no-store, private` for dynamic and personalised content.
- Consistent path interpretation between the CDN and the origin server; do not cache on the extension alone.
- Add any header that affects the response to the cache key, or ignore such headers entirely.
- Mechanisms such as Cloudflare Cache Deception Armor.

## Security headers

| Header | Role |
|---|---|
| `Strict-Transport-Security` (HSTS) | enforces HTTPS; after the first visit the browser replaces `http` with `https` itself |
| `Content-Security-Policy` (CSP) | restricts the sources of scripts and resources; a second layer against XSS |
| `X-Content-Type-Options: nosniff` | forbids MIME type guessing |
| `X-Frame-Options` | older clickjacking protection; only `DENY` or `SAMEORIGIN` |
| `Content-Security-Policy: frame-ancestors` | newer, more flexible protection against framing |
| `Set-Cookie: HttpOnly; Secure; SameSite` | protects session cookies |
| `Referrer-Policy` | limits address leaks in the Referer header |
| `Permissions-Policy` | turns off browser features the page does not need (camera, microphone, geolocation) |
| `Cross-Origin-Opener-Policy` | isolates the page from windows opened by other origins |

!!! note "frame-ancestors supersedes X-Frame-Options"
    `CSP: frame-ancestors` is the newer mechanism and can list multiple origins, whereas the deprecated `X-Frame-Options: ALLOW-FROM` is ignored by modern browsers. To allow framing from specific origins, use `frame-ancestors`. You can send both at once (XFO for older browsers), but on a conflict `frame-ancestors` wins. HSTS works fully from the first visit onwards; an entry on the `preload` list (which needs `includeSubDomains`, a `max-age` of at least a year and the `preload` token) only closes the gap on the very first connection.

!!! warning "X-XSS-Protection is deprecated"
    Do not enable `X-XSS-Protection`: modern browsers ignore it, and the old XSS filter introduced vulnerabilities of its own. Use `X-XSS-Protection: 0` or omit the header and rely on CSP. Scanners still flag it, so be ready to explain this.

## Information disclosure

The `Server`, `X-Powered-By` and `Via` headers reveal software versions (e.g. `Apache/2.4.66`, `PHP/8.4`), which makes it easier to pick an exploit. Full error messages with absolute script paths are also information disclosure (usually LOW in the report, but still reported).

## Recommendations

- Set the full set of security headers (verify with a scanner or in DevTools).
- Hide versions in headers (`server_tokens off` in [NGINX](../defense/nginx_hardening.md)).
- Turn off detailed errors in responses; log them on the server.
