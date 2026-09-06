# B4 — PIM: converting a standing grant into a just-in-time one

**Draft. One capture is still open**: proof that the activation expired without anyone acting.
It is marked below. Nothing in this report treats a pending capture as done.

## What I set out to do

Convert a standing administrative grant into an eligible-not-active grant behind approval, and
capture the full request and approval trail, without the holder losing access it legitimately
needs. The wider hypothesis was that Privileged Identity Management would supply the control the
`district.local` permission-sprawl pattern lacks. The exercise tested where that control reaches,
and where it stops.

The plan assumed the work was mostly configuration. It was not. Two of the three findings came
from reading defaults and refusals rather than from building anything.

## The setup

Proxmox host, DC01 (VM 100), and the Entra tenant holding the Microsoft Entra ID P2 trial.
No new virtual machine. No on-premises change.

Pre-flight, 2026-09-06T16:55:54Z: thin pool `Data%` 79.28, metadata 3.87, both under the 85 gate.
Host memory 6.7Gi available. DC01 running.

The trial window is Captured rather than estimated for the first time. `createdDateTime`
2026-09-04T00:00:00Z, `nextLifecycleDateTime` 2026-10-04T00:00:00Z, `isTrial` true, 100 licences.
This matters because a lapsed P2 licence deletes eligible assignments and PIM configuration, so
this exercise cannot be repeated after the window closes.

Contract and terms: `.claude/skills/tech-compass/SKILL.md`.

## What I did

1. Read the standing state on both sides. On-premises: `Domain Admins` holds `Administrator` and
   `sysadmin`. `sysadmin` carries `adminCount` 1 and membership in `SG_admin_tier0_domain`. In the
   tenant: two active directory role assignments exist in total.
2. Attempted to bring a synced on-premises group under PIM, by setting `isAssignableToRole` on
   `SG_admin_tier1_helpdesk`. Captured the refusal.
3. Created `adm-jsmith`, a cloud-native account, and assigned it the P2 licence.
4. Made User Administrator eligible-not-active on `adm-jsmith`, with no expiry on the eligibility.
5. Read the role management policy defaults before changing them.
6. Set `isApprovalRequired` to true, with the break-glass account as sole approver.
7. Tightened `maximumDuration` for end-user activation from PT8H to PT2H.
8. Registered a password and an Authenticator method on `adm-jsmith`, then requested activation
   for 30 minutes as that account.
9. Approved the request from the approver account, with justification.

Exact syntax for each step is in `evidence/`, one file per thread.

## Where Raymond was consulted

**Run order.** The published order places B1's fourth policy before B4. He said to keep the order
and to start B4. Those conflict. The order was swapped, on the argument that both exercises need
the trial but only B4's evidence is destroyed at expiry. He was told before work began.

**Portfolio deadline.** Asked whether a date exists by which the repository must be presentable.
He said no. C1 therefore stays behind C2.

**Break-glass in daily use.** Asked whether he signs in as the break-glass account for routine
tenant work. He said: "yeah I use it for everything." This answer changed the exercise. See below.

**The eligible account's name.** He proposed `pim-admin@`. The recommendation was `adm-jsmith@`,
because the account outlives the exercise and should name its function rather than the tool. He
said: "go with adm-jsmith".

**The eligible role.** User Administrator was recommended over Global Administrator, because a
failed activation on the latter would lock him out of his own tenant. He agreed.

**The approver.** Three options were named: break-glass as sole approver, leave approval off, or
invent a second admin persona. He chose the first and agreed to the PT2H window. The choice is
honest about the tenant's real limit, and that limit is now a finding rather than an omission.

## What the box said

**The tenant has one working administrator, and it is the emergency-access account.**
`roleAssignments` returned two rows and no continuation token. One grants Global Administrator to
the break-glass account. One grants Directory Readers to the first-party service principal
`Microsoft.Azure.SyncFabric`. The user inventory shows every other administrative identity
disabled, including the tenant's original Global Administrator, a Microsoft Account.
Evidence: `03-active-directory-role-assignments.md`, `04-tenant-user-inventory-and-empty-eligibility.md`.

**No group in this tenant can ever come under PIM for Groups.** All nine groups are synced from
`district.local`. All nine have `isAssignableToRole` null. The property cannot be set after a
group exists: `Request_BadRequest`, "Value for IsAssignableToRole cannot be updated for groups
assignable to role." Governing a group here means building a new cloud-only one. That is a
different design, not a repair.
Evidence: `06-licence-confirmed-and-group-surface.md`, `07-pim-for-groups-refusal.md`.

**Microsoft ships just-in-time on and human approval off.** The untouched policy already required
multi-factor authentication and a justification, and already capped activation at eight hours.
It did not require approval: `isApprovalRequired` false, `primaryApprovers` empty. The policy's
`lastModifiedDateTime` was null, so these were defaults and not prior choices.
Evidence: `10-activation-policy-defaults.md`.

