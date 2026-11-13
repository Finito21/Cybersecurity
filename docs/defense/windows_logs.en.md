---
description: "Windows log analysis in Event Viewer: the logs, the structure of an entry, key Event IDs for logons, privilege escalation, persistence and Sysmon."
---

# Windows logs

Logs are a record of system, application and service events. In post-incident analysis they let you reconstruct an incident, detect unauthorised access and malware activity. The main tool is **Event Viewer**.

## Logs and format

- Logs: **Application**, **Security**, **System**, **Setup**, **Forwarded Events** and **Applications and Services Logs**.
- Since Windows Vista, logs are in the binary `.evtx` format (`%SystemRoot%\System32\winevt\Logs`), managed by the **Windows Event Log** service.
- For security the **Security** log matters most, but the System and Application logs should be watched too.
- An event is described by fields such as the source, the identifier (Event ID), the level, the user, the time, the computer and the description.
- Most security events (object access, process creation, policy changes) are only recorded once the relevant **audit policy** (`Advanced Audit Policy`) is enabled.

## Key Event IDs

### Logon and logoff

| ID | Meaning |
|---|---|
| **4624** | successful logon; the logon type field shows the vector: 2 local/interactive, 3 network, 10 RDP |
| **4625** | failed logon; a run of these entries is a sign of brute force or password spraying. The status code tells a wrong password (`0xC000006A`) from an account that does not exist (`0xC0000064`), i.e. password spraying from account enumeration |
| **4634** | logoff (session closed) |
| **4647** | user-initiated logoff |
| **4648** | logon with explicit credentials ("Run as", can indicate lateral movement) |
| **4740** | an account was locked out after repeated failed attempts; in a domain it is logged on the domain controller (the PDC emulator), not on the workstation |

!!! warning "RDP with NLA is logon type 3"
    With Network Level Authentication on (the default), a failed RDP logon is recorded in 4625 as **type 3**, not 10. A search for "4625 type 10" misses RDP brute force.

### Kerberos and NTLM (domain controller)

| ID | Meaning |
|---|---|
| **4768** | a TGT was issued (domain logon) |
| **4769** | a service ticket was issued; RC4 encryption (`0x17`) for service accounts can be a trace of Kerberoasting |
| **4771** | Kerberos pre-authentication failed (wrong password) |
| **4776** | NTLM credential validation |

### Accounts and groups

| ID | Meaning |
|---|---|
| **4720** | a user account was created |
| **4723** | a user changed their own password |
| **4724** | an attempt to reset an account's password (by someone else, e.g. an administrator) |
| **4728 / 4732 / 4756** | a member was added to a global / local / universal group (e.g. Administrators) |

### Privilege escalation and access

| ID | Meaning |
|---|---|
| **4672** | special privileges at logon (an administrative or SYSTEM account) |
| **4663** | an attempt to access an object (file, directory); requires a SACL set on the object |
| **5140** | access to a network share |
| **4660** | an object was deleted |
| **4670** | a change to an object's permissions (ACL) |

### Persistence and signs of malware

| ID | Meaning |
|---|---|
| **4688** | a new process was created; with command-line auditing it also records full arguments (e.g. `powershell.exe` to download and run) |
| **4697** | a service was installed, recorded in the **Security** log (requires auditing) |
| **7045** | a new service was installed, in the **System** log (common with malware and tools such as PsExec) |
| **4698** | a scheduled task was created (a typical persistence method) |
| **4719** | a change to the audit policy (an attempt to hide activity) |
| **1102** | the **Security** log was cleared (covering tracks); the equivalent for other logs is event **104** in the System log |
| **4946–4948** | changes to Windows Firewall rules (a backdoor adding an exception); they need the "MPSSVC Rule-Level Policy Change" audit subcategory, and without it rule changes show up in the firewall's own log (events 2004–2006) |
| **4104** | a PowerShell script block (Script Block Logging, the `Microsoft-Windows-PowerShell/Operational` log); shows the code after decoding |
| **1100** | the event logging service shut down (a possible attempt to stop logging) |

## Sysmon

**Sysmon** (System Monitor from the Sysinternals suite) is a driver and service that extend native logging with richer events written to the `Microsoft-Windows-Sysmon/Operational` log. Useful Event IDs:

- **1** – process creation (with the file hash, command line and parent process),
- **3** – a network connection made by a process,
- **7** – image/DLL load (detecting library hijacking),
- **8** – `CreateRemoteThread` (code injection into another process),
- **11** – file creation,
- **13** – registry value modification (often used for persistence).

A good configuration (e.g. popular noise-reducing templates) is essential. Sysmon does not replace Windows auditing; it complements it with correlation context.

## Working with logs

- **Custom views**: filters by log, level, Event ID, source and date range.
- **Saving events** as evidence: the `.evtx` format (keeps the full structure) or `.xml`/`.csv` for analysis outside Event Viewer.
- **Windows Firewall**: unusual ports (e.g. TCP/4444) and protocols may indicate a backdoor or an attempt to bypass protections.

!!! warning "Clearing logs"
    Clearing or disabling the Security log is a typical part of covering tracks; it leaves Event IDs 4719 and 1102 (or 104 for other logs) and 1100. Logs should be forwarded elsewhere (e.g. to a SIEM) before an attacker can delete them.

## Recommendations

- Enable the audit policy for logon, processes (4688, ideally with command-line auditing) and object access.
- Centralise logs (event forwarding, a SIEM) and set alerts on key Event IDs, especially 1102, 4720, 4698 and 7045.
- Consider deploying Sysmon for deeper visibility into processes, network and the registry.
- Establish a baseline to tell normal activity from anomalies.
