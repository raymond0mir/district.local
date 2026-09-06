# The eligible account registers MFA, then requests activation

## Registered authentication methods

Command: `GET https://graph.microsoft.com/v1.0/users/03ee6546-f113-4ec5-ba9d-e57381b0c928/authentication/methods`
Host: Graph Explorer, tenant, signed in as the native Global Administrator
Timestamp: 2026-09-06, after Raymond completed first sign-in for `adm-jsmith`

```json
{
    "value": [
        {
            "@odata.type": "#microsoft.graph.passwordAuthenticationMethod",
            "id": "28c10230-6103-485e-b985-444c60001490",
            "password": null,
            "createdDateTime": "2026-09-06T17:50:58Z"
        },
        {
            "@odata.type": "#microsoft.graph.microsoftAuthenticatorAuthenticationMethod",
            "id": "f31afa0d-7449-4481-b372-78657dc56a25",
            "displayName": "iPhone",
            "deviceTag": "SoftwareTokenActivated",
            "phoneAppVersion": "6.8.53",
            "createdDateTime": null
        }
    ]
}
```

The password change and the Authenticator registration were done in the browser, and are Recalled
as actions. This read makes the resulting state Captured. `Enablement_EndUser_Assignment` demands
`MultiFactorAuthentication`, so this method is a precondition for activation, not a side task.

`createdDateTime` is null on the Authenticator method. Do not use this endpoint to date a
registration.

## The activation request

Command: `POST https://graph.microsoft.com/v1.0/roleManagement/directory/roleAssignmentScheduleRequests`
Host: Graph Explorer, tenant, signed in as `adm-jsmith` in a separate browser session
Timestamp: 2026-09-06T17:53:52Z, from `createdDateTime`

Body:

```json
{
  "action": "selfActivate",
  "principalId": "03ee6546-f113-4ec5-ba9d-e57381b0c928",
  "roleDefinitionId": "fe930be7-5e62-47db-91af-98c3a49a38b1",
  "directoryScopeId": "/",
  "justification": "B4: routine user administration task, time-bounded",
  "scheduleInfo": {
    "startDateTime": "2026-09-06T18:10:00Z",
    "expiration": { "type": "AfterDuration", "duration": "PT30M" }
  }
}
```

Response:

```json
{
    "id": "61998d6f-fcf3-400a-9d40-cbfa74a3bfbd",
    "status": "PendingApprovalProvisioning",
    "createdDateTime": "2026-09-06T17:53:52.0427885Z",
    "completedDateTime": "2026-09-06T18:10:00Z",
    "approvalId": "61998d6f-fcf3-400a-9d40-cbfa74a3bfbd",
    "customData": null,
    "action": "selfActivate",
    "principalId": "03ee6546-f113-4ec5-ba9d-e57381b0c928",
    "roleDefinitionId": "fe930be7-5e62-47db-91af-98c3a49a38b1",
    "directoryScopeId": "/",
    "appScopeId": null,
    "isValidationOnly": false,
    "targetScheduleId": "61998d6f-fcf3-400a-9d40-cbfa74a3bfbd",
    "justification": "B4: routine user administration task, time-bounded",
    "createdBy": {
        "application": null,
        "device": null,
        "user": {
            "displayName": null,
            "id": "03ee6546-f113-4ec5-ba9d-e57381b0c928"
        }
    },
    "scheduleInfo": {
        "startDateTime": "2026-09-06T18:10:00Z",
        "recurrence": null,
        "expiration": {
            "type": "afterDuration",
            "endDateTime": null,
            "duration": "PT30M"
        }
    },
    "ticketInfo": {
        "ticketNumber": null,
        "ticketSystem": null
    }
}
```

Both responses omit the `@odata.context` and `@microsoft.graph.tips` lines. Nothing else is
changed.

## What this shows

- `status` is `PendingApprovalProvisioning`, not Granted. The approval rule set in `evidence/11`
  is in force. Compare `evidence/08`, where an `adminAssign` returned Granted immediately.
- `approvalId` is non-null and equals the request id. `evidence/08` returned a null `approvalId`
  for the eligibility request. The difference is the action, not a configuration change.
- `createdBy.user.id` is `adm-jsmith` itself. The requester is recorded as the account, not as an
  administrator acting on its behalf.
- The requested duration is PT30M, below the PT2H ceiling in `evidence/11`.
- `adm-jsmith` holds no role at this moment. A pending request is not access.

## Status transition after approval, and one unresolved attempt

Command: `GET https://graph.microsoft.com/v1.0/roleManagement/directory/roleAssignmentScheduleRequests?$filter=principalId eq '03ee6546-f113-4ec5-ba9d-e57381b0c928'`
Host: Graph Explorer, tenant, signed in as the native Global Administrator
Timestamp: 2026-09-06, after the approval captured in `evidence/13`

The response holds exactly one request, `61998d6f-fcf3-400a-9d40-cbfa74a3bfbd`, with:

```json
{
    "status": "Granted",
    "createdDateTime": "2026-09-06T17:53:52.603Z",
    "completedDateTime": "2026-09-06T18:10:00Z",
    "approvalId": "61998d6f-fcf3-400a-9d40-cbfa74a3bfbd",
    "scheduleInfo": {
        "startDateTime": "2026-09-06T18:10:00Z",
        "expiration": { "type": "afterDuration", "endDateTime": null, "duration": "PT30M" }
    }
}
```

The same request read `PendingApprovalProvisioning` before the approval. It reads `Granted` after.
The request object records the outcome, and the approval object in `evidence/13` records the
reasoning. They are separate objects.

**Unresolved.** A deliberate over-limit request at PT4H was planned, to capture the PT2H ceiling
as a refusal. Raymond believes he sent it. No response was captured, and this endpoint returns no
PT4H object. That does not settle it: Entra may reject an over-limit request during validation,
before any request object persists, in which case a refused attempt and an attempt never sent are
indistinguishable here. The attempt is recorded as unresolved and is being re-run from a clean
state after the current activation expires.
