# district.local — curriculum, rewritten against real lab state

**Rewritten:** 2026-09-02, against the repo at commit `5769aed`.
**Run order revised:** 2026-09-05. See *The sequence*. Exercise IDs are unchanged.
**Supersedes:** the "Four Exercises + SC-300 Study" section of the Skechers analysis doc dated 2026-09-01.

This rewrite changes the *ordering, sizing, and prerequisites* of the exercises. It does not
change the goal, the SC-300 target, or the permission-sprawl thesis — those were right.

Every constraint below is labeled **Captured** (a file in the repo backs it), **Recalled**
(believed, not captured — must be verified before it's relied on), or **Inherited** (came from an
earlier build or an outside document and was never re-verified). Same contract as the reports.

---

## Why the original plan doesn't survive contact

Four things, in order of how hard they bind.

**1. The lab was past its own stop threshold. RESOLVED 2026-09-02 by Exercise A1. (Captured)**
Thin pool `Data%` is now **70.86%**, under the skill's 85% gate with 21.95 GiB of margin, after
A1 destroyed VM 105 (`kali-red`) following a verified backup. See
`exercises/2026-09-02-thin-pool-headroom-reclaim/report.md`.

*Correction to this document's earlier figure:* it previously stated the pool reached "88.47%
after three rounds of pruning." That number was **Recalled, not Captured** — it appeared in no
evidence file and propagated here from a miscited `verified-claims.md` row, now retired. The last
genuinely captured pre-A1 readings were 92.01% and 88.99%.

What has **not** changed: the volume group still has **2.00 GiB `VFree`** on a single PV
(`/dev/nvme0n1p3`, 237.47 GiB), and A1 confirmed this figure does not move when pool space is
reclaimed — freed thin blocks return to the pool, not the VG. The Latitude 5420 has one M.2 slot,
so disk expansion means replacing the 256 GB NVMe. Using removable media as a live LVM PV remains
rejected (a thin pool's extents span PVs, so a device failing risks the whole pool).

*Consequence:* the blocker is lifted. Exercises that build a VM or install an OS can proceed.
A1 also established that VM 101 is `win11-client01` — a Windows 11 client already exists, so the
original plan's "Windows 11 client (VM or hardware)" line needs no new build at all.

**2. The tenant is Entra ID Free, and that ceiling is now measured, not assumed. (Captured)**
`GET /auditLogs/signIns` returns `Authentication_RequestFromNonPremiumTenantOrB2CTenant`. That
is a named licensing refusal, captured in the 09-02 exercise.

*Consequence:* Conditional Access, Identity Protection risk detections, Continuous Access
Evaluation, token protection, and PIM are all outside what this tenant can do today. The original
plan assigned all of them to a "Free Entra tenant." A P2 trial is 30 days — which means the
license-gated work has to run as **one contiguous block**, not spread across a six-week calendar
where the trial would expire before the PIM exercise ever started.

**3. Entra Connect is live now, not staging. (Captured)**
`Get-ADSyncScheduler` reports `StagingModeEnabled: False`; a real export ran; `jsmith` signed in
to Entra ID with an on-premises credential via Password Hash Sync.

*Consequence:* good news for the JML exercise, which now has a working sync underneath it. Also
raises the stakes — every future sync is a real export, so UPN, group-membership, and
connector-account changes are no longer rehearsals.

**4. `svc-entraconnect`'s password expires approximately 2026-10-13. (Captured)**
42-day default max age, `PasswordLastSet` 2026-09-01 07:54:57. If it lapses, sync fails as an
opaque import/export error rather than an obvious expiry message.

*Consequence:* this lands inside the original plan's Week 5–6. It is
not a footnote to schedule around — it is the natural centerpiece of the nonhuman-identity
exercise, which is where it now sits.

**One more, smaller but real. (Captured)**
`qm guest exec` has no attached TTY. A PowerShell command that expects interactive input hangs
until timeout and orphans a process on the guest. Anything requiring a human to type a secret has
to run on the VM's own Proxmox console. This directly shapes how the JML workflow sets initial
passwords.

---

## What the original plan got right, kept unchanged

- Permission-sprawl as the opening frame of the JML exercise.
- SC-300 over Security+, and the argument for why.
- One body of work serving lab, cert, and portfolio simultaneously rather than three parallel efforts.
- The honest list of what lab work cannot close (CIAM, enterprise IGA platforms, multi-cloud, architecture-board experience).

---

## Report mechanics — restored to the skill

The original plan's report templates dropped things that are not optional. Restoring them:

**Section list, per `.claude/skills/tech-compass/SKILL.md`:**

```
## What I set out to do          hypothesis, two or three sentences
## The setup                     the relevant slice of the lab, plus pre-flight readings
## What I did                    commands and changes in order, actual syntax
## Where Raymond was consulted   each judgment call: what was asked, what was decided, why
## What the box said             captured output with exit codes, quoted from evidence/
## What broke, and why           dead ends and misconfigurations
## What I'd do differently       judgment, stated plainly
## Open questions                mandatory, never empty by default
```

**Three rules the original plan violated and this one doesn't:**

1. **"Where Raymond was consulted" is not optional.** It was missing from all four original
   templates. In the existing reports it is the section that shows judgment being exercised
   rather than a procedure being followed — for anything above tier-1 hiring, it is arguably the
   highest-signal section in the document. The 09-02 report's consultation point 2 (prune vs.
   extend vs. removable media, with the recommendation *against* the option Raymond himself
   raised, and his actual decision recorded) is the model.

