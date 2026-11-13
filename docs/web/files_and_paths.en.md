---
description: "Path traversal, Local File Inclusion and file upload: reading files outside the directory, web shells, path encoding, null byte and server-side validation."
---

# Files and paths

Three related classes of flaw where the application works with paths or files that come from the user: **path traversal**, **Local File Inclusion (LFI)** and unsafe **file upload**.

## Path traversal

The application joins a path with a parameter without normalising it, so a `../` sequence can leave the base directory and read system files.

```text
../../../etc/passwd                 # relative traversal
/etc/passwd                         # absolute path
....//....//....//etc/passwd        # bypassing a filter that strips ../
%2e%2e%2f  and  %252e%252e%252f     # URL and double URL encoding
..%c0%af  ..%ef%bc%8f               # overlong UTF-8 and fullwidth slash
filename=../../../etc/passwd%00.png # null byte when an extension is required
```

Try different encodings (Burp has an option to encode automatically) and Windows paths (`..\`, `C:\Windows\win.ini`).

!!! warning "The order of normalisation matters"
    A filter that strips `../` **once** and before decoding the input is bypassed by sequences like `....//` or double encoding (`%252e`) — once it has run, `../` reappears. The safe order is always the same: decode fully first, then canonicalise the path (resolve `.`, `..` and symlinks), and only at the end check that the result stays inside the base directory. Validating before normalising guarantees nothing.

!!! note "The null byte is a largely historical technique"
    `%00` truncated the path before a required extension on older runtimes (e.g. PHP < 5.3.4 or C-string-based file APIs). Modern language versions reject an embedded null byte or handle it correctly, so treat it as a vector only on legacy systems, not as a first choice.

## Local File Inclusion

When the application **includes** a file based on a parameter (`?module=network_tester.php`), the attacker can point to another file and, under the right conditions, reach code execution. Example from the lab: `include($_GET['module'])` in a router panel allowed any file to be included.

## File upload

An unsafe upload lets an executable file (a web shell) or a file leading to stored XSS be uploaded. Testing in Repeater: modifying `filename`, `Content-Type` and the body of a `multipart/form-data` request.

Red flags: the server accepts "odd" extensions, the file lands at a predictable URL, the only validation is `Content-Type` (easy to change).

### Validating the type: Content-Type versus magic bytes

- **The request `Content-Type`** comes from the client and is trivial to change — it is not proof of the real file type.
- **Magic bytes (the signature)** are the first bytes of the file (`FF D8 FF` JPEG, `89 50 4E 47` PNG, `25 50 44 46` PDF). Checking them is stronger than `Content-Type`, but still not conclusive: a file can have a valid signature and still contain code.
- **A polyglot** is a file valid in two formats at once — e.g. with a valid image header that is at the same time a valid PHP script. A signature check alone lets it through.

!!! tip "Safety comes from how the file is served, not from type detection alone"
    Because the content can be forged, what matters is that the upload directory **does not execute code** and serves files with an enforced, safe type and `X-Content-Type-Options: nosniff`. Type validation is an extra layer, not the main line of defence.

## When the application is safe

- User data does not reach the file system API directly.
- Comparison against an allowlist, or a check that the value contains only permitted characters, then joining to the base directory, normalising and confirming the result still starts with the base directory.
- Upload: server-side type validation (not just `Content-Type`), a random name, a directory without execute permission, a separate domain for user files.

## Recommendations

- Avoid passing user input into paths; use identifiers mapped to files on the server.
- Normalise and verify the path after joining, not only before.
- Keep user files outside the application directory and serve them without interpretation.
