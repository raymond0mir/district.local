# One amended consent writes three audit events, and the event named "Consent to application" hides the change

Command: GET https://graph.microsoft.com/v1.0/auditLogs/directoryAudits?$filter=activityDateTime ge 2026-09-13T00:55:00Z and activityDateTime le 2026-09-13T01:35:00Z&$top=50
Host: Graph Explorer on the Mac Mini, signed in as the native Global Administrator (`6ca413e3`)
UTC: 2026-09-14T14:59:06Z, from `date -u` on the Mac Mini

**Redactions applied.** `initiatedBy.user.ipAddress` values are kept, because they are Microsoft
service addresses and not the operator's. One `StrongAuthenticationPhoneAppDetail` value held an
Apple push notification device token for a personal handset and a `User.PUID`; both are replaced and
marked. Nothing else is altered. The response held seven records and all seven are accounted for.

## Run 2, 2026-09-13T01:22:12Z — three events, one correlationId `07436f62-c179-427f-a8ae-9055d22ef754`

Ordered as the response returned them, newest first. Note the elapsed time across all three: 13 ms.

```json
{
    "activityDisplayName": "Consent to application",
    "activityDateTime": "2026-09-13T01:22:12.5603524Z",
    "category": "ApplicationManagement",
    "operationType": "Assign",
    "loggedByService": "Core Directory",
    "result": "success",
    "initiatedBy": { "app": null, "user": {
        "id": "03ee6546-f113-4ec5-ba9d-e57381b0c928",
        "displayName": "Azure ESTS Service",
        "userPrincipalName": "adm-jsmith@raytakosharkygmail.onmicrosoft.com",
        "ipAddress": "4.151.103.193", "userType": null } },
    "targetResources": [ {
        "id": "4c43a528-ba33-40b0-8821-c8643587f351",
        "displayName": "Lab-AI-Agent-CLI",
        "type": "ServicePrincipal",
        "modifiedProperties": [
            { "displayName": "ConsentContext.IsAdminConsent", "oldValue": null, "newValue": "\"False\"" },
            { "displayName": "ConsentContext.IsAppOnly", "oldValue": null, "newValue": "\"False\"" },
            { "displayName": "ConsentContext.OnBehalfOfAll", "oldValue": null, "newValue": "\"False\"" },
            { "displayName": "ConsentContext.Tags", "oldValue": null, "newValue": "\"WindowsAzureActiveDirectoryIntegratedApp\"" },
            { "displayName": "ConsentAction.Permissions", "oldValue": null,
              "newValue": "\"[[Id: KKVDTDO6sECIIchkNYfzUb47HpG_M1xKif_yoJNjuqpGZe4DE_HFTrqd5XOBsMko, ClientId: 4c43a528-ba33-40b0-8821-c8643587f351, PrincipalId: 03ee6546-f113-4ec5-ba9d-e57381b0c928, ResourceId: 911e3bbe-33bf-4a5c-89ff-f2a09363baaa, ConsentType: Principal, Scope:  User.Read, CreatedDateTime: , LastModifiedDateTime ]] => [[Id: KKVDTDO6sECIIchkNYfzUb47HpG_M1xKif_yoJNjuqpGZe4DE_HFTrqd5XOBsMko, ClientId: 4c43a528-ba33-40b0-8821-c8643587f351, PrincipalId: 03ee6546-f113-4ec5-ba9d-e57381b0c928, ResourceId: 911e3bbe-33bf-4a5c-89ff-f2a09363baaa, ConsentType: Principal, Scope:  User.Read, CreatedDateTime: , LastModifiedDateTime ]]; \"" }
        ] } ],
    "additionalDetails": [
        { "key": "User-Agent", "value": "EvoSTS" },
        { "key": "AppId", "value": "388b9dd8-d98f-46f3-8eed-4418346e5673" } ]
}
```

