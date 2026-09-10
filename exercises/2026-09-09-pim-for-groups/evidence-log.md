# PIM for Groups — evidence log

## Captured

- **`PIM-UserAdmin-Pilot` exists, cloud-only, role-assignable, Assigned membership.** Created
  under the Global Administrator account after `adm-jsmith`'s attempt at the same call was
  refused. `onPremisesSyncEnabled: null`, `groupTypes: []`, `membershipRule: null` confirm it
  satisfies every precondition B4 named for PIM for Groups: never synced, not dynamic, not a
  Microsoft 365 group. `evidence/01`.
- **`PIM-UserAdmin-Pilot` holds `User Administrator` tenant-wide, as a standing assignment.**
  `201 Created`, `directoryScopeId: "/"`. This is the second live path to `User Administrator` in
  this tenant alongside B4's direct eligible assignment on `adm-jsmith`, left in place
  deliberately per Raymond's decision above. `evidence/02`.
- **`adm-jsmith` holds eligible membership in `PIM-UserAdmin-Pilot`, expiring 2026-12-08.** Two
  defaults surfaced and are Captured on the way to this: the required Graph scope for group
  eligibility differs from the scope for role eligibility
  (`PrivilegedEligibilitySchedule.ReadWrite.AzureADGroup`, not `RoleManagement.ReadWrite.
  Directory`), and this group's default policy refuses a permanent (`noExpiration`) eligible
  assignment where B4 found the `User Administrator` role's own default policy allows one. All
  three attempts, in order, in `evidence/03`.
- **The group's default member activation policy requires no MFA and no approval.** Activation
  maximum duration 8 hours, `On activation, require: None`, justification checked, approval
  unchecked with no approver. The settings list reports both Member and Owner as
  `Modified: No` — untouched defaults. Weaker than the Entra role default B4 captured, which
  requires MFA. Recalled from portal screenshots, not Captured. `evidence/04`.
- **The member policy is hardened: 2-hour window, Azure MFA required, approval required with one
  approver.** Saved 2026-09-10T02:23:09Z (2026-09-09 19:23:09 PDT). The Settings list corroborates
  independently — Member moved to `Modified: Yes` with a timestamp and an updating account, Owner
  still `No`. The same view's Assignment tab explains `evidence/03`'s earlier refusal outright:
  `Allow permanent eligible assignment: No`, with eligible assignments capped at 1 year. The
  single approver is the break-glass account, which also administers the tenant — the control is
  configured, separation of duties is not demonstrated, and `evidence/05` states that limitation
  rather than leaving it implied. Recalled, not Captured. `evidence/05`.
- **The activation transaction ran partway, and the gates fired.** `adm-jsmith` was denied a
  `dumbuser2` password reset while holding only eligibility; requested activation from
  My roles → Groups; got a justification field and a duration selector but **no MFA prompt**,
  which is documented behavior for a session that already satisfied MFA at sign-in; landed in
  `Pending approval`; and showed `Activated` after approval. Both sides of the approval gate
  demand free text and neither validates it. **The after-state test was never run**, so effective
  access is unproven. Recalled, not Captured. `evidence/06`.

- **Pre-flight, session two, 2026-09-10T14:13:49Z.** VM 100 and VM 107 running. Thin pool Data%
  84.12, Meta% 4.21, under the 85 gate with 0.88 points of headroom. Data% rose 0.15 points in 23.5
  hours with no VM created, no snapshot taken and no disk extended. Running guests write, thin
  volumes grow, nothing returns the blocks. The stop condition can be crossed by doing nothing.
  Two readings, not a trend. `evidence/07`.
- **The authorization gate stopped firing after activation.** Same account, same target, same
  portal route. The refusal moved from "incorrect level of administrative privilege" to "password
  writeback is not enabled in your tenant". Authorization is evaluated before tenant capability, so
  reaching the second message proves the first gate passed. `Edit properties` and `Delete` were
  greyed out before and enabled after. Recalled from screenshots. `evidence/08`.
