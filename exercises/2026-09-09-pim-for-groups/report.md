# PIM for Groups: the gates fire, the access arrives, and the log stays quiet

## What I set out to do

Test whether activated membership of a role-assignable group, governed by PIM, actually delivers
effective `User Administrator` to an eligible member. The previous exercise
(`exercises/2026-09-06-b4-pim-eligible-role`) made `adm-jsmith` eligible for the role directly. This
one puts the same role behind a group instead, which is the pattern Microsoft documents for
consolidating privileged access, and asks whether the access arrives when the gates open.

A secondary question came out of the first session and turned out to matter more: what does a
refused privileged action leave behind in the audit log.

## The setup

The Entra tenant on a P2 trial that ends 2026-10-04. One cloud-only, role-assignable security group,
`PIM-UserAdmin-Pilot` (`3265375f`), holding `User Administrator` at tenant scope as a standing
assignment. One eligible member, `adm-jsmith` (`03ee6546`), eligible to 2026-12-08. One test target,
`dumbuser2` (`11033cf6`).

Pre-flight for the second session, `evidence/07`, at 2026-09-10T14:13:49Z: VM 100 and VM 107
running, thin pool Data% 84.12 against an 85 stop condition, Meta% 4.21. The pool had risen 0.15
points in 23.5 hours with no VM created, no snapshot taken and no disk extended. Running guests
write, thin volumes grow, and nothing returns the blocks. The stop condition can be crossed by doing
nothing.

The work itself touched only the tenant.

## What I did

Session one, 2026-09-09, recorded in `evidence/01` to `06`: created the group, assigned the role to
it, granted `adm-jsmith` eligible membership, captured the untouched default member policy, hardened
that policy, and ran the activation transaction as far as `Activated` without testing the resulting
access.

Session two, 2026-09-10:

1. Confirmed the direct path was cold. `PIM` → `My roles` → `Microsoft Entra roles` →
   `Active assignments` returned `No results` for `adm-jsmith`. Without this the test attributes
   nothing, because B4's direct eligibility is still in place by decision.
2. Requested group member activation at 14:18:53Z with the justification `yah`. Approved it at
   approximately 14:20:39Z with the justification `yup`.
3. Attempted the same `dumbuser2` password reset that was refused at 02:30Z.
4. Ran `revokeSignInSessions` on `dumbuser2` at 14:32:27Z as `adm-jsmith`.
5. Captured the transaction over Graph:

```
GET /v1.0/users/11033cf6-328f-4a1a-b66d-82807b0f2acb
    ?$select=id,userPrincipalName,userType,onPremisesSyncEnabled,onPremisesDistinguishedName,
             onPremisesImmutableId,onPremisesLastSyncDateTime

GET /v1.0/users?$select=id,userPrincipalName,userType,onPremisesSyncEnabled&$top=999

GET /v1.0/users/11033cf6-328f-4a1a-b66d-82807b0f2acb
    ?$select=id,userPrincipalName,signInSessionsValidFromDateTime

GET /v1.0/identityGovernance/privilegedAccess/group/assignmentScheduleInstances
    ?$filter=groupId eq '3265375f-23f9-4d3f-81d3-15370199bc8a'

GET /v1.0/auditLogs/directoryAudits
    ?$filter=activityDateTime ge 2026-09-10T02:00:00Z
     and targetResources/any(t:t/id eq '11033cf6-328f-4a1a-b66d-82807b0f2acb')

GET /v1.0/auditLogs/directoryAudits?$filter=activityDateTime ge 2026-09-10T02:00:00Z
```

## Where Raymond was consulted

- **Group name.** I proposed `PIM-UserAdmin-Pilot`, matching the `PKI-CBA-Pilot` convention already
  in this repository. Raymond: "go with your naming convention."
- **Reuse `User Administrator`, or pick a different role.** I recommended reuse, for a direct
  contrast between role-level and group-level PIM. Raymond answered with a lived precedent rather
  than a yes: at a prior employer, new help-desk hires had permissions copied by sight from an
  existing named user, until the sysadmin insisted on drilling the access down to a group. Once the
  group existed, only the sysadmin could adjust it, and later requests went through that gate or did
  not get added. Paraphrased from his account. Reuse confirmed.
- **Who is eligible.** `adm-jsmith`. Raymond: "good."
- **Whether to remove B4's direct eligibility once the group path is proven.** Microsoft's framing of
  group-based role assignment is consolidation, one governed path rather than two, which argued for
  removal. Raymond: "leave in place for the sake of the lab, note to remove before we nuke the lab
  for whatever reason." Two live paths now exist deliberately, tracked in `EXPOSURES.md`.
