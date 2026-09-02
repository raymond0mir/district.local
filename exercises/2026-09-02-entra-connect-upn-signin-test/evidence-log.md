# Evidence log — 2026-09-02-entra-connect-upn-signin-test

Exercise question: does a real synced account actually sign in to Entra ID with its
on-premises credential, resolving the "Not Added" UPN status ambiguity left open in
`2026-09-01-entra-connect-connector-account`? Per Microsoft Learn's UPN-population rules,
the staging preview's positive signal for `sysadmin` couldn't distinguish a verified suffix
from an unverified one computing the same value by coincidence — only a real sign-in could.
**Answer: yes** — see `report.md` and `jsmith-authenticated-session-confirmed.json`.

Test account: `jsmith` (non-privileged, deliberately not `sysadmin` — Raymond's call,
2026-09-02, to keep the Domain Admins credential out of a browser-based cloud auth test
when a non-privileged restamped account proves the same mechanism).

## What was captured

1. `preflight-thin-pool-and-memory-20260902.txt` — pre-flight readings before any state
   change: Data% 92.01%, RAM 169Mi available.
2. `postprune-thin-pool-and-memory-20260902.txt` — Data% after two prune rounds: 88.99%,
   then 88.47%; RAM recovered to 1.7Gi available.
3. `staging-mode-toggle-not-in-powershell.json` — two negative PowerShell checks (no
   `*Staging*` cmdlet, no `StagingModeEnabled` param on `Set-ADSyncScheduler`) plus the
   pre-toggle `Get-ADSyncScheduler` state (`True`).
4. `staging-mode-disabled.json` — `Get-ADSyncScheduler` before/after the wizard's GUI
   toggle: `True` -> `False`.
5. `initial-sync-cycle-success.json` — `Start-ADSyncSyncCycle -PolicyType Initial` ->
   `Result: Success`.
6. `jsmith-exported-to-entra-id.json` — Graph confirms `jsmith` landed with
   `onPremisesSyncEnabled: true` and the correct UPN.
7. `jsmith-password-reset-confirmed.json` — `PasswordLastSet` before (10/3/2025, the
   untouched October baseline) and after (9/1/2026) a console-driven reset.
8. `signin-logs-blocked-by-license.json` — `Authentication_RequestFromNonPremiumTenantOrB2CTenant`,
   a real license limit, not a permissions gap.
9. `jsmith-authenticated-session-confirmed.json` — the authoritative result: `GET /me` as
   `jsmith`, clean `200`, real GUID `id` matching the export-check object, synced display
   name populated.

## What was not captured, and why

- **The `vgs pve -o+vg_free` / `pvs` readings that closed off the "extend the pool" option**
  were a single interactive exchange in this conversation, not run through `qm guest exec`
  with a filed JSON/text capture. The numbers (237.47 GiB PV, 2.00 GiB `VFree`) are quoted
  in `report.md` and `verified-claims.md` but there's no standalone evidence file for them —
  worth a fresh, properly-captured re-run if this figure needs to be cited precisely again.
- **The wizard's "Configuration complete... Staging mode has been successfully disabled"
  screen** is a screenshot — Recalled, not filed as evidence. `staging-mode-disabled.json`'s
  `Get-ADSyncScheduler` result is the real proof it cites instead.
- **Whether `qm guest exec`'s hung process (pid 4624) on DC01 was ever terminated** is
  unconfirmed — asked, not answered. Not filed anywhere because it never happened.
- **The exact UTC timestamp on every `qm guest exec` capture in this exercise** is missing —
  Raymond's pastes didn't include one, and this was flagged mid-session but not corrected
  retroactively. Every evidence file in this exercise notes the gap explicitly rather than
  inventing a timestamp.

## Process note — pre-flight gate missed, corrected mid-session

Phase 0 (pre-flight) and Phase 1 (snapshot) were handed to Raymond in the same command
block instead of gating Phase 1 on Phase 0's result. Data% was already 92.01% — above the
skill's 85% stop-threshold — before either of this exercise's snapshots existed, and the
snapshot step ran anyway. My error, caught and stated here before being asked, per the
project's capture-contract rule for self-reported technical mistakes.

Recovery: two already-superseded snapshot pairs pruned by Raymond's explicit go-ahead
(`pre-upn-restamp-20260831` on VM100, `pre-domain-join-fix-20260901` on VM102, then
`pre-secure-admin-ws-scope-fix-20260901` on VM100) — see
`evidence/preflight-thin-pool-and-memory-20260902.txt` and
`evidence/postprune-thin-pool-and-memory-20260902.txt`. Data% moved 92.01% -> 88.99% ->
88.47%, still above 85%. RAM recovered substantially (169Mi -> 1.7Gi available), resolving
that half of the original concern.

**Consulted: whether to proceed at 88.47% or pull VM101's snapshot into scope or stop for
today.** VM101's `win11-ootb` snapshot (64GB LV, real 62% data) is the only remaining large
lever, but it's outside this project's tracked VM set and is VM101's only rollback point —
not pruned without a separate, explicit decision about whether VM101 falls under this
project's snapshot discipline at all. Raymond: **"go ahead with option 2"** — proceed at
88.47% rather than pull VM101 in or stop, on the stated reasoning that the next operation
(`Start-ADSyncSyncCycle` over ~13 directory objects) is a light incremental write, not the
sustained disk-heavy pattern (an OS install) that caused the earlier crash. This is a
judgment call under residual risk, stated as such, not a claim that 88.47% is actually safe
by the skill's own written threshold.
