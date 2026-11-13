---
description: "Access control lists: packet filtering, the implicit deny, rule order, direction, wildcard masks, and standard versus extended ACLs."
---

# Access control lists

An **access control list (ACL)** is an ordered list of rules that permit or block traffic based on packet criteria. A router (or a layer 3 switch) acts as the filter, and each rule is an access control entry (**ACE**). An ACL is a practical implementation of the default-deny principle.

## How it works

- Rules are processed **sequentially**, from the top; **the first match decides** and the rest are skipped.
- At the end of every list there is an **implicit deny**: traffic with no matching rule is dropped. That is why a list with no permit rule blocks all traffic.
- Rule order matters: a more specific rule goes before a general one (otherwise the general rule shadows the specific one, which then never fires).
- One interface takes one list per protocol and direction (e.g. one inbound and one outbound for IPv4).

## Direction of application

A list only takes effect once it is applied to an interface with a direction — from the router's point of view:

- **inbound (in)**: filters packets as they enter the interface, before the router processes and routes them; this is cheaper, because dropped traffic never burdens routing;
- **outbound (out)**: filters packets already routed, just before they leave the interface.

## Wildcard masks

A wildcard mask defines which address bits are matched. It is the inverse of a subnet mask:

- a mask bit of **0**: match the corresponding address bit,
- a mask bit of **1**: ignore the corresponding address bit.

Examples:

- `192.168.1.0 0.0.0.255` — the whole `192.168.1.0/24` subnet;
- `0.0.0.0 0.0.0.0` (the `host` keyword) — a single address;
- `0.0.0.0 255.255.255.255` (the `any` keyword) — any address.

## Types of list

| Type | Criteria | Use |
|---|---|---|
| **Standard** | source IP address only | a simple filter near the traffic's destination |
| **Extended** | source and destination, protocol, ports, flags | a precise filter near the traffic's source |

Lists can be **numbered** or **named**; named ones are clearer and easier to edit. In Cisco IOS the numbering is, for example, 1–99 and 1300–1999 (standard) and 100–199 and 2000–2699 (extended) — the details depend on the vendor.

An example of a named extended list in Cisco IOS: it allows HTTPS to the web server and logs and drops the rest of the traffic from the subnet.

```text
ip access-list extended WEB-IN
 remark HTTPS to the web server
 permit tcp 192.168.10.0 0.0.0.255 host 10.0.0.80 eq 443
 deny   ip any any log
!
interface GigabitEthernet0/1
 ip access-group WEB-IN in
```

## Good practice

- **Standard ACLs** go near the destination (they match on source only, so placing them too early would cut off too much). **Extended ACLs** go near the source and are applied inbound, to drop unwanted traffic before it crosses the network.
- Document the rules (comments/`remark`); named ACLs are clearer than numbered ones.
- Test after deployment: the implicit deny can block traffic you forgot about (e.g. DNS, DHCP, return traffic of a session).
- A basic ACL is a stateless filter, not a full firewall; stateful filtering (allowing replies only for sessions started inside) needs a firewall with stateful inspection. Cisco IOS also offers partial measures: the `established` keyword, reflexive ACLs and the zone-based firewall (ZBF).

## Recommendations

- Apply least privilege: permit only the traffic that is needed and leave the rest to the implicit deny.
- Order rules from specific to general and mind the direction applied to the interface.
- Review the rules regularly and remove outdated ones.
- Log denials on critical lists (an explicit `deny ... log` rule before the end) to detect access attempts.
