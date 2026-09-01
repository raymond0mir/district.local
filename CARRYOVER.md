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

1. **`Administrator` state on DC01.** The 09-01 report says it was "disabled again at close"
   with no evidence file behind it. `qm guest exec 100 -- powershell.exe -Command "Get-ADUser
   Administrator -Properties Enabled,PasswordLastSet | Select Enabled,PasswordLastSet"`. Also
   settles whether the owed password rotation happened (its value was typed into Task
   Scheduler on VM 102 on 09-01).
2. **`ConfirmImpact` on the AdSyncConfig cmdlets**, on VM 102: `Select-String -Path 'C:\Program
   Files\Microsoft Azure Active Directory Connect\AdSyncConfig\AdSyncConfig.psm1' -Pattern
   'ConfirmImpact'`. The 09-01 stall diagnosis ("default `$ConfirmPreference` High triggers a
   prompt") is only correct if these declare `ConfirmImpact='High'`; per Microsoft Learn, High
   preference prompts only for High-impact commands. If it's Medium, the diagnosis is wrong and
   the report's Phase 3 paragraph needs a retraction.
3. **Key Admins rights on the domain root**, on DC01: `dsacls "DC=district,DC=local" | findstr /i
   "Key Admins"`. `bhound` (throwaway BloodHound account, still enabled) sits in Key Admins.
   This turns "possible shadow-credentials path" into a captured finding either way.
4. **Domain max password age**, on DC01: `Get-ADDefaultDomainPasswordPolicy | Select
   MaxPasswordAge`. `svc-entraconnect` was created with `PasswordNeverExpires: False`; this is
   the date sync silently breaks unless a rotation runbook exists.
5. **`OneShotDelegation` is gone**, on VM 102: `Get-ScheduledTask -TaskName OneShotDelegation`
   should error. This file says it was unregistered; a fresh negative read belongs in the ledger.
6. **VM 101's identity**, on the host: `qm config 101 | head`. It exists, had snapshots pruned,
   and nothing records what it is.
7. **Account Operators absence.** DC01's captured `SeInteractiveLogonRight` is 544/549/550/551
   and S-1-5-9. Microsoft's Default Domain Controllers Policy default also includes Account
   Operators (548). Something removed it and nobody has explained it; it is an inherited state.
   `gpresult /h C:\Windows\Temp\rsop.html` on DC01, then grep `SeInteractiveLogonRight` across
   the five applied GPOs' `GptTmpl.inf` in SYSVOL.

### B. Fix the 09-01 report before it is committed (`exercises/2026-09-01-entra-connect-connector-account/report.md`, still untracked)

1. **Reframe the `sysadmin` finding.** The report, this file, and a ledger row call the removal
   of `sysadmin`'s direct `BUILTIN\Administrators` grant "the wrong read" because the grant was
   "load-bearing." A grant being in use does not make it appropriate; that account holding a
   direct DC Administrators grant is the sprawl pattern the series argues against. The real
   lesson is sequencing: the lab reached zero working Tier 0 admin paths because `Administrator`
   was disabled, a root-linked GPO denied Domain Admins everywhere, and the last path was
   removed without a verified replacement. Rewrite the "What broke" paragraph and consultation
   point 1 accordingly. Keep every captured fact verbatim.
2. **Own the tiering mistake.** Phase 3 stored a Domain Admin password in Task Scheduler on
   VM 102, a Tier 1 host. Microsoft's enterprise access model says Tier 0 credentials never
   land there. The better option existed: run the delegation from DC01's console (copy
   `AdSyncConfig.psm1`, or use `dsacls`). That recommendation came from Claude at consultation
   point 5 and was the weaker option; say so. This also dissolves the proposed "Secure Admin WS
   vs. vendor procedure" memo: the GPO denying Domain Admins on member servers is correct
   tiering, and only the missing DC exclusion was a defect.
3. **Add to "What I'd do differently":** relink `Secure Admin WS` at the workstation and
   member-server OUs and remove the Deny-Apply ACE, which is a workaround; and run
   scheduled-task PowerShell with `-NonInteractive` so a prompt fails loudly instead of hanging.
4. **Move the uncaptured claim** ("disabled again at close") to Open questions unless A1 lands.
5. **Split the report in two**: the GPO lockout and tattoo half, and the connector account and
   wizard half. Its own last open question says so. Drop step 14 and consultation point 10
   (GitHub setup); that goes in the README (D).
6. **Note the UPN "Not Added" question is probably cosmetic for this tenant.** Per Microsoft
   Learn's UserPrincipalName population page, an unverified suffix makes Entra compute
   `<MailNickName>@<initial domain>`, and MailNickName falls back to the on-prem UPN prefix
   when mailNickName, proxyAddresses, and mail are absent. For `sysadmin@raytakosharkygmail.onmicrosoft.com`
   both branches produce the same value, so the staging preview cannot distinguish them. The
   live sign-in test is still the only real check, and the question only matters once a custom
   verified domain is involved.

### C. Ledger corrections (`verified-claims.md`), on the record, not quiet edits

1. **`bhound` adminCount row.** It says Key Admins is "not on the classic AdminSDHolder-protected
   list" and the value is "not explained." Microsoft Learn (Appendix C, Protected Accounts and
   Groups) lists Key Admins and Enterprise Key Admins as protected. Keep the captured facts, fix
   the interpretation, add a Retired row explaining the correction.
2. **SDProp/adminCount rows.** "Does adminCount self-clear" has a documented answer: SDProp sets
   it and never clears it. Replace the "textbook, not independently observed" hedge with a doc
   citation.
3. **`sysadmin` row's bolded clause** ("removed as sprawl ... was the only thing granting it
   console logon") is a captured fact wearing an interpretation. Split them per B1.
4. **Full pass on every row**: separate what the box printed from what was concluded, in each
   row. Only interpretations were spot-checked on 2026-09-01.

### D. README at repo root (does not exist)

A public portfolio repo currently shows `.claude`, `.obsidian`, `exercises`, and a ledger, with
no explanation. Write a short README: what district.local is, who it's for, the capture contract
in three sentences, how to read an exercise, where the ledger and CARRYOVER live, and the
permission-sprawl through-line. Consider removing the committed `.obsidian/*.json` files
(only `workspace.json` is ignored). Include the GitHub setup note removed in B5.

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

1. ~~Unregister `OneShotDelegation`~~ — **DONE**, next session. `Stop-ScheduledTask` and
   `Unregister-ScheduledTask` both confirmed exitcode 0. The stored Domain Admin credential is gone.
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
- The `constrained-admin-path` exercise framed `sysadmin`'s direct `BUILTIN\Administrators`
  membership as removable sprawl. `SeInteractiveLogonRight` on DC01 lists only 544/549/550/551
  and S-1-5-9 — that grant was the *only* thing giving `sysadmin` console logon. It was
  load-bearing, not excess. This is the strongest single finding of the session and should
  anchor the report.
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
