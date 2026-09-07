# Removing a plaintext credential from a public repository

## What I set out to do

A live account password sat in plain text in a public GitHub repository, in an evidence file from
the 2026-09-03 break-glass rotation. The standing record said the account was still live. The plan
was to disable the account, then decide how to remove the string from the repository. The first
step was to establish the account's real state, because the record for it was Recalled, not
Captured.

## The setup

Entra tenant `raytakosharkygmail.onmicrosoft.com`. All reads and writes ran in Graph Explorer from
the Mac Mini. No lab VM was touched, so no Proxmox pre-flight applied. Repository work ran on the
Mac Mini against the working tree at `~/district-local`.

The exposed object: `breakglassrotationverify@raytakosharkygmail.onmicrosoft.com`, object id
`84360e8b-3321-4e37-b9ec-10fccd0263b8`. Created 2026-09-03 for one verification step during the
break-glass rotation, with no purpose beyond it.

## What I did

1. Read the target user by UPN, selecting `signInActivity` among other properties. Failed.
2. Read the target user by UPN without `signInActivity`. Failed with `Request_ResourceNotFound`.
3. Extracted the UPN and object id from the 2026-09-03 evidence file, without printing the password:

       grep -n 'userPrincipalName\|mailNickname\|"id"' <file> | grep -v -i 'password'

   The captured UPN matched the string already sent. The string was correct.
4. Read the target user by object id. Failed with `Request_ResourceNotFound`.
5. Read `/directory/deletedItems/microsoft.graph.user`. Found the object.
6. Read `/users` filtered on `startswith(userPrincipalName,'breakglass')`. Found one live account,
   disabled.
7. Permanently deleted the object:

       DELETE https://graph.microsoft.com/v1.0/directory/deletedItems/84360e8b-3321-4e37-b9ec-10fccd0263b8

8. Re-read deleted items. Empty.
9. Scoped the string across the repository and its history, holding the value in a shell variable so
   it was never printed:

       grep -rlF "$PW" . --exclude-dir=.git
       git log --all --oneline -S"$PW" --

10. Replaced the value at line 81 with a redaction marker. Added a note below the code block naming
    the commit that still carries it.
11. Re-ran the scope check. No occurrence outside `.git`.
12. Read the exposed account's interactive sign-ins:

        GET /beta/auditLogs/signIns?$filter=userId eq '84360e8b-3321-4e37-b9ec-10fccd0263b8'

13. Read the same account's non-interactive sign-ins, by adding
    `signInEventTypes/any(t: t eq 'nonInteractiveUser')` to the filter.
14. Read every directory audit event targeting the object:

        GET /beta/auditLogs/directoryAudits?$filter=targetResources/any(t: t/id eq '84360e8b-3321-4e37-b9ec-10fccd0263b8')

Steps 12 to 14 ran after the purge. A purged object keeps its audit trail; the log is keyed on the
object id, not on the object.

## Where Raymond was consulted

- **Purge the object now, or let the 30-day window expire?** Permanent deletion is irreversible, so
  it was not run on a default. Raymond: "purge it." Run the same session.
- **Is that password string reused anywhere else?** Raymond: "no." This answer is Recalled. It
  cannot be captured from the lab. It was the reason the residual risk was described as closed in
  effect rather than merely reduced. Three later reads removed that dependency: the exposure now
  closes on captured evidence, and the Recalled answer covers only reuse outside this tenant.
- **Redact in place, or rewrite git history?** Raymond: "redact and note." The rewrite stays
  unexercised. It remains coupled to the separate, still-deferred question of the author identity in
  pushed history.

## What the box said

The account was never live at the time of this work. Quoted from
`evidence/01-account-is-soft-deleted-not-live.md`:

```json
{
    "id": "84360e8b-3321-4e37-b9ec-10fccd0263b8",
    "userPrincipalName": "84360e8b33214e37b9ec10fccd0263b8breakglassrotationverify@raytakosharkygmail.onmicrosoft.com",
    "accountEnabled": true,
    "deletedDateTime": "2026-09-03T15:02:45Z"
}
```

Two facts sit inside that one response.

The account was soft-deleted on 2026-09-03, the same day it was created. Graph prefixes the object
id onto the UPN at soft delete, which is exactly why every lookup by the original UPN returned
`Request_ResourceNotFound`. The object was findable the whole time, under a name nobody had.

`accountEnabled` reads `true` on a deleted object. That value is retained state, not a sign-in path.
A soft-deleted user cannot authenticate. Reading that field alone, without `deletedDateTime`, would
support the opposite conclusion.

After the purge, quoted from `evidence/02-purge-and-redaction.md`:

```json
{
    "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users(id,userPrincipalName,accountEnabled,deletedDateTime)",
    "value": []
}
```

The credential was never used. Both sign-in streams are empty, quoted from
`evidence/03-audit-proves-no-use-and-names-the-actor.md`:

```json
{
    "@odata.context": "https://graph.microsoft.com/beta/$metadata#auditLogs/signIns",
    "value": []
}
```

The interactive read alone would not have carried this. `auditLogs/signIns` returns interactive
events by default, so a token taken against Graph directly would not appear in it. The
non-interactive read returned the same empty collection. Both calls returned `200`, not
`Authentication_RequestFromNonPremiumTenantOrB2CTenant`, so the absence is real and not a licence
block.

`directoryAudits` returned four events and no others. The first two set the account's lifetime:

```json
{ "activityDisplayName": "Add user",    "activityDateTime": "2026-09-03T15:02:22.5383841Z", "result": "success" }
{ "activityDisplayName": "Delete user", "activityDateTime": "2026-09-03T15:02:45.8516049Z", "result": "success" }
```

The account existed for 23.3 seconds. The password write is logged with null on both sides:

