# Evidence log — B1: Security Defaults baseline and CA report-only

Two sessions. First: step 1 done, step 2 blocked on tenant licensing. Second: P2 trial confirmed,
three of four step 2 policies created report-only, fourth deferred on a CBA prerequisite. Steps
4-6 (telemetry, enforcement) not started.

## Pre-flight

All four VMs stopped; thin pool 61.62%, well under the 85% gate; 12Gi RAM available. No VM
needed for this exercise — CA and Security Defaults are tenant-level, not on-prem.
`evidence/00-lab-state-preflight.txt`.

## Step 1: Security Defaults baseline — captured

`GET /policies/identitySecurityDefaultsEnforcementPolicy` returns `isEnabled: true`. Security
Defaults is currently the tenant's only identity-security enforcement layer.
`evidence/01-security-defaults-baseline.json`.

## Step 2: CA policy creation — blocked, not a new finding

`POST /identity/conditionalAccess/policies` (require MFA, all users, report-only, break-glass
excluded) returned `403 AccessDenied`, "Your tenant is not licensed for this feature."
`evidence/02-ca-policy-create-denied-free-tier.json`.

This re-confirms `verified-claims.md:94` (A3, 2026-09-02) rather than adding a new claim: the same
tenant, same endpoint, same error, three days later. Report-only mode does not exempt policy
*creation* from the licensing gate — only Free-tier features (like reading the empty CA policies
collection) are open. `CARRYOVER.md`'s "Next exercise: B1 steps 1-3" did not check this dependency
before scheduling the session, even though `CURRICULUM.md` itself names the P2 trial as a B1
prerequisite. Process gap, not a lab misconfiguration.

## Where Raymond was consulted

Asked: starting the Microsoft Entra ID P2 trial now begins a 30-day clock, and CURRICULUM.md's own
sequencing note requires B1, B2, and B3 to run inside that one window with no second trial. Did he
want to start it now? Decision: yes, start it now. Verbatim: "yes, start the P2 trial now."

## Trial activation — not completed this session

Portal path (Entra admin center, Billing > Licenses > All products > Try/Buy products >
Microsoft Entra ID P2) requires a payment method during checkout. The payment method available
this session was not one the checkout flow accepted. Trial not started. No Graph capture exists
for this — nothing to capture, since no state changed on the tenant. Recalled only: Raymond's
description of the checkout screen, not independently observed.

## Trial confirmed, next session

`GET /subscribedSkus` shows `AAD_PREMIUM_P2`, `capabilityStatus: Enabled`, 100 prepaid units, 0
consumed. Trial is active. `evidence/03-p2-trial-license-confirmed.json`.

## Finding: CURRICULUM.md's B1 exclusion target is stale

CURRICULUM.md step 3 names `breakglass@raytakosharkygmail.onmicrosoft.com` as the exclusion
account. `GET /users/breakglass@...` returns `accountEnabled: false`. This account was rotated
out 2026-09-03 (`verified-claims.md:131`, `:106`): removed from Global Administrator, sign-in
disabled, object retained. A new break-glass account replaced it, UPN unpublished per Raymond's
decision. CURRICULUM.md was not updated after the rotation. Policy creation paused pending the
correct exclusion target. `evidence/04-old-breakglass-disabled-confirmed.json`.

## Step 2, policy 1: Require MFA for all users — captured

`POST /identity/conditionalAccess/policies` succeeded, `id 365bdd23-d0e0-49a7-8131-f63b98ea6115`,
state `enabledForReportingButNotEnforced`, current break-glass account excluded by object ID.
`evidence/05-ca-policy-01-mfa-all-users-created.json`.

## Step 2, policy 2: Block legacy authentication — captured

`POST /identity/conditionalAccess/policies` succeeded, `id 75882b6a-a9ba-4d97-bbb4-72d29277ebf4`,
state `enabledForReportingButNotEnforced`, `clientAppTypes` exchangeActiveSync + other, same
exclusion. `evidence/06-ca-policy-02-block-legacy-auth-created.json`.

## Step 2, policy 3: Require compliant or hybrid joined device — captured

`POST /identity/conditionalAccess/policies` succeeded, `id d9a6a116-0c05-4894-af2c-a2990ef44593`,
state `enabledForReportingButNotEnforced`, `compliantDevice` + `domainJoinedDevice`, same
exclusion. `evidence/07-ca-policy-03-compliant-hybrid-device-created.json`.

## Where Raymond was consulted, policy 4

Asked: which app is the named sensitive app, and which phishing-resistant method. Decision:
Salesforce (the existing A3 enterprise app object), certificate-based authentication. Verbatim:
"Salesforce, and use certificate-based authentication."

## Finding: certificate-based authentication is not usable yet

`GET /policies/authenticationMethodsPolicy/authenticationMethodConfigurations/X509Certificate`
returns `state: disabled`, `certificateAuthorityScopes: []`. No trusted CA is registered. Two
setup steps are needed before policy 4 could produce real telemetry: enable the method, and
configure a trusted CA. `evidence/08-cba-disabled-no-ca-configured.json`.

## Where Raymond was consulted, policy 4 decision

Asked: set up CBA now, create policy 4 anyway with no working control, or stop at three policies.
Decision: stop at three. Verbatim: "stop at three policies for now." Step 2 closes with three of
four report-only policies. CBA setup and policy 4 move to a future exercise.

## Finding: first exclusion-verification attempt was timed wrong

Pulled the break-glass account's 5 most recent sign-ins to verify the policy exclusions.
All 5 predate policy creation (13:50-13:53Z vs 14:10-14:12Z) — no signal either way.
The response also carried the account's real UPN and display name; redacted before writing
to disk, per the rule against publishing the current Global Administrator's identity.
`evidence/09-signin-log-predates-policies.json`.

## Open question: exclusion verification did not produce new sign-in data

Raymond signed out and back in with MFA, twice, to generate a fresh sign-in after the three
report-only policies existed. Both re-queries returned the same pre-existing records
(13:50-13:53Z), no entry newer than policy creation (14:10-14:12Z). Not explained by normal
propagation lag alone, since a real MFA sign-in was confirmed and the log still did not update
on retry. Cause unknown: could be SSO/session reuse in the browser not producing a new logged
event, or a longer indexing delay than expected. Unresolved — move to Open questions in the
report, do not state the exclusion as verified.

## Not started

Break-glass exclusion verification against real sign-in activity, report-only telemetry (step 4),
reading which policies fired (step 5), enforcement (step 6). Also open: the phishing-resistant
policy against Salesforce, blocked on CBA setup (a trusted CA plus enabling the method).
