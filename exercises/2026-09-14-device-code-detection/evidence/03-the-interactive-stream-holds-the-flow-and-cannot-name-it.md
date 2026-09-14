# The interactive stream holds four device code records, and none of them names the flow

Command: GET https://graph.microsoft.com/v1.0/auditLogs/signIns?$filter=createdDateTime ge 2026-09-13T00:55:00Z and createdDateTime le 2026-09-13T01:35:00Z&$top=50
Host: Graph Explorer on the Mac Mini, signed in as the native Global Administrator (`6ca413e3`)
UTC: 2026-09-14T15:05:51Z, from `date -u` on the Mac Mini

**This capture disproves a claim made in `evidence/01` of this same exercise.** See Corrections in
`evidence-log.md`. The claim was written before this read was returned.

**Redactions applied.** `ipAddress` and every `location` object, as a private residence.
`userDisplayName` and `userPrincipalName` of principal `6ca413e3` replaced with `<GA>`. Nothing else
is altered. The response held eight records and all eight are accounted for below.

## The four `Lab-AI-Agent-CLI` records, appId `388b9dd8-d98f-46f3-8eed-4418346e5673`

```json
{
    "id": "0287d5cf-0a1b-46aa-996f-27eab31eeb00",
    "createdDateTime": "2026-09-13T01:07:40Z",
    "userId": "03ee6546-f113-4ec5-ba9d-e57381b0c928",
    "appDisplayName": "Lab-AI-Agent-CLI",
    "correlationId": "61805a6d-2177-43cb-858c-f84fa8f73815",
    "isInteractive": true,
    "clientAppUsed": "Mobile Apps and Desktop clients",
    "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:155.0) Gecko/20100101 Firefox/155.0",
    "conditionalAccessStatus": "success",
    "ipAddress": "[redacted]",
    "location": "[redacted: private residence]",
    "servicePrincipalId": "4c43a528-ba33-40b0-8821-c8643587f351",
    "status": {
        "errorCode": 65001,
        "failureReason": "The user or administrator has not consented to use the application with ID '{identifier}'{namePhrase}. Send an interactive authorization request for this user and resource.",
        "additionalDetails": "MFA completed in Azure AD"
    },
    "authenticationAppDeviceDetails": {
        "deviceId": "", "operatingSystem": "Ios", "clientApp": "Authenticator", "appVersion": "6.8.54"
    },
    "appliedConditionalAccessPolicies": [
        { "id": "365bdd23-...", "result": "success" },
        { "id": "75882b6a-...", "result": "notApplied" },
        { "id": "d9a6a116-...", "result": "reportOnlyFailure" }
    ]
}
```

```json
{
    "id": "3d325160-4f8a-4daf-8056-56e3d8cd6100",
    "createdDateTime": "2026-09-13T01:07:46Z",
    "userId": "03ee6546-f113-4ec5-ba9d-e57381b0c928",
    "appDisplayName": "Lab-AI-Agent-CLI",
    "correlationId": "61805a6d-2177-43cb-858c-f84fa8f73815",
    "isInteractive": true,
    "clientAppUsed": "Mobile Apps and Desktop clients",
    "userAgent": "Mozilla/5.0 ... Firefox/155.0",
    "conditionalAccessStatus": "success",
    "ipAddress": "[redacted]",
    "location": "[redacted: private residence]",
    "servicePrincipalId": "4c43a528-ba33-40b0-8821-c8643587f351",
    "authenticationAppDeviceDetails": null,
    "status": {
        "errorCode": 0,
        "failureReason": "Other.",
        "additionalDetails": "MFA requirement satisfied by claim in the token"
    }
}
```

```json
{
    "id": "50175a48-3b5c-4e78-86f4-0105e7ac6e00",
    "createdDateTime": "2026-09-13T01:22:08Z",
    "userId": "03ee6546-f113-4ec5-ba9d-e57381b0c928",
    "appDisplayName": "Lab-AI-Agent-CLI",
    "correlationId": "bae290c5-0422-4859-9004-e12b7af9be12",
    "isInteractive": true,
    "clientAppUsed": "Mobile Apps and Desktop clients",
    "conditionalAccessStatus": "success",
    "ipAddress": "[redacted]",
    "location": "[redacted: private residence]",
    "authenticationAppDeviceDetails": null,
    "status": {
        "errorCode": 65001,
        "failureReason": "The user or administrator has not consented to use the application with ID '{identifier}'{namePhrase}. Send an interactive authorization request for this user and resource.",
        "additionalDetails": null
    },
    "appliedConditionalAccessPolicies": [
        { "id": "365bdd23-...", "result": "notApplied" },
        { "id": "75882b6a-...", "result": "notApplied" },
        { "id": "d9a6a116-...", "result": "reportOnlyNotApplied" }
    ]
}
```

```json
{
    "id": "dd79c411-e6d9-4d79-97b8-6a463c3eb000",
    "createdDateTime": "2026-09-13T01:22:26Z",
    "userId": "03ee6546-f113-4ec5-ba9d-e57381b0c928",
    "appDisplayName": "Lab-AI-Agent-CLI",
    "correlationId": "bae290c5-0422-4859-9004-e12b7af9be12",
    "isInteractive": true,
    "clientAppUsed": "Mobile Apps and Desktop clients",
    "conditionalAccessStatus": "success",
    "ipAddress": "[redacted]",
    "location": "[redacted: private residence]",
    "servicePrincipalId": "4c43a528-ba33-40b0-8821-c8643587f351",
    "status": {
        "errorCode": 0,
        "failureReason": "Other.",
        "additionalDetails": "MFA completed in Azure AD"
    },
    "authenticationAppDeviceDetails": {
        "deviceId": "", "operatingSystem": "Ios", "clientApp": "Authenticator", "appVersion": "6.8.54"
    },
    "appliedConditionalAccessPolicies": [
        { "id": "365bdd23-...", "result": "success" },
        { "id": "75882b6a-...", "result": "notApplied" },
        { "id": "d9a6a116-...", "result": "reportOnlyFailure" }
    ]
}
```

