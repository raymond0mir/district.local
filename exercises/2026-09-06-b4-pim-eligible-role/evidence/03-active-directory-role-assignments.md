# Active Entra directory role assignments, before PIM

**Redaction.** The Global Administrator principal's `displayName`, `mailNickname`,
`userPrincipalName`, and `identities` values are replaced with `[REDACTED]`. The account is the
break-glass account created and renamed in `exercises/2026-09-03-breakglass-rotation`. The same
redaction convention is applied there. Object GUIDs are kept. Nothing else is altered.

Command: `GET https://graph.microsoft.com/beta/roleManagement/directory/roleAssignments?$expand=principal`
Host: Graph Explorer, tenant, signed in as the native Global Administrator
Timestamp: 2026-09-06, same session as `01-preflight-and-dc01-standing-state.md`

```json
{
    "@odata.context": "https://graph.microsoft.com/beta/$metadata#roleManagement/directory/roleAssignments(principal())",
    "value": [
        {
            "id": "lAPpYvVpN0KRkAEhdxReEOMTpGz_BgRHqzYTSLtzh8g-1",
            "principalId": "6ca413e3-06ff-4704-ab36-1348bb7387c8",
            "principalOrganizationId": "e0b13496-83d1-4721-8bf9-f965f676106f",
            "resourceScope": "/",
            "directoryScopeId": "/",
            "roleDefinitionId": "62e90394-69f5-4237-9190-012177145e10",
            "principal": {
                "@odata.type": "#microsoft.graph.user",
                "id": "6ca413e3-06ff-4704-ab36-1348bb7387c8",
                "accountEnabled": true,
                "createdDateTime": "2026-09-03T14:53:20Z",
                "displayName": "[REDACTED]",
                "mailNickname": "[REDACTED]",
                "onPremisesDistinguishedName": null,
                "onPremisesDomainName": null,
                "onPremisesImmutableId": null,
                "onPremisesLastSyncDateTime": null,
                "onPremisesObjectIdentifier": null,
                "onPremisesSecurityIdentifier": null,
                "onPremisesSamAccountName": null,
                "onPremisesSyncEnabled": null,
                "onPremisesUserPrincipalName": null,
                "refreshTokensValidFromDateTime": "2026-09-03T14:53:20Z",
                "signInSessionsValidFromDateTime": "2026-09-03T14:53:20Z",
                "userPrincipalName": "[REDACTED]@raytakosharkygmail.onmicrosoft.com",
                "userType": "Member",
                "assignedLicenses": [],
                "assignedPlans": [],
                "identities": [
                    {
                        "signInType": "userPrincipalName",
                        "issuer": "raytakosharkygmail.onmicrosoft.com",
                        "issuerAssignedId": "[REDACTED]@raytakosharkygmail.onmicrosoft.com"
                    }
                ]
            }
        },
        {
            "id": "4-PYiFWPHkqVOpuYmLiHa2o564h0kMdLtxCF2iycDCc-1",
            "principalId": "88eb396a-9074-4bc7-b710-85da2c9c0c27",
            "principalOrganizationId": "e0b13496-83d1-4721-8bf9-f965f676106f",
            "resourceScope": "/",
            "directoryScopeId": "/",
            "roleDefinitionId": "88d8e3e3-8f55-4a1e-953a-9b9898b8876b",
            "principal": {
                "@odata.type": "#microsoft.graph.servicePrincipal",
                "id": "88eb396a-9074-4bc7-b710-85da2c9c0c27",
                "accountEnabled": true,
                "createdDateTime": "2026-09-02T21:16:12Z",
                "appDisplayName": "Microsoft.Azure.SyncFabric",
                "appId": "00000014-0000-0000-c000-000000000000",
                "appOwnerOrganizationId": "f8cdef31-a31e-4b4a-93e4-5f571e91255a",
                "displayName": "Microsoft.Azure.SyncFabric",
                "publisherName": "Microsoft Services",
                "servicePrincipalType": "Application",
                "signInAudience": "AzureADMultipleOrgs"
            }
        }
    ]
}
```

The service principal's unrelated properties are elided. The elision is marked here rather than
made silently. The two assignment rows and their principal identity fields are verbatim.

## What this shows

- The endpoint returned two active role assignments. There is no `@odata.nextLink`.
- One assignment is held by the break-glass account, `roleDefinitionId`
  `62e90394-69f5-4237-9190-012177145e10`.
- One assignment is held by the first-party service principal `Microsoft.Azure.SyncFabric`,
  `roleDefinitionId` `88d8e3e3-8f55-4a1e-953a-9b9898b8876b`.

**Correction, 2026-09-06.** An earlier version of this file named these two role definitions from
Claude's memory rather than from a capture. It called `88d8e3e3-8f55-4a1e-953a-9b9898b8876b`
"Directory Synchronization Accounts". That is contradicted by a later capture in this same
exercise: `06`'s successor read shows User Administrator `inheritsPermissionsFrom`
`88d8e3e3-8f55-4a1e-953a-9b9898b8876b`, and no built-in role inherits from Directory
Synchronization Accounts. Both role names are removed from this file pending a Graph read of
`roleDefinitions`. The GUIDs are Captured. The names were not.

**Resolved, 2026-09-06.** `evidence/09-role-names-verified-and-policy-located.md` captures both
names directly. `62e90394-69f5-4237-9190-012177145e10` is Global Administrator, as first stated.
`88d8e3e3-8f55-4a1e-953a-9b9898b8876b` is **Directory Readers**, not Directory Synchronization
Accounts. The service principal's assignment is a read-only directory role. The original wrong
name overstated its privilege.
- `assignedLicenses` is empty on the break-glass account.

## What this does not show

This endpoint returns active assignments only. It does not return PIM-eligible assignments.
It also does not resolve whether the tenant's original Global Administrator, a Microsoft Account,
still holds an assignment. `references/gotchas.md` records that Graph directory endpoints reject
that identity. The absence of a row for it is therefore not evidence of absence.
