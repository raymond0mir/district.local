# A3 — The Entra ID Free ceiling, measured

## What I set out to do

Map, with captured refusals rather than a reading of a Microsoft pricing page, exactly which
identity controls this tenant's Entra ID Free license blocks and which it doesn't — Conditional
Access, PIM, Identity Protection, Security Defaults, and gallery-app SAML/SCIM — so the boundary
for later Phase B work (which needs a P1/P2 trial) is known precisely rather than assumed.

## The setup

Tenant: `raytakosharkygmail.onmicrosoft.com`, signed in as the break-glass Global Admin
`breakglass@raytakosharkygmail.onmicrosoft.com`. Entirely tenant-side — no `qm guest exec`, no
DC01 state touched, so the usual thin-pool/RAM pre-flight doesn't apply here. Capture path is
Graph Explorer for API calls and the Entra admin center for the two portal-only flows (Conditional
Access and PIM have no meaningful UI-only path worth separating from their Graph behavior; SAML
and SCIM setup are portal-native).

`GET /subscribedSkus` returned an empty array — no paid SKU assigned. That's consistent with an
unlicensed/Free tenant, not a direct "tier: Free" label from Graph (Free has no assignable SKU to
report), stated at that precision rather than overclaimed.

## What I did

1. `GET /policies/identitySecurityDefaultsEnforcementPolicy` — hit a stale-session 403 first, fixed by signing out/in to Graph Explorer (not by re-consenting — see "What broke," below), then read cleanly.
2. `GET /identityProtection/riskyUsers` — attempted read.
3. `GET /identity/conditionalAccess/policies` — attempted read.
4. `POST /identity/conditionalAccess/policies` — attempted to create a policy built inert by construction (`state: disabled`, `includeUsers: None`) so a surprise success couldn't affect anyone.
5. `GET /roleManagement/directory/roleEligibilityScheduleRequests` — attempted a PIM-surface read.
6. Entra admin center: added the **Salesforce** gallery app to Enterprise Applications, attempted **Single sign-on → SAML** with placeholder values, then **Provisioning → Connect your application** with junk admin credentials.
7. Follow-up Graph reads against the resulting `servicePrincipal` object and its `synchronization/jobs` collection, to confirm the portal outcome at the object level rather than trusting screenshots alone.

## Where Raymond was consulted

No standing-privilege, security-posture, or destructive judgment calls arose in this exercise —
every write attempted was either refused by licensing before it could take effect, or built inert
by construction (the CA policy) or functionally inert by design (the Salesforce test app has no
users/groups assigned and placeholder, non-resolving endpoints). Every step was executed by
Raymond directly in Graph Explorer / the admin center, since this exercise has no `qm guest exec`
equivalent — I have no live tenant access at all here, cloud-side or otherwise.

**Open, not yet asked:** whether to delete the test Salesforce enterprise app object now that its
job here is done. Flagged in Open questions below rather than assumed.

## What the box said

**Security Defaults:** `isEnabled: true`, `controlTypes: []`. No per-user/group scoping field
exists on this object at all — the "cannot express" half of the CURRICULUM's ask isn't a refusal
to capture, it's the absence of a scoping property in the schema itself.
(`evidence/security-defaults-state-20260902T2104Z.json`)

**Identity Protection (`riskyUsers`):** `403`, `code: "Forbidden"`, *"Your tenant is not licensed
for this feature."* (`evidence/identity-protection-riskyusers-license-refusal-20260902T2109Z.json`)

**Conditional Access:** `GET` on the policies collection returns a clean `200` with `value: []`;
`POST` to create one returns `403`, `code: "AccessDenied"`, *"Your tenant is not licensed for this
feature. Please upgrade your subscription to access it."* Read is open, write is refused — an
asymmetry worth keeping on record, not something I'd have guessed from the pricing page.
(`evidence/conditional-access-list-empty-20260902T2111Z.json`,
`evidence/conditional-access-create-attempt-license-refusal-20260902T2111Z.json`)

**PIM (`roleEligibilityScheduleRequests`):** `400 Bad Request`, `code:
"AadPremiumLicenseRequired"`, *"The tenant needs to have Microsoft Entra ID P2 or Microsoft Entra
ID Governance license."* — the only refusal of the three that names its exact license
requirement in plain text, and the only one that comes back as `400` instead of `403`.
(`evidence/pim-role-eligibility-license-refusal-20260902T2112Z.json`)

**Three premium features, three different refusal shapes.** No consistent HTTP status or Graph
error code across `riskyUsers` (403/`Forbidden`), CA create (403/`AccessDenied`), and PIM
(400/`AadPremiumLicenseRequired`). Anyone building error handling against "the" Entra Free refusal
signature would need to handle all three, not one.

