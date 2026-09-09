# Carryover

Open items, 2026-09-09.

Read `EXPOSURES.md` next.

## Lab state

Not re-read this session. As of 2026-09-08T23:45:49Z: VM 100 (DC01), VM 107 (CA01) and container
106 are stopped. Pool Data% 83.69, metadata 4.19, under the 85% gate. That margin is thin. The
snapshots `snap_vm-107-disk-{0,1}_pre-cdp-setup-20260908` cover the pre-CDP state, so a new
snapshot is not needed. Run pre-flight before the first state change.

## Uncommitted, and staged

The index holds two unrelated bodies of work. Staged 2026-09-08: ADCS evidence 40 through 51, that
exercise's `evidence-log.md` and `report.md`, `EXPOSURES.md`, `references/gotchas.md`, `validate.py`.
Staged 2026-09-09: B4's `evidence/16`, `evidence-log.md` and `report.md`, plus `CURRICULUM.md`,
`CARRYOVER.md` and `verified-claims.md`.

Nothing is committed. Raymond was asked to split the two into separate commits and did not answer.
Do not commit both as one without asking again.

Credential scan passes 1, 1b, 2 and 3 were re-run 2026-09-09 and are clean on the whole tree.
Passes 4 and 5 are still owed and need Raymond: the Vaultwarden literal strings, and the current
tenant Global Administrator's name.

## B4 closed 2026-09-09

The PT4H over-limit request is captured. Entra refuses it during validation, names
`ExpirationRule`, and writes no request object. `evidence/16`. Ledger row added, CURRICULUM
updated.

## Next in the ADCS exercise

Neither step started 2026-09-09. Both are on-premises and need no public hosting.

1. Remove `DISTRICT\Domain Users`' Allow Enroll ACE from `district.localClientAuthentication`.
   Use `tmp-cainstall`'s Full Control on the template object. Do not re-grant Enterprise Admins.
2. Retire `tmp-cainstall` after step 1. Standing Full Control outliving its task.

## Still blocked

Entra CBA needs `crl.districtsafetyphoto.com` served over public HTTP. Raymond owns the domain and
has not hosted it. The 2026-09-08 chain verify used LDAP, which Entra cannot use.

## Time-sensitive

- `districtsafetyphoto.com` registration may lapse this month. Never verified. `whois` not run.
- P2 trial ends 2026-10-04T00:00:00Z. B2 runs inside it. Whether tenant CBA is P2-gated is not captured.
- `svc-entraconnect` password expires about 2026-10-13.
- `district-root.crl` expires 2027-03-07. Nothing regenerates it.

## Tooling

`validate.py` reports 16 errors, all pre-existing. It is modified in the tree and no longer writes
`validation.json`, so `validation.json` is stale.
