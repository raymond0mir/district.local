# Carryover

## Last verified
2026-09-11T01:33:28Z, guest-agent read on DC01,
`exercises/2026-09-10-domain-time-skew/evidence-log.md`, finding 47. Pool reading unchanged since
2026-09-10T18:10:11Z.

## Next safe action
No lab command queued. `TickCount` confirms DC01 loses ticks (findings 45-47); testing `ostype: l26`
against host scheduling pressure as the cause needs a test not yet designed. Otherwise: find when
DC01 lost its DNS route to `time.windows.com` (finding 43) — lab network history, not a command.

## Lab state
Unchanged since last session. VM 100 (DC01) and VM 107 (CA01) running, both booted
2026-09-09T14:19:31Z. VM 101, 102, 104 stopped. CT 103 running, CT 106 stopped. Pool Data% 80.11,
Meta% 3.84. Tenant unchanged: `PIM-UserAdmin-Pilot` holds `User Administrator` standing.
**Clocks are wrong.** DC01 is +5h 06m ahead and drifting; CA01 is +7h ahead and holding. See
`exercises/2026-09-10-domain-time-skew/report.md`.

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
- Two `AllPrincipals` consent grants. Default: remove before teardown.
- `tmp-cainstall` deletion. Default: leave disabled.
- Credential scan patterns file and passes 4-5. Default: leave the hook alone, sweep by hand.
- `adm-jsmith`'s direct eligibility (B4). Default: remove before teardown.
- What role `88d8e3e3-8f55-4a1e-953a-9b9898b8876b` is, surfaced by accident. Not investigated.
  Default: leave for now.

## Blockers
Entra CBA needs public hosting for `crl.districtsafetyphoto.com`, and CA01's clock. Owner: Raymond.
`Connect-MgGraph` still times out, including the device-code pre-auth workaround, tried and failed
2026-09-10. Use Graph Explorer; see `gotchas.md`.

## Uncommitted and staged work
Not clean. Modified: `EXPOSURES.md`, `verified-claims.md`,
`exercises/2026-09-10-domain-time-skew/evidence-log.md` and `report.md`. This session finished the
repository timestamp audit for the named exercises (none exposed), corrected a wrong claim about
when DC01's error started (a lost DNS route between 9/2 and 9/5 is the leading candidate, not the
`ostype`/`localtime` config alone, dormant since 8/31), and confirmed by a second method that
DC01's own hardware timer loses ticks against real time, not only its wall clock. Nothing staged.
Not committed; Raymond has not asked.
