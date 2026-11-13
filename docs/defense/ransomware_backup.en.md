---
description: "Protection against ransomware: the 3-2-1 backup rule, file, disk image and virtual machine backup strategies, encrypting backups and recovery."
---

# Backup and ransomware

**Ransomware** blocks access to a system or encrypts data and demands a ransom. The only reliable way out after a successful attack is **recovery from a backup**, which is why backups are the foundation of defence. These notes are based on a project combining backup and encryption.

## The 3-2-1 rule (and 3-2-1-1-0)

- **3** copies of the data,
- on **2** different media types,
- **1** copy offsite.

The **3-2-1-1-0** extension adds:

- **1** copy offline, air-gapped or immutable,
- **0** errors on restore — the copies are regularly tested and verified.

An offline or immutable copy is essential: ransomware often encrypts connected drives, network shares and any backups reachable from the host too. Immutability is provided by, for example, **Object Lock / WORM**: a copy cannot be overwritten or deleted for a set period. It also holds against a stolen admin account only in **compliance** mode; in governance mode a user with the right permission can lift the lock. Keep the backup storage credentials separate from production (a separate account or tenant, MFA).

## RPO and RTO

Two parameters set the backup schedule and architecture; they follow from business requirements:

- **RPO** (Recovery Point Objective) — how much data you can afford to lose, i.e. the maximum interval between copies. A shorter RPO means more frequent copies.
- **RTO** (Recovery Time Objective) — how quickly you must restore operation. A shorter RTO means faster (often local) recovery paths.

## Backup strategies (from the lab)

| Strategy | Tool | Advantages | Disadvantages |
|---|---|---|---|
| **Copying selected files** | Duplicity (GPG encryption, incremental copies, FTP/SFTP) | small size, can be automated with a dated script | you need to know what to copy |
| **Cloning the whole disk** | Clonezilla (device-device mode or an image) | full recovery of the system and configuration | larger size, longer process |
| **Virtual machine backup** | Proxmox + storage on TrueNAS | automation, flexible management | requires virtual infrastructure |

In the project the storage was **TrueNAS** (a storage pool, a share), and the copies were additionally encrypted to protect them from being read.

## Recovery after an attack

1. Isolate the infected system from the network, but do not power it off: memory holds traces of the attack.
2. Preserve evidence (memory and disk images, logs) before anything is reinstalled.
3. Determine the entry vector and the time of the first intrusion (logs, [post-incident analysis](windows_logs.md)). Attackers often wait weeks before encrypting, so the latest backups may already contain their tools.
4. Reset credentials, especially domain admin accounts and the `krbtgt` account (twice), and close the gap.
5. Rebuild a clean system (reinstall or a clone from before the intrusion), restore the data from a backup taken before the first intrusion and verify its integrity.

## Detection

Ransomware usually gives itself away before it encrypts the data:

- commands that delete backups and restore points: `vssadmin delete shadows`, `wmic shadowcopy delete`, `wbadmin delete catalog`, `bcdedit /set {default} recoveryenabled no` (seen as event 4688 or Sysmon 1, see [Windows logs](windows_logs.md)),
- many files renamed or written in a short time; decoy (canary) files catch this earliest,
- failed backup jobs, retention changes or a disabled backup agent.

!!! warning "Do not count on paying the ransom"
    Payment does not guarantee you get the data back or that copies the attacker stole are deleted, and it funds further attacks. Preserve evidence (disk images, logs), consider reporting to a CERT or law enforcement. The only reliable way out remains working, tested backups.

!!! warning "Test recovery"
    A backup that has never been restored can be useless (a corrupted file, a missing encryption key, an incomplete scope). Regular test restores are part of the strategy.

## Recommendations

- Deploy 3-2-1 with at least one offline or immutable copy.
- Encrypt the copies and store the keys securely (not with the copy).
- Automate backups and monitor their success; test recovery periodically.
- Backup is the last layer: it does not replace updates, segmentation and least privilege.