**The approval trail separates the two justifications.** Request at 17:53:52Z by `adm-jsmith`,
with its own stated reason. Approval at 17:57:04Z by the approver account, with a separate stated
reason. `reviewResult` moved `NotReviewed` to `Approve`. The request object records the outcome.
The approval object records the reasoning.
Evidence: `12-mfa-registered-and-activation-requested.md`, `13-approval-chain.md`.

**An activation is a real role assignment, with a clock.** At 18:10:47.01Z the role appeared in
`roleAssignments`, the same endpoint that lists standing grants, with `assignmentType` `Activated`
and `endDateTime` 18:40:45.843Z. While live, the grant is indistinguishable in effect from a
permanent one. The whole difference is time. One GUID links the request, the approval, the
schedule, and the live assignment.
Evidence: `14-activation-live.md`.

**Pending.** Proof that the assignment expired at 18:40:45.843Z with no action taken. That is B4
step 6, and it is the single capture this exercise most depends on.

## What broke, and why

The session named two role definitions from memory rather than from a capture. It called
`88d8e3e3-8f55-4a1e-953a-9b9898b8876b` "Directory Synchronization Accounts". A later read
returned Directory Readers. The wrong name overstated the service principal's privilege in a
report about privilege. Both names were then read directly from `roleDefinitions` and the
original claim was retracted in the evidence file rather than edited away.
Evidence: `09-role-names-verified-and-policy-located.md`.

A role management policy id was abbreviated to `P` in a working instruction, and the literal
character was sent in two PATCH URLs. Entra returned `UnknownError` with `MissingProvider`,
because the id encodes its provider in the first segment and is parsed before lookup. The first
failure was misread as a request-body problem, and an attempt was spent testing that wrong
hypothesis. Two attempts were lost to an abbreviation.
Evidence: `11-approval-required-and-window-tightened.md`.

The approval surface does not exist on Graph v1.0. `roleAssignmentApprovals` returns "Resource
not found for the segment". On beta the same path returns a permissions error instead, naming
`PrivilegedAccess.ReadWrite.AzureAD`. The two errors are different in kind, and reading them as
the same error would have sent the work to the portal unnecessarily.
Evidence: `13-approval-chain.md`.

A deliberate over-limit activation request at PT4H, intended to capture the PT2H ceiling as a
refusal, has no captured response. Raymond believes he sent it. The request endpoint holds no
PT4H object, which does not settle the question, because Entra may reject an over-limit request
during validation before any object persists. It is being re-run from a clean state.

`roleDefinitions` rejects the `or` operator in `$filter` and accepts `and`. One query was lost to
that.

## What I'd do differently

Read the defaults before planning the change. Half this exercise's plan assumed PIM ships with
nothing configured. It ships with time-bounding, MFA, and justification already on. The exercise
worth running was not "turn on just-in-time access". It was "find what just-in-time access does
not include", and that only became visible after reading `10-activation-policy-defaults.md`.

Check who actually administers a tenant before designing a control for it. B4 was planned around
keeping break-glass separate from a working admin account. That separation did not exist. One
question, asked before step one, would have surfaced it.

Never abbreviate an identifier in an instruction that will be pasted verbatim.

## Open questions

- Does a PT4H activation request get refused? Unresolved. The ceiling currently rests on the
  policy read alone, which is a weaker claim than a captured refusal.
- Should `adm-jsmith` become the account used for routine tenant work, returning break-glass to a
  control that is never used? The exercise built the account. Adopting it is a change in habit,
  not configuration, and habit is where break-glass accounts fail.
- `sysadmin` is synced into Entra while holding on-premises `Domain Admins` with `adminCount` 1.
  Microsoft advises against syncing privileged on-premises accounts. That guidance is documented,
  not lab-captured, and the exposure is not this exercise's to close.
- Entitlement management and most access-review capability need Entra ID Governance, not P2.
  Documented, not lab-captured. B4 step 8 asked for that boundary to be named rather than
  assumed, and naming it from documentation is the most this licence allows.
- What replaces this control when the trial lapses on 2026-10-04? Eligible assignments are
  removed and PIM configuration is deleted. The on-premises standing grant this exercise contrasts
  against will still be there.

## The contrast this exercise exists to draw

`adm-jsmith` cannot use User Administrator without multi-factor authentication, a stated reason,
another party's approval, and a clock.

`sysadmin` holds `Domain Admins` on `district.local` permanently, with `adminCount` 1, and needs
none of those things. Nothing in the on-premises directory offers an equivalent control.

The cloud grant got governance. The identical pattern on-premises did not, and stays standing.
