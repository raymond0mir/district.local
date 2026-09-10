# The activation clock starts at approval, not at request

## Capture header

```
command: GET https://graph.microsoft.com/v1.0/identityGovernance/privilegedAccess/group
             /assignmentScheduleInstances?$filter=groupId eq '3265375f-23f9-4d3f-81d3-15370199bc8a'
host:    Mac Mini, Graph Explorer, signed in as the tenant break-glass account (6ca413e3),
         confirmed by Raymond in session
utc:     approximately 2026-09-10T14:47Z
```

Scope `PrivilegedAssignmentSchedule.Read.AzureADGroup` was consented immediately before this call.
It requires admin consent, which the break-glass account can grant and `adm-jsmith` cannot.

## The read

```json
{
    "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#identityGovernance/privilegedAccess/group/assignmentScheduleInstances",
    "value": [
        {
            "id": "3265375f-23f9-4d3f-81d3-15370199bc8a_member_03ee6546-f113-4ec5-ba9d-e57381b0c928",
            "startDateTime": "2026-09-10T14:20:40.623Z",
            "endDateTime": "2026-09-10T16:20:40.03Z",
            "principalId": "03ee6546-f113-4ec5-ba9d-e57381b0c928",
            "accessId": "member",
            "groupId": "3265375f-23f9-4d3f-81d3-15370199bc8a",
            "memberType": "direct",
            "assignmentType": "activated",
            "assignmentScheduleId": "3265375f-23f9-4d3f-81d3-15370199bc8a_member_0172ae77-5cc1-4e83-9fc6-efd075e2d94c"
        }
    ]
}
```

`@odata.context` matches the resource requested. **Captured.**

## The retraction is now resolved against machine output

The three readings, in order:

| Source | Start | End |
| --- | --- | --- |
| Approver's panel, before approval | 07:18 PDT / 14:18Z | 09:18 PDT / 16:18Z |
| Assignments blade, after approval | not shown | 09:20:40 PDT / 16:20:40Z |
| `assignmentScheduleInstances` | 14:20:40.623Z | 16:20:40.03Z |

The request was submitted at 14:18Z. Approval was granted at approximately 14:20Z. The stored
window begins 14:20:40.623Z, which is approval time, and runs the full two hours configured in
`evidence/05`.

**Claude's original claim is disproven, not merely withdrawn.** `evidence/06` recorded the claim
that the activation clock runs from request time, and that a slow approver silently shortens the
granted access. It was stated from the approver's panel alone, before any confirming read existed,
and was withdrawn in that file pending evidence. The evidence now exists and contradicts it. The
requester lost none of the two hours to the pending period.

**This also confirms the inference carried in `evidence/08` and `evidence/10`.** Both derived a
start time of 14:20:40Z from the observed End time minus the policy duration, and both labelled it
as inferred rather than observed. The derived value matches the stored value to the second. Those
two files can now cite this one instead of reasoning from the End time.

**And it supersedes `evidence/09` section B**, which recorded this same call failing on a missing
scope. The failure was a Graph Explorer consent gap and not a tenant condition. Section B remains
in place as the record of what was attempted.

## What the platform displays is not what the platform stores

The approver's panel showed a window of 14:18Z to 16:18Z. The platform stored 14:20:40Z to
16:20:40Z. The panel's values are a projection computed at request time, and the platform does not
honour them once approval is delayed.

The error here is two minutes and forty seconds, because the approval was prompt. The error equals
the pending period, so an approval that sits overnight produces a panel reading wrong by the length
of the wait.

**The consequence is for anyone reconstructing an elevation window from the approval record.** An
investigator who reads the approval panel to establish when privilege ended will be wrong, in the
direction of believing access ended earlier than it did. The authoritative values are in
`assignmentScheduleInstances` while the assignment is live, and the panel should not be used for
this purpose.

## Two details worth recording

`assignmentType` is `activated`, which distinguishes this from a permanent assignment, and
`memberType` is `direct`, which confirms the membership is not inherited through a nested group.
`principalId` is `03ee6546`, `adm-jsmith`. The instance names the principal, so the elevation
itself is attributable here even though the revocation in `evidence/10` is not yet.

The stored duration is 1 hour 59 minutes 59.407 seconds rather than exactly two hours, from
`startDateTime` `.623` against `endDateTime` `.03`. The sub-second difference is noted and no claim
is made about its cause.

## Confirms the completed action fell inside the window

`evidence/10` recorded `signInSessionsValidFromDateTime` on `dumbuser2` as 2026-09-10T14:32:27Z.
That instant sits 11 minutes 47 seconds after this window opened and 1 hour 48 minutes before it
closed. Both boundaries are now Captured rather than read from a portal blade.
