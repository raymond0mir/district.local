# Carryover

## Last verified
2026-09-10T02:50:54Z, `adm-jsmith`'s group membership showing `Activated`. Pool and VM readings
last taken 2026-09-09T14:41:18Z; this session touched the tenant only.

## Next safe action
Re-run the `dumbuser2` password reset as `adm-jsmith` while group membership is active, and
confirm it succeeds where it was denied at 2026-09-10T02:30Z. That is the hypothesis of
`exercises/2026-09-09-pim-for-groups` and it is the one step not yet run. Both activations from
this session expire on their own about 04:36–04:42Z, so this needs a fresh activation first.

## Lab state
VM 100 (DC01) and VM 107 (CA01) running, unchanged since 2026-09-09T14:41:18Z. Pool Data% 83.97,
metadata 4.20 at that reading, under the 85% gate. Not re-verified this session.

Tenant, new this session: `PIM-UserAdmin-Pilot`, cloud-only and role-assignable, holds `User
Administrator` standing at tenant scope. `adm-jsmith` is an eligible member to 2026-12-08 and
activated it at 02:50:54Z for two hours. A stray activation of B4's **direct** eligibility was
approved in error at about 02:42Z; deactivation unconfirmed, expires on its own.

## Stop conditions
Pool Data% at 85 or higher. Run pre-flight before the next state change.

## Hard deadlines
- `districtsafetyphoto.com` registration may lapse this month. Unverified. `whois` not run.
- P2 trial ends 2026-10-04T00:00:00Z. PIM configuration is deleted when a P2 licence lapses, so
  `exercises/2026-09-09-pim-for-groups` must finish inside that window.
- `svc-entraconnect` password expires about 2026-10-13.
- `district-root.crl` expires 2027-03-07. Nothing regenerates it.
- `adm-jsmith`'s eligible membership in `PIM-UserAdmin-Pilot` expires 2026-12-08.

## Pending decisions
- When to delete `tmp-cainstall`. Disabled 2026-09-09, `evidence/53`. Default: leave disabled.
- Credential scan passes 4 and 5 need a patterns file at
  `~/.config/district-local/scan-patterns.txt`. Absent, so the hook prints SKIPPED. Default: leave
  it absent, keep the passes owed.
- Removing B4's direct `User Administrator` eligibility from `adm-jsmith`. Raymond decided
  2026-09-09 to keep both paths "for the sake of the lab," with removal owed before teardown.
  Default: leave in place, tracked in `EXPOSURES.md`.

## Blockers
Entra CBA needs `crl.districtsafetyphoto.com` served over public HTTP. Owner: Raymond.

Graph tooling unresolved: Graph Explorer returned stale responses, `Connect-MgGraph` timed out on
both auth flows. `evidence/04` to `06` are Recalled because of it. Detail in `gotchas.md`.

## Uncommitted and staged work
`HEAD` is `7aaad13`, matching `origin/main`. Working tree not clean: new exercise
`exercises/2026-09-09-pim-for-groups/` with `evidence-log.md` and `evidence/01` through `06`; plus
edits to `EXPOSURES.md`, `references/gotchas.md` and its plugin copy, and this file. Nothing
committed; Raymond has not asked.
