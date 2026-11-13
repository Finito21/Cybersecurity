---
description: "Wi-Fi security: WEP weaknesses, WPA2 and the handshake, KRACK, WPA3 SAE and transition mode, protected management frames, evil twin and deauth, auditing."
---

# Wireless networks

A wireless network is harder to secure than a wired one, because the medium (radio waves) is available to anyone in range. You cannot gate access with a cable or a switch port, so strong link-layer encryption and access control are essential.

## Encryption standards

| Standard | State | Notes |
|---|---|---|
| **WEP** | broken | RC4 stream cipher and short, reused initialisation vectors (IV); the key can be recovered in minutes from captured traffic. Must not be used |
| **WPA/TKIP** | obsolete | TKIP was a retrofit for WEP-era hardware; known attacks, being phased out |
| **WPA2** | common | AES-CCMP; a strong cipher, but the PSK is open to offline dictionary attack once the 4-way handshake or the PMKID is captured |
| **WPA3** | recommended | SAE (dragonfly) key exchange with forward secrecy; resistant to offline dictionary attacks and mandates protected management frames |

!!! note "PSK vs Enterprise"
    **Personal (PSK)** mode shares one password across the whole network. **Enterprise (802.1X/EAP)** mode authenticates each user individually against a RADIUS server, giving per-user credentials, revocable access and better logging. In a business environment, prefer Enterprise.

## WPA2: the handshake and KRACK

WPA2-PSK security rests on the **4-way handshake**, which derives session keys between the client and the access point from the password (PSK).

- **Offline dictionary attack.** Capturing the handshake (just the frames exchanged when a client joins) lets an attacker test password candidates **locally**, with no further contact with the network. Since 2018 the **PMKID** attack has also been known: an identifier derived from the password can be taken from the access point itself, with no client connected and no deauth. Weak or dictionary PSKs fall quickly. Defence: a long, random passphrase, and WPA3, where this offline attack is not possible.
- **KRACK (Key Reinstallation Attack).** A flaw in the handshake protocol itself: the attacker forces a party to **reinstall an already-in-use key**, resetting nonce/replay counters and enabling replay and partial decryption of frames. It needs no knowledge of the password. Defence: apply client and AP patches.

## WPA3: SAE and transition mode

WPA3 replaces PSK key derivation with **SAE (Simultaneous Authentication of Equals)**, built on the dragonfly handshake.

- **Resistance to offline attack.** Each password guess requires interaction with the network, so candidates cannot be tested from captured traffic alone. It also provides **forward secrecy** — compromising the password does not decrypt previously recorded sessions.
- **Transition mode.** A network advertising both WPA3 and WPA2 for backwards compatibility can be **downgraded**: the attacker lures a client into connecting over WPA2 and replays the classic handshake attack. In this mode PMF is only optional for WPA2 clients. Where feasible, enforce **WPA3-only** for sensitive networks.
- **Dragonblood.** A family of side-channel and downgrade attacks against early SAE implementations; mitigated by firmware updates and by **SAE Hash-to-Element (H2E)**, which the 6 GHz band (Wi-Fi 6E) requires.

## Protected management frames (PMF / 802.11w)

In classic Wi-Fi, management frames (including **deauthentication** and disassociation) are unauthenticated, so anyone in range can forge them. Hence **deauth** attacks: spoofed frames kick clients off the network, used either to disrupt service (DoS) or to force a reconnect and capture the handshake.

**802.11w (Protected Management Frames, PMF)** cryptographically protects critical management frames and blocks forged deauths. PMF is **mandatory in WPA3** and optional in WPA2 — enable it wherever the hardware allows.

## Threats

- **Eavesdropping**: with weak or no encryption, traffic can be captured passively from the air.
- **Rogue AP vs evil twin**: a *rogue AP* is an unauthorised access point plugged into the network (e.g. brought in by an employee), bypassing perimeter control. An *evil twin* is an AP impersonating a trusted SSID to lure victims into connecting for MITM or phishing (a fake login portal).
- **Deauth / disruption**: abuse of management frames to kick clients off (see PMF above). Even in an audit of your own network, limit deauth to your own test clients; disrupting other people's devices in range is illegal.
- **Attacks on APs and the router**: default admin passwords, outdated firmware, an exposed management panel, WPS (its PIN falls to brute force or the Pixie Dust attack).
- **Phishing and spoofing**: fake portals and a lack of user awareness.

## Auditing a wireless network

An audit is only run on your own network or with the owner's written permission. A typical sequence:

1. **Inventory**: access points, encryption standards and modes (PSK/Enterprise, PMF), the router, switches, end devices.
2. **Identifying weaknesses**: WEP/WPA-TKIP, WPA3 transition mode, no PMF, default passwords, WPS enabled, no segmentation (VLANs), no firewall, outdated software, no policies.
3. **Threats**: external (eavesdropping, evil twin, MITM, deauth) and internal (rogue AP, unauthorised access, malware, data loss).
4. **Modernisation recommendations**, prioritised.

## Recommendations

- Migrate from WEP/WPA-TKIP to **WPA3** (or at least WPA2-AES with a long, random password); for sensitive networks use WPA3-only, without transition mode.
- Enable **PMF (802.11w)** and disable WPS.
- In business environments, use **WPA2/WPA3-Enterprise (802.1X)** instead of a shared PSK.
- Change default passwords and update device firmware regularly.
- Separate networks for employees, guests and critical systems (VLANs, separate SSIDs); for guests, **OWE (Wi-Fi Enhanced Open)** instead of an open network, which encrypts traffic without a password.
- Strong authentication (MFA), role-based access, a firewall and IDS/IPS with rogue-AP detection.
- User training and a policy for mobile device use (BYOD).
