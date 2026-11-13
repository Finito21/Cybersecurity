---
description: "DoS and DDoS attacks: volumetric, protocol and application taxonomy, amplification and reflection, SYN flood mechanics, SYN cookies and defence."
---

# DoS and DDoS attacks

**DoS (Denial of Service)** is an attack that blocks the availability of a service. **DDoS (Distributed DoS)** uses many machines at once (often a botnet), which makes it harder to filter and to stop at the source. The target is the third pillar of the CIA triad: availability.

## Taxonomy of attacks

| Category | Goal | Examples |
|---|---|---|
| **Volumetric** | saturate link bandwidth | UDP flood, ICMP flood, amplification (DNS, NTP, memcached) |
| **Protocol (layer 3–4)** | exhaust state (connection tables, firewalls, load balancers) | SYN flood, ping of death, fragmentation |
| **Application (layer 7)** | exhaust server resources with little traffic | HTTP flood, slow requests (Slowloris), expensive queries |

Volumetric attacks are measured in bits per second (Gb/s) and saturate the link "from outside", protocol attacks in packets per second and application attacks in requests per second. Application attacks can be subtle: small but seemingly legitimate traffic (e.g. expensive database or search queries) exhausts CPU, memory or the connection pool.

## Amplification and reflection

A **reflection** attack abuses intermediary servers: the attacker sends queries with the **victim's source address spoofed**, so the replies go to the victim rather than back to the attacker. When the reply is much larger than the query, this becomes **amplification**: the attacker's small traffic turns into a huge stream aimed at the victim.

- UDP is suited to this because it needs no connection handshake (the source address is easy to spoof).
- **Open** services are abused: DNS resolvers, NTP servers (monlist), memcached. The amplification factor ranges from tens (DNS) through about 550 (NTP monlist) to tens of thousands of times (memcached).
- Systemic defence: **do not expose open resolvers**, and filter source addresses at the edge (**BCP 38 / anti-spoofing**) so the victim cannot be impersonated.

## SYN flood and SYN cookies

A SYN flood is the classic protocol attack against the TCP three-way handshake.

1. The attacker sends a stream of **SYN** packets (usually with a spoofed source address).
2. The server replies with **SYN-ACK** and reserves state for a **half-open** connection in a queue (the backlog), waiting for the **ACK**.
3. The ACK never arrives. The half-open queue fills up, and the server **refuses new, legitimate connections**.

**SYN cookies** neutralise this attack: instead of reserving memory for every SYN, the server encodes the connection state in the sequence number it sends in the SYN-ACK. State is only created once a valid ACK returns (with the reconstructed "cookie"), so the backlog never overflows. On Linux they are turned on by `net.ipv4.tcp_syncookies = 1` (usually the default), and the queue size is set by `net.ipv4.tcp_max_syn_backlog`. Shorter half-open timeouts and edge filtering help as well. The attack shows up as a sudden rise in connections in the `SYN-RECV` state (`ss -s`, `ss -tan state syn-recv`).

!!! warning "Authorised environments only"
    Attack mechanics and traffic-generating tools (e.g. `hping3`) are described only to understand how they work and for tests in your **own isolated** environment or with written permission. Carrying out a DoS attack on someone else's system is a crime (in Poland, for example, Articles 268a and 269a of the Criminal Code).

## Reducing the impact (defence)

Defence is layered: volumetric floods and application-layer attacks need different measures.

- **Rate limiting** and limiting connections per client (see [NGINX](../defense/nginx_hardening.md)); for layer 7, also cap expensive endpoints and drop slow requests early.
- **Upstream / scrubbing protection**: volumetric traffic must be absorbed **above** your own link: at the connectivity provider, a scrubbing centre, or an anycast CDN. A local firewall will not help once the link itself is saturated.
- **SYN cookies** and network-stack hardening against protocol floods.
- **Anti-spoofing (BCP 38)** and no open DNS/NTP resolvers, so you do not fuel amplification attacks.
- **Scaling and redundancy** (clusters), to absorb traffic spikes; a single instance fails sooner than a cluster.
- **Monitoring and alerts**: a sudden rise in traffic, unusual patterns, resource and connection-pool exhaustion.

## Recommendations

- Deploy request and connection limits and anti-DDoS protection appropriate to the service's exposure (upstream/CDN for volumetric traffic).
- Enable SYN cookies and anti-spoofing; close open resolvers.
- Prepare an incident response plan (contacting the provider, traffic redirection and scrubbing procedures).
- Test performance and alert thresholds before an attacker does.
