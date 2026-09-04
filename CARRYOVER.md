# Carryover

Open items only, as of 2026-09-04, closing exercise `2026-09-04-b1-conditional-access-report-only`
(setup phase — VM 101 characterized and Entra-joined; CA policy work itself not started).

Read the tech-compass skill, then this file, then `EXPOSURES.md`. Check `verified-claims.md`
before labeling a claim Inherited or Recalled. Gotchas live in
`.claude/skills/tech-compass/references/gotchas.md`.

## Lab state

VM 100 (DC01) running. VM 101 (`win11-client01`) running, 3072 MB, Entra-joined as `jsmith`. VM
102 (`entraconnect01`) running, 2048 MB, synced. VM 104 (`pfsense-fw`) running. Container 103
(Vaultwarden) running. All four VMs plus the container running concurrently — new for this lab.
Host RAM available as low as 1.2Gi at last check (2026-09-04, ~00:3xZ). Thin pool 72.13%, under
the 85% gate. Commitment now roughly 16.77 GiB on a 15 GiB host — down from 3.77 GiB over to about
1.77 GiB over, still not resolved. See `EXPOSURES.md`.

## No console login path on DC01

`SeDenyInteractiveLogonRight = Domain Admins` blocks every Domain Admins member; `Administrator`
is separately disabled. No account can interactively log into DC01's console right now. `qm guest
exec` (SYSTEM, non-interactive) is unaffected and is the only working administrative path. Source
GPO unconfirmed, likely `District Lockdown`. Deferred by Raymond's decision — see `EXPOSURES.md`.

## Time-sensitive

- DC01's eval license grace ends ~2026-09-12. 5 of 6 rearms remain.
- `svc-entraconnect`'s password expires ~2026-10-13.
- `districtsafetyphoto.com` verification window nearly elapsed.

## Next exercise

B1 steps 1-3, fresh session: Security Defaults baseline, then CA policies in report-only (require
MFA, block legacy auth, require compliant/hybrid device, require phishing-resistant auth for a
named app — Windows Hello for Business is already provisioned on VM 101), then the break-glass
exclusion. That last step needs the current tenant Global Administrator's UPN — Raymond supplies
it in session, not written here.

## Also open, not blocking

Two A3 test app objects (`Salesforce`, `A3-nongallery-test`) in Enterprise Applications — decide
delete or keep.

## Git state

Uncommitted: `EXPOSURES.md`, `verified-claims.md`, new exercise directory
`2026-09-04-b1-conditional-access-report-only`. Commit only when Raymond asks.
