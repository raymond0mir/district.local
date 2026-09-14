# Carryover

## Last verified
2026-09-13T01:22:29Z, the second device code run,
`exercises/2026-09-12-workload-identity-scope-isolation/evidence/10-one-variable-changed-and-the-refusal-became-a-success.md`.

## Next safe action
Open a free Okta org. Read Directory > Directory Integrations. Capture whether Active Directory
appears. Okta's published plan table lists AD and LDAP as neither included nor excluded. This
changes no lab state.

## Lab state
No VM touched since 2026-09-11. VM readings are not re-taken. VM 100 (DC01) and VM 107 (CA01)
running, booted 2026-09-09T14:19:31Z. VM 101, 102, 104 stopped. CT 103 running, CT 106 stopped.
Pool Data% 80.12, Meta% 3.84. **Clocks are wrong.** DC01 +5h 06m, CA01 +7h. See
`exercises/2026-09-10-domain-time-skew/report.md`.

**Tenant object from C3.** `Lab-AI-Agent-CLI`: application `e15012f9`, service principal
`4c43a528`, appId `388b9dd8`. Public client, device code flow enabled, standing user consent for
`User.Read` and `User.ReadBasic.All` from `adm-jsmith`.

## Stop conditions
Pool Data% at 85 or higher. Issue no certificate from CA01 until the clock is fixed.

## Hard deadlines
- P2 trial ends 2026-10-04T00:00:00Z. Verified. It gates `auditLogs/signIns`.
- `svc-entraconnect` password expires about 2026-10-13. Unverified.
- `adm-jsmith` eligible membership expires 2026-12-08. Verified.
- `district-root.crl` expires 2027-03-07. Nothing regenerates it.

## Pending decisions
- Okta AD agent exercise. Asked 2026-09-14. Gated on the next safe action, the DC01 clock fix, and
  a member server host. Default: none, ask first.
- Second PIM approver for Exchange and Teams Administrator. Asked 2026-09-10. Default: none, ask
  first.
- Which time fix to apply to DC01. Three candidates in `2026-09-10-domain-time-skew/report.md`.
  Default: none, ask first.
- Boot reproducibility of the clocksource defect. Default: none, ask first.
- `Lab-AI-Agent-CLI` and its consent grant. Default: delete the application at teardown.
- Two `AllPrincipals` consent grants. Default: remove before teardown.
- `tmp-cainstall` deletion. Default: leave disabled.
- `adm-jsmith`'s direct eligibility (B4). Default: remove before teardown.
- Credential scan patterns file and passes 4-5. Default: leave the hook alone, sweep by hand.
- What role `88d8e3e3-8f55-4a1e-953a-9b9898b8876b` is. Default: leave for now.

## Blockers
Graph Explorer's permissions panel will not load, so no new scope can be consented there. Signing
out of Graph Explorer does not switch accounts. Entra CBA needs public hosting for
`crl.districtsafetyphoto.com`, and CA01's clock. `Connect-MgGraph` still times out. Owner: Raymond.

## Uncommitted and staged work
Not clean. Modified: C3's `evidence-log.md`, two edits dated 2026-09-14. Its stale "Not started"
section is retired on the record, and the dropped PIM activation is logged as a consultation entry.
Nothing staged. C3's report, evidence, ledger rows and exposure entries are committed.