2. **"What broke" cannot be written in advance.** The original plan pre-filled it — "claims
   mismatch took 30 min to isolate," "Entra group didn't exist on first run," "gMSA worked
   transparently (no failures)." Those are predictions in the format of findings. Under the
   capture contract they are neither Captured, Recalled, nor Inherited; they are invented. The
   sections stay empty until the box prints something.

3. **"Open questions: None if execution is clean" is not available.** The section is mandatory
   and never empty by default. Every existing report has one, including the ones that went well.
   A clean run still leaves things unproven — name them.

**One exercise per report.** Separate hypotheses become separate reports. Several of the original
four were 3–5 reports wearing one title; the sizing below reflects that.

---

## The sequence

Eight exercises. Three cost nothing and need no new hardware. The trial is open, so the question
is no longer when to start it. The question is what actually needs it.

### Run order, revised 2026-09-05

Exercise IDs stay fixed. Reports, `EXPOSURES.md`, and the ledger cite them. The run order is
separate from the numbering. The run order governs.

| Order | Exercise | Placement reason |
|---|---|---|
| 0 | Capture the trial start date | **Complete 2026-09-06.** `GET /beta/directory/subscriptions`: `createdDateTime` 2026-09-04T00:00:00Z, `nextLifecycleDateTime` 2026-10-04T00:00:00Z. No longer Recalled |
| 1 | **B4 — PIM** | **Complete 2026-09-07.** Ran ahead of B1's fourth policy, because only B4's evidence is deleted at trial expiry |
| 2 | B1, fourth policy only | Closes B1. Needs no certificate authority and no AD CS. See B1 |
| 3 | B2 | Setup needs no licence, Captured in A3. A provisioning *run* is untested and may need P1 or P2, so run it while the trial covers it |
| 4 | B3, rotation half | Hard date about 2026-10-13. Not trial-gated |
| 5 | C2 — AD CS and CBA | On-prem. Survives expiry |
| 6 | C1 — joiner, then mover, then leaver | Graph and on-prem. Survives expiry |
| 7 | B3, gMSA and BloodHound half | Survives expiry |

**Why the order changed.** The original rule ran B1, B2 and B3 contiguous inside the trial. That
rule was written when the licence gates were unmeasured. They are now measured, and one item in
Phase B needs P2.

- PIM needs Entra ID P2 or Entra ID Governance. Source: Microsoft Learn, ID Governance licensing
  fundamentals. Not a lab capture.
- Entitlement management needs Entra ID Governance or Entra Suite. P2 alone does not reach it.
  Same source. This closes the licence question left open 2026-09-04.
- Most access-review capability needs Governance as well. Same source.
- SAML and SCIM *setup* need no paid licence, for gallery and non-gallery apps. Captured
  2026-09-02 in A3.

**Trial expiry is destructive, and that is why PIM moves first.** Microsoft Learn states that when
a P2 or Governance licence lapses, eligible role assignments are removed, active time-bound
assignments become permanent, and PIM configuration settings are deleted. PIM evidence cannot be
captured after expiry. Every other remaining exercise can.

### Phase A — unblock and bank cheap wins (no license, no new VM)

---

#### Exercise A1 — Reclaim thin-pool headroom without exposing the pool to removable media

**Hypothesis:** an external `vzdump` target on the USB stick lets a snapshot be pruned safely —
reclaiming real on-pool space — without ever making removable media part of the live LVM stack.

**Prerequisite for:** every other exercise here. Nothing that installs an OS or writes
significantly should start above the 85% gate.

**What you do:**
1. File the `vgs`/`pvs` readings properly. They are currently quoted in the 09-02 report from an
   interactive exchange, not captured as a `qm guest exec` JSON/text file — an open item in
   `CARRYOVER.md`. Fix that first; it's the number the whole exercise turns on.
2. Mount the USB stick as a `vzdump` target. Capture the mount, the filesystem, the free space.
3. Back up the largest reclaimable snapshot's VM. Verify the backup independently — a `vzdump`
   that exits 0 is not the same as a restorable archive, and the difference is the entire point.
