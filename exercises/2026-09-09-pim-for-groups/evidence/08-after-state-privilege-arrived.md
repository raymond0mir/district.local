# The after-state test: the privilege arrived, the action still failed

## Capture header

```
Source:  Microsoft Entra admin center, portal views (no command line)
Host:    Mac Mini, private browser window, signed in as adm-jsmith
UTC:     2026-09-10T14:14Z to 2026-09-10T14:30Z
```

## Source and claim label

Portal screenshots, Microsoft Entra admin center, 2026-09-10 morning PDT, `adm-jsmith` in a
private browser window. **Recalled, not Captured.** PDT is UTC-7. The Graph capture pass that
would move these to Captured is listed under Owed.

## Sequence

| Local (PDT) | UTC | Event |
| --- | --- | --- |
| 07:1x | 14:1x | `Active assignments` under My roles shows `No results`; direct path cold |
| 07:18 | 14:18 | Group member activation requested, `PIM-UserAdmin-Pilot`, reason `yah` |
| 07:20 | 14:20 | Request approved by the break-glass account, justification `yup` |
| 07:20:40 | 14:20:40 | Assignment start, inferred from End time and policy duration |
| 07:2x | 14:2x | After-state test: `dumbuser2` reset attempted, same browser session |
| 09:20:40 | 16:20:40 | Assignment end, observed |

## The control case held before activation

`My roles` → `Microsoft Entra roles` → `Active assignments` returned `No results` for
`adm-jsmith` immediately before the request. B4's direct `User Administrator` eligibility was not
active. Any privilege observed after activation is therefore attributable to the group path and
not to the direct path. This is the check the previous session lost when a stray direct
activation was approved in error.

## The refusal changed shape, and that is the finding

Both attempts used the same route: Entra ID → Users → `dumbuser2` → Reset password. The account,
the target and the control are identical. Only the activation state differs.

**Before, 2026-09-10T02:30Z, eligibility only** (`evidence/06`):

```
The password can not be reset. This may be due to an incorrect level of administrative
privilege or if trying to reset your own password.
```

**After, 2026-09-10T14:2xZ, membership Activated:**

```
Unfortunately, you cannot reset this user's password because password writeback is not
enabled in your tenant.
```

The first message is an authorization refusal. The second is a tenant capability refusal. The
portal evaluates authorization first and capability second, so reaching the second message proves
the first gate no longer fires.

**Activated group membership delivers effective `User Administrator`.** That is the hypothesis of
this exercise, and this is the evidence for it. The proof is the change in refusal text, not a
completed action.

Corroborating, in the same view: `Edit properties` and `Delete` were greyed out in the before-state
recorded in `evidence/06`. Both render enabled in the after-state screenshot.

## The test target was the wrong one

Password writeback is an Entra Connect capability that returns a cloud-initiated password change
to on-premises Active Directory. It applies to users mastered on-premises. Its appearance here
indicates Entra treats `dumbuser2` as a synced user, object id
`11033cf6-328f-4a1a-b66d-82807b0f2acb`, created 2026-09-01.

If that reading holds, this action could never have succeeded from the portal at any privilege
level, because the tenant does not have writeback enabled. The exercise chose an action gated by
two independent conditions and varied only one of them.

**This does not invalidate the result.** The authorization gate and the capability gate are
evaluated in sequence, and the observed message moved from the first to the second. It does mean
the exercise has not yet produced a completed privileged action attributable to `adm-jsmith`
through the group path.

`dumbuser2`'s sync status is asserted from the message text alone. It is not established. The
Graph read is listed under Owed.

## The activation clock starts at approval

The approver's panel displayed `Start time 9/10/2026, 7:18 AM` and `End Time 9/10/2026, 9:18 AM`
before approval — request time plus the two-hour policy maximum.

The resulting active assignment reads `End time 9/10/2026, 9:20:40 AM`. Approval occurred at
07:20. Two hours before the observed end is 07:20:40, which matches approval time and not request
time.

**A retraction is now resolved.** `evidence/06` withdrew Claude's claim that the activation clock
runs from request time, and that a slow approver silently shortens the granted access. That claim
is not merely withdrawn. It is **disproven**. The platform starts the window at approval and
grants the full configured duration. The approval panel's Start and End values are a projection
computed at request time, and the platform does not honour them once approval is delayed.

The practical consequence is small and real. An administrator reading an approval record sees a
window that is not the window granted. Any reasoning about when elevation ended, from the
approval panel alone, is wrong by the length of the pending period.

Start time was not read directly. It is inferred from the observed End time and the two-hour
policy duration captured in `evidence/05`. The Graph read settles it.

## The justification fields still validate nothing

Requester reason: `yah`. Approver justification: `yup`. `Ticket number` and `Ticket system` are
both empty, because `Require ticket information on activation` is `No`.

This repeats `evidence/06`'s finding on a separate day, through a separate submission, by both
parties to the gate. Two observations, not one.

## Owed

- A Graph read of the group assignment schedule instance, for `startDateTime` and `endDateTime`
  as the platform stores them rather than as the portal renders them.
- A Graph read of `dumbuser2`, for `onPremisesSyncEnabled`, `onPremisesDistinguishedName` and
  `onPremisesImmutableId`, to establish or refute the synced-user reading above.
- A completed privileged action attributable to `adm-jsmith` through the group path, on a target
  not gated by password writeback.
- A `directoryAudits` read covering 02:30Z to the present, to determine whether the denied
  attempt at 02:30Z produced an audit event at all. A privileged action refused at the
  authorization gate may leave no record, which would be a detection gap.