- **`dumbuser2` is mastered on-premises.** `onPremisesSyncEnabled: true`,
  `CN=dumb user2,OU=Site 1,OU=Test Users,DC=district,DC=local`, last synced 2026-09-01T23:57:46Z.
  The writeback refusal was a real capability gate, not a disguised authorization failure. Captured.
  `evidence/09`.
- **Twelve of sixteen tenant users are synced.** Four are cloud-only: `adm-jsmith`, `labadmin`, the
  rotated-out `breakglass@`, and the current Global Administrator at `6ca413e3`. That object id
  matches the `initiatedBy` principal already recorded in `EXPOSURES.md`, which confirms the
  break-glass account and the account doing routine tenant work are one object. Captured.
  `evidence/09`.
- **A completed privileged action through the group path.** `revokeSignInSessions` on `dumbuser2`
  stamped `signInSessionsValidFromDateTime: 2026-09-10T14:32:27Z`. Captured. `evidence/10`.
- **The activation window as the platform stores it.** `startDateTime 2026-09-10T14:20:40.623Z`,
  `endDateTime 2026-09-10T16:20:40.03Z`, `principalId 03ee6546`, `assignmentType activated`,
  `memberType direct`. Start is approval time, not request time. Captured. `evidence/11`.
- **Attribution of the completed action.** `directoryAudits` returns `Update user` and
  `Update StsRefreshTokenValidFrom Timestamp` at 14:32:27.46Z, `result: success`,
  `initiatedBy.user.id 03ee6546`. One portal click produced two rows sharing one `correlationId`.
  Captured. `evidence/12`.
- **The 02:30Z refusal produced no audit event, at tenant scope.** With the target filter removed,
  the nearest records are two `Validate user authentication` events at 02:30:25 and 02:31:48. The
  platform logged that the token was valid and did not log that the account was stopped. Captured.
  `evidence/13`.
- **PIM alerts on its own recommended architecture, roughly every two hours.** Five
  `RoleElevatedOutsidePimAlert` events at 03:17:42, 05:24:00, 07:42:14, 09:40:42 and 12:06:34, each
  naming `User Administrator` and `PIM-UserAdmin-Pilot`, each with a distinct request id and no
  accompanying `Core Directory` assignment. The standing role assignment on the group is the
  documented pattern. Captured. `evidence/13`.
- **Early deactivation is refused.** `Process role removal request`, 02:54:42.811766Z,
  `result: failure`, `resultReason: ActiveDurationTooShort`, 3m43s after activation. Captured.
  `evidence/13`.
- **Neither activation was deactivated; both expired.** The stray direct activation ended
  04:42:10.95Z and the group activation ended 04:51:00.99Z, both by `Azure AD PIM` with
  `ActionType: Revoke`. Captured. `evidence/13`.
- **`evidence/05` is upgraded from Recalled to Captured.** `Update role setting in PIM` at
  02:23:09.790418Z enumerates the hardening: two-hour maximum, MFA on activation, approval required
  with one approver, MFA on active assignment. `evidence/13`.
- **`evidence/06`'s MFA explanation is upgraded from documentation to evidence.**
  `IsAuthenticatedWithMfa: True` on both activation requests. The Authenticator satisfied the claim
  at sign-in 1m50s earlier, not at elevation. `evidence/13`.

## Not captured, and why

- **The default member and owner activation policies were read in the portal, not over Graph.**
  Three attempts to read `policies/roleManagementPolicyAssignments` for this group through Graph
  Explorer each returned the signed-in user's own object with `@odata.context #users/$entity`,
  once with a green `OK - 200 - 243 ms` against a URL the screenshot confirms was the correct
  `roleManagementPolicyAssignments` query. Those two facts cannot both describe one request, and
  the cause is not established. A switch to the Microsoft Graph PowerShell SDK was attempted as a
  workaround and stalled at `Connect-MgGraph`, which timed out after 120 seconds on both the
  browser and device-code flows. The policy values in `evidence/04` are therefore Recalled from
  screenshots. The Graph read that would make them Captured is still owed.
