# Carryover

Open items only, as of 2026-09-03, closing three exercises: breakglass rotation, Vaultwarden
secrets store, Vaultwarden credential migration.

Read the tech-compass skill, then this file, then `EXPOSURES.md`. Check `verified-claims.md`
before labeling a claim Inherited or Recalled. Gotchas live in
`.claude/skills/tech-compass/references/gotchas.md`.

## Lab state

VM 100 (DC01) running, rearmed 2026-09-02. VM 104 (pfsense-fw) running. VM 102 stopped — Entra
Connect not syncing. VM 101 stopped. VM 105 destroyed. Container 103 (Vaultwarden) running, holds
3 real credentials. Thin pool 72.11%, under the 85% gate. Host RAM available 3.5Gi (2026-09-03
23:32 UTC). VM state last independently checked ~17:14 UTC 2026-09-02; this session touched only
container 103.

## Time-sensitive

- DC01's eval license grace ends ~2026-09-12. 5 of 6 rearms remain. Decide: rearm, activate, or
  rebuild.
- `svc-entraconnect`'s password expires ~2026-10-13. Rotate or set a policy exemption.
- `districtsafetyphoto.com` verification window (flagged 2026-08-31) nearly elapsed.

## Next exercise

B1 unblocked: Conditional Access, report-only to enforced, per `CURRICULUM.md`.
B2 placement still owed, not blocking: run outside the P1/P2 trial on A3's setup-only evidence, or
keep it inside the trial as a safety margin. Raymond's call.

## Vaultwarden, still open

- `ADMIN_TOKEN` stays plain text in `/root/vaultwarden.env`; a vault copy now exists too. Hash it
  or remove the token.
- Container 103 runs AppArmor unconfined.
- Backups share a disk with what they protect. Cron unwitnessed.
- `vmbr1`'s host address (`10.0.0.5/24`) persisted, unproven until the next reboot.

## Infrastructure

- Restore path never verified for any VM (Vaultwarden's container backup is the lab's only
  verified restore).
- Host RAM committed 18.77Gi against 15Gi installed; whether DC01 needs 10000 MB is untested.
- 21.93 GiB of pool consumption unattributed, likely `clean-install`/`win11-ootb` snapshots
  (never `lvchange -K -ay`'d to check). pfSense has zero snapshots.

## Findings not yet acted on

- `Default Domain Policy` sets `LockoutBadCount = 0` — no lockout threshold in the domain.
- `District Lockdown`'s Restricted Groups setting targets nonexistent group "Admins" (inert).
- AD Recycle Bin not enabled, never independently captured.
- Two A3 test app objects (`Salesforce`, `A3-nongallery-test`) — decide delete or keep.

## Loose threads

- DC01 shutdowns not fully explained: 9/1 1:46:15 PM (no `wlms.exe` entry) and whether 8/31
  09:38:11 was also license-driven.
- A `pveproxy` `root@pam` auth 45s before DC01's 09-02 crash, not Raymond, unchecked.
- Two unreviewed items: `CURRICULUM.md`'s step-4 tattoo observation (before-half only) and the
  Entra Connect wizard's Filtering step.
- `jsmith` is the only restamped account taken end-to-end.

## Deferred by Raymond's decision

- Hardware: run lean, no purchases. Dell Latitude 5420, `DIMM B` empty, one M.2 slot.
- B5: split the `entra-connect-connector-account` report in two. Needs narrative rework.

## Git state

Uncommitted: `verified-claims.md`, new exercise dir. Commit only when Raymond asks. Last commit
`2867893` on `main`, pushed.
