# Carryover

Open items only, as of 2026-09-04, closing exercise
`2026-09-04-b1-security-defaults-and-ca-report-only` (blocked — step 1 done, step 2 blocked on
tenant licensing, steps 3+ not started).

Read the tech-compass skill, then this file, then `EXPOSURES.md`. Check `verified-claims.md`
before labeling a claim Inherited or Recalled. Gotchas live in
`.claude/skills/tech-compass/references/gotchas.md`.

## Lab state

All four VMs stopped as of 2026-09-04T02:25:43Z: VM 100 (DC01), VM 101 (`win11-client01`), VM 102
(`entraconnect01`), VM 104 (`pfsense-fw`). Thin pool 61.62%, well under the 85% gate. Host RAM
12Gi available with everything stopped. No VM was started this session — Security Defaults and
Conditional Access are tenant-level, not on-prem.

## No console login path on DC01

`SeDenyInteractiveLogonRight = Domain Admins` blocks every Domain Admins member; `Administrator`
is separately disabled. No account can interactively log into DC01's console right now. `qm guest
exec` (SYSTEM, non-interactive) is unaffected and is the only working administrative path. Source
GPO unconfirmed, likely `District Lockdown`. Deferred by Raymond's decision — see `EXPOSURES.md`.

## Blocked: B1 needs a Microsoft Entra ID P2 trial

CA policy creation (even report-only) is licensing-gated on Free tier —
`POST /identity/conditionalAccess/policies` returns `403 AccessDenied`, reconfirming
`verified-claims.md:94` three days after A3 first captured it. Raymond approved starting the P2
trial. Trial activation stopped at the portal checkout's payment-method step; not completed this
session. Once a trial starts, CURRICULUM.md requires B1, B2, and B3 to run inside that single
30-day window — no second trial. Resume B1 steps 2-6 once the trial is active.

## Time-sensitive

- DC01's eval license grace ends ~2026-09-12. 5 of 6 rearms remain.
- `svc-entraconnect`'s password expires ~2026-10-13.
- `districtsafetyphoto.com` verification window nearly elapsed.

## Also open, not blocking

Two A3 test app objects (`Salesforce`, `A3-nongallery-test`) in Enterprise Applications — decide
delete or keep.

## Git state

Uncommitted: new exercise directory `2026-09-04-b1-security-defaults-and-ca-report-only`. Commit
only when Raymond asks.
