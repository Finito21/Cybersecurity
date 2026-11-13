---
description: "Broken Access Control and IDOR: horizontal and vertical escalation, BOLA and BFLA, mass assignment, testing object permissions and server-side defences."
---

# Access control and IDOR

**Broken Access Control (BAC)** is a flaw where the application lets a user reach data or functions they have no rights to. **IDOR (Insecure Direct Object Reference)** is a special case: an object is referenced by an identifier (e.g. `id=124`) and the server returns it without checking whether it belongs to the logged-in user. It is category **A01** of the OWASP Top 10, and the same class of flaw leads the OWASP API Security Top 10 as **BOLA**.

## Types

| Type | Description | Example |
|---|---|---|
| **Horizontal escalation** | access to the resource of another user with the same role | `GET /invoice/124` returns someone else's invoice |
| **Vertical escalation** | gaining higher privileges | a regular user calls `POST /admin/deleteUser` |
| **Parameter tampering** | changing a business value trusted from the client | `price=1`, `role=admin`, `isAdmin=true` |

## BOLA, BFLA and mass assignment

API testing uses more precise names for the same failures. Knowing which layer is missing a check tells you where to fix it.

| Term | Layer | Maps to | Example |
|---|---|---|---|
| **BOLA** (Broken Object Level Authorization) | object instance | horizontal IDOR | `GET /api/orders/1001` returns another tenant's order |
| **BFLA** (Broken Function Level Authorization) | function / endpoint | vertical escalation | a user calls `DELETE /api/admin/users/5` |
| **Mass assignment** (half of BOPLA, alongside excessive data exposure) | object property | parameter tampering | a request body sets `"role":"admin"` on your own account |

**Mass assignment** happens when the server binds a request body straight onto a data model, so the client can set properties it should never control:

```
PATCH /api/users/me
{ "displayName": "Alice", "role": "admin", "emailVerified": true }
```

If `role` and `emailVerified` are bound automatically, the user escalates their own account. Defence: bind only an explicit allowlist of fields (a DTO / input schema), never the whole request object, and set privileged fields on the server.

## When it occurs

- The object identifier comes straight from the client and is not tied to the session.
- An admin function is hidden only in the interface, but the endpoint works for anyone (BFLA).
- The server trusts fields sent by the browser (`role`, `price`, `discount`) instead of computing them itself.
- The request body is bound onto a model without an allowlist, so extra properties are accepted (mass assignment).
- The API accepts an action (`action=delete&id=10`) without checking permissions.

## When the application is safe

- For every request the server checks whether the logged-in user is allowed to access the **specific** object, not just whether they are logged in.
- Business values (prices, discounts, roles) are computed and fetched on the server.
- Request bodies bind only allowlisted fields; privileged properties are ignored when sent by the client.
- Default deny: no allow rule means no access.
- Hard-to-guess identifiers (UUIDs) make an attack harder but **do not replace** permission checks.

## How to test

1. Log in as user A and find a request to a resource (e.g. `GET /api/orders/1001`).
2. Send it to Repeater and change only the identifier to a neighbouring one or one belonging to user B (BOLA / horizontal).
3. Compare the responses (the Comparer module). Red flags:
    - `200 OK` with someone else's data,
    - `302` to the login page, but the response body still contains data,
    - a constant `200` with a "soft" error (`{"error":"not allowed"}`) that the interface hides.
4. For vertical escalation / BFLA, take an administrator request and replay it with a regular user's session, and test method swaps (e.g. `GET`→`POST`). Test destructive actions (deleting, changing data) only on objects you created yourself.
5. For parameter tampering, change one field (`price`, `role`); for mass assignment, add a field the form never sends (`"role":"admin"`) and check whether the server accepts it (it comes back in the response or changes state).

!!! example "From the lab"
    In a CRM application the request `POST /products` with `action=delete&id=10` deleted a product, even though a regular user's interface had no such option. The backend did not check the role: broken function-level authorization and parameter trust at once.

## Recommendations

- Check object permissions on the server, on every request, in one shared mechanism (a central authorisation layer).
- Do not trust any client value that affects permissions or price.
- Bind only allowlisted input fields; keep privileged properties under server control.
- Apply least privilege: each role and account gets only the access its tasks require.
- Automated tests: the same set of requests for different roles should produce different results.
