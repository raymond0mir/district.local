# Attribution captured, and a refused privileged action that left no trace

## Capture header

```
command: GET https://graph.microsoft.com/v1.0/auditLogs/directoryAudits
             ?$filter=activityDateTime ge 2026-09-10T02:00:00Z
              and targetResources/any(t:t/id eq '11033cf6-328f-4a1a-b66d-82807b0f2acb')
host:    Mac Mini, Graph Explorer, signed in as the tenant break-glass account (6ca413e3)
utc:     approximately 2026-09-10T14:50Z
status:  OK - 200 - 501 ms
```

Scopes `AuditLog.Read.All` and `Directory.Read.All` were consented for this call. Both require
admin consent. **Captured.**

**One field is redacted.** Each `initiatedBy.user` block carried an `ipAddress` value, which is
Raymond's public address. It is replaced below with `[redacted]`. This repository is public and the
address is not needed for any claim in this file. The redaction is recorded rather than performed
in silence. Raymond has not yet decided whether IP addresses should be stripped from captures as a
standing rule; see `CARRYOVER.md`.

## The read

Two events returned. Both abbreviated to the fields that carry the claim.

```json
{
    "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#auditLogs/directoryAudits",
    "value": [
        {
            "category": "UserManagement",
            "correlationId": "6f731794-70de-46a8-9c9a-8cd0ea10e119",
            "result": "success",
            "activityDisplayName": "Update user",
            "activityDateTime": "2026-09-10T14:32:27.4602239Z",
            "loggedByService": "Core Directory",
            "operationType": "Update",
            "initiatedBy": {
                "app": null,
                "user": {
                    "id": "03ee6546-f113-4ec5-ba9d-e57381b0c928",
                    "userPrincipalName": "adm-jsmith@raytakosharkygmail.onmicrosoft.com",
                    "ipAddress": "[redacted]",
                    "agentType": "notAgentic"
                }
            },
            "targetResources": [
                {
                    "id": "11033cf6-328f-4a1a-b66d-82807b0f2acb",
                    "type": "User",
                    "userPrincipalName": "dumbuser2@raytakosharkygmail.onmicrosoft.com",
                    "modifiedProperties": [
                        {
                            "displayName": "StsRefreshTokensValidFrom",
                            "oldValue": "[\"2025-10-01T00:34:24Z\"]",
                            "newValue": "[\"2026-09-10T14:32:27Z\"]"
                        },
                        {
                            "displayName": "Included Updated Properties",
                            "oldValue": null,
                            "newValue": "\"StsRefreshTokensValidFrom\""
                        },
                        {
                            "displayName": "TargetId.UserType",
                            "oldValue": null,
                            "newValue": "\"Member\""
                        }
                    ]
                }
            ],
            "additionalDetails": [
                { "key": "UserType", "value": "Member" },
                { "key": "User-Agent", "value": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:155.0) Gecko/20100101 Firefox/155.0" }
            ]
        },
        {
            "category": "UserManagement",
            "correlationId": "6f731794-70de-46a8-9c9a-8cd0ea10e119",
            "result": "success",
            "activityDisplayName": "Update StsRefreshTokenValidFrom Timestamp",
            "activityDateTime": "2026-09-10T14:32:27.4592251Z",
            "loggedByService": "Core Directory",
            "operationType": "Update",
            "initiatedBy": {
                "app": null,
                "user": {
                    "id": "03ee6546-f113-4ec5-ba9d-e57381b0c928",
                    "userPrincipalName": "adm-jsmith@raytakosharkygmail.onmicrosoft.com",
                    "ipAddress": "[redacted]",
                    "agentType": "notAgentic"
                }
            },
            "targetResources": [
                {
                    "id": "11033cf6-328f-4a1a-b66d-82807b0f2acb",
                    "type": "User",
                    "userPrincipalName": "dumbuser2@raytakosharkygmail.onmicrosoft.com",
                    "modifiedProperties": [
                        {
                            "displayName": "StsRefreshTokensValidFrom",
                            "oldValue": "[\"2025-10-01T00:34:24Z\"]",
                            "newValue": "[\"2026-09-10T14:32:27Z\"]"
                        }
                    ]
                }
            ]
        }
    ]
}
```