```json
{ "displayName": "Password", "oldValue": null, "newValue": null }
```

Entra never records the literal. Only the repository did. The same event set
`ForceChangePassword` to `True`, so a first sign-in would have demanded a password change before
any session was usable. No first sign-in happened.

All four events name the same actor:

```json
"initiatedBy": { "user": { "id": "6ca413e3-06ff-4704-ab36-1348bb7387c8", "displayName": "Graph Explorer" } },
"performedBy": { "appId": "de8bc8b5-d9f9-48b1-a8ad-b748da725064" }
```

`6ca413e3` is the break-glass account. `de8bc8b5-d9f9-48b1-a8ad-b748da725064` is the Graph Explorer
application.

## What broke, and why

**The standing record was wrong, and it was wrong in the direction that wastes work.**
`EXPOSURES.md` said the account was confirmed live on 2026-09-07. `CARRYOVER.md` set the next step
as disabling it. Both rested on a Recalled claim. The account had been gone for four days. The
planned action could not have succeeded.

**The recorded diagnosis pointed at the wrong layer.** The record said to check Graph Explorer's
granted scopes first, because a `PATCH` had failed with `400 Request_BadRequest`. An
insufficient-scope failure in Graph returns `403 Authorization_RequestDenied`. A `400` is a
statement about the request, not about permission. Reading the error code as written, rather than
reaching for the familiar permission explanation, replaced a scope investigation with three reads.

**The failed `PATCH` still has no explanation, because it was never captured.** A `PATCH` to that
object id would return `404`. The most likely cause is that the request used the other id in the
same evidence file, a role object with no `accountEnabled` property, which produces exactly that
message. The request body was never written to a file, so this stays unresolved. The capture
contract exists for this case. The one request that would settle it is the one nobody kept.

**My own first command failed for a reason unrelated to the account.** Including `signInActivity`
in `$select` makes Graph resolve the key as a GUID, so the UPN failed at the key parser and returned
a `400` about key format. That error described the query. Read carelessly, it would have looked like
more evidence for a malformed-request theory about the account.

**The exposure was mischaracterized, in both directions.** It was described as a working credential
any repository reader could use. It was not: no live account backed the string. It was also
narrower than described in one way and broader in another. A repository reader could not restore the
object, because restoring requires tenant privilege. But the string sat in public history for four
days after the account's deletion, during which the standing record claimed it was live and nothing
acted on it.

**I claimed the exposed account held Global Administrator. It never did. Retracted.** The
classification of the exposure rested on that claim for part of the session. The role assignment
in `exercises/2026-09-03-breakglass-rotation/evidence/02-role-assignment-and-verification.md:35`
targets `directoryObjects/6ca413e3-06ff-4704-ab36-1348bb7387c8`, which is the break-glass account.
It does not target `84360e8b`. The exposed account was the object used to prove the role worked,
not a holder of it; that file's own section header says so. The error came from reading the file's
title line and its role lookup, and stopping before the assignment body four sections below. A
credential that never carried a role is a materially smaller exposure than one that did, and the
whole session's risk framing followed from getting it wrong.

**The break-glass account is still doing routine work, four days after the decision to stop.**
`EXPOSURES.md` records that `adm-jsmith` became the go-forward administrative account on
2026-09-07, and it sets that entry's test as whether future captures stop showing the break-glass
account as `initiatedBy`. The purge in this exercise ran under the break-glass account. The
decision and the purge fall on the same date and their order is not captured, so this is not proof
that the habit survived the decision. It is the first capture in which the test could have been
passed, and it was not.

**A second-order correction, in this file rather than in the evidence.** File 03's closing
analysis says the purge ran "four days after the 2026-09-07 decision" and calls it "the first test
after the decision". Both dates are 2026-09-07, so the interval is zero days, and the decision has
no captured time of day, so the purge cannot be ordered after it. The four-day figure belongs to
the account's soft delete on 2026-09-03. File 03 is committed evidence. It was edited to fix this,
`validate.py` raised `evidence-modified`, and the edit was reverted. Committed evidence does not
get quiet repairs; the correction belongs in the report and the evidence-log, which is where it
now is.

## What I'd do differently

Verify object state before writing an exposure entry that asserts it. The entry said "confirmed
still live" on the strength of a recollection. One read would have made it Captured or retracted it.

Capture failed requests, not just failed responses. The `400` from 2026-09-03 is unexplainable now
because the request body was never recorded. An error message is only half the evidence.

Delete the verification account at the end of the exercise that creates it, and capture the
deletion. The 2026-09-03 exercise did delete this account, 23.3 seconds after creating it. It
recorded nothing about having done so, which is why four days later the standing record said the
account was live and this exercise opened by planning to disable it. The audit log held the answer
the whole time. Reading it cost three requests, and it was the last thing tried rather than the
first.

Treat a repository redaction as a scope problem before it is an edit problem. Finding one file and
one commit took two commands and cost nothing. Editing first would have left the question open.

## Open questions

- Why did the 2026-09-03 `PATCH` return `400`, not `404`? Unresolvable without the original request.
- ~~Who deleted the account on 2026-09-03, and was it deliberate?~~ **Answered.**
  `directoryAudits` names the break-glass account as `initiatedBy` on the creation, the password
  write and the soft delete, all three within 23.3 seconds, from one Graph Explorer session and
  one browser. It was cleanup by the operator who made the account.
- Do other pre-2026-09-06 evidence files hold credentials that the older scan passes missed? The
  JSON-quoted pass was added 2026-09-06. This value predates it and survived every earlier pass.
- The value remains in commit `62fd7bf` in public history, by decision. The rewrite is unexercised
  and stays coupled to the deferred question of the author identity in the same history.
