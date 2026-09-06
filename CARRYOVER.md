# Carryover

Open items only, as of 2026-09-06T00:15Z.

Read the tech-compass skill, then this file, then `EXPOSURES.md`. Check `verified-claims.md`
before labeling a claim Inherited or Recalled. Gotchas live in
`.claude/skills/tech-compass/references/gotchas.md`.

## Lab state

Read 2026-09-05T23:55:32Z: pool `Data%` 78.42, metadata 3.84, under the 85% gate with about
10.2 GiB of margin. Host memory 6.6Gi available.
Running: VM 100 (DC01), VM 104 (pfSense), VM 107 (CA01), container 106 (rootca-offline).
Stopped: VM 101, VM 102, container 103. This is **not** the lab's standard opening state.
Snapshot `pre-adcs-config` on VM 107 is a valid rollback point. All `certutil` orphans are cleared.

## Run order, revised 2026-09-05

`CURRICULUM.md` governs the order. Next three:

1. Capture the P2 trial start date. `GET /beta/directory/subscriptions`. The clock is Recalled.
2. B1's fourth policy, using Windows Hello for Business under the built-in phishing-resistant
   strength. `jsmith` holds a registered method.
3. **B4 — PIM.** The only P2-gated exercise. Expiry deletes eligible assignments and PIM
   configuration.

## Decisions owed, deferred by Raymond 2026-09-05

1. B4 needs a cloud-native account for the eligible role. Break-glass stays active and outside
   PIM. `jsmith` is synced. Create an account, or name an existing one.
2. Does B1 close with `d9a6a116` held report-only, or does VM 101's device path get resolved
   first?
3. DC01 before about 2026-11-01: rearm chain only, or a rebuild on licensed media?
4. `districtsafetyphoto.com`: verify it, or drop it?
5. Is there a date the portfolio must be presentable? It reorders C1 against B4 and the README.

## AD CS, paused, now Exercise C2

No report. No longer a B1 dependency. Runs after the trial. Do not resume before B4. The blocker,
its two untested hypotheses, and the console-account lead are in `CURRICULUM.md` under C2 and in
`exercises/2026-09-05-adcs-issuing-ca-build/evidence-log.md`.

## Time-sensitive

- DC01 rearm due about 2026-09-12, then about every 10 days. 5 rearms left.
- DC01 relicensed or replaced before about 2026-11-01. That date ends the lab.
- CA01 licence grace ends about 2026-09-15. Rearm count not captured.
- P2 trial ends about 2026-10-04, derived from a Recalled start.
- `svc-entraconnect` password expires about 2026-10-13.

## B1, still open

`d9a6a116` report-only by decision. `75882b6a`'s block unexercised. Telemetry rests on one user.

## Git state

The 2026-09-05 reorder is committed and **not pushed**. `origin/main` is at `982869e`.
