# Carryover

## Last verified
2026-09-14T15:05:51Z, the interactive sign-in read,
`exercises/2026-09-14-device-code-detection/evidence/03-the-interactive-stream-holds-the-flow-and-cannot-name-it.md`.

## Next safe action
Open the Entra admin center, Monitoring, Audit logs. Widen the date filter. Download the oldest
surviving event. That fixes the `directoryAudits` retention boundary, now an exposure, without Graph
Explorer and without a lab state change.

## Lab state
No VM touched since 2026-09-11; readings not re-taken. VM 100 (DC01) and VM 107 (CA01)
running, booted 2026-09-09T14:19:31Z. VM 101, 102, 104 stopped. CT 103 running, CT 106 stopped.
Pool Data% 80.12, Meta% 3.84. **Clocks are wrong.** DC01 +5h 06m, CA01 +7h. See
`exercises/2026-09-10-domain-time-skew/report.md`.

**Tenant objects.** `Lab-AI-Agent-CLI`: app `e15012f9`, SP `4c43a528`, standing consent for
`User.Read` and `User.ReadBasic.All`. `P2P Server`: app `2c0ccf62`, SP `505610fa`, tenant-local,
created 2026-09-04, origin unrecorded.

## Stop conditions
Pool Data% at 85 or higher. Issue no certificate from CA01 until the clock is fixed.

## Hard deadlines
- P2 trial ends 2026-10-04T00:00:00Z. Verified. Gates `auditLogs/signIns`; retention drops with it.
- `svc-entraconnect` password expires about 2026-10-13. Unverified.
- `adm-jsmith` eligible membership expires 2026-12-08. Verified.
- `district-root.crl` expires 2027-03-07. Nothing regenerates it.

## Pending decisions
- Redacting the tenant domain, which embeds a personal email local-part. Asked 2026-09-14.
  Default: leave as captured; it is already throughout the repo.
- Okta AD agent exercise. Asked 2026-09-14. Gated on a free-plan check, the DC01 clock fix, and a
  member server host. Default: none, ask first.
- Second PIM approver for Exchange and Teams Administrator. Asked 2026-09-10. Default: ask first.
- Which time fix to apply to DC01. Three candidates in `2026-09-10-domain-time-skew/report.md`.
  Default: ask first.
- Boot reproducibility of the clocksource defect. Default: ask first.
- Teardown set: `Lab-AI-Agent-CLI` and its grant, two `AllPrincipals` grants, `adm-jsmith`'s direct
  B4 eligibility. Default: remove at teardown. `tmp-cainstall`: leave disabled.
- Credential scan patterns file and passes 4-5. Default: leave the hook alone, sweep by hand.

## Blockers
Graph Explorer has four recorded defects: stale `#users/$entity` bodies, a sticky address bar, a
permissions panel that will not load, and a sign-out that does not switch accounts. Prefer the Entra
admin center for audit work. Entra CBA needs public hosting for `crl.districtsafetyphoto.com`, and
CA01's clock. `Connect-MgGraph` times out. Owner: Raymond.

## Uncommitted and staged work
Not clean. New: `exercises/2026-09-14-device-code-detection/`, with a report, an evidence log and
evidence 01 to 05. Modified: `verified-claims.md`, six rows; `EXPOSURES.md`, two refined and three
added; `references/gotchas.md`, one rule narrowed and six added, both copies synced;
`validation.json`. Nothing staged.
