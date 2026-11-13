---
description: "Core security concepts: the CIA triad, authentication and authorisation, threat, vulnerability and risk, plus encryption, hashing and encoding."
---

# Security concepts

## The CIA triad

| Property | Meaning | Example of a breach |
|---|---|---|
| **Confidentiality** | only authorised people see the data | a customer database leak, reading someone else's invoice through IDOR |
| **Integrity** | data is not changed without permission | changing a price in the basket, defacing a page |
| **Availability** | the system works when it is needed | a DDoS attack, ransomware encrypting a server |

A test report rates every vulnerability by its impact on the confidentiality, integrity and availability of data.

## Identification, authentication, authorisation

| Step | Question | Example |
|---|---|---|
| **Identification** | who do you claim to be? | entering a username |
| **Authentication** | is it really you? | a password, a hardware key, an MFA code |
| **Authorisation** | what are you allowed to do? | the `admin` role can delete accounts, the `user` role cannot |
| **Accounting** | what did you actually do? | log entries: who, when, which action |

Authentication, authorisation and accounting are together called the **AAA** model; identification comes before them. Note that identification is only a claim of identity, while authentication is what confirms it.

Most critical web bugs are authorisation bugs: the application correctly checks *who* sent the request but not *whether they are allowed* to do it ([Access control and IDOR](../web/access_control.md)).

## Threat, vulnerability, risk

- **Vulnerability**: a weakness in a system, e.g. a parameter that is not validated.
- **Threat**: someone or something that can exploit the weakness, e.g. an attacker on the internet.
- **Exploit**: a way of taking advantage of a vulnerability.
- **Risk**: the likelihood of exploitation combined with the impact.

A vulnerability without a realistic threat (e.g. one that needs physical access to the server room) is low risk; one that is easy to exploit from the internet and exposes data is critical.

## Encryption, hashing, encoding

Three operations on data that are often confused:

| Operation | Reversible? | Key | What it is for |
|---|---|---|---|
| **Encoding** | yes, without a key | no | changing the representation of data (Base64, URL-encoding, hex); gives no confidentiality |
| **Hashing** (digest) | no (one-way) | no (optionally a salt) | integrity and password storage; a fixed-length digest |
| **Encryption** | yes, with a key | yes | confidentiality of data |

A common mistake is "I secured the password with Base64" — that is only encoding, anyone can reverse it. Passwords are stored as a salted hash with a slow function (bcrypt, scrypt, Argon2), not plain SHA. Encryption needs a key and can be reversed; a good hash cannot.

Encryption itself splits into:

- **Symmetric**: the same key encrypts and decrypts (e.g. AES). Fast, but both sides must first securely share one key.
- **Asymmetric**: a key pair — public and private (e.g. RSA, ECC). Slower; used to agree a session key and for digital signatures. What the public key encrypts, only its matching private key can decrypt.

In HTTPS the two are combined: asymmetric cryptography authenticates the server and agrees on a key, and a fast symmetric cipher encrypts the actual traffic. In TLS 1.3 the key is agreed only through (EC)DHE; RSA or ECDSA are used only to sign (to authenticate the server).

## Design principles

- **Defence in depth**: several independent layers of protection, e.g. input validation, parameterised queries, a WAF and minimal privileges for the database account.
- **Least privilege**: users, services and processes get only the rights they need.
- **Default deny**: everything that is not explicitly allowed is forbidden (this is how ACLs and allowlists work).
- **Do not trust the client**: everything that comes from the browser (parameters, headers, cookies, hidden fields) can be changed. The interface may block something, but the server decides.
- **Secure defaults**: no default passwords, test accounts disabled, debug mode off.

## Red, blue and purple teams

| Team | Job |
|---|---|
| **Red team, pentesters** | find and confirm vulnerabilities, simulate an attacker within an agreed scope |
| **Blue team, SOC** | monitor, detect and handle incidents, maintain the defences |
| **Purple team** | joint exercises: each attack is immediately compared with what the defence detected |
