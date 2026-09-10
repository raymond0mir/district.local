# Carryover

## Last verified
2026-09-10T14:52Z, unfiltered `directoryAudits` read. Pool and VM readings 2026-09-10T14:13:49Z,
`exercises/2026-09-09-pim-for-groups/evidence/07-session-2-preflight.md`.

## Next safe action
Start the next exercise: make a reporting role PIM-eligible, so an administrator can review their
own actions without a standing grant. `User Administrator` cannot read `directoryAudits`, and the
obvious remedy is a permanent role attachment. This lab already has the machinery to time-box it.

## Lab state
VM 100 (DC01) and VM 107 (CA01) running. Pool Data% 84.12, Meta% 4.21. Data% rose 0.15 points in
23.5 hours with no provisioning; running guests grow thin volumes and nothing reclaims.

Tenant: `PIM-UserAdmin-Pilot` holds `User Administrator` standing at tenant scope. `adm-jsmith` is
eligible to 2026-12-08. The 2026-09-10 activation ran 14:20:40.623Z to 16:20:40.03Z and expires on
its own. B4's direct eligibility remains in place by decision.

## Stop conditions
Pool Data% at 85 or higher. Headroom 0.88 points, and it rises while idle. Run pre-flight before the
next state change.

## Hard deadlines
- P2 trial ends 2026-10-04T00:00:00Z. Verified.
- `svc-entraconnect` password expires about 2026-10-13. Unverified.
- `adm-jsmith` eligible membership expires 2026-12-08. Verified.
- `district-root.crl` expires 2027-03-07. Nothing regenerates it.
- `districtsafetyphoto.com` may lapse this month. Unverified, `whois` not run.

## Pending decisions
- Two `AllPrincipals` consent grants created 2026-09-10, in `EXPOSURES.md`. Asked 2026-09-10.
  Default: leave in place, tracked, remove before teardown.
- Whether to strip IP addresses from captures as a standing rule. Asked 2026-09-10. Default: redact
  case by case, as done in `evidence/12` and `evidence/13`.
- Capture headers for `evidence/04`, `05` and `06`. Claude will not invent the timestamps. Asked
  2026-09-10. Default: leave the three WARNs open.
- `tmp-cainstall` deletion. Default: leave disabled.
- Credential-scan patterns file absent. Default: leave absent, passes 4 and 5 owed.
- B4's direct eligibility on `adm-jsmith`. Default: leave in place, remove before teardown.

## Blockers
Entra CBA needs `crl.districtsafetyphoto.com` over public HTTP. Owner: Raymond.
`Connect-MgGraph` still times out on both auth flows. Graph Explorer works; see `gotchas.md`.

## Uncommitted and staged work
`HEAD` is `fd60ab7`, matching `origin/main`. Nothing committed this session; Raymond has not asked.
Working tree: `exercises/2026-09-09-pim-for-groups/` gains `report.md` and `evidence/07` through
`13`, edits to `evidence/02`, `03`, `08`, `09` and `evidence-log.md`; plus `EXPOSURES.md`,
`verified-claims.md`, `CONSIDERATIONS.md`, `gotchas.md` and its plugin copy, and this file.

`validate.py` reports 2 ERROR, both `evidence-modified` on `evidence/02` and `03`. They are declared
in the evidence log's Corrections and in `CONSIDERATIONS.md`, and both clear on commit.