- **Capture the ungoverned default first, or configure hardened settings immediately.** Raymond:
  "your call, go with microsoft if not sure." Microsoft's scenario guidance for groups that elevate
  into a directory role calls for approval on member activation, not owner only. Captured the default
  first, then hardened.
- **Running `Revoke sessions` on `dumbuser2`.** The action touches account state, so it waited on his
  word. I recommended it because password reset was impossible in this tenant for reasons below.
  Raymond: "go, just revoked sessions on dumbuser2 via the entra portal."

## What the box said

**The refusal changed shape, and that is the proof.** Same account, same target, same route through
the portal. Only the activation state differed.

Before, at 02:30Z, holding eligibility only:

```
The password can not be reset. This may be due to an incorrect level of administrative
privilege or if trying to reset your own password.
```

After, at approximately 14:29Z, holding activated membership:

```
Unfortunately, you cannot reset this user's password because password writeback is not
enabled in your tenant.
```

An authorization refusal became a tenant capability refusal. The portal evaluates authorization
first, so reaching the second message proves the first gate stopped firing. `Edit properties` and
`Delete` were greyed out in the before-state and rendered enabled in the after-state.

**The completed action.** `evidence/10`:

```json
{ "id": "11033cf6-328f-4a1a-b66d-82807b0f2acb",
  "signInSessionsValidFromDateTime": "2026-09-10T14:32:27Z" }
```

**Attributed.** `evidence/12`:

```json
{ "result": "success",
  "activityDisplayName": "Update user",
  "activityDateTime": "2026-09-10T14:32:27.4602239Z",
  "initiatedBy": { "user": { "id": "03ee6546-f113-4ec5-ba9d-e57381b0c928" } } }
```

**Inside the window.** `evidence/11`:

```json
{ "startDateTime": "2026-09-10T14:20:40.623Z",
  "endDateTime":   "2026-09-10T16:20:40.03Z",
  "principalId":   "03ee6546-f113-4ec5-ba9d-e57381b0c928",
  "assignmentType": "activated",
  "memberType":     "direct" }
```

`adm-jsmith` held `User Administrator` only through activated group membership, with the direct path
confirmed cold beforehand, and completed a privileged action the directory recorded as successful
and attributed to that account. The hypothesis is answered from machine output at every link.

**The clock starts at approval, and the approval panel lies about it.** The approver's panel showed
`Start 14:18Z` and `End 16:18Z`, request time plus the two-hour maximum. The platform stored
`14:20:40.623Z` to `16:20:40.03Z`, approval time plus two hours. The requester lost none of the
window to the 2m40s spent pending. The panel's values are a projection computed at request time, and
its error equals the length of the pending period. An investigator reconstructing an elevation window
from the approval record will believe access ended earlier than it did.

**`User Administrator` cannot read the log of its own actions.** The same activated session that
reset tokens on a user was refused `auditLogs/directoryAudits` with
`Authentication_RequestFromUnsupportedUserRole`. The reporting API admits Global Administrator,
Global Reader, Security Administrator, Security Reader, Reports Reader and Compliance Administrator.
The identical query returned `200` under the break-glass account, which demonstrates the boundary
from both sides rather than a client fault.

**The refusal left nothing.** Across the whole tenant from 02:00Z, no event corresponds to the 02:30Z
denial. The nearest records are two `Validate user authentication` events at 02:30:25 and 02:31:48.
The platform logged that the token was valid. It did not log that the account was stopped.

**PIM alerts on its own recommended architecture.** Five `RoleElevatedOutsidePimAlert` events at
03:17:42, 05:24:00, 07:42:14, 09:40:42 and 12:06:34, roughly two-hourly, each naming
`User Administrator` and `PIM-UserAdmin-Pilot`, each with a distinct request id and no accompanying
`Core Directory` assignment. The standing role assignment on the group is the documented pattern for
PIM for Groups, and PIM's alert engine treats it as a role assigned outside PIM.

**Early deactivation is refused.** `Process role removal request` at 02:54:42.811766Z,
`result: failure`, `resultReason: ActiveDurationTooShort`, 3m43s after activation.

## What broke, and why

**The test target was chosen before the tenant was checked.** `dumbuser2` is mastered on-premises —
`onPremisesSyncEnabled: true`, `CN=dumb user2,OU=Site 1,OU=Test Users,DC=district,DC=local` — and
this tenant does not have password writeback enabled. An administrative password reset against that
user was impossible at any privilege level. The exercise picked an action gated by two independent
conditions and varied only one of them.

