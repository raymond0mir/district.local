# Break-glass sign-ins that postdate the three report-only CA policies

Command: GET https://graph.microsoft.com/v1.0/auditLogs/signIns?$top=20
Host: Graph Explorer, signed in as the current break-glass Global Administrator
UTC timestamp: 2026-09-05T16:08:17Z (host `date -u`, Proxmox console, same turn)

HTTP status code not captured. A full response body with `@odata.nextLink` was returned.

Redactions applied: the break-glass `userPrincipalName` and `userDisplayName` are replaced per the
portfolio rule against publishing the current Global Administrator's identity. `ipAddress` and
`location.geoCoordinates` are replaced because they identify a private residence. The object ID is
retained because policy exclusion arrays are keyed on it and the claim cannot be checked without it.

## What this proves

The prior exercise recorded that no sign-in entry appeared for this account after a confirmed MFA
sign-in. That is disproved. Two entries postdate all three policies.

Policy creation times, from `2026-09-04-b1-security-defaults-and-ca-report-only`:
365bdd23 at 14:10:14Z, 75882b6a at 14:11:55Z, d9a6a116 at 14:12:50Z.

| createdDateTime      | appDisplayName  | errorCode | conditionalAccessStatus | B1 policies present |
|----------------------|-----------------|-----------|--------------------------|---------------------|
| 2026-09-04T14:19:38Z | Graph Explorer  | 0         | notApplied               | all three           |
| 2026-09-04T14:19:33Z | Graph Explorer  | 50140     | notApplied               | all three           |

Entry 1 of 2, verbatim except for the redactions named above:

    "id": "3388ca4e-566a-4c7c-bd5d-fd8fcb600f00",
    "createdDateTime": "2026-09-04T14:19:38Z",
    "userDisplayName": "<break-glass display name, redacted>",
    "userPrincipalName": "<break-glass UPN, redacted>",
    "userId": "6ca413e3-06ff-4704-ab36-1348bb7387c8",
    "appDisplayName": "Graph Explorer",
    "ipAddress": "<redacted>",
    "clientAppUsed": "Browser",
    "correlationId": "01a06cc9-c5f8-7867-b277-f1bcc02f737a",
    "conditionalAccessStatus": "notApplied",
    "isInteractive": true,
    "resourceDisplayName": "Microsoft Graph",
    "status": {
        "errorCode": 0,
        "failureReason": "Other.",
        "additionalDetails": "MFA requirement satisfied by claim in the token"
    },
    "deviceDetail": {
        "deviceId": "", "displayName": "", "operatingSystem": "MacOs",
        "browser": "Firefox 155.0", "isCompliant": false, "isManaged": false, "trustType": null
    },
    "appliedConditionalAccessPolicies": [
        { "id": "SecurityDefaults",
          "displayName": "Security Defaults",
          "enforcedGrantControls": ["Mfa"], "enforcedSessionControls": [],
          "result": "success" },
        { "id": "365bdd23-d0e0-49a7-8131-f63b98ea6115",
          "displayName": "B1 - Require MFA for all users (report-only)",
          "enforcedGrantControls": ["Mfa"], "enforcedSessionControls": [],
          "result": "reportOnlyNotApplied" },
        { "id": "75882b6a-a9ba-4d97-bbb4-72d29277ebf4",
          "displayName": "B1 - Block legacy authentication (report-only)",
          "enforcedGrantControls": ["Block"], "enforcedSessionControls": [],
          "result": "reportOnlyNotApplied" },
        { "id": "d9a6a116-0c05-4894-af2c-a2990ef44593",
          "displayName": "B1 - Require compliant or hybrid joined device (report-only)",
          "enforcedGrantControls": ["RequireCompliantDevice"], "enforcedSessionControls": [],
          "result": "reportOnlyNotApplied" }
    ]

Entry 2 of 2 carries the identical four-policy array and the identical four `result` values. It
differs only in `status`: errorCode 50140, "This occurred due to 'Keep me signed in' interrupt when
the user was signing in." It also carries `authenticationAppDeviceDetails` naming Authenticator
6.8.53 on iOS. The two entries share `correlationId` 01a06cc9-c5f8-7867-b277-f1bcc02f737a, so they
are two legs of one interactive sign-in that satisfied MFA.

## What this does not prove

`reportOnlyNotApplied` means the policy was evaluated in report-only mode and did not apply. It
does not name the cause. Exclusion of this account and a condition that did not match produce the
same value. This file does not verify the exclusion. It removes the missing-log blocker only.

## Second finding, unrelated to the hypothesis

`Security Defaults` appears with `result: success` and `enforcedGrantControls: ["Mfa"]` on every
entry in this response, including both entries that postdate the three CA policies. Security
Defaults was still enforcing MFA in this tenant on 2026-09-04 at 14:19:38Z, after the CA policies
existed. Current state not read in this file. See evidence file 02.

## Third finding: jsmith has no post-policy sign-in

The same response carried two `jsmith` entries, 2026-09-04T00:37:32Z and 00:37:34Z, both from
Microsoft Device Registration Client and Microsoft Authentication Broker on DESKTOP-O860UU9
(`trustType: Azure AD joined`, `deviceId` 7b564046-16ba-4d3d-8baf-6745b6e93267). Both predate the
policies and both carry an empty `appliedConditionalAccessPolicies` array. No non-excluded user has
signed in since the policies were created. The contrast case does not exist yet in the log.
