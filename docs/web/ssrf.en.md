---
description: "Server-Side Request Forgery: reaching the internal network and cloud metadata, out-of-band testing, bypassing blocklists and blind SSRF."
---

# SSRF

**Server-Side Request Forgery (SSRF)** is a vulnerability where an attacker forces the server to send a request to an address they choose. The server becomes a proxy, which lets them reach internal resources unreachable from the internet, scan the internal network from behind the firewall, read cloud metadata (`169.254.169.254`) or local files (`file://`). In the OWASP Top 10 2025 it is part of **A01 Broken Access Control** (its own category, A10, in the 2021 edition).

## When it occurs

Anywhere the application accepts a URL or IP address and fetches data from it without verification: importing data from a URL, PDF and page-screenshot generators, loading avatars, link previews, webhooks and API integrations.

## When the application is safe (defence in depth)

- An **allowlist** of permitted domains and addresses instead of a blocklist; validate *after* resolving the name to an IP, and pin exactly that verified address to the connection (otherwise DNS rebinding swaps the IP between the check and the request).
- Block whole ranges, not single addresses: loopback (`127.0.0.0/8`, `::1`), link-local including metadata (`169.254.0.0/16`), private (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), `0.0.0.0/8` (on Linux `0.0.0.0` reaches localhost), CGNAT (`100.64.0.0/10`), ULA (`fc00::/7`, including the AWS IPv6 metadata address `fd00:ec2::254`) and IPv4-mapped IPv6 addresses (`::ffff:127.0.0.1`).
- Not following redirects, or re-validating the target on every redirect.
- Validating the response (whether it is actually the expected resource type).
- Network isolation: the application server has no access to critical internal services.

## How to test

The free Burp has no Collaborator module, so you need an external server to listen.

!!! warning "Limits of an SSRF test"
    - On engagements, use your own listener (your own VPS or a self-hosted interactsh); public services such as webhook.site only in labs, because they store client data with a third party.
    - With cloud metadata, stop at confirming access; do not fetch the role credentials (`iam/security-credentials`).
    - Only confirm that internal services (Redis, MySQL) are reachable; do not send them commands that change state.

1. Find a function that fetches data from a URL and send the request to Repeater.
2. Replace the vulnerable parameter (`url=`, `image=`, `src=`, `endpoint=`) with a unique address on your listener. A request appearing in its log confirms SSRF (the server made an outbound connection).
3. Test ports and protocols: `http://listener.example:8080/id`, `file:///etc/passwd`, `gopher://`, `dict://`.
4. Aim at internal resources: `http://127.0.0.1`, `http://169.254.169.254/latest/meta-data/`, common service ports (`:6379` Redis, `:3306` MySQL).
5. Check whether the validation withstands the usual blocklist bypasses:

```text
http://2130706433        # 127.0.0.1 in decimal
http://0x7f000001        # 127.0.0.1 in hex
http://127.0.0.1.        # trailing dot
http://localtest.me      # a domain that resolves to 127.0.0.1
http://[::1]/            # IPv6 loopback
http://[::ffff:7f00:1]   # 127.0.0.1 as an IPv4-mapped IPv6 address
```

6. **Blind SSRF** (the server only returns "OK"): compare response times (`127.0.0.1` faster than an external address) and check the request headers in your listener's log (e.g. the `User-Agent` reveals the library and hints at next steps).

!!! warning "DNS rebinding and redirects defeat validation"
    Checking a URL or IP *before* the request is not enough if the server resolves the name a second time at connect time. In **DNS rebinding** the attacker controls a domain with a short TTL: the first lookup returns a public address (which passes validation), the next returns an internal address that the server actually uses. Likewise a **3xx redirect** from a trusted domain can send the client to `169.254.169.254` or `127.0.0.1` if it blindly follows `Location`. Defence: pin the verified address to the connection and do not trust redirects (or validate every hop).

!!! example "From the lab"
    An endpoint in a CRM application accepted a full address (`endpoint=...&product_id=1`). This let the server's requests be directed wherever the attacker wanted: a classic SSRF through a configurable endpoint.

## Recommendations

- An allowlist of target addresses, blocking private, link-local and metadata ranges, no redirects, and pinning the verified IP to the connection.
- A separate, isolated component (an egress proxy) for fetching external resources.
- In the cloud, enforce IMDSv2: metadata first requires a token (a `PUT` request with a TTL header) before any data can be read, so a simple `GET`-style SSRF cannot reach the role credentials. For containers, also set the response hop limit to 1 so a container cannot reach the host's metadata. It is a hardening measure, not a replacement for network segmentation.