```json
{
    "activityDisplayName": "Remove delegated permission grant",
    "activityDateTime": "2026-09-13T01:22:12.54935Z",
    "operationType": "Unassign",
    "loggedByService": "Core Directory",
    "result": "success",
    "initiatedBy": { "user": {
        "id": "03ee6546-f113-4ec5-ba9d-e57381b0c928",
        "displayName": "Azure ESTS Service",
        "userPrincipalName": "adm-jsmith@raytakosharkygmail.onmicrosoft.com",
        "ipAddress": "4.151.103.193" } },
    "targetResources": [ {
        "id": "911e3bbe-33bf-4a5c-89ff-f2a09363baaa",
        "displayName": "Microsoft Graph",
        "type": "ServicePrincipal",
        "modifiedProperties": [
            { "displayName": "DelegatedPermissionGrant.Scope",
              "oldValue": "\" User.Read\"", "newValue": "\" User.Read User.ReadBasic.All\"" },
            { "displayName": "DelegatedPermissionGrant.ConsentType",
              "oldValue": "\"Principal\"", "newValue": "\"Principal\"" },
            { "displayName": "DelegatedPermissionGrant.PrincipalId",
              "oldValue": "\"03ee6546-f113-4ec5-ba9d-e57381b0c928\"",
              "newValue": "\"03ee6546-f113-4ec5-ba9d-e57381b0c928\"" },
            { "displayName": "ServicePrincipal.ObjectID", "oldValue": null,
              "newValue": "\"4c43a528-ba33-40b0-8821-c8643587f351\"" }
        ] } ],
    "additionalDetails": [ { "key": "AppId", "value": "00000003-0000-0000-c000-000000000000" } ]
}
```

```json
{
    "activityDisplayName": "Add delegated permission grant",
    "activityDateTime": "2026-09-13T01:22:12.5473486Z",
    "operationType": "Assign",
    "loggedByService": "Core Directory",
    "result": "success",
    "initiatedBy": { "user": {
        "id": "03ee6546-f113-4ec5-ba9d-e57381b0c928",
        "displayName": "Azure ESTS Service",
        "userPrincipalName": "adm-jsmith@raytakosharkygmail.onmicrosoft.com",
        "ipAddress": "4.151.103.193" } },
    "targetResources": [ {
        "id": "911e3bbe-33bf-4a5c-89ff-f2a09363baaa",
        "displayName": "Microsoft Graph",
        "type": "ServicePrincipal",
        "modifiedProperties": [
            { "displayName": "DelegatedPermissionGrant.Scope",
              "oldValue": "\" User.Read\"", "newValue": "\" User.Read User.ReadBasic.All\"" },
            { "displayName": "DelegatedPermissionGrant.ConsentType",
              "oldValue": "\"Principal\"", "newValue": "\"Principal\"" },
            { "displayName": "ServicePrincipal.ObjectID", "oldValue": null,
              "newValue": "\"4c43a528-ba33-40b0-8821-c8643587f351\"" }
        ] } ],
    "additionalDetails": [ { "key": "AppId", "value": "00000003-0000-0000-c000-000000000000" } ]
}
```

## Run 1, 2026-09-13T01:07:44Z — three events, one correlationId `f869a98c-e040-48a1-9083-bf699a9e8a25`

```json
{
    "activityDisplayName": "Consent to application",
    "activityDateTime": "2026-09-13T01:07:44.7957825Z",
    "operationType": "Assign",
    "initiatedBy": { "user": {
        "id": "03ee6546-f113-4ec5-ba9d-e57381b0c928",
        "displayName": "Azure ESTS Service",
        "userPrincipalName": "adm-jsmith@raytakosharkygmail.onmicrosoft.com",
        "ipAddress": "4.149.22.36" } },
    "targetResources": [ {
        "id": "4c43a528-ba33-40b0-8821-c8643587f351",
        "displayName": "Lab-AI-Agent-CLI",
        "type": "ServicePrincipal",
        "modifiedProperties": [
            { "displayName": "ConsentAction.Permissions", "oldValue": null,
              "newValue": "\"[] => [[Id: KKVDTDO6sECIIchkNYfzUb47HpG_M1xKif_yoJNjuqpGZe4DE_HFTrqd5XOBsMko, ClientId: 4c43a528-ba33-40b0-8821-c8643587f351, PrincipalId: 03ee6546-f113-4ec5-ba9d-e57381b0c928, ResourceId: 911e3bbe-33bf-4a5c-89ff-f2a09363baaa, ConsentType: Principal, Scope:  User.Read, CreatedDateTime: , LastModifiedDateTime ]]; \"" }
        ] } ]
}
```

```json
{
    "activityDisplayName": "Add app role assignment grant to user",
    "activityDateTime": "2026-09-13T01:07:44.7947858Z",
    "category": "UserManagement",
    "operationType": "Assign",
    "targetResources": [ {
        "id": "4c43a528-ba33-40b0-8821-c8643587f351",
        "displayName": "Lab-AI-Agent-CLI",
        "type": "ServicePrincipal",
        "modifiedProperties": [
            { "displayName": "AppRole.Id", "oldValue": null, "newValue": "\"00000000-0000-0000-0000-000000000000\"" },
            { "displayName": "AppRole.Value", "oldValue": null, "newValue": "\"\"" },
            { "displayName": "AppRoleAssignment.CreatedDateTime", "oldValue": null, "newValue": "\"2026-09-13T01:07:44.6477758Z\"" },
            { "displayName": "User.ObjectID", "oldValue": null, "newValue": "\"03ee6546-f113-4ec5-ba9d-e57381b0c928\"" },
            { "displayName": "User.PUID", "oldValue": null, "newValue": "[redacted: personal identifier]" }
        ] } ]
}
```

