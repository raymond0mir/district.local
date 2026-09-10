# Carryover

## Last verified
2026-09-10T14:52Z, unfiltered `directoryAudits` read. Pool and VM readings 2026-09-10T14:13:49Z,
`exercises/2026-09-09-pim-for-groups/evidence/07-session-2-preflight.md`.

## Next safe action
Reclaim thin-pool headroom. Nothing that touches a VM can proceed past the 85 gate, and the gate is
closing with no work being done. Raymond decided 2026-09-10 that this is the next session's first
item. Run the privileged-access-path audit in the same session if time allows; it changes no state
and consumes no pool. It is queued in `EXPOSURES.md`, not in `CURRICULUM.md`'s run order.

## Lab state
VM 100 (DC01) and VM 107 (CA01) running. Pool Data% 84.12, Meta% 4.21. VM 107 carries three snapshot
sets: `pre-adcs-config`, `pre-ca-cert-reissue-20260908`, `pre-cdp-setup-20260908`. Its after-state
was confirmed 2026-09-08.

Tenant: `PIM-UserAdmin-Pilot` holds `User Administrator` standing at tenant scope. `adm-jsmith` is
eligible to 2026-12-08. The 2026-09-10 activation expired at 16:20:40Z.

## Stop conditions
Pool Data% at 85 or higher. Headroom 0.88 points. Data% rose 0.15 points in 23.5 hours with nothing
provisioned, which extrapolates to the gate about 2026-09-16. **Two readings, not a rate.** Treat
the date as indicative. Run pre-flight before the next state change.

## Hard deadlines
- P2 trial ends 2026-10-04T00:00:00Z. Verified. PIM configuration is deleted when it lapses.
- `svc-entraconnect` password expires about 2026-10-13. Unverified.
- `adm-jsmith` eligible membership expires 2026-12-08. Verified.
- `district-root.crl` expires 2027-03-07. Nothing regenerates it.
- `districtsafetyphoto.com` may lapse this month. Unverified, `whois` not run.

## Pending decisions
- Which VM 107 snapshots to prune. Asked 2026-09-10. Default: none without Raymond naming them.
- Two `AllPrincipals` consent grants, 2026-09-10, in `EXPOSURES.md`. Default: leave, remove before
  teardown.
- Stripping IP addresses from captures as a standing rule. Asked 2026-09-10. Default: redact case by
  case.
- Capture headers for `evidence/04`, `05`, `06` of the PIM exercise. Claude will not invent the
  timestamps. Default: leave the three WARNs open.
- `tmp-cainstall` deletion. Default: leave disabled.
- Credential-scan patterns file absent. Default: leave absent, passes 4 and 5 owed.
- B4's direct eligibility on `adm-jsmith`. Default: leave, remove before teardown.

## Blockers
Entra CBA needs `crl.districtsafetyphoto.com` over public HTTP. Owner: Raymond.
`Connect-MgGraph` times out on both auth flows. Graph Explorer works; see `gotchas.md`.

## Uncommitted and staged work
None. Working tree clean, matching `origin/main`.

`validate.py` reports 0 ERROR, 35 WARN, 24 INFO. Three of those WARNs are the missing capture
headers on `evidence/04`, `05` and `06` of the PIM exercise, listed under Pending decisions.