**Gallery-app SAML SSO (Salesforce) — succeeds cleanly on Free.** Saved without any licensing
error. The resulting `servicePrincipal` confirms it at the object level:
`preferredSingleSignOnMode: "saml"`, the placeholder reply URL and identifier we entered, and a
real auto-generated signing certificate (`keyCredentials`, valid 2026-09-02 through 2029-09-02).
This is federated SAML, not the password-based "basic SSO" fallback the CURRICULUM's Recalled
note anticipated. (`evidence/gallery-app-saml-sso-configured-live-20260902T2120Z.json`)

**Gallery-app SCIM provisioning (Salesforce) — no license gate found, genuinely untested past
that.** The admin-credentials form appears with no upsell. "Test connection" with junk credentials
returned Salesforce's own `InvalidCredentials`, not an Entra refusal — that's the lab hitting "no
real Salesforce tenant to test against," not a Free-tier wall. `GET .../synchronization/jobs`
confirms no job object was ever created, so whether Free would block an actual provisioning run
further downstream is a real open question, not a result.
(`evidence/gallery-app-scim-provisioning-attempt-20260902T2116Z.json`)

**Already Confirmed before this exercise, restated for completeness:** `GET /auditLogs/signIns`
refuses with `Authentication_RequestFromNonPremiumTenantOrB2CTenant` (`verified-claims.md` line 54).

## What broke, and why

**A Graph Explorer token went stale mid-session.** The first Security Defaults query failed with
`AccessDenied` / "required scopes are missing in the token," and the Modify Permissions tab
showed both relevant scopes already in `Unconsent` state (i.e. already tenant-consented) — the
consent was real, the bearer token in the browser session just predated it. Re-consenting would
have changed nothing; signing out and back in did. Worth remembering for any future Graph
Explorer session in this tenant: a stale-token 403 and a genuine missing-consent 403 look
identical in the error body and need different fixes.

**The SCIM thread hit a real capability boundary of this lab, not a licensing wall.** Testing
whether Entra Free blocks an actual provisioning *run* (as opposed to the setup screens) needs a
live third-party SaaS tenant to provision into, which this lab doesn't have and has no obvious
reason to acquire just for this question.

## The licensing recommendation

I don't have the Skechers req document itself in this repo to cite line-by-line, so this is
scoped to exactly what this exercise tested, not to a specific job posting's control list.

**What Free actually covers, demonstrated rather than assumed:** Security Defaults (tenant-wide
MFA and legacy-auth blocking, no scoping), reading the CA policy surface, and — new information
from today — federated SAML SSO and SCIM provisioning *setup* for at least one gallery app.

**What Free cannot do at all, each confirmed by a real refusal:** enforce Conditional Access
(create/write refused, though reading is open), Identity Protection risk detection, and PIM
(just-in-time role activation, access reviews on roles). These three map cleanly to Microsoft's
own tier boundary: **P1** buys Conditional Access; **P2** buys PIM and Identity Protection (P2
also includes everything in P1).

**For a 100-user org wanting the controls this exercise actually tested:** P1 is the floor if
Conditional Access matters at all — it was the one Free refuses outright with no partial
credit. Whether P2 is worth the incremental spend depends specifically on whether PIM's
just-in-time privileged access is a stated requirement, versus something CA's session controls
and a well-run Restricted Groups/AGDLP model on-prem could substitute for. SSO and provisioning
for a handful of gallery SaaS apps do **not** appear to require any paid tier, per today's
direct test — a genuine cost saving over what I'd have assumed going in, though see the
non-gallery caveat below before quoting this as blanket fact.

## What I'd do differently

Run `GET /subscribedSkus` first, before anything else — I built the whole exercise on the
tenant-is-Free premise from prior context and only checked it directly at the end. It happened to
hold up, but that's exactly the kind of assumption this skill exists to stop.

I'd also test a **non-gallery (custom) SAML/SCIM app**, not just a gallery one, in a follow-up.
CURRICULUM's original Recalled note was specifically about non-gallery apps needing P1 — Salesforce
being a gallery app with a pre-built template doesn't actually test that claim at all. The gallery
result and the non-gallery claim are two different things that got conflated in the original plan.

## Open questions

- **Whether Entra Free blocks an actual SCIM provisioning run (not just setup) is untested.**
  Needs a real third-party SaaS tenant this lab doesn't have. Filed as genuinely open, not assumed
  either way.
- **The non-gallery SAML/SCIM licensing claim from CURRICULUM.md is still untested.** This
  exercise tested a gallery app; the P1 claim was specifically about non-gallery custom apps.
- **Whether to delete the test Salesforce enterprise app object.** It's inert (no user/group
  assignments, `appRoleAssignmentRequired: true`, placeholder endpoints) but it's a real directory
  object now. Raymond's call, not assumed.
- **Security Defaults' "cannot scope/exclude" claim rests on the absence of a property in the
  schema (`GET` returns no per-user field), not on an attempted-and-refused exclusion.** A
  positive test — e.g. checking whether any per-user MFA-registration exemption exists anywhere in
  the tenant's config — was not attempted.
