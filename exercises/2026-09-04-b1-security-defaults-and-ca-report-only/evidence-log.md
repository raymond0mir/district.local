# Evidence log — B1: Security Defaults baseline and CA report-only (attempt)

Short session. Step 1 completed. Step 2 blocked on tenant licensing before any policy was
created. Steps 3+ not started.

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

## Not started this session

CA report-only policies (MFA, legacy auth block, compliant/hybrid device, phishing-resistant
auth), break-glass exclusion verification, telemetry, enforcement. All wait on the P2 trial.
