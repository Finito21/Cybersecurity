---
description: "Layer 2 attacks: CAM flooding, VLAN hopping, STP protection, DHCP snooping, DAI, IP Source Guard, port security, and 802.1X and EAP access."
---

# LAN security

Layer 2 attacks (switches) are dangerous because they operate below firewalls and routing: a host on the same segment can sniff or redirect traffic before it ever reaches the firewall. The starting point for defence is controlling who connects to the network and how.

## Attacks on switches

| Attack | Mechanism | Defence |
|---|---|---|
| **CAM flooding (MAC flooding)** | flooding the address table with fake MACs; once it overflows the switch acts as a hub and floods frames to all ports (sniffing) | **port security**: a MAC address limit per port |
| **VLAN hopping (rogue trunk)** | the attacker impersonates a switch and uses DTP to negotiate a trunk, reaching every VLAN | disable DTP (access mode, `switchport nonegotiate`) |
| **VLAN hopping (double tagging)** | a frame with two 802.1Q tags; the switch strips the first (equal to the native VLAN) and forwards the frame into another VLAN | set the native VLAN to an unused VLAN, not assigned to access ports; tag the native VLAN (`vlan dot1q tag native`) |
| **STP manipulation** | spoofed BPDU frames make the attacker's host the root bridge, so traffic passes through it (MITM) | **BPDU guard** and **root guard** |
| **ARP spoofing** | forged ARP replies bind the gateway's IP to the attacker's MAC (MITM) | **Dynamic ARP Inspection (DAI)** |
| **DHCP spoofing** | a rogue DHCP server hands out its own gateway and DNS (MITM) | **DHCP snooping**, trusted ports |
| **DHCP starvation** | exhausting the address pool with fake requests | port security, DHCP snooping rate limiting |

### Port security

- Limits the number of allowed MAC addresses per port; only authorised MACs get access. Defends against MAC flooding and (indirectly) DHCP starvation.
- Addresses: static (configured by hand), dynamic (learned, volatile) and sticky (learned but written into the configuration).
- Violation response:
    - `protect` — silently drops the excess frames,
    - `restrict` — drops and logs (counter, SNMP),
    - `shutdown` — puts the port into error-disabled (the default and safest option).

### VLAN hopping

- **Rogue trunk (switch spoofing)** abuses DTP auto-negotiation: a host impersonates a switch, brings up a trunk and sees the traffic of every VLAN. Defence: static access mode on user ports with DTP disabled; trunking only on designated, manually configured ports.
- **Double tagging** works because the switch strips only the outer tag. The attacker sends a frame with two tags: an outer one equal to the trunk's native VLAN (which is carried untagged) and an inner one pointing at the victim VLAN. The attack is one-way (no reply path). Defence: set the native VLAN to a separate, unused ID that carries no user traffic, tag the native VLAN on trunks (`vlan dot1q tag native`) and allow only the VLANs you need on each trunk (`switchport trunk allowed vlan`).

### STP protection

Both mechanisms defend the spanning tree, but in different places:

- **BPDU guard** is applied to access ports (with PortFast). Any BPDU received there signals an unexpected switch — the port immediately goes into error-disabled.
- **Root guard** is applied to ports facing other switches. If a port receives a superior BPDU trying to take over the root role, it is blocked (root-inconsistent) until the attack stops. It protects a stable root bridge.

### DHCP snooping, DAI and IP Source Guard

Three layers built on one binding table (MAC–IP–port–VLAN) that DHCP snooping populates:

- **DHCP snooping** splits ports into trusted (toward the legitimate DHCP server) and untrusted (users); server replies (OFFER/ACK) from an untrusted port are dropped. It blocks DHCP spoofing and can rate-limit requests (starvation).
- **Dynamic ARP Inspection (DAI)** checks ARP packets on untrusted ports against the binding table; replies with a forged IP–MAC pair are dropped. It blocks ARP spoofing. Hosts with static IPs are not in the DHCP snooping table, so they need ARP ACLs, and uplink ports must be marked trusted; otherwise DAI drops legitimate traffic.
- **IP Source Guard** filters traffic on a port against the binding table — only packets with the assigned source IP (and MAC) are forwarded. It blocks IP address spoofing.

## 802.1X and EAP

**802.1X** is a port-based network access control standard: a device must authenticate before the port forwards any traffic other than the authentication itself.

| Role | Description |
|---|---|
| **Supplicant** | the device (client) that wants to authenticate |
| **Authenticator** | the switch or access point enforcing control on the port |
| **Authentication server** | usually RADIUS, checks the credentials and returns a decision (plus attributes, e.g. a VLAN) |

**EAP (Extensible Authentication Protocol)** is a framework for various authentication methods negotiated between the supplicant and the server:

| Method | Credentials | Trade-off |
|---|---|---|
| **EAP-TLS** | certificates on both sides | strongest, mutual authentication; needs a PKI and client-certificate management |
| **PEAP** / **EAP-TTLS** | server certificate + password inside a TLS tunnel (e.g. MS-CHAPv2) | easier to deploy; requires validating the server certificate, otherwise it is open to impersonation and credential capture |
| **EAP-MD5** | password hash, no tunnel | obsolete: no mutual authentication or encryption, open to dictionary attacks; useless over Wi-Fi |

!!! warning "Server certificate validation"
    In PEAP and EAP-TTLS all credential protection rests on the TLS tunnel. If the supplicant does not validate the server certificate (and the CA name), an attacker can stand up a rogue access point and capture the MS-CHAPv2 exchange.

## Monitoring and access control

- **Active and passive monitoring**: generating and analysing test traffic, or observing traffic without interfering.
- **NAC (Network Access Control)** solutions combine authentication (802.1X, MAC-based authorisation, a captive portal for guests), device compliance checks before admission (patch level, antivirus) and the assignment of an access policy (VLAN, ACL, QoS) based on identity.

## Recommendations

- Enable port security; disable DTP and set user ports to access mode.
- Build DHCP/ARP defence in layers: DHCP snooping, with DAI and IP Source Guard on top.
- Protect STP: BPDU guard on access ports, root guard on inter-switch ports.
- Segment the network into VLANs (employees, guests and critical systems separately); set the native VLAN to an unused ID.
- Authenticate network access (802.1X with EAP-TLS where possible; in PEAP/EAP-TTLS enforce server certificate validation).
