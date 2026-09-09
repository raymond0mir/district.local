# An over-limit activation request is refused at validation, and no request object persists

Captured 2026-09-09, three days after the exercise. This file closes the open question carried
in `report.md`: does a PT4H activation request get refused when the policy maximum is PT2H?

Host: Graph Explorer, signed in as `adm-jsmith`.
UTC timestamp: 2026-09-09T14:01:38Z, from `date -u` in the Proxmox host shell.

## The ceiling still reads PT2H at the time of the test

Command: `GET https://graph.microsoft.com/v1.0/policies/roleManagementPolicies/DirectoryRole_e0b13496-83d1-4721-8bf9-f965f676106f_6710deb2-862a-4457-95cb-a7b2dd297ca0/rules/Expiration_EndUser_Assignment`

```json
{
    "@odata.type": "#microsoft.graph.unifiedRoleManagementPolicyExpirationRule",
    "id": "Expiration_EndUser_Assignment",
    "isExpirationRequired": true,
    "maximumDuration": "PT2H",
    "target": {
        "caller": "EndUser",
        "operations": [
            "all"
        ],
        "level": "Assignment",
        "inheritableSettings": [],
        "enforcedSettings": []
    }
}
```

The `PT2H` value set in `evidence/11` is unchanged. The ceiling is live at the moment of the
request below.

## The PT4H request is refused

Command: `POST https://graph.microsoft.com/v1.0/roleManagement/directory/roleAssignmentScheduleRequests`

Request body:

```json
{
  "action": "selfActivate",
  "principalId": "03ee6546-f113-4ec5-ba9d-e57381b0c928",
  "roleDefinitionId": "fe930be7-5e62-47db-91af-98c3a49a38b1",
  "directoryScopeId": "/",
  "justification": "B4 re-run: over-limit request, to capture the PT2H ceiling as a refusal.",
  "scheduleInfo": {
    "expiration": { "type": "afterDuration", "duration": "PT4H" }
  }
}
```

Response body:

```json
{
    "error": {
        "code": "RoleAssignmentRequestPolicyValidationFailed",
        "message": "The following policy rules failed: ExpirationRule - The duration in the request is greater than maximum allowed duration",
        "innerError": {
            "date": "2026-09-09T14:01:18",
            "request-id": "a9b61522-435c-42b3-8172-2722c990b06c",
            "client-request-id": "f08d02ab-5828-f316-1e41-a1128f08c98e"
        }
    }
}
```

## What this proves

The ceiling is enforced. It is not advisory. The request never reached the approval stage.

The error names the rule that refused it: `ExpirationRule`. It does not return a generic
validation failure. The named rule ties the refusal to the duration alone, without a control
request.

The refusal happens during validation, before any request object is written. The error carries a
`request-id` but no request object id. Nothing was created to cancel.

## What this settles about the 2026-09-06 attempt

`evidence/12` recorded that a PT4H attempt was planned, that Raymond believed he sent it, and that
`roleAssignmentScheduleRequests` held no PT4H object. That absence was treated as unresolved,
because a refused attempt and an unsent attempt were indistinguishable.

This capture explains the absence. An over-limit request never persists an object. The empty
result on 2026-09-06 is the expected result of a sent-and-refused request.

This does not prove the 2026-09-06 request was sent. It removes the empty endpoint as evidence
against it. The mechanism is now Captured. The 2026-09-06 attempt stays Recalled.

## Not captured

- The HTTP status codes. Graph Explorer's response bodies were pasted without the status line.
  The `error.code` identifies the failure without them.
- The clean-state read of `roleAssignmentScheduleInstances` before the request. The refusal cites
  `ExpirationRule`, so an existing active assignment is not a competing explanation.
- The control request at PT2H, using the same body. It would prove the body shape is valid. The
  named rule in the error already carries the attribution.
