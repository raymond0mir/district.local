# B1: Security Defaults baseline and Conditional Access, report-only (3 of 4 policies)

## What I set out to do

Run CURRICULUM.md's Exercise B1, steps 1-3: capture the Security Defaults baseline, build
Conditional Access policies in report-only mode, and exclude the break-glass account from each
before any enforcement. VM 101's Entra join and `jsmith`'s WHfB registration were already
Confirmed from a prior setup exercise.

## The setup

Two sessions, same exercise. First session: pre-flight in the Proxmox host shell,
2026-09-04T02:25:43Z. All four VMs stopped, thin pool 61.62% (under the 85% gate), 12Gi RAM
available. `evidence/00-lab-state-preflight.txt`. No VM state change was needed either session —
Security Defaults and Conditional Access are tenant-level controls, reached through Graph
Explorer, not the lab VMs.

## What I did

1. `GET /policies/identitySecurityDefaultsEnforcementPolicy`. Captured the baseline before any CA
   policy existed.
2. `POST /identity/conditionalAccess/policies` for a report-only MFA policy. Failed on licensing.
3. Raymond started the Microsoft Entra ID P2 trial. Checkout stopped on a prepaid card the flow
   rejected; a different card completed it, between sessions.
4. `GET /subscribedSkus` confirmed the trial active.
5. `GET /users/breakglass@raytakosharkygmail.onmicrosoft.com` to get the exclusion target's
   object ID and enabled state, before reusing it.
6. Three `POST /identity/conditionalAccess/policies` calls, one per control: MFA for all users,
   block legacy authentication, require compliant or hybrid-joined device. Each report-only,
   each excluding the current break-glass account by object ID.
7. Attempted to verify the exclusion against real sign-in activity via `GET /auditLogs/signIns`.

## Where Raymond was consulted

Starting the P2 trial commits CURRICULUM.md's B1-B2-B3 sequencing to one 30-day window, no second
trial. Asked whether to start it now. Decision: yes. Verbatim: "yes, start the P2 trial now."

The fourth policy (phishing-resistant auth) needed two decisions CURRICULUM.md left open: which
app, and which phishing-resistant method (FIDO2, Windows Hello for Business, or
certificate-based authentication). Decision: Salesforce, certificate-based authentication.
Verbatim: "Salesforce, and use certificate-based authentication."

Certificate-based authentication turned out disabled tenant-wide, with no trusted CA configured —
real setup work, not a flag to flip. Asked whether to build that now, create the fourth policy
anyway with no working control behind it, or stop at three. Decision: stop at three. Verbatim:
"stop at three policies for now."

## What the box said

- Security Defaults: `isEnabled: true`. `evidence/01-security-defaults-baseline.json`.
- First CA policy attempt: `403 AccessDenied`, "Your tenant is not licensed for this feature."
  `evidence/02-ca-policy-create-denied-free-tier.json`.
- P2 trial: `AAD_PREMIUM_P2`, `capabilityStatus: Enabled`, 100 prepaid units, 0 consumed.
  `evidence/03-p2-trial-license-confirmed.json`.
- `breakglass@raytakosharkygmail.onmicrosoft.com`: `accountEnabled: false`.
  `evidence/04-old-breakglass-disabled-confirmed.json`.
- Three CA policies created, each `201`, state `enabledForReportingButNotEnforced`:
  `evidence/05-ca-policy-01-mfa-all-users-created.json`,
  `evidence/06-ca-policy-02-block-legacy-auth-created.json`,
  `evidence/07-ca-policy-03-compliant-hybrid-device-created.json`.
- Certificate-based authentication: `state: disabled`, `certificateAuthorityScopes: []`.
  `evidence/08-cba-disabled-no-ca-configured.json`.
- Sign-in log checks against the break-glass account's object ID: five records, all predating
  policy creation by 17-22 minutes; two later checks after a fresh MFA sign-in returned the same
  records again, no new entry. `evidence/09-signin-log-predates-policies.json`.

## What broke, and why

The first CA policy attempt failed on licensing, re-confirming `verified-claims.md:94` (Exercise
A3, 2026-09-02) rather than adding a new finding — same tenant, same endpoint, same error, three
days apart. `CARRYOVER.md` had scheduled "B1 steps 1-3" without checking that CURRICULUM.md names
the P2 trial as those steps' own prerequisite. Process gap, not a lab misconfiguration.

Trial checkout rejected the first payment method offered: a prepaid card. Microsoft's signup flow
identifies prepaid cards by BIN and declines them regardless of billing details. A card tied to a
real bank account cleared it on a later attempt.

CURRICULUM.md's own text named `breakglass@raytakosharkygmail.onmicrosoft.com` as "the natural
exclusion" for B1's policies. That account was rotated out 2026-09-03 — disabled, stripped of
Global Administrator (`verified-claims.md:106`, `:131`) — and CURRICULUM.md was never updated
after the rotation. Excluding a disabled account from an enforced policy would have left no
working break-glass path. Caught before any policy was created with the wrong exclusion; fixed in
CURRICULUM.md this session.

The fourth policy assumed certificate-based authentication was ready to reference in a grant
control. It is not: the method is disabled, and no certificate authority is registered at all.
CURRICULUM.md itself had flagged CBA as "more work" than FIDO2 or WHfB — that warning held.

Exclusion verification did not resolve. Two attempts pulled the break-glass account's sign-in
log, once before any post-policy sign-in existed (predictable — the sign-ins were all older than
the policies), and twice more after Raymond signed out and back in with MFA. Both later pulls
returned the same pre-existing records, no entry newer than policy creation. A confirmed MFA
sign-in not producing a new logged event is not explained by ordinary propagation lag alone.

## What I'd do differently

Check a curriculum exercise's own named prerequisites and account references before treating its
step list as ready to run. Two separate staleness problems surfaced this session this way: a
missing trial dependency, and a rotated-out account name. Both were catchable by reading
CURRICULUM.md's own cross-references before the first write call, not after a failed one.

## Open questions

- Why the break-glass account's sign-in log did not show a new entry after a confirmed MFA
  sign-in. Possible causes not distinguished: browser SSO/session reuse skipping a logged event,
  or an indexing delay longer than the between-attempts wait covered. Exclusion is not verified.
- Whether report-only telemetry (CURRICULUM.md step 4) needs a minimum observation window before
  reading it is meaningful — not established.
- Whether to build the fourth policy once certificate-based authentication is actually set up, or
  reconsider FIDO2/WHfB instead, given the CBA setup gap just found.
- The two leftover A3 test app objects (`Salesforce`, `A3-nongallery-test`) in Enterprise
  Applications — Salesforce is now in active use as B1's sensitive-app target; whether
  `A3-nongallery-test` should be deleted or kept is still undecided.
