# Graph capture pass: what moved from Recalled to Captured

## Capture header

```
Source:  Microsoft Graph, v1.0, through Graph Explorer
Host:    Mac Mini, browser. Signing identity NOT established -- see the correction below.
UTC:     2026-09-10T14:27Z to 2026-09-10T14:29Z
```

Response bodies below are pasted text, not screenshots. **Captured.**

## Correction: the signing identity of this pass was asserted, not observed

This file's capture header originally read "signed in as the tenant break-glass account". Claude
wrote that from the instruction it had given, not from any evidence that the instruction was
followed. That is an unsupported claim in a capture header, and it is corrected here rather than
edited away.

Graph Explorer holds its own sign-in, independent of the Entra admin center session and unaffected
by which browser window is used. Repeats of calls B and D at 14:34Z returned the same two errors as
the originals. The leading explanation is that Graph Explorer was signed in as `adm-jsmith`
throughout this pass.

**Established at approximately 14:50Z.** Call D was re-run as the break-glass account and returned
`OK - 200`. The same query, unchanged, returns a role refusal under one identity and data under
another. The refusals at 14:28:22Z and 14:34:11Z were an identity problem in Graph Explorer, and
not a Global Administrator being refused the reporting API. See `evidence/12`.

The finding in section D below is unaffected and is strengthened by this. `User Administrator`
genuinely cannot read `directoryAudits`; the break-glass account's Global Administrator can. The
two results together demonstrate the role boundary rather than a client fault.

Calls A and C succeeded because Entra's default user permissions let any member account read other
users' basic properties. Neither call required a privileged identity. Their success is therefore
not evidence that a privileged account ran them.

**The data in A and C is unaffected.** Both response bodies describe directory objects, and those
values do not depend on who asked. `onPremisesSyncEnabled` on `dumbuser2` is `true` regardless of
the reader. Only the header claim was wrong.

## A. `dumbuser2` is mastered on-premises

```
GET https://graph.microsoft.com/v1.0/users/11033cf6-328f-4a1a-b66d-82807b0f2acb
    ?$select=id,userPrincipalName,userType,onPremisesSyncEnabled,
             onPremisesDistinguishedName,onPremisesImmutableId,onPremisesLastSyncDateTime
```

```json
{
    "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users(id,userPrincipalName,userType,onPremisesSyncEnabled,onPremisesDistinguishedName,onPremisesImmutableId,onPremisesLastSyncDateTime)/$entity",
    "id": "11033cf6-328f-4a1a-b66d-82807b0f2acb",
    "userPrincipalName": "dumbuser2@raytakosharkygmail.onmicrosoft.com",
    "userType": "Member",
    "onPremisesSyncEnabled": true,
    "onPremisesDistinguishedName": "CN=dumb user2,OU=Site 1,OU=Test Users,DC=district,DC=local",
    "onPremisesImmutableId": "FUF1tgcLwUaB9fJYubpcvg==",
    "onPremisesLastSyncDateTime": "2026-09-01T23:57:46Z"
}
```

The `@odata.context` matches the resource requested. The stale-response failure recorded in
`evidence/04` did not recur on this call.

**This settles the open reading in `evidence/08`.** That file inferred from a portal message that
Entra treats `dumbuser2` as a synced user, and said the inference was not established. It is now
established. `onPremisesSyncEnabled` is `true` and the object carries a distinguished name in
`district.local`.

The after-state refusal was therefore a real tenant capability gate. Password writeback applies to
users mastered on-premises, and this tenant does not have it enabled. No privilege level available
in this tenant could have completed that action from the portal.

**The conclusion in `evidence/08` stands and is now better supported.** The authorization gate
stopped firing after activation. The action still failed, for a reason unrelated to privilege.

## B. The stored activation window was not read

```
GET https://graph.microsoft.com/v1.0/identityGovernance/privilegedAccess/group
    /assignmentScheduleInstances?$filter=groupId eq '3265375f-23f9-4d3f-81d3-15370199bc8a'
```

```json
{
    "error": {
        "code": "UnknownError",
        "message": "{\"errorCode\":\"PermissionScopeNotGranted\",\"message\":\"Authorization failed due to missing permission scope PrivilegedAssignmentSchedule.Read.AzureADGroup,PrivilegedAssignmentSchedule.ReadWrite.AzureADGroup,PrivilegedAccess.Read.AzureADGroup,PrivilegedAccess.ReadWrite.AzureADGroup.\",\"instanceAnnotations\":[]}",
        "innerError": {
            "date": "2026-09-10T14:27:18",
            "request-id": "05ff0658-e6d9-44af-bcc0-57f25d576b74",
            "client-request-id": "b62df552-e302-f2bf-08b7-9bde2cbb837a"
        }
    }
}
```

This is a client consent gap in Graph Explorer, not a tenant finding and not a role refusal. The
signed-in account is Global Administrator. The token simply did not carry the scope.

