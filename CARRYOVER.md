# Carryover

## Last verified
2026-09-11T14:58:41Z, host and guest reads during the 900 s induced-load test,
`exercises/2026-09-10-domain-time-skew/evidence-log.md`, finding 53.

## Next safe action
None queued. The tick-rate question is closed (finding 53): loss is concentrated at or near boot,
not ongoing. Pick a time fix or a boot-reproducibility test (both pending below), or the next item
from `EXPOSURES.md`'s queue or `CURRICULUM.md`'s new Exercise C3. Raymond's call.

## Lab state
Unchanged since last session. VM 100 (DC01) and VM 107 (CA01) running, booted 2026-09-09T14:19:31Z.
VM 101, 102, 104 stopped. CT 103 running, CT 106 stopped. Pool Data% 80.12, Meta% 3.84. **Clocks
are wrong.** DC01 is +5h 06m ahead and drifting; CA01 is +7h ahead and holding. DC01's hardware
timer runs at roughly half real elapsed time since boot; four tests found no ongoing loss rate
after boot. See `exercises/2026-09-10-domain-time-skew/report.md`.

## Stop conditions
Pool Data% at 85 or higher. Issue no certificate from CA01 until the clock is fixed.

## Hard deadlines
- P2 trial ends 2026-10-04T00:00:00Z. Verified.
- `svc-entraconnect` password expires about 2026-10-13. Unverified.
- `adm-jsmith` eligible membership expires 2026-12-08. Verified.
- `district-root.crl` expires 2027-03-07. Nothing regenerates it.

## Pending decisions
- **Second PIM approver for Exchange and Teams Administrator. Asked 2026-09-10, paused at
  Raymond's request. Default: none, ask first.** Both baselines are Captured and clean; only
  Exchange Administrator's default requires MFA to self-activate. See
  `exercises/2026-09-10-pim-policy-authoring/evidence-log.md`.
- Which time fix to apply to DC01. Three candidates in `2026-09-10-domain-time-skew/report.md`.
  Default: none, ask first.
- Whether to test boot-time reproducibility of the clocksource defect (finding 53), a state
  change. Default: none, ask first.
- Two `AllPrincipals` consent grants. Default: remove before teardown.
- `tmp-cainstall` deletion. Default: leave disabled.
- Credential scan patterns file and passes 4-5. Default: leave the hook alone, sweep by hand.
- `adm-jsmith`'s direct eligibility (B4). Default: remove before teardown.
- What role `88d8e3e3-8f55-4a1e-953a-9b9898b8876b` is, surfaced by accident. Default: leave for
  now.

## Blockers
Entra CBA needs public hosting for `crl.districtsafetyphoto.com`, and CA01's clock. Owner: Raymond.
`Connect-MgGraph` still times out, device-code workaround included, failed 2026-09-10. Use Graph
Explorer; see `gotchas.md`.

## Uncommitted and staged work
Not clean. Modified by this session: `exercises/2026-09-10-domain-time-skew/evidence-log.md` and
`report.md` (findings 51-53, tick-rate resolved), `EXPOSURES.md` (superseded a stale entry, added
finding 53), and `references/gotchas.md` (both copies, synced) with `qm guest exec`'s
load-latency behavior. **Modified outside this session: `CURRICULUM.md` carries a new, uncommitted
Exercise C3, added 2026-09-11, not Claude's.** Nothing staged. Not committed; not asked.
