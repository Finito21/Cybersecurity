---
description: "System defence: Windows log analysis, Linux security, NGINX server hardening, backups against ransomware and vulnerability scanning."
---

# Defence

The defender's side (blue team): detecting incidents, hardening systems and preparing for an attack.

| Page | What it covers |
|---|---|
| [Windows logs](windows_logs.md) | Event Viewer, key Event IDs, Sysmon, detecting attacks in logs |
| [Linux](linux_security.md) | permissions, SUID and capabilities, escalation, hardening and monitoring |
| [NGINX](nginx_hardening.md) | hiding the version, request limits, headers and TLS |
| [Backup and ransomware](ransomware_backup.md) | backup strategies and recovery after an attack |
| [Vulnerability scanning](vulnerability_scanning.md) | Nessus, OpenVAS, InsightVM and where scanners fit in the process |

!!! tip "Attack and defence together"
    Every vulnerability in the [Web applications](../web/index.md) section has a counterpart on the defence side: detection in the logs, hardened configuration, reduced impact. Read both sections side by side.

!!! warning "Only with permission"
    The techniques described here are used only on your own systems, in a lab or with the owner's written permission, within the agreed scope.
