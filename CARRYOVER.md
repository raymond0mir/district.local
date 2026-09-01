# Carryover — 2026-09-01 session

## Next session: review follow-ups (written 2026-09-01, for whichever model picks this up)

Context you need and won't otherwise have: a review-only pass on 2026-09-01 audited the
`tech-compass` skill, `verified-claims.md`, this file, and the 09-01 exercise. The skill was
rewritten and committed (`f91ecce`); read `.claude/skills/tech-compass/SKILL.md` first and
follow it. Session rules: Claude has no live access to the lab. Every lab command is pasted to
Raymond, he runs it from the Proxmox host shell, and pastes the output back. Ask before anything
touching standing privilege, security posture, or deletion. Everything below is documentation
work except section A, which is captures Raymond runs.

### A. Captures to request from Raymond (one command each, file each under a new exercise or as an addendum)

1. ~~**`Administrator` state on DC01.**~~ **FULLY DONE, same day.** Found `Enabled: True`,
   contradicting the report's "disabled again at close" claim. Raymond chose to fix the
   underlying gap rather than just re-disable: `sysadmin` added to Domain Admins, login proven
   by an actual interactive console session (not inferred from group membership), then
   `Administrator` disabled again with a real second path in place. Also forced a correction to
   the `sysadmin`/`constrained-admin-path` reframing (see "Corrections this session forced on
   earlier work" below) — the original "load-bearing, not excess" framing was itself wrong.
   Evidence: `exercises/2026-09-01-entra-connect-connector-account/evidence/administrator-close-out-check.json`,
   `.../evidence/sysadmin-domain-admins-and-administrator-disabled.json`. **Also fully closed:**
   `Administrator`'s password (previously typed into Task Scheduler on VM 102) was rotated
   without ever disclosing the new value to any channel — `.../evidence/administrator-password-rotated-no-disclosure.json`.
   Nothing outstanding on this item.
2. ~~**`ConfirmImpact` on the AdSyncConfig cmdlets.**~~ **DONE.** Every function in the module,
   including all three called during delegation, declares `ConfirmImpact="high"`. The 09-01
   report's stall diagnosis was correct, not just plausible — no correction needed. Evidence:
   `exercises/2026-09-01-entra-connect-connector-account/evidence/adsyncconfig-confirmimpact-verified.json`.
3. ~~**Key Admins rights on the domain root.**~~ **FULLY DONE.** Key Admins holds domain-wide
   write rights over `msDS-KeyCredentialLink` (SPECIAL ACCESS, confirmed via `dsacls`) — a
   structural fact about this domain, still true. `bhound`, the only member, was a live
   shadow-credentials path; Raymond's decision was both remove from Key Admins and disable the
   account, done and verified same day (`MemberOf: {}`, `Enabled: False`). Evidence:
   `exercises/2026-09-01-entra-connect-connector-account/evidence/key-admins-domain-root-rights.json`,
   `.../evidence/bhound-remediated.json`. Also resolves the report's open question about
   `bhound`'s fate, and moots the "will its export fail" question since it won't sync as
   enabled. Also corrected a wrong ledger interpretation this uncovered: Key Admins **is**
   AdminSDHolder-protected per Microsoft Learn, so `bhound`'s `adminCount: 1` was never a
   mystery.
4. ~~**Domain max password age.**~~ **DONE.** 42 days. `svc-entraconnect`'s `PasswordLastSet`
   (9/1/2026 7:54:57 AM, already captured) puts its expiry at approximately **2026-10-13** —
   sync silently breaks around then unless rotated or exempted first. No action taken, just
   dated. Also caught and fixed a stale ledger clause while updating this: the delegation that
   later succeeded in this same exercise (`delegation-complete.json`) had never been added to
   `verified-claims.md` — it is now. Evidence:
   `exercises/2026-09-01-entra-connect-connector-account/evidence/svc-entraconnect-password-expiry.json`.
5. ~~**`OneShotDelegation` is gone.**~~ **It was NOT — good catch by checking rather than
   trusting this file.** A second instance existed, re-registered to retry delegation after the
   `-Confirm:$false` fix, holding a live `DISTRICT\Administrator` credential
   (`LogonType: Password`, `RunLevel: Highest`). The "Immediate, before anything else" item 1
   below only covered the first, stalled instance. Found and removed same day, confirmed via a
   genuine "not found" error. Evidence:
   `exercises/2026-09-01-entra-connect-connector-account/evidence/oneshotdelegation-second-instance-removed.json`.
6. ~~**VM 101's identity.**~~ **DONE.** Raymond's test admin station — his description, not a
   `qm guest exec` capture (informational, not filed as evidence). `qm config 101` confirms it
   exists with a guest agent, OVMF/UEFI, 2 cores, 4096 MiB RAM, created 2025-09-30.
7. **Account Operators absence.** DC01's captured `SeInteractiveLogonRight` is 544/549/550/551
   and S-1-5-9. Microsoft's Default Domain Controllers Policy default also includes Account
   Operators (548). Something removed it and nobody has explained it; it is an inherited state.
   `gpresult /h C:\Windows\Temp\rsop.html` on DC01, then grep `SeInteractiveLogonRight` across
   the five applied GPOs' `GptTmpl.inf` in SYSVOL.

### B. Fix the 09-01 report (`exercises/2026-09-01-entra-connect-connector-account/report.md`, committed as of `978ea2e`)

1. ~~**Reframe the `sysadmin` finding.**~~ **DONE.**
2. ~~**Own the tiering mistake**~~, including correcting consultation point 5 and dissolving the
   proposed Secure Admin WS memo. **DONE.**
3. ~~**Add to "What I'd do differently"**: `-NonInteractive`, relink `Secure Admin WS`.~~ **DONE.**
4. ~~**Move the uncaptured claim to Open questions**~~ — moot, A1 landed and the report was
   corrected to state what actually happened instead. **DONE.**
5. **Split the report in two: the GPO lockout/tattoo half, and the connector account/wizard
   half.** Explicitly held, Raymond's call 2026-09-02 (or later same session) — needs real
   narrative rework (separate "What I set out to do" framing, deciding how today's addendum
   content divides between the two threads), not mechanical cut-and-paste. Still open, do this
   as its own focused pass. Drop step 14 and consultation point 10 (GitHub setup) into the
   README (D) when this happens.
6. ~~**Note the UPN "Not Added" question is probably cosmetic for this tenant.**~~ **DONE.**

### C. Ledger corrections (`verified-claims.md`) — ALL DONE, 2026-09-01/02

1. ~~**`bhound` adminCount row.**~~ **DONE.** Corrected on the record; Key Admins is protected.
2. ~~**SDProp/adminCount rows.**~~ **DONE**, with a real citation (Microsoft's AskDS blog, "Five
   common questions about AdminSdHolder and SDProp") confirming `adminCount` never self-clears —
   by design, not just undocumented behavior nobody had verified.
3. ~~**`sysadmin` row's bolded clause.**~~ **DONE**, split fact from interpretation.
4. ~~**Full pass on every row.**~~ **DONE.** Read all 58 Confirmed and 13 Retired rows. Beyond
   the three above, nothing else carries an unlabeled normative judgment riding inside a factual
   claim. Two rows (Domain Admins tier0/`sysadmin` at line ~28, `Secure Admin WS` consequence at
   line ~53) synthesize already-confirmed facts into a conclusion, but descriptively, not as
   judgment calls dressed as findings — left as-is.

### D. README at repo root — DONE, 2026-09-02

Written: what district.local is, who it's for, the capture contract, how to read an exercise,
where the ledger and CARRYOVER live, the permission-sprawl through-line, and a short note on the
lab and how the repo is set up (folding in what would have been the GitHub-setup content from
B5's dropped step 14 / consultation point 10). Also untracked the three committed `.obsidian/*.json`
config files (empty/generic, no secrets, just clutter) and changed `.gitignore` from ignoring
only `workspace.json` to the whole `.obsidian/` directory.

### E. Rewrite this file per the new skill

The skill now says CARRYOVER holds only what is still open and is overwritten at each close.
Everything below this section is the 09-01 handoff with DONE items struck through and a header
that says the report isn't written. After B is done, collapse it to open items only.

### F. Prose pass on the six committed reports

Structure and evidence citations were checked; prose was not. The constrained-admin-path report
is 309 lines and needs an addendum after B1 ("the removal was right, the ordering was wrong").
For each report: does it lead with the finding, is it under roughly 150 lines, does "What the
box said" quote rather than summarize.

### G. Reconcile the plugin copy of the skill

The app's plugin copy (under `~/Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin/.../skills/tech-compass/SKILL.md`)
is the pre-review version. Invoking `/tech-compass` outside the repo loads it. Either re-import
from the repo or remove it; the repo copy is canonical per its header.

### H. Known-exposures page, from captured facts only

One page listing what the evidence already shows: `bhound` enabled in Key Admins, `Administrator`
rotation owed, AD Recycle Bin off, `svc-entraconnect` expiry (A4), the five applied GPOs on DC01
nobody has fully read, `districtsafetyphoto.com` verification window nearly elapsed. Doubles as
the next exercise queue.

---

Session paused mid-delegation. This file is the state handoff; `report.md` is not yet written.

## Immediate, before anything else

1. ~~Unregister `OneShotDelegation`~~ — **DONE at the time**, for the first, stalled instance
   only. **This claim was wrong as a statement about the task overall**: a second instance was
   re-registered later the same exercise to retry delegation after the ShouldProcess fix, and
   was never cleaned up after it succeeded — found and removed 2026-09-01, see section A item 5
   above. Left here uncorrected as the historical record of what was believed at the time; the
   current state is in section A.
2. ~~Determine what the stalled task wrote~~ — **DONE, confirmed zero.** `dsacls` against the
   domain root returned no matches for `svc-entraconnect`. The stall happened before any ACE was
   written — delegation has not been done at all yet, from scratch.
3. **Rotate `DISTRICT\Administrator` again at the end of the whole thread.** Its password was
   typed into a Task Scheduler credential store during this session. Not urgent while the task
   is gone, but it should not be the long-term value.
4. **Diagnose the forest-enumeration stall before re-attempting the same way.** See "Why the task
   may have stalled" below — re-running blind risks the same hang.

## Where the Entra Connect thread actually stands

- `svc-entraconnect` exists, enabled, `MemberOf` empty, in `OU=Service Accounts`,
  SID `...-1128`. No delegated permissions confirmed applied yet.
- Deliberate deviations Raymond made from the creation command as given, both his call:
  `PasswordNeverExpires: False` (defensible — Microsoft recommends `True` for sync accounts, but
  a never-expiring standing service credential is exactly the sprawl pattern) and
  `UserPrincipalName` empty (probably harmless — connector binds by sAMAccountName/DN, untested).
- Decision on record: **basic read + ms-DS-ConsistencyGuid + Password Hash Sync + restricted
  permissions**. PHS grants `Replicating Directory Changes` + `Replicating Directory Changes All`
  on the domain root — DCSync-equivalent, by Microsoft's design, not by misconfiguration.
- Still to run once the stall is resolved: all three permission cmdlets (none confirmed complete),
  then `Set-ADSyncRestrictedPermissions -ADConnectorAccountDN <dn> -Credential $cred` at the
  console (it takes a credential directly, so it needs no scheduled task).
- Then: fully exit and relaunch the Entra Connect wizard — still the untested "stale wizard state"
  hypothesis from the 2026-08-31 exercise, now on a machine that is actually domain-joined.

## Why the task stalled — DIAGNOSED

Confirmed root cause, next session. Isolated `Get-ADForest` + domain enumeration alone: 0.13s,
not the bottleneck (ruled out DNS/GC lookup and the RAM-pressure hypotheses as causes of THIS
stall specifically). Read `AdSyncConfig.psm1` directly (`GrantADPermissionsOnAllDomains`,
~line 1863): the per-domain loop is gated by `If ($PSCmdlet.ShouldProcess($domain, $Message))`.
These cmdlets support `-Confirm`, and PowerShell's default `$ConfirmPreference` (`High`) means a
domain-root permission grant triggers an interactive Y/N confirmation prompt. Under a scheduled
task with no attached console, the prompt has nothing to read from and blocks indefinitely rather
than erroring — matches the observed symptom exactly (stopped right after the per-domain log line,
before `GrantAcls` ran, no error, no progress across repeated queries).

FIX APPLIED AND VERIFIED WORKING: `-Confirm:$false` added to all three calls. Re-ran via the
same scheduled-task mechanism — `LastTaskResult: 0`, transcript completed to `=== DONE ===`.
Delegation is DONE — BasicRead + MsDsConsistencyGuid + PasswordHashSync all confirmed applied
by direct before/after ACL comparison in the transcript (svc-entraconnect gained
`Replicating Directory Changes` + `Replicating Directory Changes All` at the domain root after
PasswordHashSync specifically — see `exercises/2026-09-01-entra-connect-connector-account/evidence/delegation-complete.json`).

`Set-ADSyncRestrictedPermissions` — DONE, verified against the live object (`AreAccessRulesProtected: True`,
tight explicit ACL), not just the console line (which was ambiguous on its own — a single status
line, no completion message, unlike the other three cmdlets). See `exercises/2026-09-01-entra-connect-connector-account/evidence/delegation-complete.json`.

**Wizard relaunch — DONE, cleared the exact step that blocked entra-connect-install.** Signed in
with breakglass@raytakosharkygmail.onmicrosoft.com, added district.local via svc-entraconnect
(password had to be reset — Raymond forgot it; see `exercises/2026-09-01-entra-connect-connector-account/evidence/wizard-cleared-connect-directories.txt`
for the disclosure-pattern note on that one). See `exercises/2026-09-01-entra-connect-connector-account/evidence/vm102-not-domain-joined.json` and
`wizard-cleared-connect-directories.txt` for the full chain.

**Open, unresolved: `raytakosharkygmail.onmicrosoft.com` UPN suffix shows "Not Added"** in the
wizard despite being confirmed `Available`/verified in the actual tenant portal. Ruled out: stale
wizard cache (full relaunch, same result), missing Graph/login connectivity (all reachable). One
hypothesis (a specific missing endpoint) was proposed by Claude and DISPROVEN — retracted on the
record in `exercises/2026-09-01-entra-connect-connector-account/evidence/upn-suffix-not-added-unexplained.json`. Root cause still unknown. Raymond
proceeded via the wizard's own override checkbox, accepting the risk knowingly. **The real test
is a live sign-in with a synced user's on-prem credential — do this once sync is out of staging.**

**Wizard reached "Ready to configure" and was installed WITH STAGING MODE ENABLED**, per Raymond's
decision — first-ever sync from this DC, deliberately previewed before exporting anything live.
Confirmed the wizard is genuinely using svc-entraconnect (both `raytakosharkygmail.onmicrosoft.com
- AAD Connector` and `district.local Connector` named explicitly on the Ready-to-configure summary).

## Next session, in order

Staging preview checked — see `exercises/2026-09-01-entra-connect-connector-account/evidence/staging-preview-findings.txt` for full detail. Summary:
- **"System Admin" mystery from the session's opening minutes is closed**: it's sysadmin's
  AD display name, confirmed by opening its staged object properties. Not a separate account.
- **sysadmin's computed UPN looks correct**: `sysadmin@raytakosharkygmail.onmicrosoft.com`,
  positive (not conclusive) signal that the "Not Added" wizard warning is a false negative.
- **`bhound` will very likely fail real export**: its computed UPN is `bhound@district.local` —
  Entra Connect's fallback for a missing UPN is `sAMAccountName@<on-prem domain>`, not blank, and
  `district.local` is non-routable / never verifiable in the tenant. Mechanism now understood
  precisely, not just predicted.

1. Promote out of staging mode (Synchronization Service Manager or rerun the wizard), watch what
   actually happens to `bhound` specifically — expect a clean failure with a capturable error, or
   an unexpected success worth understanding either way.
2. Decide `bhound`'s fate: give it a real UPN, exclude from sync scope, or finally delete it
   (aging BloodHound-capstone throwaway, still `Enabled: true`, logged on as recently as
   2026-08-27 per `verified-claims.md`).
3. **The authoritative test for the whole "Not Added" question**: a real synced account
   (`sysadmin` or another restamped user) attempting an actual Entra ID sign-in with their
   on-premises credential.
4. Write `report.md` for this exercise — there is a LOT of material: the Secure Admin WS scope
   bug + tattoo, the sysadmin reframing, the VM102 domain-join correction, the ShouldProcess
   scheduled-task stall and its diagnosis, the wizard success, the UPN suffix mystery (Claude's
   own retracted hypothesis included), and the staging-preview findings above. This is easily the
   densest exercise in the project so far and should probably be split into two reports if it
   keeps growing (infrastructure/GPO half vs. Entra Connect delegation half) — worth deciding
   that explicitly rather than defaulting to one giant file.

## Corrections this session forced on earlier work

- `verified-claims.md` row asserting VM102 was **domain-joined** was **false** — retired.
  It rested on a screenshot of Server Manager reading `Workgroup: DISTRICT.LOCAL`, which is
  Server Manager reporting the machine is *not* joined. Never captured via `qm guest exec`.
- **Corrected same day, 2026-09-01, after the review flagged it**: the note above originally
  read `constrained-admin-path`'s removal of `sysadmin`'s direct `BUILTIN\Administrators` grant
  as a mistake, because removing it left `sysadmin` with no console path. That conflated "was in
  use" with "was appropriate" — the removal targeted real sprawl and was correct. The actual
  defect was sequencing: by this exercise, `Administrator` was disabled, `Secure Admin WS` denied
  Domain Admins everywhere including DC01, and `sysadmin`'s path had been removed with no
  verified replacement — three closures stacking into a full lockout. Fixed same day: `sysadmin`
  added to Domain Admins, login proven interactively, then `Administrator` disabled again with a
  real second path in place (`exercises/2026-09-01-entra-connect-connector-account/evidence/sysadmin-domain-admins-and-administrator-disabled.json`).
  See the corrected "What broke" entry and addendum in that exercise's `report.md`.
- The `entra-connect-install` exercise's unexplained wizard error ("domain cannot be contacted",
  five hypotheses, none conclusive) now has a strong candidate cause: the machine was never in
  the domain. Strong candidate, **not proven** — the wizard has not been re-run.
- Claude asserted mid-session that Secure Admin WS was legitimately blocking Domain Admins on
  VM102 "as designed." That was wrong at the time (VM102 processed no domain GPO — it was not
  joined) and became true only after the join. Both halves belong in the write-up.

## Open questions to carry into the report

- Did the stalled task write any ACEs? (see step 2 above)
- Why did `Secure Admin WS` exist linked at the domain root with no Tier 0 exclusion — deliberate
  or setup scope creep? Origin never established; only its current scope was captured.
- Does the tattooed `SeDenyInteractiveLogonRight` re-apply to DC01 on the next GPO refresh cycle
  now that the GPO is security-filtered out? Filtering should prevent it, but this was not
  observed over time — only immediately after `gpupdate`.
- Is `Secure Admin WS` vs. Microsoft's documented Entra Connect deployment procedure a genuine
  conflict worth formally proposing a Tier 0 exclusion for? (Raymond's stakeholder framing:
  deliver the working system *and* the memo, decision owner above him.)
- `bhound` still has no UPN and would fail sync. Unresolved since the hybrid-identity exercise.
- `districtsafetyphoto.com` verification never happened; registration window roughly a month
  from 2026-08-31.
