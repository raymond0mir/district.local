# Carryover

Open items only, as of 2026-09-06T00:15Z. Exercise `2026-09-05-adcs-issuing-ca-build` is
**paused mid-build** for a second time, not closed. No report written yet.

Read the tech-compass skill, then this file, then `EXPOSURES.md`. Check `verified-claims.md`
before labeling a claim Inherited or Recalled. Gotchas live in
`.claude/skills/tech-compass/references/gotchas.md`.

## Lab state

Read 2026-09-05T23:55:32Z: pool `Data%` 78.42, metadata 3.84, under the 85% gate with about
10.2 GiB of margin. Host memory 6.6Gi available.
Running: VM 100 (DC01), VM 104 (pfSense), VM 107 (CA01), container 106 (rootca-offline).
Stopped: VM 101, VM 102, container 103. This is **not** the lab's standard opening state.
Snapshot `pre-adcs-config` on VM 107 is a valid rollback point. All `certutil` orphans are cleared.

## The blocker, now localised

`certutil -installcert C:\ca01.cer` blocks on an established LDAP connection to DC01:389.
`CACertHash` stays null, `CertSvc` cannot start, and no AD object exists for the issuing CA.
Cause: run under `qm guest exec`, `certutil` authenticates as `CA01$`, which is denied the
Configuration-container write. `certutil -dspublish` from CA01 proves the denial and returns in
under a second.

**Still unexplained:** why a denial that is fast in `dspublish` becomes an indefinite block in
`-installcert`. Two hypotheses, untested: it retries or waits rather than failing, or it raises a
credential prompt that cannot render in session 0.

**Next step.** Run `certutil -installcert C:\ca01.cer` at CA01's console, from an elevated prompt,
as an account **without** Enterprise Admins. That separates the two hypotheses at no privilege
cost. Then decide on a temporary re-grant.

## Blocking that next step

**No console logon to CA01 works.** The local `Administrator` password Raymond holds is rejected.
`DISTRICT\tmp-cainstall` holds local administrator on CA01 and is untested as a console account.
Try it first.

`tmp-cainstall` is out of Enterprise Admins by decision. Enterprise Admins now holds only the
disabled `Administrator`. Re-grant, if needed, runs as SYSTEM via `qm guest exec` on DC01.

## Time-sensitive

- CA01 licence grace ends about 2026-09-15. DC01's ends about 2026-09-12, 5 of 6 rearms left.
- P2 trial, 30-day clock, exact start Recalled.
- `svc-entraconnect` password expires about 2026-10-13.
- `districtsafetyphoto.com` verification window nearly elapsed.

## B1, still open

Four items unchanged: `d9a6a116` report-only by decision, `75882b6a`'s block unexercised,
telemetry resting on one user, and the fourth CA policy blocked on CBA.

## Git state

Committed and pushed through `ffddbea`. This exercise's directory is uncommitted. Commit only
when Raymond asks.