## Attribution is Captured, and the hypothesis is closed

`initiatedBy.user.id` is `03ee6546-f113-4ec5-ba9d-e57381b0c928`, `adm-jsmith`. `result` is
`success`. `activityDateTime` is 14:32:27.46Z, inside the window of 14:20:40.623Z to 16:20:40.03Z
Captured in `evidence/11`.

`evidence/10` proved the revocation happened and could not prove who performed it, because
`signInSessionsValidFromDateTime` carries no actor. This read carries the actor.

**The exercise's hypothesis is now proven end to end from machine output.** `adm-jsmith` held
`User Administrator` only through activated membership of `PIM-UserAdmin-Pilot`, with the direct
path confirmed cold beforehand, and completed a privileged action that the directory recorded as
successful and attributed to that account.

The two events share one `correlationId`. A single portal click produced two audit rows,
`Update user` and `Update StsRefreshTokenValidFrom Timestamp`, 1 millisecond apart. A detection
rule counting events rather than correlation ids will double-count this action.

## The refusal left nothing behind

The filter covers `activityDateTime ge 2026-09-10T02:00:00Z` against this exact target. The window
therefore includes 2026-09-10T02:30Z, when `adm-jsmith` was refused the `dumbuser2` password reset
while holding eligibility only, recorded in `evidence/06`.

**No event appears for 02:30Z.** The response contains two events and both are the 14:32:27Z
success pair.

The likely mechanism is that the portal evaluated authorization before issuing any directory write.
No write was attempted, so `Core Directory` had nothing to log. `directoryAudits` records changes to
the directory, not attempts to change it.

**The defensive consequence is the finding.** An account can probe the boundaries of its own
privilege through the Entra portal, one blade at a time, and generate no entry in the directory
audit log. Only what succeeds is recorded. A defender watching `directoryAudits` sees an
administrator's successful actions and is blind to everything that administrator tried and could
not do.

This matters most for the exact scenario this lab is built around. An account that has accumulated
standing grants nobody reviews can be tested for what it can reach, silently, before anything is
used.

**This claim is scoped to `directoryAudits` filtered to one target.** It does not assert that no
telemetry anywhere recorded the refusal. Sign-in logs record the session. The confirming read
listed under Owed removes the target filter, to separate "no event exists" from "an event exists
that does not name `dumbuser2` as a target resource".

## The identity question is settled

The identical query returned `Authentication_RequestFromUnsupportedUserRole` at 14:28:22Z and
14:34:11Z, and `OK - 200` here. Only the signed-in account changed.

The refusals were an identity problem in Graph Explorer, not a Global Administrator being refused
the reporting API. The finding in `evidence/09` section D stands and is strengthened:
`User Administrator` cannot read `directoryAudits`, and Global Administrator can. The pair
demonstrates the role boundary from both sides.

## An unexplained value

`StsRefreshTokensValidFrom` on `dumbuser2` held `2025-10-01T00:34:24Z` before this change.

`evidence/09` Captured this object's `onPremisesLastSyncDateTime` as `2026-09-01T23:57:46Z`, and the
portal reports its cloud creation date as 2026-09-01. A timestamp from October 2025 on an object
created in the tenant in September 2026 is not explained by anything Captured so far.

One candidate reading is that the on-premises source object predates the cloud object by eleven
months, having been built during the October 2025 build, and that the value derives from the source.
**That reading is not established and no claim is made.** It is recorded because the October 2025
build is the reason this repository's evidence discipline exists, and a stray artefact of it
surfacing inside an unrelated capture is worth chasing rather than ignoring.

## Owed

- The same read with the `targetResources` clause removed, to confirm the 02:30Z refusal produced
  no event of any kind rather than an event naming a different target.
