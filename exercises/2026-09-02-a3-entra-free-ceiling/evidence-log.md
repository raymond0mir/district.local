# Evidence log — A3: the Entra ID Free ceiling, measured

Capture path: Graph Explorer (https://developer.microsoft.com/graph/graph-explorer), run by
Raymond signed in as `breakglass@raytakosharkygmail.onmicrosoft.com`, pasted back with response
status and body. No `qm guest exec` needed — this exercise is tenant-side, not DC01-side.

## Plan (per CURRICULUM.md Exercise A3)

1. Capture refusals: Conditional Access policy creation, PIM enablement, Identity Protection risk
   query. (`signIns` refusal already Confirmed — `verified-claims.md` line 54.)
2. Capture what Security Defaults currently enforces.
3. Attempt one gallery-app SAML config and one SCIM provisioning setup; capture what happens.
4. Write the licensing recommendation.

## Captured this session

- **Security Defaults state**: `isEnabled: true`, `controlTypes: []` — enabled, no per-user/group
  scoping surface exposed by the API. First attempt hit a stale-session-token 403
  (`AccessDenied`, "required scopes are missing") even though Modify Permissions showed
  `Policy.Read.All` / `Policy.ReadWrite.SecurityDefaults` already tenant-consented; fixed by
  signing out/in to Graph Explorer, not by re-consenting. `evidence/security-defaults-state-20260902T2104Z.json`.
- **Identity Protection (`riskyUsers`) refusal**: `403 Forbidden`, code `Forbidden`, "Your tenant
  is not licensed for this feature." `evidence/identity-protection-riskyusers-license-refusal-20260902T2109Z.json`.
- **Conditional Access — read succeeds, write refused**: `GET` on the (empty) policies collection
  returns `200`; `POST` to create one (built inert: `state: disabled`, `includeUsers: None`)
  returns `403`, code `AccessDenied`, "not licensed... upgrade your subscription." Read/write
  asymmetry is itself a finding. `evidence/conditional-access-list-empty-20260902T2111Z.json`,
  `evidence/conditional-access-create-attempt-license-refusal-20260902T2111Z.json`.
- **PIM (`roleEligibilityScheduleRequests`) refusal**: `400 Bad Request`, code
  `AadPremiumLicenseRequired`, names the exact licenses ("Microsoft Entra ID P2 or Microsoft
  Entra ID Governance license"). `evidence/pim-role-eligibility-license-refusal-20260902T2112Z.json`.
- **Three premium-feature refusals, three different shapes**: no consistent HTTP status or error
  code across riskyUsers (403/`Forbidden`), CA create (403/`AccessDenied`), PIM (400/
  `AadPremiumLicenseRequired`) — worth a line in the report on its own.
- `signIns` refusal was already Confirmed before this exercise —
  `verified-claims.md` line 54, `Authentication_RequestFromNonPremiumTenantOrB2CTenant`.

- **Gallery-app SAML SSO (Salesforce) — succeeds cleanly on Free.** Portal save succeeded
  (Recalled — screenshots), confirmed at the object level (Captured) via the servicePrincipal:
  `preferredSingleSignOnMode: "saml"`, real reply URLs, a live auto-generated signing certificate.
  No license refusal anywhere in the flow. `evidence/gallery-app-saml-sso-configured-live-20260902T2120Z.json`.
- **Gallery-app SCIM provisioning (Salesforce) — no license gate found, but genuinely untested
  past "Test connection."** The admin-credentials form appears with no upsell; "Test connection"
  with junk credentials returns Salesforce's own `InvalidCredentials`, not an Entra refusal.
  `GET .../synchronization/jobs` confirms no job object was created — this lab has no real
  Salesforce tenant to push past that step, so whether Free blocks provisioning further downstream
  is an open question, not a result. `evidence/gallery-app-scim-provisioning-attempt-20260902T2116Z.json`.

- **Non-gallery (custom) SAML SSO — also succeeds cleanly on Free, closing the original gap.**
  Same outcome as the gallery app: portal save succeeded, and the resulting servicePrincipal
  confirms `preferredSingleSignOnMode: "saml"` with a live signing certificate, tagged
  `WindowsAzureActiveDirectoryCustomSingleSignOnApplication` to mark it custom rather than
  gallery-templated. `evidence/nongallery-app-saml-and-scim-attempt-20260902T2132Z.json`.
- **Non-gallery SCIM provisioning setup — same "no gate, no real backend" outcome as gallery.**
  Generic "Bearer authentication" connector form appears with no upsell; junk credentials fail
  with `CredentialValidationUnavailable` (a real network attempt against the fake endpoint), not a
  licensing refusal.

**This closes CURRICULUM.md's step 3 gap.** The original Recalled note ("SAML SSO for non-gallery
apps... requires P1") is now directly tested and does not hold, at least through app setup and
SSO configuration — retracted on the record here and in `verified-claims.md`/`CARRYOVER.md`, not
quietly revised.

## Not yet captured

- The licensing recommendation write-up (CURRICULUM step 4) — depends on the above; next.
