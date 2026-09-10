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
