# Carryover

## Last verified
2026-09-09T14:38:18Z, from `evidence/53`. Pool and VM readings below are older, from
2026-09-08T23:45:49Z, and were not re-read.

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
- Delete `tmp-cainstall`. Decided 2026-09-09: disable now, delete after a retention window.
  Disabled in `evidence/53`. Its Full Control ACE on `district.localClientAuthentication` still
  stands as an object, unusable while the account is disabled. Deletion is irreversible because AD
  Recycle Bin is disabled. Default: leave it disabled. Enable AD Recycle Bin before any deletion.
- Credential scan passes 4 and 5 need Raymond: the Vaultwarden literal strings, and the current
  tenant Global Administrator's name. Default: passes stay owed, no commit until they run.

## Blockers
Entra CBA needs `crl.districtsafetyphoto.com` served over public HTTP. Owner: Raymond. He owns the
domain and has not hosted it. The 2026-09-08 chain verify used LDAP, which Entra cannot use.

## Uncommitted and staged work
Nothing is staged. `fdf8dcc`, the contract split, is committed and pushed. `ad1263e`, the ADCS
exercise, is committed and not pushed. The tree holds only this file and `validation.json`, both
refreshed after `ad1263e`.

Corrections, 2026-09-09. `validate.py` still writes `validation.json` on `--json`. Its ERROR
count depends on what is tracked: 1 with the ADCS evidence untracked, 18 staged, 1 again after
`ad1263e`. Quote no bare count without saying which. Work described as staged was never staged;
the index was empty. The `Domain Users` Allow Enroll ACE removal, described as not started, is
done in `evidence/52`.
