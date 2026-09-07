# Purge of the deleted object, and redaction of the repository copy

## Purge

    DELETE https://graph.microsoft.com/v1.0/directory/deletedItems/84360e8b-3321-4e37-b9ec-10fccd0263b8
    Host: Graph Explorer
    2026-09-07, after the reads in file 01

The response status code was not captured. Graph Explorer returns `204 No Content` with an empty
body on success, and no output was pasted back. The verification read below is the captured proof,
not the status code.

## Verification

    GET https://graph.microsoft.com/v1.0/directory/deletedItems/microsoft.graph.user?$select=id,userPrincipalName,accountEnabled,deletedDateTime
    Host: Graph Explorer
    2026-09-07, immediately after the DELETE

```json
{
    "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users(id,userPrincipalName,accountEnabled,deletedDateTime)",
    "value": []
}
```

The same read returned one object before the DELETE. It now returns none. The object is
permanently purged and cannot be restored. The 30-day restore window is closed 26 days early.

## Repository redaction

Raymond chose redact-in-place over history rewrite on 2026-09-07.

Scope check before the edit, run on the Mac Mini:

    grep -rlF "<the password string>" . --exclude-dir=.git
    git log --all --oneline -S"<the password string>" --

```
exercises/2026-09-03-breakglass-rotation/evidence/02-role-assignment-and-verification.md
62fd7bf Rotate the break-glass account; retire two undocumented legacy Global Admins
```

One file in the working tree held the string. One commit introduced it. The string was 24
characters.

The value at line 81 was replaced with a redaction marker. A note was added below the code block.
The note states that git history still carries the value at commit `62fd7bf`.

Verification after the edit:

    grep -rlF "<the password string>" . --exclude-dir=.git

```
(no output)
```

The string is gone from the working tree. It remains in `.git`, by decision.