4. Only after verification, prune the on-pool snapshot. Capture `Data%` before and after.
5. Re-derive the overcommit ratio. `EXPOSURES.md` notes the ~3.6x figure (864.93 GiB against
   237.47 GiB) is stale — the pool was extended and pruned since, and only `Data%` was rechecked.
   This closes that exposure properly.

**Consultation point to expect:** whether VM 101's `win11-ootb` snapshot comes into scope. It is
the pool's single largest real consumer (64 GB LV, 62% actual data) and VM 101's only rollback
point, and it was explicitly declined once already on 09-02. That decision is Raymond's, by name,
not inferred.

**Closes:** two `EXPOSURES.md` infrastructure items, one `CARRYOVER.md` evidence gap.
**SC-300 coverage:** none. This one is infrastructure, and the report should say so plainly
rather than reaching for a mapping that isn't there.

---

#### Exercise A2 — Read the unread policy surface, and de-fragilize the domain-root link

**Hypothesis:** `Secure Admin WS`'s domain-root link with a Deny-Apply exception for Domain
Controllers can be replaced by linking at the OUs it actually means to govern, removing the
lockout mechanism entirely rather than fencing it off.

**Why this is worth doing despite being AD hygiene, not Entra architecture:** the story is a
change-management story. A fix was applied under pressure that works *and* leaves a tripwire — a
future GPO edit dropping the exception, or a new DC added without checking for it, silently
reintroduces the exact lockout this project already hit. Recognizing that your own remediation is
load-bearing on a fragile condition, and then going back to fix it properly, is a more mature
signal than never having hit the lockout.

**What you do:**
1. Fully read `Default Domain Policy` and `District Lockdown` — two of the five GPOs in DC01's
   effective RSoP that have never been examined at the same depth as the other three. An unread
   policy surface on a domain controller is its own finding.
2. Establish, or explicitly fail to establish, the origin of the domain-root link — deliberate
   design or setup-time scope creep. Open in `CARRYOVER.md`. If it can't be determined, say so;
   that's a legitimate outcome.
3. Re-link at the workstation/member-server OUs, drop the Deny-Apply exception, verify effective
   scope on DC01 and on VM 102 before and after.
4. Check whether the tattooed `SeDenyInteractiveLogonRight` re-tattoos DC01 across a refresh
   cycle — observed only immediately after the original fix, never over time. This needs elapsed
   time, so start the observation early in the exercise and read it at the end.

**Snapshot before step 3.** This is the change class that already caused one lockout.

**Closes:** three `CARRYOVER.md` items, two `EXPOSURES.md` items.
**SC-300 coverage:** thin — hybrid identity prerequisites at most. Don't oversell it.

---

#### Exercise A3 — The Entra ID Free ceiling, measured

**Hypothesis:** the set of identity controls this tenant can actually enforce today is much
smaller than the set SC-300 examines, and the boundary can be mapped precisely with captured
refusals rather than read off a pricing page.

**Why this exercise exists at all — it was not in the original plan, and it should have been:**
knowing which control requires which license, and being able to say so from having hit the error
rather than from having read a comparison table, is an *architect* skill. It also decides which
later exercises need a paid license at all, so establishing it before opening a trial is simply
the right order. It needs no license of its own and produces a genuinely differentiated artifact.

**What you do:**
1. Capture, with error codes, what Free refuses. One is already in hand:
   `Authentication_RequestFromNonPremiumTenantOrB2CTenant` from `GET /auditLogs/signIns`.
   Attempt Conditional Access policy creation, PIM enablement, and an Identity Protection risk
   query, and capture each refusal verbatim.
2. Configure what Free *does* give you: Security Defaults. Capture what it enforces, on whom, and
   what it cannot express — the inability to scope, exclude, or stage is exactly why organizations
   move to Conditional Access, and being able to articulate that from the Free side is a better
   answer than reciting CA features.
3. **Resolve the SAML/SCIM licensing question before Phase B.** ~~My understanding — **Recalled,
   not verified** — is that SCIM automatic user provisioning requires P1, and that SAML SSO for
   non-gallery apps does too, while some gallery apps offer basic SSO on Free.~~ **Retracted
   2026-09-02, tested directly, not just superseded:** neither claim held. Federated SAML SSO
   configures and saves cleanly on Free for both a gallery app (Salesforce) and a fully custom
   non-gallery app, each confirmed live at the `servicePrincipal` object level with a real
   auto-generated signing certificate. SCIM provisioning setup likewise hits no license gate for
   either app type through the "Test connection" step — the only wall hit, both times, was this
   lab having no real third-party tenant to connect to, not a Microsoft licensing refusal. Whether
   an actual provisioning *run* past that point would hit a gate is still genuinely untested. Full
   account in `exercises/2026-09-02-a3-entra-free-ceiling/report.md`.
