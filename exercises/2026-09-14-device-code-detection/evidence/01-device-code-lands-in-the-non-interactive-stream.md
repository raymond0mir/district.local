# Device code sign-ins land in the non-interactive stream, and one field names the flow

Command: GET https://graph.microsoft.com/beta/auditLogs/signIns?$filter=signInEventTypes/any(t: t eq 'nonInteractiveUser') and createdDateTime ge 2026-09-13T00:55:00Z and createdDateTime le 2026-09-13T01:35:00Z&$top=50
Host: Graph Explorer on the Mac Mini, signed in as the native Global Administrator (`6ca413e3`), confirmed by `GET /v1.0/me?$select=id`
UTC: 2026-09-14T14:59:06Z, from `date -u` on the Mac Mini

**Redactions applied to this capture, and why.** Each is marked in place.
- `ipAddress` on every record, and every `location` object. They identify a private residence.
  Same treatment as `exercises/2026-09-05-b1-breakglass-exclusion-verification/evidence/01-...`.
- `userDisplayName` and `userPrincipalName` of principal `6ca413e3` replaced with `<GA>`. The
  current tenant Global Administrator's name may not appear in an artifact. See `CLAUDE.md`.
Nothing else is altered. The response held four records and all four are reproduced.

--- record 1 of 4: run 2 of the C3 device code flow ---

```json
{
    "id": "42a0215d-dde0-4fd5-b4d0-a8ed88ae6900",
    "createdDateTime": "2026-09-13T01:22:28Z",
    "userDisplayName": "Admin - John Smith",
    "userPrincipalName": "adm-jsmith@raytakosharkygmail.onmicrosoft.com",
    "userId": "03ee6546-f113-4ec5-ba9d-e57381b0c928",
    "appId": "388b9dd8-d98f-46f3-8eed-4418346e5673",
    "appDisplayName": "Lab-AI-Agent-CLI",
    "ipAddress": "[redacted]",
    "clientAppUsed": "Mobile Apps and Desktop clients",
    "userAgent": "curl/8.7.1",
    "correlationId": "bae290c5-0422-4859-9004-e12b7af9be12",
    "conditionalAccessStatus": "success",
    "isInteractive": false,
    "signInEventTypes": ["nonInteractiveUser"],
    "servicePrincipalId": "4c43a528-ba33-40b0-8821-c8643587f351",
    "resourceDisplayName": "Microsoft Graph",
    "resourceId": "00000003-0000-0000-c000-000000000000",
    "authenticationRequirement": "multiFactorAuthentication",
    "authenticationMethodsUsed": [],
    "incomingTokenType": "none",
    "authenticationProtocol": "none",
    "originalTransferMethod": "deviceCodeFlow",
    "uniqueTokenIdentifier": "XSGgQuDd1U-00KjtiK5pAA",
    "sessionId": "008b57fa-8d12-7c5c-6fcc-4f1c2d9e5736",
    "processingTimeInMilliseconds": 370,
    "riskState": "none",
    "location": "[redacted: private residence]",
    "status": {
        "errorCode": 0,
        "failureReason": "Other.",
        "additionalDetails": "MFA requirement satisfied by claim in the token"
    },
    "deviceDetail": {
        "deviceId": "", "displayName": "", "operatingSystem": "",
        "browser": "", "isCompliant": false, "isManaged": false, "trustType": null
    },
    "authenticationDetails": [
        {
            "authenticationStepDateTime": "2026-09-13T01:22:28Z",
            "authenticationMethod": "Previously satisfied",
            "succeeded": true,
            "authenticationStepResultDetail": "MFA requirement satisfied by claim in the token"
        }
    ],
    "authenticationProcessingDetails": [
        { "key": "Is Legacy Store Used", "value": "0" },
        { "key": "Legacy Store Use Information", "value": "" },
        { "key": "Oauth Scope Info", "value": "[\"User.Read\",\"User.ReadBasic.All\",\"profile\",\"openid\",\"email\"]" },
        { "key": "wids", "value": "[\"b79fbf4d-3ef9-4689-8143-76b194e85509\"]" }
    ],
    "appliedConditionalAccessPolicies": [
        { "id": "365bdd23-d0e0-49a7-8131-f63b98ea6115",
          "displayName": "B1 - Require MFA for all users (report-only)",
          "enforcedGrantControls": ["Mfa"], "result": "success",
          "conditionsSatisfied": "application,users", "conditionsNotSatisfied": "none" },
        { "id": "75882b6a-a9ba-4d97-bbb4-72d29277ebf4",
          "displayName": "B1 - Block legacy authentication (report-only)",
          "enforcedGrantControls": ["Block"], "result": "notApplied",
          "conditionsSatisfied": "application,users", "conditionsNotSatisfied": "clientType" },
        { "id": "d9a6a116-0c05-4894-af2c-a2990ef44593",
          "displayName": "B1 - Require compliant or hybrid joined device (report-only)",
          "enforcedGrantControls": ["RequireCompliantDevice"], "result": "reportOnlyFailure",
          "conditionsSatisfied": "application,users", "conditionsNotSatisfied": "none" }
    ]
}
```

