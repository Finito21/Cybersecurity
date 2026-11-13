---
description: "Hardening serwera NGINX: ukrycie wersji server_tokens, limity żądań i połączeń, nagłówki bezpieczeństwa, konfiguracja TLS oraz ograniczanie uploadu."
---

# NGINX

Nawet podstawowa konfiguracja serwera WWW znacząco podnosi bezpieczeństwo utrzymywanych aplikacji. Notatka pokazuje, co ustawić w pierwszej kolejności.

## Ukrycie wersji

```nginx
http {
    server_tokens off;   # serwer nie przedstawia się wersją w nagłówku Server i stronach błędów
}
```

To drobna, ale najczęściej wymieniana zmiana: utrudnia atakującemu dobranie exploita pod konkretną wersję.

## Limity żądań i połączeń

Ograniczają brute force i ataki aplikacyjne DoS:

```nginx
http {
    limit_req_zone  $binary_remote_addr zone=reqs:10m  rate=10r/s;   # limit ogólny
    limit_req_zone  $binary_remote_addr zone=login:10m rate=5r/m;    # logowanie: 5 prób na minutę
    limit_conn_zone $binary_remote_addr zone=conns:10m;

    server {
        limit_req_status  429;   # 429 (Too Many Requests) zamiast domyślnego 503 (Service Unavailable)
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

`burst` dopuszcza krótkie skoki ruchu, a `nodelay` obsługuje je natychmiast (zamiast kolejkować). Limit ogólny 10 żądań na sekundę pozwalałby na dziesiątki tysięcy prób hasła na godzinę, dlatego logowanie ma osobną, dużo ostrzejszą strefę.

Za serwerem pośredniczącym (reverse proxy) lub CDN ograniczaj po prawdziwym adresie klienta: skonfiguruj `real_ip` (`set_real_ip_from`, `real_ip_header X-Forwarded-For`, `real_ip_recursive on`), inaczej `$binary_remote_addr` wskaże proxy i jeden klucz obejmie wszystkich.

!!! warning "set_real_ip_from tylko dla zaufanych adresów"
    W `set_real_ip_from` wpisuje się wyłącznie zakresy własnych proxy lub CDN. Zbyt szeroki zakres pozwala klientowi podać dowolny `X-Forwarded-For`, obejść limity i zrzucić winę na cudzy adres w logach.

## Nagłówki bezpieczeństwa

```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "SAMEORIGIN" always;
add_header Content-Security-Policy "default-src 'self'" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

`default-src 'self'` to bardzo restrykcyjny punkt wyjścia dla CSP: dostosuj go do zasobów aplikacji (skrypty, style, obrazy z CDN). Flaga `always` wysyła nagłówek także przy odpowiedziach błędów (4xx/5xx).

!!! warning "Dziedziczenie add_header"
    `add_header` **nie sumuje się** między blokami. Jeśli dowolny `location` (lub `server`) ma własny `add_header`, zastępuje on *wszystkie* nagłówki z bloków nadrzędnych – te z `http`/`server` nie zostaną wtedy wysłane. Powtórz komplet nagłówków w każdym bloku, który dodaje własny, albo wydziel je do pliku i dołącz przez `include`.

Szczegóły każdego nagłówka: [Cache i nagłówki](../web/cache_and_headers.md).

## TLS

```nginx
server {
    listen 443 ssl;
    http2  on;                        # NGINX >= 1.25.1 (wcześniej: listen ... http2;)
    server_name example.com;

    ssl_certificate     /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

    ssl_protocols             TLSv1.2 TLSv1.3;   # bez SSLv3 oraz TLS 1.0/1.1
    ssl_prefer_server_ciphers off;               # przy TLS 1.3 wybór szyfru zostaw klientowi
    ssl_session_cache         shared:SSL:10m;
    ssl_session_timeout       1d;
    ssl_session_tickets       off;
}
```

!!! note "OCSP stapling"
    Let's Encrypt wyłączył OCSP w 2025 i jego certyfikaty nie zawierają już adresu OCSP, więc `ssl_stapling` nic przy nich nie daje. Przy CA, które nadal udostępnia OCSP, stapling wymaga też `ssl_trusted_certificate` (łańcuch CA) i dyrektywy `resolver`.

- Konkretny zestaw szyfrów i parametrów najlepiej wygenerować z [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/) (profil *intermediate*, a gdy starsi klienci nie są potrzebni, *modern*).
- Certyfikaty z zaufanego CA (np. Let's Encrypt / certbot); automatyzuj odnawianie i monitoruj datę ważności.
- Wymuś `http` → `https` osobnym blokiem `server` na porcie 80 z przekierowaniem 301. Nagłówek HSTS włączaj dopiero, gdy cała domena (z subdomenami) działa przez HTTPS, bo blokuje on powrót do HTTP na czas `max-age`.

## Inne ustawienia

- `client_max_body_size` ogranicza rozmiar przesyłanych plików (ochrona przed przeciążeniem i nadużyciem uploadu).
- `autoindex off` wyłącza wyświetlanie zawartości katalogów.
- Ograniczenie metod HTTP do potrzebnych, blokada dostępu do plików ukrytych i kopii (`.git`, `.env`, `*.bak`).
- Przed aplikacją warto wdrożyć **WAF** jako dodatkową warstwę.

!!! tip "Sprawdź składnię"
    Po każdej zmianie: `nginx -t` (test konfiguracji) i dopiero potem przeładowanie. Zmiany testuj w środowisku nieprodukcyjnym.

## Rekomendacje

- Zacznij od `server_tokens off`, limitów żądań i kompletu nagłówków bezpieczeństwa.
- Utrzymuj nowoczesną konfigurację TLS i aktualne certyfikaty.
- Minimalizuj powierzchnię: wyłącz wyświetlanie zawartości katalogów, ogranicz metody i rozmiar żądań.
