# Carryover

Open items only, as of 2026-09-05, closing exercise
`2026-09-05-b1-breakglass-exclusion-verification` (break-glass exclusion verified on all three
policies; B1 step 1 closed).

Read the tech-compass skill, then this file, then `EXPOSURES.md`. Check `verified-claims.md`
before labeling a claim Inherited or Recalled. Gotchas live in
`.claude/skills/tech-compass/references/gotchas.md`. Read them before the next tenant or host
command; nine lines were added this session.

## Lab state

Captured 2026-09-05T16:17:01Z: thin pool Data% 61.62, Meta% 3.27, 10Gi available. VMs 100, 101 and
102 stopped, VM 104 running.

VM 101 was started for the contrast sign-in and stopped again at 2026-09-05T16:51:16Z, leaving
11Gi available. All four VMs are back to their opening state. Nothing else moved.

`qm shutdown 101` failed first: VM 101 sets `agent: 1` but runs no working guest agent, so it takes
no scripted administrative path at all. See `EXPOSURES.md` and the gotchas file.

## B1 next steps

1. Step 1 is done. All three exclusions are verified by machine output. Do not re-run it.
2. The next gate is the Security Defaults transition, not enforcement. Security Defaults is the
   only control enforcing MFA here, it accepts no exclusions, and it must be disabled before any CA
   policy can enforce. Plan the order and the window length first. See `EXPOSURES.md`.
3. `d9a6a116` would block VM 101 today (`reportOnlyFailure`, Azure AD joined and not compliant).
   Decide before enforcing: enroll in Intune, change the grant, or scope the policy.
4. `75882b6a`'s exclusion is verified but its block has never been exercised. A legacy-auth attempt
   is the only test.
5. Step 4 (telemetry volume) still needs more than one user's single session.
6. The fourth policy stays blocked on certificate-based auth and a trusted CA, both absent.

## No console login path on DC01

Unchanged. `SeDenyInteractiveLogonRight = Domain Admins` blocks every member; `Administrator` is
disabled. `qm guest exec` remains the only administrative path. Deferred by Raymond's decision.

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
