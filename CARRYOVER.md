# Carryover

## Last verified
2026-09-09. Lab readings below are from 2026-09-08T23:45:49Z and were not re-read this session.
Git state and evidence files were read this session.

## Next safe action
Attempt enrollment on `district.localClientAuthentication` as a user outside `PKI-CBA-Pilot`.
`evidence/52` names this gap: it proves the `Domain Users` ACE is gone, and does not prove
`PKI-CBA-Pilot` alone gates enrollment. Run pre-flight first. It touches CA01.

## Lab state
As of 2026-09-08T23:45:49Z: VM 100 (DC01), VM 107 (CA01) and container 106 are stopped. Pool Data%
83.69, metadata 4.19. That margin is thin. Snapshots
`snap_vm-107-disk-{0,1}_pre-cdp-setup-20260908` cover the pre-CDP state.
Evidence: `exercises/2026-09-05-adcs-issuing-ca-build/evidence/`.

## Stop conditions
Pool Data% at 85 or higher. Run pre-flight before the first state change.

## Hard deadlines
- `districtsafetyphoto.com` registration may lapse this month. Unverified. `whois` not run.
- P2 trial ends 2026-10-04T00:00:00Z. B2 runs inside it.
- `svc-entraconnect` password expires about 2026-10-13.
- `district-root.crl` expires 2027-03-07. Nothing regenerates it.

## Pending decisions
- Delete `tmp-cainstall`. Consultation point 5 requires it. The account still exists, removed from
  Enterprise Admins but not from the domain. Deletion needs Raymond. Default: leave it, and carry
  the standing Full Control as a named exposure.
- Split the tree into two commits. Asked 2026-09-08. Unanswered. Default: commit nothing. Do not
  re-ask as new.
- Credential scan passes 4 and 5 need Raymond: the Vaultwarden literal strings, and the current
  tenant Global Administrator's name. Default: passes stay owed, no commit until they run.

## Blockers
Entra CBA needs `crl.districtsafetyphoto.com` served over public HTTP. Owner: Raymond. He owns the
domain and has not hosted it. The 2026-09-08 chain verify used LDAP, which Entra cannot use.

## Uncommitted and staged work
Nothing is staged. The index is empty. The tree holds two unrelated bodies of work, all unstaged
or untracked: the ADCS exercise (evidence 40 through 52, its evidence log and report,
`EXPOSURES.md`, `references/gotchas.md`, `validate.py`), and the 2026-09-09 contract split
(`CLAUDE.md`, `SKILL.md`, `CONSIDERATIONS.md`, `CARRYOVER.md`, `validation.json`).

Corrections, 2026-09-09. Three prior carryover claims were wrong:
`validate.py` reports 1 ERROR, not 16, and still writes `validation.json` on `--json`.
Work described as staged was never staged; the index was empty.
The `Domain Users` Allow Enroll ACE removal was described as not started. It is done, in
`evidence/52`.
