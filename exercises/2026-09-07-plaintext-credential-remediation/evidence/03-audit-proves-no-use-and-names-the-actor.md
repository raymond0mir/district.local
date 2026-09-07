# The audit log proves the credential was never used, and names the acting identity

Read in Graph Explorer from the Mac Mini, 2026-09-07, after the purge recorded in file 02.

**Redactions.** Two strings from the raw responses are removed here and must stay out of every
repo artifact:

- the current tenant Global Administrator's `userPrincipalName`, per the standing rule. Its object
  id `6ca413e3-06ff-4704-ab36-1348bb7387c8` is published, following the convention recorded at
  `exercises/2026-09-06-b4-pim-eligible-role/evidence/04-tenant-user-inventory-and-empty-eligibility.md`.
- the operator's source IP address.

The `directoryAudits` response is quoted field by field rather than whole. The full response
carried four events with repeated boilerplate. Every field used to support a claim below is
quoted verbatim. Nothing else was read.

## Read 1 — interactive sign-ins for the exposed account

    GET https://graph.microsoft.com/beta/auditLogs/signIns?$filter=userId eq '84360e8b-3321-4e37-b9ec-10fccd0263b8'
    Host: Graph Explorer
    2026-09-07

```json
{
    "@odata.context": "https://graph.microsoft.com/beta/$metadata#auditLogs/signIns",
    "value": []
}
```

The call returned `200` with an empty collection, not the
`Authentication_RequestFromNonPremiumTenantOrB2CTenant` error. The read worked; the result is a
real absence, not a licence block. The P2 trial runs to 2026-10-04.

## Read 2 — non-interactive sign-ins for the exposed account

    GET https://graph.microsoft.com/beta/auditLogs/signIns?$filter=userId eq '84360e8b-3321-4e37-b9ec-10fccd0263b8' and signInEventTypes/any(t: t eq 'nonInteractiveUser')
    Host: Graph Explorer
    2026-09-07

```json
{
    "@odata.context": "https://graph.microsoft.com/beta/$metadata#auditLogs/signIns",
    "value": []
}
```

Read 1 alone would not have been enough. `auditLogs/signIns` returns interactive events by
default, so a token acquired against Graph directly would not appear there. Both streams are
empty.

## Read 3 — every directory audit event targeting the exposed account

    GET https://graph.microsoft.com/beta/auditLogs/directoryAudits?$filter=targetResources/any(t: t/id eq '84360e8b-3321-4e37-b9ec-10fccd0263b8')
    Host: Graph Explorer
    2026-09-07

Four events returned, oldest last in the response. Ordered here oldest first.

### Event 1 — password set

```json
{
    "activityDisplayName": "Update PasswordProfile",
    "activityDateTime": "2026-09-03T15:02:22.1518557Z",
    "operationType": "Update",
    "result": "success",
    "targetResources": [
        {
            "id": "84360e8b-3321-4e37-b9ec-10fccd0263b8",
            "userPrincipalName": "breakglassrotationverify@raytakosharkygmail.onmicrosoft.com",
            "modifiedProperties": [
                { "displayName": "ForceChangePassword", "oldValue": "\"False\"", "newValue": "\"True\"" },
                { "displayName": "Password", "oldValue": null, "newValue": null }
            ]
        }
    ]
}
```

Entra logs the password write with null values on both sides. The directory never records the
literal. Only the repository did.

`ForceChangePassword` is `True`. A first sign-in would have required a password change before the
session was usable.

### Event 2 — account created

```json
{
    "activityDisplayName": "Add user",
    "activityDateTime": "2026-09-03T15:02:22.5383841Z",
    "operationType": "Add",
    "result": "success",
    "targetResources": [
        {
            "id": "84360e8b-3321-4e37-b9ec-10fccd0263b8",
            "userPrincipalName": "breakglassrotationverify@raytakosharkygmail.onmicrosoft.com",
            "modifiedProperties": [
                { "displayName": "AccountEnabled", "oldValue": "[]", "newValue": "[true]" },
                { "displayName": "DisplayName", "oldValue": "[]", "newValue": "[\"breakglass-rotation-verify\"]" },
                { "displayName": "StsRefreshTokensValidFrom", "oldValue": "[]", "newValue": "[\"2026-09-03T15:02:22Z\"]" },
                { "displayName": "UserType", "oldValue": "[]", "newValue": "[\"Member\"]" }
            ]
        }
    ]
}
```

