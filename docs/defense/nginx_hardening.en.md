---
description: "NGINX server hardening: hiding the version with server_tokens, request and connection limits, security headers, TLS configuration and upload limits."
---

# NGINX

Even a basic web server configuration significantly raises the security of the applications it serves. These notes show what to set first.

## Hiding the version

```nginx
http {
    server_tokens off;   # the server does not advertise its version in the Server header or error pages
}
```

This is a small change, but the one most often cited: it makes it harder for an attacker to pick an exploit for a specific version.

## Request and connection limits

They limit brute force and application DoS attacks:

```nginx
http {
    limit_req_zone  $binary_remote_addr zone=reqs:10m  rate=10r/s;   # general limit
    limit_req_zone  $binary_remote_addr zone=login:10m rate=5r/m;    # login: 5 attempts a minute
    limit_conn_zone $binary_remote_addr zone=conns:10m;

    server {
        limit_req_status  429;   # 429 Too Many Requests instead of the default 503 Service Unavailable
        limit_conn_status 429;

        location / {
            limit_req  zone=reqs burst=20 nodelay;
            limit_conn conns 10;
        }

        location /login {
            limit_req  zone=login burst=5;
        }
    }
}
```

`burst` allows short traffic spikes, and `nodelay` serves them immediately instead of queuing. A general limit of 10 requests a second would still allow tens of thousands of password guesses an hour, so login gets its own, much stricter zone.

Behind a reverse proxy or CDN, limit by the real client address: configure `real_ip` (`set_real_ip_from`, `real_ip_header X-Forwarded-For`, `real_ip_recursive on`), otherwise `$binary_remote_addr` points at the proxy and one key covers everyone.

!!! warning "set_real_ip_from only for trusted addresses"
    List only the ranges of your own proxies or CDN in `set_real_ip_from`. A range that is too broad lets a client send any `X-Forwarded-For`, get around the limits and put someone else's address in the logs.

## Security headers

```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "SAMEORIGIN" always;
add_header Content-Security-Policy "default-src 'self'" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

`default-src 'self'` is a very strict starting point for a CSP: tune it to the application's assets (scripts, styles, images from a CDN). The `always` flag sends the header on error responses (4xx/5xx) as well.

!!! warning "add_header inheritance"
    `add_header` directives **do not accumulate** across blocks. If any `location` (or `server`) sets its own `add_header`, it replaces *all* the headers from the parent blocks — the ones from `http`/`server` are then not sent. Repeat the full set of headers in every block that adds its own, or move them to a file and pull it in with `include`.

Details of each header: [Cache and headers](../web/cache_and_headers.md).

## TLS

```nginx
server {
    listen 443 ssl;
    http2  on;                        # NGINX >= 1.25.1 (earlier: listen ... http2;)
    server_name example.com;

    ssl_certificate     /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

    ssl_protocols             TLSv1.2 TLSv1.3;   # no SSLv3 or TLS 1.0/1.1
    ssl_prefer_server_ciphers off;               # with TLS 1.3 let the client pick the cipher
    ssl_session_cache         shared:SSL:10m;
    ssl_session_timeout       1d;
    ssl_session_tickets       off;
}
```

!!! note "OCSP stapling"
    Let's Encrypt shut down OCSP in 2025 and its certificates no longer carry an OCSP URL, so `ssl_stapling` does nothing with them. With a CA that still runs OCSP, stapling also needs `ssl_trusted_certificate` (the CA chain) and a `resolver` directive.

- Generate the exact cipher set and parameters with the [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/) (the *intermediate* profile, or *modern* when you do not need older clients).
- Certificates from a trusted CA (e.g. Let's Encrypt / certbot); automate renewal and monitor the expiry date.
- Force `http` → `https` with a separate `server` block on port 80 doing a 301 redirect. Enable HSTS only once the whole domain (and its subdomains) works over HTTPS, because it blocks any fallback to HTTP for the `max-age` period.

## Other settings

- `client_max_body_size` limits the size of uploaded files (protection against overload and upload abuse).
- `autoindex off` disables directory listing.
- Limiting HTTP methods to those needed, blocking access to hidden files and copies (`.git`, `.env`, `*.bak`).
- Putting a **WAF** in front of the application is a worthwhile extra layer.

!!! tip "Check the syntax"
    After every change: `nginx -t` (configuration test) and only then reload. Test changes in a non-production environment.

## Recommendations

- Start with `server_tokens off`, request limits and the full set of security headers.
- Keep a modern TLS configuration and up-to-date certificates.
- Minimise the surface: disable directory listing, limit methods and request size.