The result survives, because the two gates are evaluated in sequence and the observed message moved
from the first to the second. But it took three additional captures to establish that, and the
cleanest proof of the hypothesis had to come from a different action entirely. Twelve of the
tenant's sixteen users are synced; of the four cloud-only accounts, two are break-glass, one is
`adm-jsmith` itself, and one is `labadmin` whose roles have never been read. No confirmed valid
password-reset target exists in this tenant today.

**I recorded a signing identity I had not confirmed.** `evidence/09`'s capture header originally
said the Graph reads ran as the break-glass account. I wrote that from the instruction I had given,
not from evidence. Two later calls proved Graph Explorer had been signed in as `adm-jsmith`, which
holds its own sign-in independent of the portal session and unaffected by which browser window is
used. The response bodies were unaffected, because directory object values do not depend on who
reads them. The header was wrong and is corrected on the record rather than edited away.

**PIM for Groups splits its Graph scopes three ways.** Writing group eligibility needs
`PrivilegedEligibilitySchedule.ReadWrite.AzureADGroup`, not the role-level
`RoleManagement.ReadWrite.Directory`. Reading an active group assignment needs a third family,
`PrivilegedAssignmentSchedule.Read.AzureADGroup`. Each is a separate admin-consent decision, and
`adm-jsmith` can consent to none of them.

**Fixing that created a permanent grant.** Consenting the read scope widened Graph Explorer's
delegated permissions to `AllPrincipals` across a set that includes `Directory.ReadWrite.All`,
`RoleManagement.ReadWrite.Directory` and `User.EnableDisableAccount.All`. A second application,
Microsoft Graph Command Line Tools, received a similar grant at 02:00:33Z during the
`Connect-MgGraph` attempts that never succeeded. Neither grant is bounded in time and neither is
scheduled for review.

**A stray activation contaminated the first session's attempt.** On 2026-09-09 an activation was
requested against B4's direct eligibility rather than the group, and approved before the mistake was
caught. Session two's first step exists because of it.

**Two claims of mine were wrong and are retracted on the record.** I asserted from the approval panel
alone that the activation clock runs from request time and that a slow approver silently shortens
access; `evidence/11` disproves it. I asserted that bringing the group under PIM needed a separate
"Discover groups" step; the first eligibility request onboards the group automatically.

## What I'd do differently

Check what the tenant can actually do before choosing the action that tests privilege. One read of
`onPremisesSyncEnabled` and the writeback state would have selected `revokeSignInSessions` at the
start and removed three captures from the critical path.

Never write an actor into a capture header that I have not seen. The signing identity is part of the
evidence, not part of the instruction.

Price a consent prompt before clicking it. The grant that unblocked one read is permanent,
tenant-wide, and larger than the read required. Recording what it cost is the minimum; the better
answer is to ask whether the query could have run another way.

Treat "the control fired" and "the access arrived" as two separate claims from the outset. The first
session proved the first and called the exercise nearly done. It was half done, and the half that
was missing is the half an interviewer would ask about.

## Open questions

- What is PIM's minimum active duration before deactivation is permitted? `ActiveDurationTooShort`
  fired at 3m43s. The threshold is not established.
- Can the `RoleElevatedOutsidePimAlert` for a PIM-for-Groups architecture be suppressed without also
  suppressing genuine out-of-PIM assignments? If not, adopting the documented pattern costs a
  detection capability permanently.
- Does any telemetry outside `directoryAudits` record a refused privileged action? Sign-in logs
  record the session. Nothing found so far records the attempt.
- Should the reporting role be made PIM-eligible, so an administrator can review their own actions
  without a standing grant? This is the governed answer to the gap in `evidence/09` section D and is
  the strongest candidate for the next exercise.
- What is `wids` value `b79fbf4d-3ef9-4689-8143-76b194e85509`? It appears on both `adm-jsmith` and
  the break-glass account.
- Why does the Access Reviews service write a parallel record of every PIM approval?
- Why did `dumbuser2` carry `StsRefreshTokensValidFrom` of `2025-10-01T00:34:24Z` when its cloud
  object was created 2026-09-01? The October 2025 build is the reason this repository's evidence
  discipline exists, and a value from it surfacing here is worth chasing.
- Does deactivation or expiry actually revoke effective access, or only the assignment record?
- The owner activation policy has never been opened.
