# `adm-jsmith` granted eligible membership in `PIM-UserAdmin-Pilot`

Three attempts, kept in order. The first two failures are the evidence for two separate defaults;
only the third call changed to work around them.

## Attempt 1: missing scope

Command: `POST https://graph.microsoft.com/v1.0/identityGovernance/privilegedAccess/group/eligibilityScheduleRequests`
Body: `accessId: member`, `principalId: 03ee6546-f113-4ec5-ba9d-e57381b0c928` (`adm-jsmith`, reused
from `exercises/2026-09-06-b4-pim-eligible-role/evidence/05-adm-jsmith-created.md`), `groupId:
3265375f-23f9-4d3f-81d3-15370199bc8a`, `action: adminAssign`, `scheduleInfo.expiration.type:
noExpiration`.
Host: Graph Explorer, tenant, signed in as the native Global Administrator (break-glass).
Timestamp: 2026-09-09T20:48:37Z, from `innerError.date`.

```json
{
    "error": {
        "code": "UnknownError",
        "message": "{\"errorCode\":\"PermissionScopeNotGranted\",\"message\":\"Authorization failed due to missing permission scope PrivilegedEligibilitySchedule.ReadWrite.AzureADGroup,PrivilegedAccess.ReadWrite.AzureADGroup.\",\"instanceAnnotations\":[]}"
    }
}
```

`RoleManagement.ReadWrite.Directory`, already consented for the role-assignment step in
`evidence/02`, does not cover group eligibility. Fixed by consenting to
`PrivilegedEligibilitySchedule.ReadWrite.AzureADGroup` in Graph Explorer's Modify Permissions tab.

## Attempt 2: policy refuses permanent assignment

Same body, scope now resolved.
Timestamp: 2026-09-09T20:49:11Z, from `innerError.date`.

```json
{
    "error": {
        "code": "RoleAssignmentRequestPolicyValidationFailed",
        "message": "The following policy rules failed: ExpirationRule - The policy does not allow permanent assignment"
    }
}
```

`PIM-UserAdmin-Pilot`'s default eligibility policy refuses `noExpiration`. B4's identical
`noExpiration` request for the `User Administrator` role itself succeeded
(`exercises/2026-09-06-b4-pim-eligible-role/evidence/08-eligibility-granted.md`). The two
untouched defaults disagree: PIM for Entra roles allows permanent eligibility; PIM for Groups, on
this group, does not.

## Attempt 3: bounded expiration succeeds

Body changed only in `scheduleInfo.expiration`: `type: afterDateTime`, `endDateTime:
2026-12-08T20:49:00Z` — ninety days out, matching Microsoft's own example duration for group
eligibility ([Plan a PIM deployment](https://learn.microsoft.com/entra/id-governance/privileged-identity-management/pim-deployment-plan#plan-and-implement-pim-for-pim-for-groups)).
Timestamp: 2026-09-09T20:50:34Z, from `createdDateTime`.

```json
{
    "id": "bead11a5-a9d6-46dc-b620-d345de38db55",
    "status": "Provisioned",
    "createdDateTime": "2026-09-09T20:50:34.7824837Z",
    "completedDateTime": "2026-09-09T20:50:35.3027954Z",
    "action": "adminAssign",
    "principalId": "03ee6546-f113-4ec5-ba9d-e57381b0c928",
    "accessId": "member",
    "groupId": "3265375f-23f9-4d3f-81d3-15370199bc8a",
    "createdBy": {
        "user": {
            "id": "6ca413e3-06ff-4704-ab36-1348bb7387c8"
        }
    },
    "scheduleInfo": {
        "expiration": {
            "type": "afterDateTime",
            "endDateTime": "2026-12-08T20:49:00Z"
        }
    }
}
```

## What this shows

- `adm-jsmith` is now an eligible **member** of `PIM-UserAdmin-Pilot`, expiring 2026-12-08, not
  standing. `status: Provisioned` confirms the request completed, not merely queued.
- `createdBy.user.id` is `6ca413e3-06ff-4704-ab36-1348bb7387c8` — the break-glass account's object
  id, independently matching the identity `EXPOSURES.md` already tracks as the one performing
  routine work in this tenant. Consistent with, not new information about, that standing question.
- Two distinct untouched defaults are now Captured for this group: the required permission scope
  differs from the equivalent role-level call, and the eligibility policy caps assignment
  duration where the role-level policy did not. Neither has been hardened yet — this file
  captures the defaults, per the decision in `evidence-log.md` to observe before configuring.

## What this does not show

Whether `adm-jsmith` can actually *activate* this eligibility yet, and under what policy
(approval, MFA, activation duration). The group's own activation policy has not been read or
configured. Not tested: activation itself, or whether the standing `User Administrator`
assignment from `evidence/02` already grants effective access regardless of this eligibility.