4. Write the licensing decision up as a recommendation: what a 100-user org actually needs to buy
   to enforce the controls the Skechers req names, and what it gets for free.

**SC-300 coverage:** substantial, and underrated — licensing and feature boundaries appear
throughout the exam and most candidates memorize rather than measure them.

---

### Phase B — the trial window

**The trial opened 2026-09-04 and runs 30 days.** The end date is derived from a Recalled start.
Treat about 2026-10-04 as provisional until run-order step 0 captures it.

~~Do not open the trial until A1–A3 are complete and A3's step 3 has answered the SAML/SCIM
licensing question.~~ **Superseded 2026-09-05.** A1 and A3 are done. The trial is open. A3
answered the SAML/SCIM question. The replacement rule: run the P2-gated work first. Only B4 is
P2-gated.

---

#### Exercise B1 — Conditional Access, report-only to enforced

**Hypothesis:** a CA baseline can be brought from report-only to enforced without locking anyone
out, and the report-only telemetry will show at least one policy scoping assumption to be wrong
before enforcement makes it expensive.

**Setup, corrected:** the original plan wanted a new Windows 11 client VM. **VM 101 appears to
already be one** — it holds a `win11-ootb` snapshot. But VM 101's purpose is currently a
**Recalled** claim (Raymond's description, never independently captured), and it sits outside this
project's tracked VM set. Characterize it first: what OS, what domain state, what's on it. If it
is a domain-joined Windows 11 box, the storage blocker for this exercise disappears entirely.
That single check is worth doing before A1 even, because it may change how much headroom A1 needs
to reclaim.

**Phishing-resistant auth — decided 2026-09-05. Use Windows Hello for Business.** The built-in
**Phishing-resistant MFA strength** accepts any one of three methods: Windows Hello for Business
or platform credential, a FIDO2 security key, or Entra certificate-based authentication. Source:
Microsoft Learn, Conditional Access authentication strengths. Not a lab capture.

`jsmith` holds a registered WHfB method on VM 101, Confirmed 2026-09-04. The fourth policy
therefore needs no hardware key, no certificate authority, and no console access to CA01.
**AD CS is not a B1 dependency.** It moves to C2 and runs on its own merit.

**Status, 2026-09-05.** Steps 1 to 3 are done. `365bdd23` and `75882b6a` enforce. `d9a6a116` is
held report-only by decision, because it would block VM 101. The fourth policy is the only step
left.

**What you do:**
1. Baseline: capture what Security Defaults was enforcing before CA replaces it. The two are
   mutually exclusive — turning CA on means turning Security Defaults off, and that transition is
   itself a finding worth capturing rather than clicking through.
2. Policies in report-only: require MFA for all cloud apps; block legacy auth; require compliant
   or hybrid-joined device; require phishing-resistant auth for a named sensitive app.
3. **Exclusions are the exercise.** A break-glass account must be excluded from every policy
   before any of them enforce. `breakglass@raytakosharkygmail.onmicrosoft.com` is **stale** —
   rotated out 2026-09-03, disabled, no longer Global Administrator (`verified-claims.md:106`,
   `:131`). Use the current break-glass account instead; Raymond supplies its object ID in
   session, since its UPN stays unpublished. Capture the exclusion, and capture the verification
   that it works, *before* enforcing anything. The
   sequencing lesson from `sysadmin` applies directly here: the failure mode is not the control,
   it is enforcing the control before the break-glass path is proven.
4. Let report-only run and gather real sign-ins. `jsmith` has a registered MFA method and a
   tested identity — the only account currently in that state. Whether the other eight restamped
   accounts get the same treatment is undecided per `CARRYOVER.md`, and report-only telemetry from
   one user is thin. Decide deliberately whether to onboard more.
5. Read the CA telemetry: which policies fired, which didn't, and why. Sign-in logs are available
   under P2 — this is one of the things the trial actually buys.
6. Enforce, one policy at a time, verifying break-glass access after each.

**Likely two reports, not one:** the report-only build and the enforcement transition have
different hypotheses. Split them if the telemetry phase produces anything substantial.

**SC-300 coverage:** Implement authentication; implement Conditional Access; Zero Trust.

---

#### Exercise B4 — PIM: convert a standing grant into a just-in-time one

**Numbered B4 because exercise IDs are fixed. Ran second.** Extracted from B3 step 6 on
2026-09-05.

**Status: complete, 2026-09-07.** Report:
`exercises/2026-09-06-b4-pim-eligible-role/report.md`. Everything below is corrected against what
the exercise captured. The original plan's framing was wrong in three places, and the corrections
are the exercise's value.

**Hypothesis as run:** a standing administrative grant can be converted to eligible-not-active
behind approval, the full request and approval trail can be captured, and the grant can be shown
to remove itself with no person in the record.

**Correction 1 — the exercise is not "turn on just-in-time access".** The original text assumed
PIM ships with nothing configured, and that the work was enabling it. It is not. An untouched
role management policy already requires multi-factor authentication, already requires a
justification, and already caps activation at PT8H. What it does not do is require approval:
`isApprovalRequired` false, `primaryApprovers` empty. The policy's `lastModifiedDateTime` was
null, so those are platform defaults.

The exercise worth running is **finding what just-in-time access does not include**. A tenant that
enables PIM and changes nothing gets an audit trail, not a control. It records who asked and why.
It does not record that anyone agreed.

**Correction 2 — step 3 does not exist.** The original text said "Enable PIM for Entra roles.
Capture what the tenant changes at enablement." Current tenants have no discrete consent action;
PIM is present once P2 is. There is nothing to capture at enablement. Read the role management
policy defaults instead. That read is where the finding is.

**Correction 3 — step 7 assumed a working administrator account that did not exist.** The
original text said to keep break-glass permanently active and outside PIM, which presumes a
separate account for routine work. This tenant had none. `roleAssignments` returned two rows:
Global Administrator on the break-glass account, and Directory Readers on a first-party service
principal. Every other administrative identity was disabled, including the tenant's original
Global Administrator. The account labelled break-glass was the account in daily use.

So the exercise created `adm-jsmith`, cloud-native and licensed, as the working administrator,
and made User Administrator eligible-not-active on it behind approval. Adopting that account for
routine work is a change in habit, not configuration. That decision was taken 2026-09-07.

**The group refusal is categorical, not a single refusal.** The original step 2 expected one
refusal on one synced group. All nine groups in the tenant are synced and all have
`isAssignableToRole` null, and the property cannot be set after a group exists. No existing group
in this tenant can ever come under PIM for Groups. Governing a group requires building a new
cloud-only role-assignable group, which is a different design rather than a repair.

**What the exercise proved.** The activation expired at its deadline. Core Directory unassigned
the role 0.9 seconds later with `initiatedBy.app.displayName` `MS-PIM`. PIM logged the reason six
seconds after that, actor "Azure AD PIM", null `userPrincipalName`, null `ipAddress`. Neither
audit entry names a human. The eligibility survived, so the control is repeatable.

**Closed 2026-09-09.** The PT4H over-limit request was re-run and captured. Entra refuses it
during validation with `RoleAssignmentRequestPolicyValidationFailed`, and the message names
`ExpirationRule`. The ceiling is enforced, not advisory, and it no longer rests on the policy read
alone. No request object is written, which explains the empty endpoint on 2026-09-06. Evidence:
`exercises/2026-09-06-b4-pim-eligible-role/evidence/16-over-limit-activation-refused-at-validation.md`.

**The on-prem contrast is the report's strongest section.** `adm-jsmith` cannot use User
Administrator without MFA, a stated reason, another party's approval, and a clock. `sysadmin`
holds `Domain Admins` on `district.local` permanently, with `adminCount` 1, and needs none of
those. The cloud grant got governance. The identical pattern on-premises did not.

**Licence ceiling, named rather than assumed.** Entitlement management and most access-review
capability need Entra ID Governance, not P2. Source: Microsoft Learn. Not a lab capture.

**SC-300 coverage:** Manage privileged identity (PIM); plan and implement identity governance.

---

#### Exercise B2 — SAML and SCIM against one application

**Hypothesis:** an end-to-end SSO and provisioning flow can be built and then deliberately broken
in ways that produce distinguishable, diagnosable failures.

**Placement, decided 2026-09-05. Run B2 inside the trial, after B4.** A3 captured that SAML SSO
and SCIM provisioning *setup* need no licence, for a gallery app and a non-gallery app, tested
both ways. A3 could not test whether an actual provisioning *run* — this exercise's real
deliverable — hits a gate that setup alone does not. That residual risk is the reason B2 stays
inside the window: if a run needs P1 or P2, the trial covers it, and after expiry the tenant
returns to Free. B4 still runs first, because B4's evidence is the evidence expiry destroys.

**What you do:** substantially as the original plan had it — the technical content there was
sound. Two changes:

- **Deliberate failure injection is the deliverable, not a garnish.** Wrong entity ID, unmapped
  NameID, wrong audience URI, a scoping filter that silently drops users. Capture each failure's
  actual error text and the diagnostic path that isolated it. This is the part that reads as
  Tier 2–3 work rather than a wizard walkthrough — and the original plan buried it at step 4 of 10.
- **Blur PII in captured assertions, keep the structure.** Correct in the original, worth
  repeating: the assertion structure is the evidence, the claim values are not.

**Do not pre-write what breaks.** The original plan asserted "claims mismatch took 30 min to
isolate" before running anything. Whatever actually happens is the finding.

**SC-300 coverage:** Implement access management for apps; manage enterprise applications;
federation.

---

#### Exercise B3 — Nonhuman identity, built around the service account you already have

**This is the largest single change from the original plan.** The original invented three
synthetic service accounts to demonstrate nonhuman identity security. The lab already contains a
better one.

`svc-entraconnect` is a real, live, production-shaped nonhuman identity with:

- **A real blast radius**, captured: `Replicating Directory Changes` + `Replicating Directory
  Changes All` at the domain root — DCSync-equivalent, full domain compromise if the credential
  leaks. Granted deliberately, by Microsoft's documented design, for Password Hash Sync.
- **Real mitigations already in place**, captured: no admin group membership, object hardened via
  `Set-ADSyncRestrictedPermissions`, password never disclosed to any channel.
- **A real deadline:** expiry ~2026-10-13, on a now-live sync where failure surfaces as an opaque
  import/export error.

A synthetic gMSA demo is a tutorial. Rotating the credential on a live DCSync-capable account
without breaking a running hybrid sync — and proving afterward that sync still works — is the
job. Do that.

**What you do:**
1. **Decide the rotation strategy first, and record why.** Rotate manually before expiry, or
   configure a fine-grained password policy exemption. `CARRYOVER.md` records this as explicitly
   undecided. The tradeoff — a recurring operational task versus a standing exemption from
   password policy on a DCSync-capable account — is exactly the kind of question an architecture
   role is asked, and there is a defensible answer either way as long as the reasoning is on the
   record. This is Raymond's call, not a default.
2. **Establish the rollback path before touching the credential.** Snapshot VM 102. Know what
   "sync is broken" will look like and how you'd revert, before you can break it.
3. Rotate. Handle the secret on the Proxmox console, not through `qm guest exec` — the no-TTY
   constraint means an interactive prompt will hang and orphan a process, which is now a captured
   behavior, not a theory.
4. **Prove sync still works afterward**, the same way the 09-02 exercise proved it in the first
   place: a real export and a real sign-in, not a green checkmark in a UI.
5. **Then** add a gMSA for comparison — one, not three. Something genuinely useful in the lab
   (a scheduled backup task is the natural candidate, and pairs with A1's `vzdump` work). The
   contrast that matters: automatic rotation with no operator involvement versus the manual
   sequence you just performed by hand on `svc-entraconnect`. Having done both, in that order, is
   what makes the comparison worth anything.
6. ~~**PIM, if the trial is still open.**~~ **Moved 2026-09-05 to Exercise B4**, and moved ahead
   of this exercise in the run order. Leaving the only P2-gated work at step 6 of the last Phase B
   exercise put it at maximum risk from the clock. The `sysadmin` candidate named here was also
   wrong; see B4.
7. **BloodHound: verify before relying on it.** The original plan states BloodHound CE is
   "already running." What the repo actually shows is an **Inherited** write-up
   (`~/Downloads/district-lab-bloodhound-writeup.md`, from a 2026-06-17 session) and a `bhound`
   AD account that was disabled 2026-09-01. VM 105 is Kali, but whether BloodHound CE is
   installed and running is uncaptured. Confirm or install it as step 1 of any use.
   **And reconcile the discrepancy while you're there:** the inherited write-up claims 59 groups;
   the captured `Get-ADGroup -Filter *` returned 55. That gap has been open since 08-31. Closing
   it — with a real answer for where four groups went — is a small, self-contained, genuinely
   good portfolio moment about not trusting your own prior documentation.

**Two reports minimum.** The rotation is one hypothesis; the gMSA/PIM/BloodHound work is another.

**SC-300 coverage:** Manage privileged identity (PIM); plan and implement identity governance;
security governance.

---

### Phase C — after the trial

---

#### Exercise C1 — Joiner-mover-leaver as code

**Placed last deliberately.** Most of it is Graph and on-prem AD, both of which survive the trial
expiring. Running it after B1–B3 also means the CA policies, the service-account model, and the
provisioning path it has to respect all already exist — so the workflow is written against a real
environment rather than a blank one.

**Hypothesis, and the thesis:** provisioning by role definition rather than by copying a named
user's access eliminates the accumulation pattern at its source. This is the permission-sprawl
thesis with code attached, and it opens the report — as the original plan correctly specified.

**What changes from the original plan:**

- **Scope it down to joiner first.** The original bundled joiner, mover, leaver, three mock
  cycles, failure injection, and audit capture into one exercise. Under the one-hypothesis rule
  that is three reports. Build joiner, write it up, then mover, then leaver. Leaver is the most
  interesting of the three and deserves its own — idempotency, token revocation, device wipe, and
  what to preserve for audit are four separate design decisions.
- **Initial password handling is a design decision forced by the lab. (Captured constraint)**
  `qm guest exec` has no TTY, so a workflow that prompts for a password hangs and orphans a
  process. The options — a generated secret written to a secure channel, a forced change at first
  logon, or a console-only step that breaks the automation — each have a real tradeoff. Pick one,
  and justify it. This is a better artifact than the automation itself.
- **App registration with client credentials is the actual Graph gap.** The original plan says
  "never had Graph API access." That's now stale: real delegated Graph work exists in this repo
  via Graph Explorer, using the break-glass account because the tenant's original Global Admin is
  a Microsoft Account that Graph directory endpoints reject. What's genuinely missing is an **app
  registration with client credentials and least-privilege application scopes** — non-interactive,
  unattended auth. Frame the gap that narrowly; it's more accurate and more credible.
- **Azure Automation and Logic Apps need an Azure subscription**, not just a tenant. Not free the
  way the tenant is. A scheduled task or a script run from VM 102 proves the same workflow logic
  without the billing relationship. Decide deliberately.
- **Entra Connect is live.** Every mock joiner this workflow creates is a real export to a real
  tenant. Plan the cleanup before creating anything, and account for the eight restamped accounts
  and `jsmith` already in the directory.

**SC-300 coverage:** Plan and implement identity governance; manage identity lifecycle;
implement access management.

---

#### Exercise C2 — AD CS issuing CA, and certificate-based authentication

**Added 2026-09-05.** This work was already started under
`exercises/2026-09-05-adcs-issuing-ca-build/`, ahead of the plan and inside the trial window. It
was started to unblock B1's fourth policy. That dependency does not exist. See B1.

**Placement.** After the trial. AD CS is on-prem and survives expiry. Whether tenant CBA is
P2-gated is **not captured**: A3 tested Conditional Access, PIM, Identity Protection, Security
Defaults and SAML/SCIM, not CBA. Capture that before assuming either way.

**State at pause, 2026-09-05.** The offline root CA exists on container 106 with correct
extensions. CA01 holds a valid certificate and cannot start. `certutil -installcert` blocks on a
denied Configuration-container write, because under `qm guest exec` it authenticates as `CA01$`.
Two blockers stack: no console logon to CA01 works, and no enabled account holds Enterprise
Admins. `DISTRICT\tmp-cainstall` holds local administrator on CA01 and is untested as a console
account. Try it first. Any Enterprise Admins re-grant runs as SYSTEM through `qm guest exec` on
DC01. Full state is in that exercise's `evidence-log.md`.

**Do not resume this before B4.** Two sessions have gone into it inside a window that only PIM
needs.

**SC-300 coverage:** Implement authentication; phishing-resistant methods.

---

#### Exercise C3 — Workload identity scope isolation: device code flow, audited at the token

**Added 2026-09-11.** Proposed by Raymond from an external PoC outline. Not yet run. No license
gate — needs no P2 and no on-prem step, so it does not have to wait for anything else in Phase C.

**Hypothesis:** an app registration restricted to one delegated scope produces an access token
that Microsoft Graph enforces regardless of the signed-in user's own administrative rights. The
token, not the human, is the boundary.

**Why this belongs in the curriculum, not just a demo:** every exercise so far governs a human or
a synced on-premises identity. This is the first exercise aimed at a non-human, non-interactive
client — the shape an AI agent or a CLI tool actually takes when it authenticates. The
permission-sprawl thesis has not been tested at this layer: an app registration's own API
permissions list, and what a device-code client can be scoped to hold.

**Consultation point to expect:** which tenant runs this. The district.local tenant already
carries live PIM, CA policies, and Entra Connect state; a new app registration there is a small,
easily-cleaned addition to a tenant already under governance. A separate throwaway tenant isolates
the PoC completely but adds setup cost and produces no contrast with the rest of the lab. Raymond's
call.

**What you do, corrected against a first draft that had three defects:**

1. Register `Lab-AI-Agent-CLI`. Single-tenant. No redirect URI. Enable "Allow public client
   flows."
2. Remove every API permission except `User.Read`. Confirm no admin-consent scope remains.
3. Check the tenant's user-consent policy before the first run. A tenant with user consent
   restricted refuses the flow at sign-in with `AADSTS65001`, independent of the app's own scope.
4. Request a device code. Poll the token endpoint on the returned `interval`, not once. A single
   immediate poll returns `authorization_pending`, not a token.
5. Decode the JWT. Replace `-` and `_` with `+` and `/` before base64 decoding — JWTs use
   base64url, and a raw `[Convert]::FromBase64String` throws on a payload holding either
   character.
6. Read `scp` and `appid`. Read `aud` knowing its form depends on the app manifest's
   `accessTokenAcceptedVersion` — a v1-formatted token carries Graph's GUID, not the URL, even
   when requested from the v2.0 endpoint.
7. Call `GET /v1.0/me` first, as a positive control. It must return 200 before the negative test
   means anything.
8. Call `GET /v1.0/directoryRoles`, or `GET /v1.0/users`, as the negative test. Expect 403,
   `Authorization_RequestDenied`. `/v1.0/users` draws the narrower line: it fails on
   `User.Read.All`, not an admin-role scope, closer to how an agent's own accumulated grants would
   actually be bounded.

**Closes:** nothing yet. New candidate.

**SC-300 coverage:** Implement access management for apps — delegated vs. application
permissions, admin and user consent, app registration scope restriction.

---

## Calendar

Deliberately not a week-by-week grid. The original's grid assumed each exercise takes its
estimate; the actual record is eight reports in three days, of which **two were unplanned
incidents that hijacked the session** — a DC crash and a GPO lockout. The realistic planning
assumption is that roughly one exercise in four turns into something else entirely, and that is
a feature of the work, not a scheduling failure.

What's fixed, and what floats:

| Fixed | Why |
|---|---|
| ~~A1 before anything that builds or installs~~ **DONE 2026-09-02** | Was 91.06% `Data%` vs an 85% gate; now 70.86%. `VFree` still 2.00 GiB and structurally unfixable without new hardware |
| ~~A3 step 3 before the trial opens~~ **PARTIALLY DONE 2026-09-02** | Gallery-app SAML and SCIM setup both hit no Free-tier gate — but the original claim was about *non-gallery* apps, untested. See `CARRYOVER.md` for the still-open decision on B2's placement |
| ~~B1 → B2 → B3 contiguous~~ **Superseded 2026-09-05** | Written when the licence gates were unmeasured. Only B4 needs P2 |
| B4 before the trial ends, about 2026-10-04 | Expiry deletes eligible assignments and PIM configuration. That evidence cannot be recaptured |
| B2 inside the trial, after B4 | Setup needs no licence (A3, Captured). A provisioning run is untested and may need P1 or P2 |
| `svc-entraconnect` rotated before ~2026-10-13 | Live sync; opaque failure mode |
| DC01 rearmed about every 10 days: ~09-12, ~09-22, ~10-02 | An expired grace period shuts DC01 down mid-session. It has already done so twice |
| DC01 relicensed or replaced before ~2026-11-01 | 5 rearms left, 10 days each. That date ends the lab, not the trial |
| C1 and C2 after the trial | Neither needs it |

Everything else floats. Sequence is load-bearing; dates are not.

**Why this order degrades gracefully:** A1–A3 need no paid license and close nine tracked open
items between them. If the trial never opens, Phase A alone is still a coherent, defensible body
of work. That was not true of the original ordering, where the first exercise required licensing
that hadn't been verified as necessary yet.

---

## SC-300 study, adjusted

The original study plan pairs each exam domain with a lab exercise. Keep that — it was the best
idea in the document. Two adjustments:

- **Identity governance and PIM content is now front-loaded into Phase B**, since the trial gates
  it. Study those domains alongside the trial rather than at the end.
- **The licensing and feature-boundary content from A3 is exam-relevant and needs no license**,
  so it can be studied first.

**On the exam registration:** the original doc described the same payment as both non-recurring
and as including a retake attempt. Those contradict each other. My recollection — **Recalled,
not verified** — is that a base voucher does *not* include a retake, and that Exam Replay is a
separate bundle. Confirm on the Microsoft certification page before relying on it. Flagging
rather than asserting, deliberately: this is the same rule the reports run under, and a plan is
not exempt from it.

---

## What this still does not close

Unchanged from the original doc, which was honest about it:

- **Customer identity (CIAM/CxM)** — no path in district.local; separate job family.
- **Enterprise IGA platforms** (SailPoint, Okta Identity Governance) — Entra ID Governance is a
  stand-in, not the product.
- **Multi-cloud identity at scale** — Entra/Azure only.
- **Architecture board experience** — comes from being hired.

One thing to add to that list, because the rewrite makes it visible:

- **Scale.** Every exercise here runs against a 13-user, 55-group domain on a laptop. The designs
  are real; the load is not. That's worth saying out loud in an interview before someone else
  says it — the honest framing is that the lab proves you can design and diagnose the mechanism,
  and your prior job proves you can operate at 500 users across six sites. Those are two different
  claims and you have evidence for both, separately.
