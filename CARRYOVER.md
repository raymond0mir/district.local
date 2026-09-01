# Carryover — 2026-09-01 session

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
