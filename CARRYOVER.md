# Carryover

## Last verified
2026-09-12T16:59:35Z, Graph read of `roleManagement/directory/roleDefinitions`,
`exercises/2026-09-12-workload-identity-scope-isolation/evidence/05-wids-b79fbf4d-is-not-a-role.md`.

## Next safe action
Create `Lab-AI-Agent-CLI` in the Entra admin center. Single tenant, no redirect URI, public client
flows on, `User.Read` only, no admin consent. Then validate it with Graph reads. Exercise C3,
`exercises/2026-09-12-workload-identity-scope-isolation`, paused at that step.

## Lab state
No VM was touched this session; all work was in the tenant. These readings are from 2026-09-11 and
were not re-taken. VM 100 (DC01) and VM 107 (CA01) running, booted 2026-09-09T14:19:31Z. VM 101,
102, 104 stopped. CT 103 running, CT 106 stopped. Pool Data% 80.12, Meta% 3.84. **Clocks are
wrong.** DC01 is +5h 06m, CA01 is +7h. See `exercises/2026-09-10-domain-time-skew/report.md`.

## Stop conditions
Pool Data% at 85 or higher. Issue no certificate from CA01 until the clock is fixed.

## Hard deadlines
- P2 trial ends 2026-10-04T00:00:00Z. Verified.
- `svc-entraconnect` password expires about 2026-10-13. Unverified.
- `adm-jsmith` eligible membership expires 2026-12-08. Verified.
- `district-root.crl` expires 2027-03-07. Nothing regenerates it.

## Pending decisions
- Second PIM approver for Exchange and Teams Administrator. Asked 2026-09-10. Default: none, ask
  first.
- Which time fix to apply to DC01. Three candidates in `2026-09-10-domain-time-skew/report.md`.
  Default: none, ask first.
- Whether to test boot reproducibility of the clocksource defect. Default: none, ask first.
- Two `AllPrincipals` consent grants. Default: remove before teardown.
- `tmp-cainstall` deletion. Default: leave disabled.
- `adm-jsmith`'s direct eligibility (B4). Default: remove before teardown.
- Credential scan patterns file and passes 4-5. Default: leave the hook alone, sweep by hand.
- What role `88d8e3e3-8f55-4a1e-953a-9b9898b8876b` is. Default: leave for now.
- `Lab-AI-Agent-CLI` and its service principal, once created. Default: remove at teardown.

## Blockers
Graph Explorer's permissions panel will not load, so no new scope can be consented there. Build in
the portal and validate with Graph reads. Entra CBA needs public hosting for
`crl.districtsafetyphoto.com`, and CA01's clock. Owner: Raymond. `Connect-MgGraph` still times out.

## Uncommitted and staged work
Not clean. New: `exercises/2026-09-12-workload-identity-scope-isolation/`, an `evidence-log.md` and
five evidence files. Modified: `CURRICULUM.md`, two retracted calendar rows; `EXPOSURES.md`, three
entries; `verified-claims.md`, one row; `exercises/2026-09-09-pim-for-groups/report.md`, one open
question closed; `references/gotchas.md`, both copies synced. Nothing staged. Not committed; not
asked.
