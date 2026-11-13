---
description: "Interview questions for a web application pentester role with short answers: HTTPS, HSTS, XSS, privilege escalation, caching and JWT."
---

# Interview questions

Questions collected while preparing for pentester interviews. They check not only knowledge of attacks but also an understanding of how the browser and protocols work.

??? question "What happens technically when you open an https://… address in a browser?"
    The browser resolves the name in DNS, opens a TCP connection (or QUIC with HTTP/3), performs the TLS handshake (key exchange, verification of the certificate and the chain of trust), sends an HTTP `GET` request, receives the response, parses the HTML, fetches resources (CSS, JS, images) and runs scripts according to the policies (Same-Origin Policy, CSP).

??? question "How does encryption in HTTPS work, and why does typing http:// open the https:// version?"
    In the TLS handshake, asymmetric cryptography is used to authenticate the server and agree on a session key, and the data is encrypted with a fast symmetric cipher. The switch to HTTPS comes from a server redirect and the **HSTS** header (`Strict-Transport-Security`): after the first visit the browser itself replaces `http://` with `https://` for the given time. The HSTS preload list works even on the first visit.

??? question "Is DOM XSS a stored XSS or a reflected XSS?"
    Neither: it is a separate category. In DOM XSS, malicious data reaches a dangerous function (e.g. `innerHTML`) in a client-side script; the server may never see it (e.g. the URL fragment after `#`). The data source itself can be persistent or reflected.

??? question "What is the difference between horizontal and vertical privilege escalation?"
    **Horizontal**: access to the data or functions of another user with the same role (e.g. someone else's orders, IDOR). **Vertical**: gaining a higher role (e.g. a regular user performs administrator actions).

??? question "Injected JavaScript looks correct in the page source but does not run. Why?"
    Most often **Content Security Policy** blocks it: the policy forbids inline scripts or scripts from sources outside the list. Other causes: a `<script>` inserted via `innerHTML` is never executed (the HTML5 spec says so), data inserted with `textContent` instead of HTML, a context where the code is not interpreted, a sandboxed `iframe`.

??? question "How do you confirm Blind SQL Injection?"
    By comparing responses to a condition that is always true and one that is always false (a difference in content or length: the boolean variant), or by measuring response time with a deliberate delay on the database side (the time-based variant). Forcing an outbound connection to a server you control (out-of-band) also helps. Details: [SQL Injection](../web/sql_injection.md).

??? question "What is DNS rebinding?"
    The attacker controls a domain whose DNS record has a very short time to live. First the domain points to the attacker's server, and after the page loads it points to an internal address (e.g. `127.0.0.1` or a router in the victim's network). The browser still treats it as the same origin, so a script can talk to the internal service. Defence: checking the `Host` header, authenticating local services, blocking DNS responses with private addresses.

??? question "What mistakes can be made when adding a cache?"
    Caching a response with private data and serving it to other users (**Web Cache Deception**), or caching a response modified by the attacker through an unkeyed header (**Web Cache Poisoning**). The causes are differences in how the cache and the server interpret paths, and missing `Cache-Control: no-store, private` headers. Details: [Cache and headers](../web/cache_and_headers.md).

??? question "The session cookie is a JWT. What should you look for?"
    Acceptance of the `none` algorithm or no signature check, a weak HMAC secret, algorithm confusion (RS256 and HS256), no expiry (`exp`) and no revocation on logout, roles in the payload that the server trusts without checking, sensitive data in the payload (it is only encoded). Details: [Sessions and authentication](../web/sessions.md).

??? question "You found a stored self-XSS (visible only on your own account). How do you assess its real impact?"
    Check whether it can be combined with **CSRF** (forcing the payload to be saved on the victim's account), with **login CSRF** or forcing the victim to log in to the attacker's account, with **Web Cache Poisoning** or Deception (the page with the payload is cached for others), and with a feature that lets other users view or share the profile.
