# B4 — PIM: convert a standing grant into a just-in-time one — evidence log

Started 2026-09-06. Run order item 0 folded in. See Where Raymond was consulted for the
B1-before-B4 swap.

## Captured

- Pre-flight readings, Domain Admins membership, and `sysadmin`'s standing state.
  Thin pool Data% 79.28, under the 85 gate. Domain Admins holds `Administrator` and
  `System Admin` (`sysadmin`). `sysadmin` has `adminCount` 1, `Enabled` true, and membership in
  `Domain Admins` and `SG_admin_tier0_domain`. `whenChanged` 2026-09-01T00:27:04Z.
  This is the standing grant B4 tests, and it confirms B4's premise without change.
  `evidence/01-preflight-and-dc01-standing-state.md`
- The P2 trial window. `createdDateTime` 2026-09-04T00:00:00Z, `nextLifecycleDateTime`
  2026-10-04T00:00:00Z, `isTrial` true, 100 licences. Retires the Recalled clock.
  `evidence/02-p2-trial-window-captured.md`
- Active Entra directory role assignments before PIM. Two rows only. Global Administrator on the
  break-glass account. Directory Synchronization Accounts on `Microsoft.Azure.SyncFabric`.
  `evidence/03-active-directory-role-assignments.md`

- Tenant user inventory, 15 objects. The original Global Administrator,
  `raytakosharky_gmail.com#EXT#@...`, is disabled. `breakglass` and `labadmin` are disabled.
  The break-glass account is the only enabled account holding an active directory role.
  `sysadmin` is synced to Entra and enabled while holding on-premises `Domain Admins`.
  `evidence/04-tenant-user-inventory-and-empty-eligibility.md`
- `adm-jsmith` created, cloud-native, id `03ee6546-f113-4ec5-ba9d-e57381b0c928`. Password typed
  by Raymond in Graph Explorer, never sent to Claude, redacted in the evidence file.
  `evidence/05-adm-jsmith-created.md`
- An over-limit activation request at PT4H is refused during validation. The error is
  `RoleAssignmentRequestPolicyValidationFailed` and it names `ExpirationRule`. No request object
  persists. Captured 2026-09-09, with the PT2H ceiling re-read in the same session.
  `evidence/16-over-limit-activation-refused-at-validation.md`

## Not captured, and why

- The empty PIM eligibility result. Raymond reported HTTP 200 with an empty `value`. The literal
  body was not pasted, so the before-state is Recalled. Re-run pending.
- `usageLocation` and `accountEnabled` on `adm-jsmith`. The create response does not echo them.
  Read-back pending.
- The P2 licence assignment on `adm-jsmith`. Response body not pasted. Read-back pending.
- Whether the disabled original Global Administrator holds any role assignment. It returned no
  row from `roleAssignments` and cannot sign in. Not pursued further.

## Where Raymond was consulted

- **Run order.** Asked whether to hold the published order, which places B1's fourth policy
  before B4. He answered "no hard date, keep the run order — start B4". Claude flagged the
  conflict and swapped items 1 and 2, on the receipt that both exercises need the trial but only
  B4's evidence is deleted at expiry. Paraphrase of Claude's reasoning; his instruction is quoted.
- **Portfolio deadline.** Asked whether a date exists by which the repository must be
  presentable. He answered no. C1 therefore stays after C2 in the run order.
- **Eligible role.** Claude recommended User Administrator, on the argument that it is the
  standing grant real tenants never remove, and that a failed Global Administrator activation
  would lock him out of his own tenant. He answered "user administrator, yeah". Decided.
- **Eligible account name.** He proposed `pim-admin@`. Claude recommended `adm-jsmith@`, on the
  argument that the account outlives the exercise and should name its function rather than the
  tool. He answered "go with adm-jsmith". Decided.
- **Approver, and the activation window.** Claude named three options: break-glass as sole
  approver, leave approval off, or invent a second admin persona. Claude recommended the first,
  on the argument that it produces a real approval trail and honestly exposes the limit of a
  single-administrator tenant. Claude also recommended tightening `maximumDuration` from PT8H to
  PT2H. He answered "option 1, and yeah tighten it to PT2H". Decided.