```json
{
    "activityDisplayName": "Add delegated permission grant",
    "activityDateTime": "2026-09-13T01:07:44.6367747Z",
    "operationType": "Assign",
    "targetResources": [ {
        "id": "911e3bbe-33bf-4a5c-89ff-f2a09363baaa",
        "displayName": "Microsoft Graph",
        "type": "ServicePrincipal",
        "modifiedProperties": [
            { "displayName": "DelegatedPermissionGrant.Scope", "oldValue": null, "newValue": "\" User.Read\"" },
            { "displayName": "DelegatedPermissionGrant.ConsentType", "oldValue": null, "newValue": "\"Principal\"" }
        ] } ]
}
```

## The seventh record, 2026-09-13T01:07:39Z

```json
{
    "activityDisplayName": "Update user",
    "activityDateTime": "2026-09-13T01:07:39.3747702Z",
    "category": "UserManagement",
    "operationType": "Update",
    "initiatedBy": { "user": null, "app": {
        "appId": null, "displayName": "Azure MFA StrongAuthenticationService",
        "servicePrincipalId": "ba2b121f-6a40-4e56-8a19-f0b97cf4619e" } },
    "targetResources": [ {
        "id": "03ee6546-f113-4ec5-ba9d-e57381b0c928",
        "type": "User",
        "userPrincipalName": "adm-jsmith@raytakosharkygmail.onmicrosoft.com",
        "modifiedProperties": [
            { "displayName": "StrongAuthenticationPhoneAppDetail",
              "oldValue": "[redacted: holds an Apple push token for a personal handset; PhoneAppVersion 6.8.53, LastAuthenticatedTimestamp 2026-09-10T14:17:03Z]",
              "newValue": "[redacted: same token; PhoneAppVersion 6.8.54, LastAuthenticatedTimestamp 2026-09-13T01:07:38.8683523Z]" },
            { "displayName": "Included Updated Properties", "oldValue": null, "newValue": "\"StrongAuthenticationPhoneAppDetail\"" }
        ] } ]
}
```

## What this proves

**1. One amended consent writes three audit events, not one and not two.** C3's open question
predicted two. The answer is three, inside 13 milliseconds, under one `correlationId`.

**2. The event a human would read is the one that hides the change.** `Consent to application`
carries `ConsentAction.Permissions` with `Scope:  User.Read` on **both sides** of its `=>`. Read
that event alone and nothing changed. The two events that do carry the change are named
`Add delegated permission grant` and `Remove delegated permission grant`, and both record
`DelegatedPermissionGrant.Scope` moving from `" User.Read"` to `" User.Read User.ReadBasic.All"`.

**3. The same event type reports correctly on a first consent and incorrectly on an amendment.**
Run 1's `Consent to application` reads `"[] => [[... Scope:  User.Read ...]]"`, which is accurate.
Run 2's reads `User.Read => User.Read`, which is not. The defect is specific to amending an
existing grant, which is the case C3 proved an administrator cannot see elsewhere either.

**4. An `Unassign` operation recorded an addition.** `Remove delegated permission grant` carries
`operationType` `Unassign` and an `oldValue`/`newValue` pair identical to the `Assign` event beside
it: the scope grows in both. Nothing was removed. A rule that treats `Unassign` as a revocation
misreads this event.

**5. `initiatedBy` names a Microsoft service as the actor and carries the human's identity
underneath it.** `displayName` reads `Azure ESTS Service` on all six consent events, while `id` and
`userPrincipalName` name `adm-jsmith`. `ipAddress` reads `4.151.103.193` and `4.149.22.36`, which
are Microsoft addresses, not the operator's. The standing rule in `references/gotchas.md` says to
read a null `ipAddress` as the signal of a platform-initiated entry. That signal does not fire here:
the address is populated, and it is still not the actor's.

**6. Correlating the audit event to the human's real source requires the sign-in log.** The audit
events carry a Microsoft address. `evidence/01` carries the operator's address for the same two
runs. The join is `userId` plus the time window, because the `correlationId` values differ between
the two surfaces.
