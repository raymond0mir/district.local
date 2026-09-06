# The two role definitions, verified, and the policy that governs activation

## Verification of `62e90394-69f5-4237-9190-012177145e10`

Command: `GET https://graph.microsoft.com/v1.0/roleManagement/directory/roleDefinitions/62e90394-69f5-4237-9190-012177145e10?$select=id,displayName,isBuiltIn`
Host: Graph Explorer, tenant
Timestamp: 2026-09-06, same session

```json
{
    "id": "62e90394-69f5-4237-9190-012177145e10",
    "displayName": "Global Administrator",
    "isBuiltIn": true,
    "inheritsPermissionsFrom": [
        { "id": "88d8e3e3-8f55-4a1e-953a-9b9898b8876b" }
    ]
}
```

## Verification of `88d8e3e3-8f55-4a1e-953a-9b9898b8876b`

Command: `GET https://graph.microsoft.com/v1.0/roleManagement/directory/roleDefinitions/88d8e3e3-8f55-4a1e-953a-9b9898b8876b?$select=id,displayName,isBuiltIn`
Host: Graph Explorer, tenant
Timestamp: 2026-09-06, same session

```json
{
    "id": "88d8e3e3-8f55-4a1e-953a-9b9898b8876b",
    "displayName": "Directory Readers",
    "isBuiltIn": true,
    "inheritsPermissionsFrom": []
}
```

Both responses are reformatted to drop the `@odata.context` lines. No value is altered.

## Resolution of the correction in `evidence/03`

- `62e90394-69f5-4237-9190-012177145e10` is Global Administrator. Claude's memory was correct.
  It is now Captured rather than asserted.
- `88d8e3e3-8f55-4a1e-953a-9b9898b8876b` is **Directory Readers**, not Directory Synchronization
  Accounts. Claude's memory was wrong. The corrected name is Captured.
- Consequence for `evidence/03`: the second active role assignment in the tenant grants
  **Directory Readers** to the first-party service principal `Microsoft.Azure.SyncFabric`. That
  is a read-only directory role, not a synchronisation role. The earlier wrong name overstated
  that assignment's privilege.

## The policy that governs User Administrator at tenant scope

Command: `GET https://graph.microsoft.com/v1.0/policies/roleManagementPolicyAssignments?$filter=scopeId eq '/' and scopeType eq 'DirectoryRole' and roleDefinitionId eq 'fe930be7-5e62-47db-91af-98c3a49a38b1'&$expand=policy`
Host: Graph Explorer, tenant
Timestamp: 2026-09-06, same session

```json
{
    "value": [
        {
            "id": "DirectoryRole_e0b13496-83d1-4721-8bf9-f965f676106f_6710deb2-862a-4457-95cb-a7b2dd297ca0_fe930be7-5e62-47db-91af-98c3a49a38b1",
            "policyId": "DirectoryRole_e0b13496-83d1-4721-8bf9-f965f676106f_6710deb2-862a-4457-95cb-a7b2dd297ca0",
            "scopeId": "/",
            "scopeType": "DirectoryRole",
            "roleDefinitionId": "fe930be7-5e62-47db-91af-98c3a49a38b1",
            "policy": {
                "id": "DirectoryRole_e0b13496-83d1-4721-8bf9-f965f676106f_6710deb2-862a-4457-95cb-a7b2dd297ca0",
                "displayName": "DirectoryRole",
                "description": "DirectoryRole",
                "isOrganizationDefault": false,
                "scopeId": "/",
                "scopeType": "DirectoryRole",
                "lastModifiedDateTime": null,
                "lastModifiedBy": {
                    "displayName": null,
                    "id": null
                }
            }
        }
    ]
}
```

`lastModifiedDateTime` is null and `lastModifiedBy` is empty. The policy has never been edited.
Whatever its rules contain is the platform default, not a prior choice made in this tenant.

The `$filter` here combined three clauses with `and` and was accepted. `evidence/08` records that
the same endpoint family rejects `or`. The limitation is the operator, not the use of `$filter`.