- **Break-glass in daily use.** Asked whether he signs in as the break-glass account for
  day-to-day tenant work. He answered "yeah I use it for everything". This is Recalled, and it
  matches the captured role assignments. It makes the account a break-glass account in name only.
  B4 step 7's assumption of a separate working administrator account is wrong for this tenant.

## Corrections

- **Claude named two role definitions from memory, 2026-09-06.** `evidence/03` asserted that
  `62e90394-69f5-4237-9190-012177145e10` is Global Administrator and that
  `88d8e3e3-8f55-4a1e-953a-9b9898b8876b` is Directory Synchronization Accounts. Neither name came
  from a capture. The second is contradicted by the `roleDefinitions` read for User Administrator,
  which returns `inheritsPermissionsFrom` `88d8e3e3-8f55-4a1e-953a-9b9898b8876b`. Built-in roles
  inherit from Directory Readers, not from Directory Synchronization Accounts. Both names are
  struck from `evidence/03`. Resolved the same session by direct reads, captured in
  `evidence/09`. Global Administrator was right. Directory Synchronization Accounts was wrong;
  the role is Directory Readers, which is read-only. The wrong name overstated the service
  principal's privilege. Caught by Claude, unprompted.
- **Claude wrote an unsupported `$filter`, 2026-09-06.** `roleDefinitions` returned
  `Request_UnsupportedQuery`, "Or operator not supported for this entity set". The same endpoint
  family accepts `and`. Captured in `evidence/08`. Goes to `references/gotchas.md` at close.
- **Claude abbreviated a policy id and cost two attempts, 2026-09-06.** The instruction wrote the
  role management policy id as `P`, and the literal `P` was sent in two PATCH URLs. Both returned
  `UnknownError` / `MissingProvider`. Claude read the first failure as a request-body problem and
  proposed a body change, which was the wrong hypothesis. The URL was the fault. Recorded in
  `evidence/11`. Goes to `references/gotchas.md` at close.
- **Claude stated that B4 had not started, 2026-09-09.** Asked for the biggest blocker, Claude
  read `CARRYOVER.md`'s line "B4's PT4H re-run is owed" and reported B4 as not started, with a
  deadline of 2026-10-04. Claude repeated the error in a management-level summary and asked
  Raymond to reserve four hours. `CURRICULUM.md` line 137 records B4 complete 2026-09-07. The
  owed work was one unresolved question, and it took one API call. The cause was reading carryover
  without reading `CURRICULUM.md`'s status column. Corrected before the re-run began.

## Open questions

- `sysadmin` is synced to Entra while holding on-premises `Domain Admins` with `adminCount` 1.
  Microsoft advises against syncing on-premises privileged accounts. Documented, not lab-captured.
  Out of B4's scope. Decide at close whether it enters `EXPOSURES.md`.
- The `R M` row in `evidence/04` holds Raymond's personal address in the original Global
  Administrator's UPN. The standing redaction rule covers the current Global Administrator only.
  The 2026-09-04 PII decision is still deferred. Decide before commit.
- Does the tenant's original Microsoft Account Global Administrator still hold an active
  assignment? Unresolvable through the endpoints used so far.
- Does a PIM-eligible user need an assigned P2 licence? Microsoft documents that each user
  eligible for a PIM-managed role needs one. Not lab-captured. The break-glass account holds an
  active Global Administrator grant with `assignedLicenses` empty, which does not settle the
  eligible case.

## Not started

- ~~B4 steps 2 through 8.~~ **Stale, corrected 2026-09-09.** This line was written mid-exercise and
  never updated. Steps 2 through 8 ran. `CURRICULUM.md` records B4 complete 2026-09-07, and
  `report.md` covers the steps. Nothing in B4 is unstarted.

## Design change, 2026-09-06

B4 as written in `CURRICULUM.md` makes a role eligible on a new cloud-native account, and keeps
break-glass active and outside PIM. That plan assumed a working administrator account already
exists. It does not. The revised design:

1. Create `adm-jsmith`, cloud-native, as the working administrator account.
2. Make one Entra role eligible-not-active on it, behind approval, time-bound.
3. Return the break-glass account to a control that is never used for routine work.

The tenant's real starting condition is one account that is simultaneously the only administrator
and the emergency-access path. Name that in the report. It is the permission-sprawl pattern
reached from the opposite direction: not sprawl by copying, but concentration by never splitting.
