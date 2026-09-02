# district.local — curriculum, rewritten against real lab state

**Rewritten:** 2026-09-02, against the repo at commit `5769aed`.
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

Six exercises. Three cost nothing and need no new hardware. Three sit inside a single P2 trial
window that should not be opened until the first three are done.

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
3. **Resolve the SAML/SCIM licensing question before Phase B.** My understanding — **Recalled,
   not verified** — is that SCIM automatic user provisioning requires P1, and that SAML SSO for
   non-gallery apps does too, while some gallery apps offer basic SSO on Free. Do not plan
   around my recollection. Attempt one gallery-app SAML config and one SCIM provisioning setup on
   Free and capture what happens. The answer determines whether Exercise B2 has to live inside the
   trial window or can run outside it — which is worth a real capture, not a guess.
4. Write the licensing decision up as a recommendation: what a 100-user org actually needs to buy
   to enforce the controls the Skechers req names, and what it gets for free.

**SC-300 coverage:** substantial, and underrated — licensing and feature boundaries appear
throughout the exam and most candidates memorize rather than measure them.

---

### Phase B — inside one 30-day P2 trial

**Do not open the trial until A1–A3 are complete and A3's step 3 has answered the SAML/SCIM
licensing question.** The clock is the scarcest resource in this plan. Order below is by "hardest
to redo if the trial lapses" — the JML work is deliberately last because most of it is
Graph and on-prem, which survive the trial expiring.

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

**Phishing-resistant auth is a decision point, not an assumption.** FIDO2 needs a hardware key;
Windows Hello for Business needs a working device and enrollment path. Whether to buy a key is
Raymond's call. Certificate-based authentication is the no-hardware fallback, and it is more work. Decide before starting, and record the decision and its reasoning in the report.

**What you do:**
1. Baseline: capture what Security Defaults was enforcing before CA replaces it. The two are
   mutually exclusive — turning CA on means turning Security Defaults off, and that transition is
   itself a finding worth capturing rather than clicking through.
2. Policies in report-only: require MFA for all cloud apps; block legacy auth; require compliant
   or hybrid-joined device; require phishing-resistant auth for a named sensitive app.
3. **Exclusions are the exercise.** A break-glass account must be excluded from every policy
   before any of them enforce. `breakglass@raytakosharkygmail.onmicrosoft.com` already exists and
   is already the account Graph directory endpoints accept — it is the natural exclusion. Capture
   the exclusion, and capture the verification that it works, *before* enforcing anything. The
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

#### Exercise B2 — SAML and SCIM against one application

**Hypothesis:** an end-to-end SSO and provisioning flow can be built and then deliberately broken
in ways that produce distinguishable, diagnosable failures.

**Placement depends on A3 step 3.** If SCIM turns out to need P1, this runs inside the trial and
should come before B3. If Free covers it, pull it out of the window entirely and run it in Phase A.

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
6. **PIM, if the trial is still open.** Put an eligible-not-active role behind approval and
   capture the request/approval audit trail. `sysadmin` is the obvious candidate — it currently
   holds standing Domain Admins membership added 2026-09-01, and its `adminCount` is stuck at 1
   and will not self-clear. Converting a standing grant into a just-in-time one is the
   permission-sprawl thesis with a control attached.
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
| B1 → B2 → B3 contiguous | One 30-day trial, no second chance |
| `svc-entraconnect` rotated before ~2026-10-13 | Live sync; opaque failure mode |
| C1 after the trial | Doesn't need it |

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
