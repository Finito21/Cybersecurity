---
description: "SQL Injection: what it is, the union, error, boolean and time-based variants, testing in Burp and defence through parameterised queries."
---

# SQL Injection

**SQL Injection (SQLi)** is a vulnerability where user data reaches an SQL query and is interpreted as part of the command rather than as plain text. An attacker can read or change data, bypass login and sometimes run system commands. It is part of the **A05 Injection** category (OWASP Top 10 2025).

## When it occurs

Anywhere user data (URL parameters, form fields, headers, cookies, JSON/XML) is inserted into a query by concatenating text instead of parameterising. This also covers `ORDER BY` and `LIMIT` clauses and column names, which are sometimes built dynamically. Escaping-based defences (e.g. `addslashes`) can be bypassed when the application and the database disagree on the character set (multi-byte characters such as GBK); parameterised queries are not affected.

## When the application is safe

- **Parameterised queries** (prepared statements): the query is defined in advance and the data travels separately and is never executed as code. This is the primary and most important defence.
- Strong typing: a field that expects a number rejects everything else.
- Minimal privileges for the database account (a separate read-only account where that is enough).
- Correct and consistent character encoding handling.

## Variants and how to test

First check whether the parameter affects the query: append a single quote (`'`) and watch for a syntax error, a 500 status or a change in content. For a numeric parameter, compare `id=10` with `id=11-1`: the same response suggests SQLi.

| Variant | When | How to confirm |
|---|---|---|
| **Union-based** | the query result appears on the page | `ORDER BY n` finds the number of columns, `UNION SELECT` adds your own data |
| **Error-based** | the application shows database errors | a function that forces an error containing the subquery result |
| **Boolean-based (blind)** | no errors or data, but the page reacts differently | comparing `AND 1=1` and `AND 1=2` |
| **Time-based (blind)** | no visible difference | a delay on the database side and measuring response time |

```text
' ORDER BY 3-- -           # find the number of columns
' UNION SELECT NULL,version(),NULL-- -   # extraction test
1' AND 1=1-- -   vs   1' AND 1=2-- -     # boolean-based
```

!!! note "Syntax depends on the database"
    In MySQL `--` only starts a comment when followed by a space, hence `-- -` (or `#`, `%23` in a URL). The database version comes from `version()` in MySQL and PostgreSQL, `@@version` in MSSQL and `SELECT banner FROM v$version` in Oracle, where every `UNION SELECT` also needs `FROM dual`.

In Burp the variants are tested in Repeater (one change at a time) or in Intruder with a payload list. **sqlmap** automates this, but you should understand what it does.

!!! warning "Status codes and blind SQLi"
    A 500 after a single quote is a strong signal. With blind SQLi, the difference in response length or time matters, not the status code itself.

!!! warning "What cannot be parameterised"
    Parameters bind values only, not object names. Table names, column names and the `ORDER BY` direction cannot be bound. If they must come from input, map them through an allowlist of permitted values; never concatenate them into the text.

## Second-order SQLi

In second-order SQLi the data is stored safely in one place, and the injection fires later, when another function reads it back from the database and concatenates it into a new query without parameterisation. Example: a username containing a single quote stored at registration, then used literally in a query during a password change. This is why every query must be parameterised, including those operating on data already in the database, not only on fresh input.

!!! note "Filters and WAFs are not a fix"
    Blocking keywords or characters can be bypassed (different encodings, comments, syntax variants), so treat a WAF as an extra layer, not the real defence. Parameterisation in code is the only reliable solution.

## Recommendations

- Parameterised queries everywhere, including dynamic queries and reports.
- ORMs and query builders help, but raw queries and manual interpolation inside them are still vulnerable.
- Stored procedures offer no protection if they build dynamic SQL by concatenation internally.
- Validation of the type and format of input (an allowlist), especially for fragments that cannot be bound.
- Error messages without database details; details only in the logs.
- A database account with minimal privileges.
