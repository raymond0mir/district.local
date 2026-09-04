# B1: Security Defaults baseline and Conditional Access, report-only (blocked)

## What I set out to do

Run CURRICULUM.md's Exercise B1, steps 1-3: capture the Security Defaults baseline, create
Conditional Access policies in report-only mode, then exclude the break-glass account from each
before any enforcement. VM 101 and jsmith's Entra join and WHfB registration were already
Confirmed from the prior session's setup phase.

## The setup

Pre-flight, Proxmox host shell, 2026-09-04T02:25:43Z: all four VMs stopped, thin pool 61.62%
(under the 85% gate), 12Gi RAM available. No VM state change was needed — Security Defaults and
Conditional Access are tenant-level controls, not on-prem ones. `evidence/00-lab-state-preflight.txt`.

## What I did

1. `GET /policies/identitySecurityDefaultsEnforcementPolicy` via Graph Explorer, signed in as the
   break-glass Global Administrator account. Captured the baseline before any CA policy exists.
2. `POST /identity/conditionalAccess/policies` to create a report-only policy requiring MFA for
   all cloud apps, excluding the break-glass account by object ID.
3. Asked Raymond whether to start the Microsoft Entra ID P2 trial, since step 2 failed on
   licensing. He said yes.
4. Attempted trial activation in the Entra admin center (Billing > Licenses > All products >
   Try/Buy products > Microsoft Entra ID P2).

## Where Raymond was consulted

Asked: CURRICULUM.md requires B1, B2, and B3 to run inside one 30-day P2 trial window, with no
second trial. Start the trial now, committing that window? Decision: yes. Verbatim: "yes, start
the P2 trial now."

## What the box said

- Security Defaults: `isEnabled: true`. `evidence/01-security-defaults-baseline.json`.
- CA policy creation: `403 AccessDenied`, "Your tenant is not licensed for this feature. Please
  upgrade your subscription to access it."
  `evidence/02-ca-policy-create-denied-free-tier.json`.

## What broke, and why

The CA policy creation failure is not new breakage. It reconfirms `verified-claims.md:94`
(Exercise A3, 2026-09-02): the same tenant, same endpoint, same error text, three days apart.
Report-only mode does not exempt policy *creation* from the Free-tier licensing gate — only
reading the (empty) CA policies collection is open on Free.

The real break is procedural. `CARRYOVER.md` moved straight to "B1 steps 1-3" without checking
CURRICULUM.md's own stated prerequisite for those steps: an active P2 trial. The dependency was
named in the plan and dropped from the handoff.

Trial activation stopped at the payment-method step in the portal checkout flow. No tenant state
changed. This is a lab-external dependency, not a technical failure in the lab itself.

## What I'd do differently

Check a curriculum exercise's own stated prerequisites before writing it into carryover as the
next session's starting point, not just its step list. A ready-looking "next exercise" note
skipped a licensing dependency that was already on record two files away.

## Open questions

- When the P2 trial will be started — depends on payment method availability, outside this
  session's control.
- Whether `verified-claims.md:94` should cite this session's evidence file as a second
  confirmation, or stay as-is with a single citation. Not decided; leaning toward leaving it
  alone, since nothing about the claim changed.
- Steps 2-6 of B1 (report-only policies, break-glass exclusion, telemetry, enforcement) remain
  entirely unstarted, pending the trial.
