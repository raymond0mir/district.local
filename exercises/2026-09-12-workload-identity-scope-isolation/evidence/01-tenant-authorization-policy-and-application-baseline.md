# Tenant authorization policy, and the application baseline before C3

Two read-only Graph calls, bracketed by `date -u` on the Mac Mini.

```
Bracket open:  Sat Sep 12 16:29:11 UTC 2026   (date -u, Mac Mini)
Bracket close: Sat Sep 12 16:30:50 UTC 2026   (date -u, Mac Mini)
```

**Signing identity: the native Global Administrator, `6ca413e3-06ff-4704-ab36-1348bb7387c8`.**
~~Not recorded at capture time.~~ **Corrected 2026-09-12, same session.** The account chip was not
read before the queries ran, so the identity was Recalled when this file was written. It is now
Captured from the access token that was already in force at the time: issued 16:25:16Z, before both
queries, carrying that `oid` and the Global Administrator role template id in `wids`. See
`evidence/03-graph-explorer-token-decoded.md`.

---

## Capture 1

```
Command: GET https://graph.microsoft.com/v1.0/policies/authorizationPolicy
Host:    Graph Explorer, browser on the Mac Mini
UTC:     between 2026-09-12T16:29:11Z and 2026-09-12T16:30:50Z
```

```json
{
    "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#policies/authorizationPolicy/$entity",
    "id": "authorizationPolicy",
    "allowInvitesFrom": "everyone",
    "allowedToSignUpEmailBasedSubscriptions": true,
    "allowedToUseSSPR": true,
    "allowEmailVerifiedUsersToJoinOrganization": true,
    "allowUserConsentForRiskyApps": null,
    "blockMsolPowerShell": false,
    "displayName": "Authorization Policy",
    "description": "Used to manage authorization related settings across the company.",
    "guestUserRoleId": "10dae51f-b6af-4016-8d66-8c2a99b929b3",
    "defaultUserRolePermissions": {
        "allowedToCreateApps": true,
        "allowedToCreateSecurityGroups": true,
        "allowedToCreateTenants": true,
        "allowedToReadBitlockerKeysForOwnedDevice": true,
        "allowedToReadOtherUsers": true,
        "permissionGrantPoliciesAssigned": [
            "ManagePermissionGrantsForSelf.microsoft-user-default-recommended",
            "ManagePermissionGrantsForSelf.microsoft-user-default-allow-consent-apps",
            "ManagePermissionGrantsForOwnedResource.microsoft-dynamically-managed-permissions-for-team",
            "ManagePermissionGrantsForOwnedResource.microsoft-dynamically-managed-permissions-for-chat"
        ]
    }
}
```

No exit code applies. Graph Explorer returned the body without error.

## Capture 2

```
Command: GET https://graph.microsoft.com/v1.0/applications?$select=id,appId,displayName,signInAudience,createdDateTime
Host:    Graph Explorer, browser on the Mac Mini
UTC:     between 2026-09-12T16:29:11Z and 2026-09-12T16:30:50Z
```

```json
{
    "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#applications(id,appId,displayName,signInAudience,createdDateTime)",
    "value": [
        {
            "id": "1ff624a7-588a-43e4-a308-981e07238012",
            "appId": "16956e9c-5e2a-4e24-8b9b-476b86e52c16",
            "displayName": "A3-nongallery-test",
            "signInAudience": "AzureADMyOrg",
            "createdDateTime": "2026-09-02T21:31:42Z"
        },
        {
            "id": "2c0ccf62-d781-449f-a32c-5eb0976db760",
            "appId": "004ad450-5909-445f-969a-d3798ab41880",
            "displayName": "P2P Server",
            "signInAudience": "AzureADMyOrg",
            "createdDateTime": "2026-09-04T00:35:35Z"
        },
        {
            "id": "4594847b-d92e-453c-9699-f2042c8eb7a0",
            "appId": "c1f11389-d107-4472-a2c5-bfa98a6d50b2",
            "displayName": "Salesforce",
            "signInAudience": "AzureADMyOrg",
            "createdDateTime": "2026-09-02T21:15:21Z"
        },
        {
            "id": "5b79b5db-8138-441d-9782-3e123ab56c8c",
            "appId": "2c5b458f-0270-4e2c-93c3-c95f56ff13df",
            "displayName": "ConnectSyncProvisioning_ENTRACONNECT01_adc55fdcf513",
            "signInAudience": "AzureADMyOrg",
            "createdDateTime": "2026-09-01T17:45:14Z"
        }
    ]
}
```

---

## What these two captures establish

- **`Lab-AI-Agent-CLI` does not exist.** Four application registrations exist, and none carries that
  name. This is the teardown checklist for the exercise.
- **Any member account in this tenant can register an application.** `allowedToCreateApps` is
  `true`. A workload identity in `district.local` does not require an administrator to create it.
- **Any member account can create a tenant.** `allowedToCreateTenants` is `true`.
- **Any member account can read other users.** `allowedToReadOtherUsers` is `true`. A `GET /users`
  that succeeds proves nothing about the caller's privilege, which the negative test must account
  for.
- **User consent is not switched off.** `permissionGrantPoliciesAssigned` names two
  `ManagePermissionGrantsForSelf` policies. The exact permission set each one admits is not read
  yet, so whether `adm-jsmith` can consent to `User.Read` without an administrator is still open.
  The empirical answer arrives at the device code sign-in: `AADSTS65001` means no.
- **One application has no recorded provenance in this repository.** `P2P Server`, appId
  `004ad450-5909-445f-969a-d3798ab41880`, created 2026-09-04T00:35:35Z. No exercise in
  `exercises/` records creating it. Provenance is not captured. Do not assume it is a Microsoft
  first-party object; that claim is Recalled.
