# Carryover

Open items, 2026-09-06T18:45Z.

Read `EXPOSURES.md` next. The skill holds the contract; gotchas live in its `references/`.

## Lab state

Read 2026-09-06T16:55:54Z: pool `Data%` 79.28, metadata 3.87, under the 85% gate. Host memory
6.7Gi available.
Running: VM 100 (DC01), VM 104, VM 107 (CA01), container 106. Stopped: VM 101, VM 102,
container 103. **Not** the standard opening state. `pre-adcs-config` on VM 107 is a valid
rollback point.

## B4 — finish these three reads first

`report.md` is marked Draft and names the gap. Do not publish it first.

All three filter on `principalId eq '03ee6546-f113-4ec5-ba9d-e57381b0c928'`, under
`/v1.0/roleManagement/directory/`.

1. The unactioned expiry. `roleAssignments` and `roleAssignmentScheduleInstances`, both empty.
2. `roleEligibilityScheduleInstances`. Eligibility must survive the expiry. If it did not, the
   control is single-use.
3. The PT4H over-limit request, re-run as `adm-jsmith` from a clean state. Unresolved: no
   response was captured, and the endpoint cannot tell a refusal from an attempt never sent.
   Body in `evidence/12`.

Then fold the results into `report.md`, add ledger rows, and drop the Draft marker.

## Decisions owed

1. Does routine tenant work move to `adm-jsmith`? That exposure closes on habit, not
   configuration.
2. `districtsafetyphoto.com`: verify, or drop? Recommended drop; window nearly gone.
3. DC01 before about 2026-11-01: rearm chain, or rebuild? Recommended rearm only.
4. `CURRICULUM.md`'s B4 text still frames the exercise as turning just-in-time access on. The
   defaults capture disproves that.
5. `evidence/04` carries Raymond's personal address, inside the original Global Administrator's
   UPN. The redaction rule covers the current one only. PII decision still deferred.

Answered 2026-09-06: no hard portfolio date, so C1 stays behind C2. B1's fourth policy and B4
swapped, because only B4's evidence dies at expiry.



## Time-sensitive

- DC01 rearm due about 2026-09-12, then every 10 days. 5 rearms left.
- DC01 relicensed or replaced before about 2026-11-01. That date ends the lab.
- CA01 licence grace ends about 2026-09-15. Rearm count not captured.
- P2 trial ends 2026-10-04T00:00:00Z. **Captured**, no longer derived.
- `svc-entraconnect` password expires about 2026-10-13.

## Still open elsewhere

B1: `d9a6a116` report-only, `75882b6a`'s block unexercised, telemetry on one user. B1's fourth
policy runs after B4. C2 (AD CS): no report; blocker in `CURRICULUM.md`.

## Repository and git

`origin/main` reached `e7a64bb` on 2026-09-06. Run `git status` for anything after it.
`validate.py` baseline: 1 ERROR, 11 WARN, 24 INFO. Re-run it.
Pass 4 of the credential scan has never run; it needs the Vaultwarden strings.