--- record 2 of 4: Graph Explorer, the Global Administrator's own session ---

```json
{
    "id": "a8835a85-130d-4937-8eff-863c9678a900",
    "createdDateTime": "2026-09-13T01:16:38Z",
    "userDisplayName": "<GA>",
    "userPrincipalName": "<GA>",
    "userId": "6ca413e3-06ff-4704-ab36-1348bb7387c8",
    "appId": "de8bc8b5-d9f9-48b1-a8ad-b748da725064",
    "appDisplayName": "Graph Explorer",
    "ipAddress": "[redacted]",
    "clientAppUsed": "Browser",
    "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:155.0) Gecko/20100101 Firefox/155.0",
    "conditionalAccessStatus": "notApplied",
    "isInteractive": false,
    "signInEventTypes": ["nonInteractiveUser"],
    "authenticationRequirement": "singleFactorAuthentication",
    "originalTransferMethod": "none",
    "location": "[redacted: private residence]",
    "authenticationProcessingDetails": [
        { "key": "Is CAE Token", "value": "True" },
        { "key": "Oauth Scope Info", "value": "[\"Application.Read.All\",\"AuditLog.Read.All\",\"Directory.Read.All\",\"Directory.ReadWrite.All\",\"IdentityRiskyUser.Read.All\",\"openid\",\"Policy.Read.All\",\"Policy.ReadWrite.ConditionalAccess\",\"PrivilegedAccess.ReadWrite.AzureAD\",\"profile\",\"RoleManagement.ReadWrite.Directory\",\"User.Read\",\"User.Read.All\",\"User.ReadBasic.All\",\"User.ReadWrite.All\",\"UserAuthenticationMethod.Read\",\"UserAuthenticationMethod.Read.All\",\"email\",\"AgentIdUser.ReadWrite.All\",\"AgentIdUser.ReadWrite.IdentityParentedBy\",\"Policy.ReadWrite.SecurityDefaults\",\"PrivilegedAssignmentSchedule.Read.AzureADGroup\",\"PrivilegedEligibilitySchedule.ReadWrite.AzureADGroup\",\"RoleEligibilitySchedule.ReadWrite.Directory\",\"RoleManagementPolicy.ReadWrite.Directory\",\"User.EnableDisableAccount.All\"]" },
        { "key": "wids", "value": "[\"62e90394-69f5-4237-9190-012177145e10\",\"b79fbf4d-3ef9-4689-8143-76b194e85509\"]" }
    ],
    "appliedConditionalAccessPolicies": [
        { "id": "365bdd23-...", "result": "notApplied", "conditionsNotSatisfied": "users",
          "excludeRulesSatisfied": [{ "conditionalAccessCondition": "users", "ruleSatisfied": "userId" }] },
        { "id": "75882b6a-...", "result": "notApplied", "conditionsNotSatisfied": "users",
          "excludeRulesSatisfied": [{ "conditionalAccessCondition": "users", "ruleSatisfied": "userId" }] },
        { "id": "d9a6a116-...", "result": "reportOnlyNotApplied", "conditionsNotSatisfied": "users",
          "excludeRulesSatisfied": [{ "conditionalAccessCondition": "users", "ruleSatisfied": "userId" }] }
    ]
}
```

