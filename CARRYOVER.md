# Carryover

Open items only, as of 2026-09-04, closing exercise
`2026-09-04-b1-security-defaults-and-ca-report-only` (P2 trial confirmed, 3 of 4 report-only
policies created, exclusion verification unresolved).

Read the tech-compass skill, then this file, then `EXPOSURES.md`. Check `verified-claims.md`
before labeling a claim Inherited or Recalled. Gotchas live in
`.claude/skills/tech-compass/references/gotchas.md`.

## Lab state

Unchanged from last close: all four VMs stopped, thin pool 61.62%, 12Gi RAM available. No VM was
touched this session — B1's CA work is tenant-level, via Graph Explorer.

## B1 next steps

1. Resolve exclusion verification first, before trusting any of the three report-only policies.
   Two attempts at pulling the break-glass account's sign-in log after a confirmed MFA sign-in
   returned no new entry — unexplained, not just slow. See report's Open questions.
2. CBA setup is its own prerequisite for the fourth policy (phishing-resistant auth, Salesforce):
   a trusted CA plus enabling the method, both currently absent.
3. Steps 4-5 (report-only telemetry, reading which policies fired) need real sign-in volume first
   — not a same-session task.
4. Step 6 (enforcement) waits on all of the above.

## No console login path on DC01

`SeDenyInteractiveLogonRight = Domain Admins` blocks every Domain Admins member; `Administrator`
is separately disabled. `qm guest exec` (SYSTEM, non-interactive) remains the only working
administrative path. Deferred by Raymond's decision — see `EXPOSURES.md`.

## Time-sensitive

- P2 trial is active, 30-day clock running; exact start timestamp not captured (Recalled only).
  B1, B2, B3 must complete inside this window per CURRICULUM.md.
- DC01's eval license grace ends ~2026-09-12. 5 of 6 rearms remain.
- `svc-entraconnect`'s password expires ~2026-10-13.
- `districtsafetyphoto.com` verification window nearly elapsed.

## Also open, not blocking

`A3-nongallery-test` app object in Enterprise Applications — decide delete or keep. `Salesforce`
is now in active use as B1's sensitive-app target, no longer undecided.

## Git state

Uncommitted: today's evidence log, report, evidence files, `verified-claims.md` and
`EXPOSURES.md` updates, and a `CURRICULUM.md` correction (stale break-glass account reference).
Commit only when Raymond asks.
