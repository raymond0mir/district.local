# Carryover

## Last verified
2026-09-09T14:41:18Z, pool and VM state, read directly this session. `validate.py` re-run clean
in this session, 0 ERROR, 29 WARN, 24 INFO — not lab-timestamped, a local repo check.

## Next safe action
Attempt enrollment on `district.localClientAuthentication` as a user outside `PKI-CBA-Pilot`.
`evidence/52` names this gap: it proves the `Domain Users` ACE is gone, and does not prove
`PKI-CBA-Pilot` alone gates enrollment. VM 100 and VM 107 are already running; pre-flight is only
needed again if resuming after a gap.

## Lab state
As of 2026-09-09T14:41:18Z: VM 100 (DC01) and VM 107 (CA01) running, started this session. Pool
Data% 83.97, metadata 4.20 — under the 85% gate, margin narrower than the prior 83.69% reading.
Container 106 and other guests not re-read. Not filed to a numbered evidence file; a routine
pre-flight check, not a finding.

## Stop conditions
Pool Data% at 85 or higher. Run pre-flight before the next state change.

## Hard deadlines
- `districtsafetyphoto.com` registration may lapse this month. Unverified. `whois` not run.
- P2 trial ends 2026-10-04T00:00:00Z. B2 runs inside it.
- `svc-entraconnect` password expires about 2026-10-13.
- `district-root.crl` expires 2027-03-07. Nothing regenerates it.

## Pending decisions
- When to delete `tmp-cainstall`. Decided 2026-09-09: disable now, delete after a retention
  window — `evidence/53`. The window itself is not yet named. Default: leave it disabled. Enable
  AD Recycle Bin before any deletion, since a delete is not otherwise reversible.
- Credential scan passes 4 and 5 need a patterns file at
  `~/.config/district-local/scan-patterns.txt`, one literal string per line: the Vaultwarden values
  and the current tenant Global Administrator's name. Raymond holds both. Until it exists the hook
  prints SKIPPED and does not block. Default: leave the file absent, and keep the passes owed.

## Blockers
Entra CBA needs `crl.districtsafetyphoto.com` served over public HTTP. Owner: Raymond. He owns the
domain and has not hosted it. The 2026-09-08 chain verify used LDAP, which Entra cannot use.

## Uncommitted and staged work
None. Working tree clean, `HEAD` at `20c3ac9`, matches `origin/main`. Everything through the ADCS
exercise, the `validate.py` immutability fix, and the member-server report's missing section is
committed and pushed.