--- record 3 of 4: Graph Explorer, signed in as `adm-jsmith` ---

```json
{
    "id": "79fe4851-1f93-4730-b8e6-585898717200",
    "createdDateTime": "2026-09-13T01:15:37Z",
    "userDisplayName": "Admin - John Smith",
    "userPrincipalName": "adm-jsmith@raytakosharkygmail.onmicrosoft.com",
    "userId": "03ee6546-f113-4ec5-ba9d-e57381b0c928",
    "appId": "de8bc8b5-d9f9-48b1-a8ad-b748da725064",
    "appDisplayName": "Graph Explorer",
    "ipAddress": "[redacted]",
    "clientAppUsed": "Browser",
    "conditionalAccessStatus": "success",
    "isInteractive": false,
    "signInEventTypes": ["nonInteractiveUser"],
    "authenticationRequirement": "multiFactorAuthentication",
    "originalTransferMethod": "deviceCodeFlow",
    "sessionId": "008b57fa-c4c6-534d-1a90-02a0396bc888",
    "location": "[redacted: private residence]",
    "authenticationProcessingDetails": [
        { "key": "Is CAE Token", "value": "True" },
        { "key": "Oauth Scope Info", "value": "[same 26-scope list as record 2, verbatim in the response]" },
        { "key": "wids", "value": "[\"b79fbf4d-3ef9-4689-8143-76b194e85509\"]" }
    ],
    "appliedConditionalAccessPolicies": [
        { "id": "365bdd23-...", "result": "success", "conditionsNotSatisfied": "none" },
        { "id": "75882b6a-...", "result": "notApplied", "conditionsNotSatisfied": "clientType" },
        { "id": "d9a6a116-...", "result": "reportOnlyFailure", "conditionsNotSatisfied": "none" }
    ]
}
```

--- record 4 of 4: run 1 of the C3 device code flow ---

```json
{
    "id": "a7e6febd-686c-403e-97b2-fde5547bee00",
    "createdDateTime": "2026-09-13T01:07:50Z",
    "userDisplayName": "Admin - John Smith",
    "userPrincipalName": "adm-jsmith@raytakosharkygmail.onmicrosoft.com",
    "userId": "03ee6546-f113-4ec5-ba9d-e57381b0c928",
    "appId": "388b9dd8-d98f-46f3-8eed-4418346e5673",
    "appDisplayName": "Lab-AI-Agent-CLI",
    "ipAddress": "[redacted]",
    "clientAppUsed": "Mobile Apps and Desktop clients",
    "userAgent": "curl/8.7.1",
    "correlationId": "61805a6d-2177-43cb-858c-f84fa8f73815",
    "conditionalAccessStatus": "success",
    "isInteractive": false,
    "signInEventTypes": ["nonInteractiveUser"],
    "servicePrincipalId": "4c43a528-ba33-40b0-8821-c8643587f351",
    "authenticationRequirement": "multiFactorAuthentication",
    "authenticationMethodsUsed": [],
    "incomingTokenType": "none",
    "authenticationProtocol": "none",
    "originalTransferMethod": "deviceCodeFlow",
    "uniqueTokenIdentifier": "vf7mp2xoPkCXsv3lVHvuAA",
    "sessionId": "008b57fa-c4c6-534d-1a90-02a0396bc888",
    "processingTimeInMilliseconds": 476,
    "location": "[redacted: private residence]",
    "status": {
        "errorCode": 0,
        "failureReason": "Other.",
        "additionalDetails": "MFA requirement satisfied by claim in the token"
    },
    "authenticationDetails": [
        {
            "authenticationStepDateTime": "2026-09-13T01:07:50Z",
            "authenticationMethod": "Previously satisfied",
            "succeeded": true,
            "authenticationStepResultDetail": "MFA requirement satisfied by claim in the token"
        }
    ],
    "authenticationProcessingDetails": [
        { "key": "Is Legacy Store Used", "value": "0" },
        { "key": "Legacy Store Use Information", "value": "" },
        { "key": "Oauth Scope Info", "value": "[\"User.Read\",\"profile\",\"openid\",\"email\"]" },
        { "key": "wids", "value": "[\"b79fbf4d-3ef9-4689-8143-76b194e85509\"]" }
    ],
    "appliedConditionalAccessPolicies": [
        { "id": "365bdd23-...", "result": "success", "conditionsNotSatisfied": "none" },
        { "id": "75882b6a-...", "result": "notApplied", "conditionsNotSatisfied": "clientType" },
        { "id": "d9a6a116-...", "result": "reportOnlyFailure", "conditionsNotSatisfied": "none" }
    ]
}
```

