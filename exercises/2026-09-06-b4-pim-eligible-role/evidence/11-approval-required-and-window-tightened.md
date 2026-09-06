# Approval required, activation bounded to two hours

**Redaction.** The approver's `description`, which Entra populated with the current native Global
Administrator's display name, is replaced with `[REDACTED]`. Its `userId` GUID is kept, and
matches `evidence/03`. No other value is altered.

## Two failed attempts, caused by Claude

Command: `PATCH https://graph.microsoft.com/v1.0/policies/roleManagementPolicies/P/rules/Approval_EndUser_Assignment`
Host: Graph Explorer, tenant
Timestamps: 2026-09-06T17:43:39 and 2026-09-06T17:45:02, from the errors' `innerError.date`

```json
{
    "error": {
        "code": "UnknownError",
        "message": "{\"errorCode\":\"MissingProvider\",\"message\":\"The provider is missing.\",\"instanceAnnotations\":[]}",
        "innerError": {
            "date": "2026-09-06T17:43:39",
            "request-id": "d0c96737-c536-49a6-8ea0-f30c5181d1f4",
            "client-request-id": "93a66831-af96-e23b-7f31-3372fc3482be"
        }
    }
}
```

```json
{
    "error": {
        "code": "UnknownError",
        "message": "{\"errorCode\":\"MissingProvider\",\"message\":\"The provider is missing.\",\"instanceAnnotations\":[]}",
        "innerError": {
            "date": "2026-09-06T17:45:02",
            "request-id": "5db5404d-a4e8-48f3-8ec1-b1c732563a45",
            "client-request-id": "e91c8183-5973-07d8-ef24-7cb9a2d73c88"
        }
    }
}
```

**Cause.** Claude wrote the policy id as the shorthand `P` in the instructions, and the literal
character `P` was sent in the URL. A role management policy id encodes its provider as the first
segment, `DirectoryRole_...`. Entra parses the id before it looks the object up, so a malformed
id returns `UnknownError` with `MissingProvider` rather than `404 Not Found`. Graph Explorer also
displayed "No resource was found matching this query" under the address bar.

Two attempts were spent on this. The first was read as a body-shape problem, and the second
attempt removed `description` and `isBackup` from the approver object to test that reading. That
hypothesis was never tested, because the URL was the fault in both attempts. It is recorded as
untested, not as disproven.

## Approval rule, after the change

Command: `GET https://graph.microsoft.com/v1.0/policies/roleManagementPolicies/DirectoryRole_e0b13496-83d1-4721-8bf9-f965f676106f_6710deb2-862a-4457-95cb-a7b2dd297ca0/rules/Approval_EndUser_Assignment`
Host: Graph Explorer, tenant
Timestamp: 2026-09-06, same session

```json
{
    "@odata.type": "#microsoft.graph.unifiedRoleManagementPolicyApprovalRule",
    "id": "Approval_EndUser_Assignment",
    "target": {
        "caller": "EndUser",
        "operations": ["all"],
        "level": "Assignment",
        "inheritableSettings": [],
        "enforcedSettings": []
    },
    "setting": {
        "isApprovalRequired": true,
        "isApprovalRequiredForExtension": false,
        "isRequestorJustificationRequired": true,
        "approvalMode": "SingleStage",
        "approvalStages": [
            {
                "approvalStageTimeOutInDays": 1,
                "isApproverJustificationRequired": true,
                "escalationTimeInMinutes": 0,
                "isEscalationEnabled": false,
                "primaryApprovers": [
                    {
                        "@odata.type": "#microsoft.graph.singleUser",
                        "userId": "6ca413e3-06ff-4704-ab36-1348bb7387c8",
                        "description": "[REDACTED]"
                    }
                ],
                "escalationApprovers": []
            }
        ]
    }
}
```

`isApprovalRequired` moved from false to true. The default was captured in `evidence/10`.

**Field asymmetry.** The PATCH body set the approver as `"id"`. The read-back returns `"userId"`.
Entra also populated `description` on its own, with the approver's display name, although the
PATCH body sent no `description`. Do not assume a rule's write shape matches its read shape.

## Expiration rule, after the change

Command: `GET https://graph.microsoft.com/v1.0/policies/roleManagementPolicies/DirectoryRole_e0b13496-83d1-4721-8bf9-f965f676106f_6710deb2-862a-4457-95cb-a7b2dd297ca0/rules/Expiration_EndUser_Assignment`
Host: Graph Explorer, tenant
Timestamp: 2026-09-06, same session

```json
{
    "@odata.type": "#microsoft.graph.unifiedRoleManagementPolicyExpirationRule",
    "id": "Expiration_EndUser_Assignment",
    "isExpirationRequired": true,
    "maximumDuration": "PT2H",
    "target": {
        "caller": "EndUser",
        "operations": ["all"],
        "level": "Assignment",
        "inheritableSettings": [],
        "enforcedSettings": []
    }
}
```

`maximumDuration` moved from PT8H to PT2H. `isExpirationRequired` was already true by default.

Both read-backs omit the `@odata.context` and `@microsoft.graph.tips` lines. Nothing else is
changed.

## State of the control

An activation of User Administrator by `adm-jsmith` now needs, in order: multi-factor
authentication, a requester justification, approval by the break-glass account with an approver
justification, and it expires within two hours.

The approver and the only other administrator are the same account. This is the ceiling of a
single-administrator tenant. Approval here delays an action; it does not divide it between two
people. Say that in the report rather than presenting the control as complete.
