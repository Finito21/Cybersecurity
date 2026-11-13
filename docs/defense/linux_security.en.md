---
description: "Linux security: permissions, the SUID bit and capabilities, common escalation paths (sudo, cron, timers), firewall, hardening and auditd/journald monitoring."
---

# Linux

The basics of Linux security from the defender's perspective: permissions, common escalation paths and hardening. Offensive techniques are described so you know what to harden and what to look for in an audit.

## Permissions

- File permissions: read, write, execute, separately for the owner, the group and others (`ls -la`).
- Octal notation: `chmod 640` is read and write for the owner, read for the group, nothing for others.
- The **SUID bit** lets a file run with the owner's privileges (the letter `s` in the owner field). The related **SGID** bit does the same for the group, and the **sticky bit** protects files in shared directories (e.g. `/tmp`).
- A poorly chosen SUID on a program that can spawn a shell or read arbitrary files is a path to escalation. Inventory with: `find / -perm -4000 -type f 2>/dev/null`.
- **Capabilities** (POSIX capabilities) split root's privileges into smaller rights granted to individual binaries (`getcap -r / 2>/dev/null`). Capabilities such as `cap_setuid` or `cap_dac_read_search` can be as dangerous as SUID.

!!! note "GTFOBins"
    **GTFOBins** is a catalogue of "living off the land" Unix binaries that, when given SUID, allowed via `sudo` or granted a capability, let you break out of a restricted shell, read or write arbitrary files, or obtain root. Cross-check SUID and `sudo` audit results against this list to judge the real risk.

## Common privilege escalation paths

Common paths include:

- **Kernel exploits**: using a flaw in a vulnerable kernel version (check `uname -a`, exploit databases).
- **sudo misconfiguration**: commands allowed without a password (`sudo -l`), or programs that can spawn a shell.
- **Dangerous capabilities**: binaries granted `cap_setuid+ep` and similar capabilities.
- **A writable `/etc/passwd` or `/etc/shadow`**: adding an account with root privileges. A *readable* `/etc/shadow` is a risk too, because the hashes can be cracked offline.
- **Cron jobs and systemd timers**: a script run with high privileges that you can write to; this also covers writable `.service` and `.timer` units.
- **Services running as root**: e.g. a misconfigured Docker. Membership of the `docker` group (access to its socket) is equivalent to root.

!!! note "Context"
    These techniques are described to understand what to harden and what to look for in an audit. They are used only on your own or authorised systems.

## Firewall and ports

- Closing unused ports and blocking unnecessary protocols reduces the attack surface.
- The default-deny principle: permit only the traffic that is needed (e.g. SSH from selected addresses) and block the rest.
- Tools: `iptables`/`nftables`, `ufw`, and for automatically blocking addresses after repeated failed attempts, `fail2ban`.

A minimal nftables ruleset with default deny (SSH only from the admin network):

```text
table inet filter {
  chain input {
    type filter hook input priority 0; policy drop;
    ct state established,related accept
    iif "lo" accept
    ip saddr 192.168.50.0/24 tcp dport 22 accept
  }
}
```

## Hardening and monitoring

- System and package updates (patching known CVEs).
- Least privilege: separate service accounts, no unnecessary root access, carefully configured `sudo`.
- Disabling unnecessary services and accounts, changing default passwords, hardening SSH in `sshd_config`: `PermitRootLogin no`, `PasswordAuthentication no`, `KbdInteractiveAuthentication no`, `AllowGroups` with a chosen group and `MaxAuthTries`.
- **Logs and monitoring**:
    - `/var/log` (`auth.log`, `syslog`) and `journalctl` to review events (e.g. `journalctl -u ssh` on Debian and Ubuntu, `journalctl -u sshd` on RHEL and Fedora); `Failed password` and `Invalid user` entries are password and account guessing. Enable persistent journald storage.
    - **auditd** records system calls and file access according to rules (`auditctl`, reviewed with `ausearch`/`aureport`) and adds "who, what, when" context to authentication logs; an example rule: `-w /etc/passwd -p wa -k identity`.
    - **File integrity monitoring**: AIDE or Tripwire compare the system against a baseline; `dpkg --verify` and `rpm -Va` also help.
    - Alerts on unusual processes, new accounts and listening connections.

## Recommendations

- Regularly review SUID/SGID files, granted capabilities and the `sudo` configuration.
- Keep the kernel and packages updated; remove unnecessary services.
- Enable auditd and file integrity monitoring; centralise authentication logs and monitor the creation of new accounts and services.
