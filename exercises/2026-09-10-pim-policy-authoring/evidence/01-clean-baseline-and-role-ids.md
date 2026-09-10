# Exchange Administrator and Teams Administrator hold no eligible or active assignment

Command: `GET https://graph.microsoft.com/v1.0/roleManagement/directory/roleDefinitions?$filter=displayName eq 'Exchange Administrator'`
Command: `GET https://graph.microsoft.com/v1.0/roleManagement/directory/roleDefinitions?$filter=displayName eq 'Teams Administrator'`
Command: `GET https://graph.microsoft.com/v1.0/roleManagement/directory/roleEligibilityScheduleInstances?$filter=roleDefinitionId eq '<roleId>'` (run once per role id below)
Command: `GET https://graph.microsoft.com/v1.0/roleManagement/directory/roleAssignmentScheduleInstances?$filter=roleDefinitionId eq '<roleId>'` (run once per role id below)
Host: Graph Explorer, tenant
Timestamp: 2026-09-10, UTC date only — exact time not captured, no host `date -u` paired with this
Graph read

Exchange Administrator: `id` and `templateId` both `29232cdf-9323-42fd-ade2-1d097af3e4de`. `isBuiltIn`
true, `isEnabled` true. `inheritsPermissionsFrom` names `88d8e3e3-8f55-4a1e-953a-9b9898b8876b` — a
different role, not the target of this exercise. See Corrections in the evidence log for a
substitution mixup this caused.

Teams Administrator: `id` and `templateId` both `69091246-20e8-4a56-aa4d-066075b2a7a8`. `isBuiltIn`
true, `isEnabled` true. Same `inheritsPermissionsFrom` value as above.

`roleEligibilityScheduleInstances` filtered on each role's own id returns `"value": []`.
`roleAssignmentScheduleInstances` filtered on each role's own id returns `"value": []`. Neither role
has an eligible or active assignment, PIM-governed or standing, for any principal, in either
direction. Both roles start from a clean slate for this exercise.