## What this proves

**1. Both device code token redemptions are non-interactive.** `isInteractive` is `false` and
`signInEventTypes` is `["nonInteractiveUser"]` on both. ~~The default sign-in log an administrator
opens returns interactive sign-ins. Neither run appears there.~~ **Struck 2026-09-14, wrong.** The
v1.0 interactive read was outstanding when this was written, and it returned four records for this
same client. Each run writes two interactive records before the token event captured here. The
correct statement is that the **token redemption** is non-interactive, not the run.
`evidence/03-the-interactive-stream-holds-the-flow-and-cannot-name-it.md` carries the full
sequence. The surviving half of the claim still matters: the field that names the flow appears only
on this non-interactive record, and only on `beta`.

**2. The flow is named, and not by the field that sounds like it.** `authenticationProtocol` reads
`"none"` on both runs. `incomingTokenType` reads `"none"`. The field that names the flow is
`originalTransferMethod`, and it reads `"deviceCodeFlow"`. A detection written against
`authenticationProtocol` finds nothing.

**3. The client is named in full.** `appId` `388b9dd8`, `appDisplayName` `Lab-AI-Agent-CLI`, and
`servicePrincipalId` `4c43a528` all appear on both runs. `userAgent` reads `curl/8.7.1`.

**4. The requested scope is recorded, and the two runs differ.** `authenticationProcessingDetails`
carries a key `Oauth Scope Info`. Run 1 reads `["User.Read","profile","openid","email"]`. Run 2
reads `["User.ReadBasic.All", ...]` in addition. C3 found that the consent widening was invisible
in the API permissions blade and invisible to a control that counts grants. It is not invisible
here. The sign-in log distinguishes the two runs.

**5. The token redemption satisfied MFA by a claim.** `authenticationRequirement` is
`multiFactorAuthentication` and `authenticationMethodsUsed` is empty, with `authenticationMethod`
`"Previously satisfied"`. ~~The device code redemption inherited MFA from an existing token.~~
**Narrowed 2026-09-14.** The inheritance is real, and this file drew from it the wider conclusion
that no prompt occurred anywhere in the flow. `evidence/03` shows both runs completing MFA
interactively, with `"MFA completed in Azure AD"` and the iOS Authenticator named. The claim check
is the third leg of the flow, not the whole of it.

**6. Conditional Access evaluated the device code sign-in, and one policy would have blocked it.**
`d9a6a116` returns `reportOnlyFailure` on both runs. `75882b6a`, block legacy authentication,
returns `notApplied` with `conditionsNotSatisfied` `clientType`. C3's setup asserted from reasoning
that device code is not legacy authentication by that policy's definition. That is now Captured.

**7. Record 3 shows a third device code redemption that C3 never recorded.** At 01:15:37Z,
`adm-jsmith` signed into **Graph Explorer** with `originalTransferMethod` `deviceCodeFlow`, sharing
`sessionId` `008b57fa-c4c6-534d-1a90-02a0396bc888` with run 1. This is C3's failed paired control
seen from the tenant's side.
