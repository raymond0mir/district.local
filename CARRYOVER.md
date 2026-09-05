# Carryover

Open items only, as of 2026-09-05, closing exercise
`2026-09-05-b1-security-defaults-transition` (Security Defaults disabled; `365bdd23` and
`75882b6a` enforced for real; `d9a6a116` held report-only by decision; enforcement verified
live).

Read the tech-compass skill, then this file, then `EXPOSURES.md`. Check `verified-claims.md`
before labeling a claim Inherited or Recalled. Gotchas live in
`.claude/skills/tech-compass/references/gotchas.md`. Read them before the next tenant or host
command; three lines were added this session.

## Lab state

Confirmed 2026-09-05T19:16:42Z: VMs 100, 101, 102 stopped. VM 104 running. Matches the lab's
standard opening state. Pool Data% last read 66.28% at 18:45:01Z, under the 85% gate.

## B1 next steps

1. Security Defaults transition is done. `365bdd23` (MFA for all) and `75882b6a` (block
   legacy auth) genuinely enforce. Do not re-run this.
2. `d9a6a116` (compliant or hybrid device) stays report-only by deliberate decision — it would
   block VM 101 if enforced. Decide: enroll VM 101 in Intune, change the grant, or scope the
   policy. Not yet decided.
3. `75882b6a` is enforced but its block itself is unexercised. A legacy-auth attempt is the
   only real test.
4. Step 4 (telemetry volume) still needs more than one user's single session.
5. The fourth policy stays blocked on certificate-based auth and a trusted CA, both absent.

## No console login path on DC01

Unchanged. `SeDenyInteractiveLogonRight = Domain Admins` blocks every member; `Administrator`
is disabled. `qm guest exec` remains the only administrative path. Deferred by Raymond's
decision.

## Time-sensitive

- P2 trial active, 30-day clock, exact start Recalled. B1-B2-B3 must fit inside it.
- DC01 eval license grace ends ~2026-09-12. 5 of 6 rearms remain.
- `svc-entraconnect` password expires ~2026-10-13.
- `districtsafetyphoto.com` verification window nearly elapsed.

## Also open, not blocking

`A3-nongallery-test` app object: delete or keep, undecided. Whether to onboard more restamped
accounts for telemetry, undecided since 2026-09-04.

## Git state

Uncommitted: this exercise's directory, `verified-claims.md`, `EXPOSURES.md`, this file, and
`references/gotchas.md` plus its plugin copy. Commit only when Raymond asks.