### Event 3 — soft delete

```json
{
    "activityDisplayName": "Delete user",
    "activityDateTime": "2026-09-03T15:02:45.8516049Z",
    "operationType": "Delete",
    "result": "success",
    "targetResources": [
        {
            "id": "84360e8b-3321-4e37-b9ec-10fccd0263b8",
            "userPrincipalName": "84360e8b33214e37b9ec10fccd0263b8breakglassrotationverify@raytakosharkygmail.onmicrosoft.com",
            "modifiedProperties": [
                { "displayName": "Is Hard Deleted", "oldValue": null, "newValue": "\"False\"" }
            ]
        }
    ]
}
```

The UPN is already mangled in this event. The rename is part of the delete operation itself, not a
later background job.

### Event 4 — hard delete, this session

```json
{
    "activityDisplayName": "Hard Delete user",
    "activityDateTime": "2026-09-07T17:55:34.1473136Z",
    "operationType": "Delete",
    "result": "success",
    "targetResources": [
        {
            "id": "84360e8b-3321-4e37-b9ec-10fccd0263b8",
            "modifiedProperties": [
                { "displayName": "Is Hard Deleted", "oldValue": null, "newValue": "\"True\"" }
            ]
        }
    ]
}
```

This is the purge recorded in file 02. It gives the purge the UTC timestamp that the `DELETE`
response did not.

### The actor, identical on all four events

```json
"initiatedBy": {
    "app": null,
    "user": {
        "id": "6ca413e3-06ff-4704-ab36-1348bb7387c8",
        "displayName": "Graph Explorer",
        "userPrincipalName": "[REDACTED: current tenant Global Administrator]",
        "ipAddress": "[REDACTED: operator source IP]"
    }
},
"performedBy": { "appId": "de8bc8b5-d9f9-48b1-a8ad-b748da725064" },
"additionalDetails": [
    { "key": "User-Agent", "value": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:155.0) Gecko/20100101 Firefox/155.0" }
]
```

`de8bc8b5-d9f9-48b1-a8ad-b748da725064` is the Graph Explorer application. `6ca413e3` is the
break-glass account holding Global Administrator.

## What this proves

**The credential was never used.** The account existed for 23.3 seconds: created
`2026-09-03T15:02:22.5383841Z`, soft-deleted `2026-09-03T15:02:45.8516049Z`. No interactive
sign-in, no non-interactive sign-in, and no audit event other than its own creation and deletion.
No role was ever assigned to it. The password required a change at first sign-in, and no first
sign-in happened.

The exposure closes on evidence. It no longer rests on the Recalled statement that the string is
not reused elsewhere.

**The account never held Global Administrator.** The role assignment in
`exercises/2026-09-03-breakglass-rotation/evidence/02-role-assignment-and-verification.md:35`
targets `directoryObjects/6ca413e3-06ff-4704-ab36-1348bb7387c8`, the break-glass account. It does
not target `84360e8b`. That file's own section header states the purpose of the exposed account:
"privilege actually exercised, not just claimed in a token." The exposed account was the proof that
Global Administrator worked, not a holder of it.

Claude asserted in session on 2026-09-07 that the exposed account had been granted Global
Administrator, and classified the exposure on that basis. That was wrong. It came from reading the
file's title line and its role lookup, and not the assignment body four sections below. Recorded
here because the claim shaped how the exposure was described for part of the session.

**Nothing unexplained happened on 2026-09-03.** The same identity created and deleted the account
23 seconds apart, in one Graph Explorer session, from one browser. This answers the open question
that asked who deleted it and whether it was deliberate. It was cleanup.

**The break-glass account is still the acting identity for routine work.** All four events carry
`initiatedBy.user.id` `6ca413e3`. Event 4 ran on 2026-09-07, four days after the 2026-09-07
decision recorded in `EXPOSURES.md` that `adm-jsmith` is the go-forward administrative account.
`EXPOSURES.md` sets that entry's test as whether future captures stop showing the break-glass
account as `initiatedBy`. This capture is the first test after the decision, and it shows the
break-glass account. The entry's separate claim that Raymond signs in as this account for routine
work is now supported by audit data rather than by recollection.
