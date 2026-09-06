# The approved activation becomes a live role assignment

Command: `GET https://graph.microsoft.com/v1.0/roleManagement/directory/roleAssignmentScheduleInstances?$filter=principalId eq '03ee6546-f113-4ec5-ba9d-e57381b0c928'`
Host: Graph Explorer, tenant, signed in as the native Global Administrator
Timestamp: 2026-09-06, after 18:11Z

```json
{
    "value": [
        {
            "id": "5wuT_mJe20eRr5jDpJo4sUZl7gMT8cVOup3lc4GwySg-1",
            "principalId": "03ee6546-f113-4ec5-ba9d-e57381b0c928",
            "roleDefinitionId": "fe930be7-5e62-47db-91af-98c3a49a38b1",
            "directoryScopeId": "/",
            "appScopeId": null,
            "startDateTime": "2026-09-06T18:10:47.01Z",
            "endDateTime": "2026-09-06T18:40:45.843Z",
            "assignmentType": "Activated",
            "memberType": "Direct",
            "roleAssignmentOriginId": "5wuT_mJe20eRr5jDpJo4sUZl7gMT8cVOup3lc4GwySg-1",
            "roleAssignmentScheduleId": "61998d6f-fcf3-400a-9d40-cbfa74a3bfbd"
        }
    ]
}
```

Command: `GET https://graph.microsoft.com/v1.0/roleManagement/directory/roleAssignments?$filter=principalId eq '03ee6546-f113-4ec5-ba9d-e57381b0c928'`
Host and timestamp: as above

```json
{
    "value": [
        {
            "id": "5wuT_mJe20eRr5jDpJo4sUZl7gMT8cVOup3lc4GwySg-1",
            "principalId": "03ee6546-f113-4ec5-ba9d-e57381b0c928",
            "principalOrganizationId": "e0b13496-83d1-4721-8bf9-f965f676106f",
            "directoryScopeId": "/",
            "roleDefinitionId": "fe930be7-5e62-47db-91af-98c3a49a38b1"
        }
    ]
}
```

Both responses omit `@odata.context` and `@microsoft.graph.tips`. Nothing else is changed.
This second query is filtered to one principal. It is not the tenant-wide read in `evidence/03`.

## What this shows

- `assignmentType` is `Activated`, not `Assigned`. The grant came from an activation, and the
  object says so.
- The role appears in `roleAssignments`, the same endpoint that lists standing grants. While a
  PIM activation is live, it is a real role assignment and is indistinguishable in effect from a
  permanent one. The difference is `endDateTime`, and the difference is entirely about time.
- `roleAssignmentScheduleId` is `61998d6f-fcf3-400a-9d40-cbfa74a3bfbd`, the same GUID as the
  request and the approval. One identifier links request, approval, schedule, and live assignment.
- `startDateTime` is 18:10:47.01Z. The request asked for 18:10:00Z. Provisioning added 47 seconds.
  A scheduled start is approximate. Do not use a requested start time as an evidence timestamp.
- `endDateTime` is 18:40:45.843Z. The window measures from provisioning, not from the requested
  start. Elapsed time is 29 minutes 58.8 seconds, against a requested PT30M.
