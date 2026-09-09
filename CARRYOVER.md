# Carryover

## Last verified
2026-09-09T20:12:05Z, `PKI-CBA-Pilot` restoration confirmed on DC01, `evidence/54`. Pool and VM
readings last taken 2026-09-09T14:41:18Z, not re-read this session; no VM or pool state changed.

## Next safe action
None queued. `report.md` for `exercises/2026-09-05-adcs-issuing-ca-build` is written — extended in
place with `evidence/54`'s close, matching how `evidence/52` and `53` were folded in — and awaits
Raymond's review before commit. The next exercise comes from his read of the report or a pick from
`EXPOSURES.md`'s queue.

## Lab state
VM 100 (DC01) and VM 107 (CA01) running, unchanged since 2026-09-09T14:41:18Z. Pool Data% 83.97,
metadata 4.20 at that reading, under the 85% gate. Not re-verified this session.

## Stop conditions
Pool Data% at 85 or higher. Run pre-flight before the next state change.

## Hard deadlines
- `districtsafetyphoto.com` registration may lapse this month. Unverified. `whois` not run.
- P2 trial ends 2026-10-04T00:00:00Z.
- `svc-entraconnect` password expires about 2026-10-13.
- `district-root.crl` expires 2027-03-07. Nothing regenerates it.

## Pending decisions
- When to delete `tmp-cainstall`. Disabled 2026-09-09, `evidence/53`. Default: leave disabled.
- Credential scan passes 4 and 5 need a patterns file at
  `~/.config/district-local/scan-patterns.txt`: the Vaultwarden values and the current tenant
  Global Administrator's name. Absent, so the hook prints SKIPPED and does not block. Default:
  leave the file absent, keep the passes owed.
- `report.md` is written and awaiting Raymond's review. Commit only when he says go.

## Blockers
Entra CBA needs `crl.districtsafetyphoto.com` served over public HTTP. Owner: Raymond.

## Uncommitted and staged work
`HEAD` is `0f0a931`, matching `origin/main` — nothing ahead to push. Working tree is not clean:
modified `EXPOSURES.md`, `verified-claims.md`, `report.md` and `evidence-log.md` under
`exercises/2026-09-05-adcs-issuing-ca-build/`; new `evidence/54-pki-cba-pilot-gates-enrollment-
non-member-denied.txt` in the same exercise. All from this session's enrollment test and the
report update that followed it. Whole-tree credential scan run clean: pass 2's 7 hits are
pre-existing `Get-Random` password-generation idioms from 2026-09-01 and 2026-09-05, none touched
this session. Not committed; Raymond is reviewing `report.md` before commit.
