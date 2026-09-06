# User Administrator held as eligible, not standing

## A failed query, kept

Command: `GET https://graph.microsoft.com/v1.0/roleManagement/directory/roleDefinitions?$filter=id eq '62e90394-...' or id eq '88d8e3e3-...'&$select=id,displayName,isBuiltIn`
Host: Graph Explorer, tenant
Timestamp: 2026-09-06T17:26:33, from the error's `innerError.date`

```json
{
    "error": {
        "code": "Request_UnsupportedQuery",
        "message": "Or operator not supported for this entity set.",
        "innerError": {
            "date": "2026-09-06T17:26:33",
            "request-id": "69ee6b4a-e3fd-4fda-bd28-6e891398eada",
            "client-request-id": "96f32ba6-ff60-c8b7-9a56-f7d24d186b21"
        }
    }
}
```

The query was Claude's. `roleDefinitions` rejects the `or` operator in `$filter`. The two role
names are therefore still unverified, and `evidence/03` still carries the correction notice.

## The eligibility request

Command: `POST https://graph.microsoft.com/v1.0/roleManagement/directory/roleEligibilityScheduleRequests`
Host: Graph Explorer, tenant, signed in as the native Global Administrator
Timestamp: 2026-09-06T17:27:07Z, from `createdDateTime`

Body:

```json
{
  "action": "adminAssign",
  "justification": "B4: hold User Administrator as eligible, not standing",
  "roleDefinitionId": "fe930be7-5e62-47db-91af-98c3a49a38b1",
  "directoryScopeId": "/",
  "principalId": "03ee6546-f113-4ec5-ba9d-e57381b0c928",
  "scheduleInfo": {
    "startDateTime": "2026-09-06T17:30:00Z",
    "expiration": { "type": "noExpiration" }
  }
}
```

Response:

```json
{
    "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#roleManagement/directory/roleEligibilityScheduleRequests/$entity",
    "id": "dad8b2e4-4623-4881-bc23-29002df81aea",
    "status": "Granted",
    "createdDateTime": "2026-09-06T17:27:07.7776711Z",
    "completedDateTime": "2026-09-06T17:30:00Z",
    "approvalId": null,
    "customData": null,
    "action": "adminAssign",
    "principalId": "03ee6546-f113-4ec5-ba9d-e57381b0c928",
    "roleDefinitionId": "fe930be7-5e62-47db-91af-98c3a49a38b1",
    "directoryScopeId": "/",
    "appScopeId": null,
    "isValidationOnly": false,
    "targetScheduleId": "dad8b2e4-4623-4881-bc23-29002df81aea",
    "justification": "B4: hold User Administrator as eligible, not standing",
    "createdBy": {
        "application": null,
        "device": null,
        "user": {
            "displayName": null,
            "id": "6ca413e3-06ff-4704-ab36-1348bb7387c8"
        }
    },
    "scheduleInfo": {
        "startDateTime": "2026-09-06T17:30:00Z",
        "recurrence": null,
        "expiration": {
            "type": "noExpiration",
            "endDateTime": null,
            "duration": null
        }
    },
    "ticketInfo": {
        "ticketNumber": null,
        "ticketSystem": null
    }
}
```

## What this shows

- `status` Granted. `isValidationOnly` false. The eligibility exists.
- `createdBy.user.id` is `6ca413e3-06ff-4704-ab36-1348bb7387c8`, the break-glass account. The
  audit trail records the tenant's only enabled administrator granting the eligibility that is
  meant to replace its own daily use.
- `approvalId` is null. An `adminAssign` action does not route through approval. Approval governs
  activation, not assignment. Do not read the null as a missing control.
- `expiration.type` is `noExpiration`. Eligibility is permanent. The bound belongs on activation,
  and that bound is not set yet.
- `adm-jsmith` holds no active role at this point. Eligibility is not access.
