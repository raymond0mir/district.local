# Carryover

Open items only, as of 2026-09-02 (session continuing from earlier the same day). This file is
overwritten at each session close per `.claude/skills/tech-compass/SKILL.md` — resolved work
lives in `report.md` files, `evidence-log.md` files, and `verified-claims.md`, not here.

## From today's exercise: `2026-09-02-entra-connect-upn-signin-test`

**Resolved today, for the record:** Entra Connect is genuinely out of staging mode
(`Get-ADSyncScheduler` confirms `StagingModeEnabled: False`); a real export sync succeeded;
`jsmith` exported to Entra ID and then actually signed in with an on-premises AD credential via
Password Hash Sync, resolving the practical question the "Not Added" UPN status raised. Full
detail in `exercises/2026-09-02-entra-connect-upn-signin-test/report.md`.

Still open from today:

- **Root cause of the wizard's "Not Added" domain status.** Practically moot now (sign-in and
  export both work regardless) but never explained. Worth chasing only if it resurfaces as
  something that actually blocks a real operation.
- **The Proxmox thin pool's headroom problem is unresolved, not just patched.** `Data%` sits at
  88.47% as of this exercise's close, with only 2.00 GiB `VFree` in the VG (single PV,
  `/dev/nvme0n1p3`, 237.47 GiB) — no easy `lvextend` path without adding real storage. Raymond
  has a spare SD card/USB stick available; using it as a live PV was considered and rejected
  (blast radius spans the whole thin pool if removable media fails; poor sustained-write
  performance for exactly the disk-pressure pattern that's already crashed this lab once). The
  better-shaped fix discussed but not executed: use the USB stick as an external `vzdump` backup
  target, then prune the corresponding on-pool snapshot once the backup is confirmed good —
  reclaims real space without exposing live VM writes to slow/flaky media. Not urgent, but the
  next exercise that needs headroom shouldn't re-litigate this from scratch.
- **Whether the `qm guest exec` hung process (pid 4624) on DC01 was ever terminated is
  unconfirmed.** Quick check: `qm guest exec 100 -- powershell.exe -Command "Get-Process -Id
  4624 -ErrorAction SilentlyContinue"`.
- **`jsmith` now has a registered MFA method and a live, tested Entra ID identity** — the first
  restamped account taken end-to-end. Whether the other eight restamped accounts get the same
  treatment eventually, or `jsmith` stays the project's single test case, is undecided.
- **Entra Connect is now live, not staging.** Every future sync from this DC is a real export.
  Nothing currently assumes otherwise, but it changes the stakes of any future UPN, group
  membership, or connector-account change — worth keeping in mind starting the next exercise.
- **Sign-in logs (`GET /auditLogs/signIns`) are unavailable on this tenant's Entra Free
  license** (`Authentication_RequestFromNonPremiumTenantOrB2CTenant`) — a real, named
  constraint, not a permissions gap. Any future exercise wanting sign-in-log evidence needs
  either a licensing decision or the `GET /me`-as-the-user fallback already proven to work here.
- **The `vgs`/`pvs` readings behind "no room to extend the pool" were never filed as a proper
  evidence capture** — quoted in `report.md` from a single interactive exchange, not a
  `qm guest exec` JSON/text file. Re-run and file properly if this number needs to be cited
  precisely again.

## Still open from before today

- **B5 — split `exercises/2026-09-01-entra-connect-connector-account/report.md` in two.**
  Explicitly held, Raymond's call: needs real narrative rework (separate "What I set out to do"
  framing for the GPO-lockout/tattoo half vs. the connector-account/wizard half), not mechanical
  cut-and-paste. Drop step 14 and consultation point 10 (GitHub setup) when this happens — that
  content now lives in `README.md`.
- **`svc-entraconnect`'s password expires approximately 2026-10-13** (42-day default max age,
  `PasswordLastSet` 2026-09-01 07:54:57 AM). Rotate before then or set up a fine-grained password
  policy exemption — not yet decided which.
- **Origin of `Secure Admin WS`'s domain-root GPO link** — deliberate design choice or setup-time
  scope creep — was never established, only its current effective scope.
- **Whether the tattooed `SeDenyInteractiveLogonRight` could re-tattoo DC01** on a future GPO
  refresh cycle was never observed over time, only immediately after the one fix applied.
- **AD Recycle Bin is not enabled on `district.local`** — flagged by the Entra Connect wizard's
  own completion screen, not addressed.
- **The wizard's "Filtering" step was never actually reviewed** — screenshot skipped, contents
  unknown.
- **`districtsafetyphoto.com` verification never happened.** The roughly one-month registration
  window flagged 2026-08-31 has nearly elapsed.
- **Two of the five GPOs applying to DC01 have never been fully read** — `Default Domain Policy`
  and `District Lockdown`, per `EXPOSURES.md`.