- **`adm-jsmith` cannot create the role-assignable group.** Signed into Graph Explorer as
  `adm-jsmith`, the `POST /groups` call with `isAssignableToRole: true` returned `403
  Authorization_RequestDenied, "Insufficient privileges to complete the operation."` A separate
  "Need admin approval" prompt also appeared for the `Group.ReadWrite.All` permission itself,
  which `adm-jsmith` cannot self-consent. Two candidate causes are tangled in one screenshot: a
  missing OAuth consent, and `adm-jsmith` holding only `User Administrator` (eligible, from B4)
  where creating a role-assignable group needs `Privileged Role Administrator`
  ([Create a role-assignable group in Microsoft Entra ID](https://learn.microsoft.com/entra/identity/role-based-access-control/groups-create-eligible)).
  Screenshot, Recalled, not separated into the two causes. This is the same shape as the lived
  precedent Raymond gave for decision 2 above: only the sysadmin, not the routine account, could
  touch the governing group.

- **The `Expired assignments` tab was never opened.** Asked for during session two and not
  reported. `evidence/13` answers the underlying question from the audit log instead, so the tab is
  no longer needed.
- **The Owner activation policy detail values.** Still never opened, in either session.
- **PIM's minimum active duration before deactivation is permitted.** `ActiveDurationTooShort` fired
  at 3m43s. The threshold itself is not established and no figure is claimed.

## Where Raymond was consulted
- **Group name.** I proposed `PIM-UserAdmin-Pilot`, matching the `PKI-CBA-Pilot` convention
  already in this repo. Raymond: "go with your naming convention."
- **Reuse `User Administrator`, the role B4 already made `adm-jsmith` eligible for directly, or
  pick a different role.** I recommended reuse, for a direct role-level-vs-group-level PIM
  contrast. Raymond gave a lived precedent instead of a straight yes: at a prior employer, new
  help-desk hires had permissions "copied by sight" from an existing named user, until the
  sysadmin there insisted on drilling access down to a group. Once the group existed, only the
  sysadmin could adjust it, and later permission requests either went through that gate or didn't
  get added at all. Paraphrased from his account. Reuse confirmed.
- **Who's eligible.** `adm-jsmith`. Raymond: "good."
- **Whether to remove B4's direct role-eligibility on `adm-jsmith` once the group path is
  proven.** Microsoft's own framing of group-based role assignment is consolidation — one
  governed path, not two running at once — which argued for removing it. Raymond: "leave in
  place for the sake of the lab, note to remove before we nuke the lab for whatever reason." Two
  live paths to `User Administrator` now exist, deliberately, as a decided and tracked state, not
  an oversight. Tracked in `CARRYOVER.md`'s pending decisions.
- **The group's activation policy: capture the ungoverned default first, or configure hardened
  settings immediately.** Raymond: "your call, go with microsoft if not sure." Microsoft's
  scenario-specific guidance for groups that elevate into a Microsoft Entra role calls for
  approval on eligible **member** activation, not only owner — stronger than the generic
  PIM-for-Groups deployment example, which shows approval required for Owner only and is written
  for lower-stakes resources (Key Vault, Intune, app roles), not role elevation. Capture the
  default first, matching B4's own order for the role-level policy, then harden to require
  approval on both member and owner activation.

## Corrections

- **Claude asserted that the activation clock runs from request time, and that a slow approver
  silently shortens the granted access.** Stated from the approver's panel alone, which showed
  Start 19:36 / End 21:36 PDT. The resulting assignment reads `Start time 19:50:54` — approval
  time. The two disagree, the End time was never read, and the claim was made before the
  confirming read existed. Withdrawn, and recorded in `evidence/06` rather than silently dropped.
- **Claude stated that bringing the group under PIM management needed a separate portal-only
  step, "Discover groups," as its own later turn.** Wrong. Microsoft's own API reference states a
  group cannot be explicitly onboarded to PIM for Groups at all: the first call that creates an
  assignment or eligibility request for it, or updates its policy, onboards it automatically if
  it wasn't already. `evidence/03`'s successful eligibility request already onboarded
  `PIM-UserAdmin-Pilot` — no further step was needed, and none was taken.
  ([Govern membership and ownership of groups by using PIM for Groups](https://learn.microsoft.com/graph/api/resources/privilegedidentitymanagement-for-groups-api-overview?view=graph-rest-1.0#onboarding-groups-to-pim-for-groups))
  Consistent with the one-way-door warning already given before the group was created: once
  onboarded, a group can't be offboarded.

- **Claude recorded a signing identity it had not confirmed.** `evidence/09`'s capture header
  originally read "signed in as the tenant break-glass account". That was written from the
  instruction Claude had given, not from evidence. Two later calls proved Graph Explorer had been
  signed in as `adm-jsmith`, which holds its own sign-in independent of the portal session and
  unaffected by which browser window is used. The response bodies are unaffected, because directory
  object values do not depend on who reads them. The header was corrected on the record, first to
  state the explanation as unestablished and then to state it as established once the break-glass
  re-run returned `200`. Caught by the evidence, not by Raymond.
- **Claude told Raymond the outstanding Graph reads had no deadline. That was wrong for one of
  them.** `assignmentScheduleInstances` returns only live instances, so the stored activation window
  would have become unreadable at 16:20:40Z. Corrected in session, before the deadline passed.
- **Claude's claim that the activation clock runs from request time is now disproven, not merely
  withdrawn.** `evidence/06` withdrew it pending evidence. `evidence/11` contradicts it with machine
  output. The full two hours ran from approval.
- **Two evidence files were edited after they were committed.** `evidence/02` and `evidence/03`
  cited two B4 evidence files by bare number, without the filename, so the cited paths resolved to
  nothing and `validate.py` reported two `reference-missing` ERRORs at session start. The intended
  targets were `exercises/2026-09-06-b4-pim-eligible-role/evidence/08-eligibility-granted.md` and
  `exercises/2026-09-06-b4-pim-eligible-role/evidence/05-adm-jsmith-created.md`. Claude completed both
  citations to the full filenames while the exercise was still open. Writing `report.md` closed the
  exercise, and `check_evidence_immutability` then reported both as `evidence-modified`. The edits
  are declared here rather than left to look like tampering. They change citations only, not
  claims. See `CONSIDERATIONS.md` for the tooling behavior.

## Open questions

- Whether the group's own PIM activation policy (member and owner, which are configured
  separately) inherits any tightening already applied to the `User Administrator` role itself in
  `exercises/2026-09-06-b4-pim-eligible-role`, or starts back at the untouched default —
  `isApprovalRequired: false`, no approvers — that `EXPOSURES.md` names as the tenant-wide
  starting state for every role except that one.

## Not started

- The Owner policy's detail values. The settings list reports it unmodified; its activation tab
  was never opened.
- A Graph read of either policy, to move `evidence/04` and `evidence/05` from Recalled to
  Captured.
- **The after-state test.** Re-run the `dumbuser2` password reset as `adm-jsmith` while group
  membership is active, and confirm it now succeeds where it was denied at 19:30. Without this the
  exercise proves the gates fire and not that the access arrives. This is the hypothesis.
- Reading the End time on the activated assignment, to settle the retracted clock-start claim in
  Corrections.
- Confirming whether the stray direct `User Administrator` activation was deactivated, or expired
  on its own at about 21:42 PDT.
- Confirming deactivation or expiry actually revokes effective access.
- Removing B4's direct role-eligibility on `adm-jsmith`, per the pending decision in
  `CARRYOVER.md` — deferred to before the lab is torn down, not this session.
- `report.md` for this exercise.