## The four Graph Explorer records, appId `de8bc8b5-d9f9-48b1-a8ad-b748da725064`

```json
{ "id": "e889a0c1-c566-4744-a6bf-d89647fc6200", "createdDateTime": "2026-09-13T01:15:33Z",
  "userId": "03ee6546-...", "correlationId": "01a09855-6ea6-7186-ae80-e3b48c38d39d",
  "isInteractive": true, "conditionalAccessStatus": "failure",
  "status": { "errorCode": 50097, "failureReason": "Device authentication is required." } }

{ "id": "5beec047-646e-445d-9948-14b39a540801", "createdDateTime": "2026-09-13T01:15:34Z",
  "userId": "03ee6546-...", "correlationId": "01a09855-6ea6-7186-ae80-e3b48c38d39d",
  "isInteractive": true, "conditionalAccessStatus": "success",
  "status": { "errorCode": 50140,
              "failureReason": "This occurred due to 'Keep me signed in' interrupt when the user was signing in." } }

{ "id": "88b0e952-f6c3-487e-a3c5-6683cc728400", "createdDateTime": "2026-09-13T01:15:36Z",
  "userId": "03ee6546-...", "correlationId": "01a09855-6ea6-7186-ae80-e3b48c38d39d",
  "isInteractive": true, "conditionalAccessStatus": "success",
  "status": { "errorCode": 0, "additionalDetails": "MFA requirement satisfied by claim in the token" } }

{ "id": "5beec047-646e-445d-9948-14b326630801", "createdDateTime": "2026-09-13T01:16:37Z",
  "userDisplayName": "<GA>", "userPrincipalName": "<GA>",
  "userId": "6ca413e3-06ff-4704-ab36-1348bb7387c8",
  "correlationId": "01a09856-6318-788a-ab9e-915e146b9f0f",
  "isInteractive": true, "conditionalAccessStatus": "notApplied",
  "status": { "errorCode": 0, "additionalDetails": null } }
```

## What this proves

**1. A device code flow writes to both streams, and `evidence/01`'s claim that neither run appears
in the interactive log is wrong.** Each run produces three records in a fixed order:

| | Run 1 | Run 2 | Stream | Meaning |
|---|---|---|---|---|
| Consent not yet granted | 01:07:40Z | 01:22:08Z | interactive | `errorCode` 65001 |
| Consent written | 01:07:44Z | 01:22:12Z | `directoryAudits` | three events, `evidence/02` |
| Authentication succeeds | 01:07:46Z | 01:22:26Z | interactive | `errorCode` 0 |
| Token redeemed | 01:07:50Z | 01:22:28Z | non-interactive | `evidence/01` |

The interactive and non-interactive records of one run share no `correlationId`. Run 1's
interactive pair carries `61805a6d`, and so does its non-interactive token event. Run 2's
interactive pair carries `bae290c5`, and so does its token event. The `correlationId` is the join
across streams.

**2. The interactive record cannot tell a reader the sign-in was a device code flow.** `v1.0`
returns no `originalTransferMethod` property. The interactive records show `clientAppUsed`
`"Mobile Apps and Desktop clients"` and a Firefox `userAgent`, which describes any desktop client.
The only record that names `deviceCodeFlow` is the non-interactive token event on `beta`. A
defender reading the default log sees a successful sign-in to a named application and no indication
of the flow that produced it.

**3. `userAgent` differs between the two streams for one run.** The interactive records carry
Firefox. The non-interactive token event carries `curl/8.7.1` (`evidence/01`). That split is the
device code flow itself: a browser authenticates the human, and a separate client redeems the
token. A detection that pivots on `userAgent` sees two different clients for one authentication.

**4. MFA was completed interactively, and `evidence/01`'s reading of it is wrong.** Both runs'
successful interactive records read `"MFA completed in Azure AD"`, with
`authenticationAppDeviceDetails` naming the iOS Authenticator at version 6.8.54. `evidence/01`
concluded from the token event alone that MFA was satisfied by a claim and never prompted. The
claim satisfaction is real, and it is the third event inheriting what the second event established.

**5. The `Update user` event in `evidence/02` is now explained.** At 01:07:39Z, one second before
run 1's first interactive record, `Azure MFA StrongAuthenticationService` bumped
`PhoneAppVersion` from 6.8.53 to 6.8.54. The Authenticator app that answered the MFA prompt
recorded its own version change in the directory.

**6. The first record of each run is a failure that is not a failure.** `errorCode` 65001 reads
"The user or administrator has not consented". It is the expected first leg of a consent-requiring
flow, four seconds before the consent is written. Counting 65001 as an incident produces a false
positive on every first-time consent.

**7. C3's failed paired control is visible from the tenant side.** Graph Explorer at 01:15:33Z
returns `errorCode` 50097, "Device authentication is required", followed by 50140, the
"Keep me signed in" interrupt, then success at 01:15:36Z, all under one `correlationId` and all for
`adm-jsmith`. The Global Administrator's own Graph Explorer sign-in follows at 01:16:37Z under a
different `correlationId`. The browser did re-authenticate; it did not change who Graph Explorer
was for the read that followed.
