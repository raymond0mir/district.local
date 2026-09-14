# P2P Server is a tenant-local registration, and it appeared three seconds after a device join

Command: GET https://graph.microsoft.com/v1.0/servicePrincipals(appId='004ad450-5909-445f-969a-d3798ab41880')?$select=id,appId,displayName,servicePrincipalType,accountEnabled,appOwnerOrganizationId,createdDateTime,tags,appRoleAssignmentRequired,servicePrincipalNames
Command: GET https://graph.microsoft.com/v1.0/applications(appId='004ad450-5909-445f-969a-d3798ab41880')?$select=id,appId,displayName,createdDateTime,signInAudience,publisherDomain
Host: Graph Explorer on the Mac Mini, signed in as the native Global Administrator (`6ca413e3`)
UTC: 2026-09-14, between 15:05Z and the session close. Exact per-call times not captured; see Not captured in `evidence-log.md`.

**Scope of this file.** It records what the two objects are and when they appeared. It does not
record what created them. That claim depends on two `directoryAudits` reads that were outstanding
when this file was written, and it is deliberately left to a later capture.

--- the service principal ---

```json
{
    "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#servicePrincipals(id,appId,displayName,servicePrincipalType,accountEnabled,appOwnerOrganizationId,createdDateTime,tags,appRoleAssignmentRequired,servicePrincipalNames)/$entity",
    "id": "505610fa-43e4-4e65-990e-364f5794827b",
    "appId": "004ad450-5909-445f-969a-d3798ab41880",
    "displayName": "P2P Server",
    "servicePrincipalType": "Application",
    "accountEnabled": true,
    "appOwnerOrganizationId": "e0b13496-83d1-4721-8bf9-f965f676106f",
    "createdDateTime": "2026-09-04T00:35:36Z",
    "tags": [],
    "appRoleAssignmentRequired": false,
    "servicePrincipalNames": [
        "004ad450-5909-445f-969a-d3798ab41880",
        "urn:p2p_cert"
    ]
}
```

--- the application object ---

```json
{
    "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#applications(id,appId,displayName,createdDateTime,signInAudience,publisherDomain)/$entity",
    "id": "2c0ccf62-d781-449f-a32c-5eb0976db760",
    "appId": "004ad450-5909-445f-969a-d3798ab41880",
    "displayName": "P2P Server",
    "createdDateTime": "2026-09-04T00:35:35Z",
    "signInAudience": "AzureADMyOrg",
    "publisherDomain": "raytakosharkygmail.onmicrosoft.com"
}
```

## What this proves

**1. The object is owned by this tenant, and the Recalled alternative is retired.** C3's baseline
recorded `P2P Server` as an application with no provenance and warned that calling it a Microsoft
first-party object was Recalled, not established. Three captured fields settle it against that
reading: `appOwnerOrganizationId` is `e0b13496-83d1-4721-8bf9-f965f676106f`, this tenant;
`publisherDomain` is this tenant's own default domain; `signInAudience` is `AzureADMyOrg`. A
Microsoft first-party service principal carries Microsoft's tenant in `appOwnerOrganizationId`. This
one does not.

**2. Both halves of the workload identity exist, one second apart.** The application object was
created at 00:35:35Z and the service principal at 00:35:36Z. This is the same two-object shape that
C3 captured for `Lab-AI-Agent-CLI`, which Raymond built by hand in the portal.

**3. It sits three seconds after VM 101's Entra join.** The device registered at
2026-09-04T00:35:33Z, Captured in
`exercises/2026-09-04-b1-conditional-access-report-only/evidence/jsmith-registered-devices-vm101-entra-join-20260904T0035Z.json`.
The application object followed at +2s and the service principal at +3s. The correlation is stated
here as a time relationship. It is not yet a causal claim.

**4. `tags` is empty.** A service principal provisioned through the application gallery or through
a consent flow normally carries at least one tag, such as
`WindowsAzureActiveDirectoryIntegratedApp`, which the C3 consent audit events showed being written
for `Lab-AI-Agent-CLI`. This object carries none.

**5. `servicePrincipalNames` holds `urn:p2p_cert`.** The value is a URN naming a certificate
identity rather than a URL or a GUID. What Microsoft uses it for is not established by this capture.

**6. A re-read eight days later returned the C3 baseline's values unchanged.** `id`, `appId`,
`displayName`, `createdDateTime` and `signInAudience` match
`exercises/2026-09-12-workload-identity-scope-isolation/evidence/01-tenant-authorization-policy-and-application-baseline.md`
exactly. The object has not been modified since it was first observed.
