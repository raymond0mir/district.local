# Finding the approval surface, and approving the activation

**Redaction.** `reviewedBy.displayName`, `reviewedBy.userPrincipalName`, and `reviewedBy.mail`
carry the current native Global Administrator's identity. All three are replaced with
`[REDACTED]`. The `id` GUID is kept and matches `evidence/03`. No other value is altered.

## The endpoint does not exist on v1.0

Command: `GET https://graph.microsoft.com/v1.0/roleManagement/directory/roleAssignmentApprovals/61998d6f-fcf3-400a-9d40-cbfa74a3bfbd?$expand=steps`
Host: Graph Explorer, tenant, signed in as the native Global Administrator
Timestamp: 2026-09-06T17:55:05

```json
{
    "error": {
        "code": "BadRequest",
        "message": "Resource not found for the segment 'roleAssignmentApprovals'.",
        "innerError": {
            "date": "2026-09-06T17:55:05",
            "request-id": "d36c9c02-53de-4954-ad8d-3105f86ac2de",
            "client-request-id": "49d36a6d-afde-8bdf-f887-f5d99e9ae3fa"
        }
    }
}
```

## On beta the segment exists, and the scope is the blocker

Command: the same request against `beta`
Timestamp: 2026-09-06T17:55:34

```json
{
    "error": {
        "code": "",
        "message": "Valid permissions not present. User needs one of the following permissions for this action : PrivilegedAccess.ReadWrite.AzureAD,PrivilegedAccess.Read.AzureAD",
        "innerError": {
            "date": "2026-09-06T17:55:34",
            "request-id": "24cf6c9c-79e0-4cf4-88cc-02487abe7139",
            "client-request-id": "f8379475-214e-aa5f-6a9b-c5e7c793cfce"
        }
    }
}
```

The two errors are different in kind. v1.0 rejects the path. Beta accepts the path and rejects
the token. `PrivilegedAccess.ReadWrite.AzureAD` was then consented in Graph Explorer.

## The pending approval step

Command: `GET https://graph.microsoft.com/beta/roleManagement/directory/roleAssignmentApprovals/61998d6f-fcf3-400a-9d40-cbfa74a3bfbd?$expand=steps`
Timestamp: 2026-09-06, after consent

```json
{
    "id": "61998d6f-fcf3-400a-9d40-cbfa74a3bfbd",
    "steps": [
        {
            "id": "61998d6f-fcf3-400a-9d40-cbfa74a3bfbd",
            "displayName": null,
            "reviewedDateTime": null,
            "reviewResult": "NotReviewed",
            "status": "InProgress",
            "assignedToMe": true,
            "justification": null,
            "reviewedBy": null
        }
    ]
}
```

The step id equals the approval id, which equals the request id from `evidence/12`. Three
identifiers, one GUID. `assignedToMe` true confirms the signed-in account is the approver named
in `evidence/11`.

## The approval

Command: `PATCH https://graph.microsoft.com/beta/roleManagement/directory/roleAssignmentApprovals/61998d6f-fcf3-400a-9d40-cbfa74a3bfbd/steps/61998d6f-fcf3-400a-9d40-cbfa74a3bfbd`
Host: Graph Explorer, tenant, signed in as the native Global Administrator
Status: 204 No Content, reported by Raymond

Body:

```json
{
  "reviewResult": "Approve",
  "justification": "Approved: routine user administration, 30-minute window, requester is the designated working admin account"
}
```

Read-back:

```json
{
    "id": "61998d6f-fcf3-400a-9d40-cbfa74a3bfbd",
    "steps": [
        {
            "id": "61998d6f-fcf3-400a-9d40-cbfa74a3bfbd",
            "displayName": null,
            "reviewedDateTime": "2026-09-06T17:57:04.546911Z",
            "reviewResult": "Approve",
            "status": "Completed",
            "assignedToMe": true,
            "justification": "Approved: routine user administration, 30-minute window, requester is the designated working admin account",
            "reviewedBy": {
                "id": "6ca413e3-06ff-4704-ab36-1348bb7387c8",
                "displayName": "[REDACTED]",
                "userPrincipalName": "[REDACTED]@raytakosharkygmail.onmicrosoft.com",
                "mail": "[REDACTED]@raytakosharkygmail.onmicrosoft.com"
            }
        }
    ]
}
```

Both read-backs omit `@odata.context`, `steps@odata.context`, and `@microsoft.graph.tips`.

## What this shows

- `reviewResult` moved from `NotReviewed` to `Approve`, `status` from `InProgress` to `Completed`.
- `reviewedDateTime` 2026-09-06T17:57:04Z. The request was made at 17:53:52Z. Elapsed time between
  request and approval is three minutes and twelve seconds.
- `reviewedBy.id` is the break-glass account. `evidence/12` records `createdBy.user.id` as
  `adm-jsmith`. The requester and the approver are different objects, and the record proves it.
- Both justifications are stored. The requester's reason and the approver's reason are separately
  retrievable, which is what an approval adds over an audit trail.

## The limit this does not remove

The approver is the tenant's only other enabled administrator, and Raymond signs in as it for
routine work. The record shows two objects. It does not show two people. A tenant with one
administrator cannot buy separation of duties by turning on approval.
