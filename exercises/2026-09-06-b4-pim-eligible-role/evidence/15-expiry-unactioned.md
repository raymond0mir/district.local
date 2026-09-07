# The activation expired, the eligibility survived, and no person acted

Captured 2026-09-07, the day after the activation. The audit log write latency that affected
earlier exercises is not a factor at this distance.

## The activation is gone

Command: `GET https://graph.microsoft.com/v1.0/roleManagement/directory/roleAssignments?$filter=principalId eq '03ee6546-f113-4ec5-ba9d-e57381b0c928'`

```json
{ "value": [] }
```

Command: `GET https://graph.microsoft.com/v1.0/roleManagement/directory/roleAssignmentScheduleInstances?$filter=principalId eq '03ee6546-f113-4ec5-ba9d-e57381b0c928'`

```json
{ "value": [] }
```

Both endpoints held a row for this principal in `evidence/14`. Both are now empty. Nobody ran a
removal.

## The eligibility survived

Command: `GET https://graph.microsoft.com/v1.0/roleManagement/directory/roleEligibilityScheduleInstances?$filter=principalId eq '03ee6546-f113-4ec5-ba9d-e57381b0c928'`

```json
{
    "value": [
        {
            "id": "5wuT_mJe20eRr5jDpJo4sUZl7gMT8cVOup3lc4GwySg-1-e",
            "principalId": "03ee6546-f113-4ec5-ba9d-e57381b0c928",
            "roleDefinitionId": "fe930be7-5e62-47db-91af-98c3a49a38b1",
            "directoryScopeId": "/",
            "appScopeId": null,
            "startDateTime": "2026-09-06T17:30:40.193Z",
            "endDateTime": null,
            "memberType": "Direct",
            "roleEligibilityScheduleId": "dad8b2e4-4623-4881-bc23-29002df81aea"
        }
    ]
}
```

`endDateTime` null. The expiry removed the activation and left the eligibility. The control is
repeatable, not single-use. `adm-jsmith` can activate again, and must pass approval again.

The eligibility instance began at 17:30:40.193Z. `evidence/08` requested 17:30:00Z. Provisioning
added 40 seconds, matching the 47-second offset on the activation in `evidence/14`.

## Two audit entries, six seconds apart, from two services

Command: `GET https://graph.microsoft.com/v1.0/auditLogs/directoryAudits?$filter=activityDateTime ge 2026-09-06T18:35:00Z and activityDateTime le 2026-09-06T18:50:00Z`

The response holds two entries and nothing else in that fifteen-minute window.

**First, Core Directory performs the removal.**

```json
{
    "id": "Directory_9154767b-525c-4bd4-b76c-4bfa9c053b3a_FSD0Z_121401637",
    "category": "RoleManagement",
    "result": "success",
    "activityDisplayName": "Remove member from role",
    "activityDateTime": "2026-09-06T18:40:46.7455924Z",
    "loggedByService": "Core Directory",
    "operationType": "Unassign",
    "initiatedBy": {
        "user": null,
        "app": {
            "appId": null,
            "displayName": "MS-PIM",
            "servicePrincipalId": "bdefcbb6-d8b2-497d-a944-b683d9a36b0c",
            "servicePrincipalName": null
        }
    },
    "targetResources": [
        {
            "id": "03ee6546-f113-4ec5-ba9d-e57381b0c928",
            "type": "User",
            "userPrincipalName": "adm-jsmith@raytakosharkygmail.onmicrosoft.com",
            "modifiedProperties": [
                {"displayName":"Role.ObjectID","oldValue":"\"40a84a16-f7af-47f1-aa96-3f93b7d572cd\"","newValue":null},
                {"displayName":"Role.DisplayName","oldValue":"\"User Administrator\"","newValue":null},
                {"displayName":"Role.TemplateId","oldValue":"\"fe930be7-5e62-47db-91af-98c3a49a38b1\"","newValue":null},
                {"displayName":"Role.WellKnownObjectName","oldValue":"\"UserAccountAdmins\"","newValue":null}
            ]
        }
    ]
}
```

**Then PIM records why.**

```json
{
    "id": "PIM_cc22d319-a360-4006-bbf8-99d66b1d0926_e0b13496-83d1-4721-8bf9-f965f676106f_134331936526770240",
    "category": "RoleManagement",
    "result": "success",
    "activityDisplayName": "Remove member from role (PIM activation expired)",
    "activityDateTime": "2026-09-06T18:40:52.677024Z",
    "loggedByService": "PIM",
    "operationType": "Delete",
    "initiatedBy": {
        "app": null,
        "user": {
            "id": "9dfd627f-bdc5-4b1c-af9d-c85097fdeff8",
            "displayName": "Azure AD PIM",
            "userPrincipalName": null,
            "ipAddress": null,
            "userType": null
        }
    },
    "additionalDetails": [
        {"key":"AuditType","value":"RemoveActivatedRole"},
        {"key":"ActionType","value":"Revoke"},
        {"key":"OriginRoleAssignmentId","value":"5wuT_mJe20eRr5jDpJo4sUZl7gMT8cVOup3lc4GwySg-1"},
        {"key":"RoleAssignmentRequestId","value":"61998d6f-fcf3-400a-9d40-cbfa74a3bfbd"}
    ]
}
```

Both entries are quoted in part. The `@odata.context`, `@microsoft.graph.tips`, the PIM entry's
nine `targetResources`, and its remaining `additionalDetails` keys are omitted. The omission is
marked here rather than made silently. Every field shown is verbatim.

## What this shows

- **No person removed the grant.** The Core Directory entry's `initiatedBy` is an application,
  `MS-PIM`. The PIM entry's `initiatedBy.user.displayName` is "Azure AD PIM", a platform identity
  with a null `userPrincipalName` and a null `ipAddress`. Neither entry names a human.
  This is B4's hypothesis proven: the removal needed no one to remember it.
- **The removal ran within a second of the deadline.** `evidence/14` captured `endDateTime`
  18:40:45.843Z. Core Directory unassigned at 18:40:46.7455924Z, 0.9 seconds later.
- **Two services, two records, six seconds apart.** Core Directory logs the directory change and
  calls it `Unassign`. PIM logs the reason and calls it `Revoke`, with `AuditType`
  `RemoveActivatedRole`. A query scoped to one service sees half the story.
- **A role has two identifiers.** `Role.ObjectID` is `40a84a16-f7af-47f1-aa96-3f93b7d572cd`, the
  directory role object. `Role.TemplateId` is `fe930be7-5e62-47db-91af-98c3a49a38b1`, the role
  definition used everywhere else in this exercise. They are not interchangeable.
- **The request id links the whole chain.** `RoleAssignmentRequestId` is
  `61998d6f-fcf3-400a-9d40-cbfa74a3bfbd`, the same GUID as the request, the approval, the approval
  step, the schedule, and the live assignment.