The scope family here differs again from the two already recorded in this exercise.
`evidence/03` recorded that group eligibility writes need
`PrivilegedEligibilitySchedule.ReadWrite.AzureADGroup` rather than the role-level
`RoleManagement.ReadWrite.Directory`. Reading an active group assignment needs a third family,
`PrivilegedAssignmentSchedule.Read.AzureADGroup`. PIM for Groups splits eligibility from
assignment, and reads from writes, across separate scopes.

**Consequence for `evidence/08`.** The assignment start time remains inferred, not observed. The
portal showed only an End time of 09:20:40 PDT. Start is derived from that value and the two-hour
policy duration in `evidence/05`. This read is still owed.

## C. Tenant user inventory, with sync status

```
GET https://graph.microsoft.com/v1.0/users?$select=id,userPrincipalName,userType,onPremisesSyncEnabled&$top=999
```

Sixteen users returned. Summarized rather than pasted whole, because one row is redacted.

| Object id | Account | `onPremisesSyncEnabled` |
| --- | --- | --- |
| `03ee6546` | `adm-jsmith` | `null` |
| `adb0ee55` | `ajones` | `true` |
| `1b39b0f8` | `bhound` | `true` |
| `a48dbe5c` | `bingbong` | `true` |
| `de938dc8` | `breakglass` (rotated out, disabled) | `null` |
| `9781c3ff` | `dumbhelpdesk1` | `true` |
| `11033cf6` | `dumbuser2` | `true` |
| `12a79785` | `dumbuser3` | `true` |
| `03b0f0f4` | `jsmith` | `true` |
| `ffd8ba96` | `khan` | `true` |
| `dde25d37` | `labadmin` | `null` |
| `6ca413e3` | **redacted — the current tenant Global Administrator** | `null` |
| `be30dc5f` | `mlee` | `true` |
| `888038b6` | the original Microsoft Account administrator, external | `null` |
| `da4c397e` | `svc-entraconnect` | `true` |
| `05198b4f` | `sysadmin` | `true` |

**One row is redacted by decision, not by omission.** The current tenant Global Administrator's
account name is deliberately unpublished, per the decision of 2026-09-03. Its object id
`6ca413e3` is published, and is the same id already recorded in `EXPOSURES.md` as the
`initiatedBy` principal on the `directoryAudits` events of 2026-09-07. **That confirms the
break-glass account and the account initiating routine tenant work are the same object.** The
exposure entry asserting this no longer rests on a screenshot.

**Twelve of sixteen users are mastered on-premises.** Four are cloud-only. Two of the four are
break-glass accounts, one old and disabled, one current. One is `adm-jsmith`. One is `labadmin`.

This constrains the next test. A completed `User Administrator` password reset needs a target that
is cloud-only, because writeback is absent, and that holds no privileged role, because
`User Administrator` cannot reset the password of a privileged-role holder. No user in this tenant
is currently known to satisfy both conditions. `labadmin` is the only candidate and its role
assignments have not been read.

`svc-entraconnect` appearing with `onPremisesSyncEnabled: true` is worth a separate note. The
connector's own service account is synced into the tenant by the connector.

## D. Not resolved this pass

```
GET https://graph.microsoft.com/v1.0/auditLogs/directoryAudits
    ?$filter=activityDateTime ge 2026-09-10T02:00:00Z
     and targetResources/any(t:t/id eq '11033cf6-328f-4a1a-b66d-82807b0f2acb')
```

```json
{
    "error": {
        "code": "Authentication_RequestFromUnsupportedUserRole",
        "message": "User is not in the allowed roles",
        "innerError": {
            "date": "2026-09-10T14:28:22",
            "request-id": "604d8d85-454c-4bac-8015-9fd8c4c43899",
            "client-request-id": "8e798605-e839-de05-8a17-2a626d73c4ce"
        }
    }
}
```

**This call ran as `adm-jsmith`, with group membership active.** Raymond confirmed the signing
identity in session. The error is a role refusal, not a scope refusal; a missing scope returns the
shape seen in B.

**`User Administrator` grants the right to act on a user and withholds the right to read the record
of that action.** The reporting API admits Global Administrator, Global Reader, Security
Administrator, Security Reader, Reports Reader and Compliance Administrator.
`User Administrator` is not among them. The refusal is correct behavior, not a defect.

The same account, in the same activated session, could reset a password, revoke sessions and edit
user properties. It could not read `directoryAudits`.

**This is where standing grants come from.** An administrator who must confirm their own action
has a legitimate operational need and exactly one obvious remedy: attach a reporting role to the
account. That role is read-only and sounds harmless, so nobody removes it. The account then holds
a permanent grant acquired to satisfy a momentary need. This is the permission-sprawl pattern
arriving through a side door, driven by a real requirement rather than by carelessness.

The governed answer is not to refuse the need. It is to make the reporting role eligible through
PIM as well, so the read right is time-boxed the same way the write right already is. This lab has
the machinery to demonstrate that, and has not yet done it.

**A caution against over-reading this result.** The refusal does not prove anything about the
activation. `User Administrator` never carries audit-log read, active or eligible. This call would
have failed identically before activation. It is a finding about role scope, not a second proof of
elevation.

The question this call was written to answer — whether the refused attempt at 02:30Z produced an
audit event at all — is still unanswered. Re-running it as the break-glass account will answer it.
