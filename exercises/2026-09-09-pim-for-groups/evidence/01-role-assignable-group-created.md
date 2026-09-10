# `PIM-UserAdmin-Pilot` created as a cloud-only, role-assignable group

## The attempt

Command: `POST https://graph.microsoft.com/v1.0/groups`
Body:
```json
{
    "description": "Eligible for just-in-time User Administrator, governed by PIM for Groups",
    "displayName": "PIM-UserAdmin-Pilot",
    "mailEnabled": false,
    "mailNickname": "pimuseradminpilot",
    "securityEnabled": true,
    "isAssignableToRole": true
}
```
Host: Graph Explorer, tenant, signed in as the native Global Administrator (break-glass), after
`adm-jsmith`'s attempt at the same call was refused — `evidence-log.md`, Not captured section.
Timestamp: 2026-09-09T20:43:34Z, from the response's `createdDateTime`.

```json
{
    "id": "3265375f-23f9-4d3f-81d3-15370199bc8a",
    "createdDateTime": "2026-09-09T20:43:34Z",
    "description": "Eligible for just-in-time User Administrator, governed by PIM for Groups",
    "displayName": "PIM-UserAdmin-Pilot",
    "groupTypes": [],
    "isAssignableToRole": true,
    "mailEnabled": false,
    "mailNickname": "pimuseradminpilot",
    "membershipRule": null,
    "membershipRuleProcessingState": null,
    "onPremisesSyncEnabled": null,
    "securityEnabled": true,
    "securityIdentifier": "S-1-12-1-845494111-1295983609-924177281-2327615745",
    "visibility": "Private"
}
```

## What this shows

- `isAssignableToRole: true` persisted at creation, under the account that holds Global
  Administrator. This is a real Graph API response, pasted as text, not a screenshot — Captured.
- `onPremisesSyncEnabled: null` and `groupTypes: []` confirm this is a fresh cloud-only security
  group, not synced from `district.local` and not a Microsoft 365 group. This satisfies the
  precondition `evidence/06` and `evidence/07` in `exercises/2026-09-06-b4-pim-eligible-role`
  named: PIM for Groups and role assignment both need a group that was never synced, because
  `isAssignableToRole` cannot be set on an existing group and dynamic or on-premises-synced
  groups can't be managed in PIM for Groups.
- `membershipRule: null` confirms Assigned membership, not dynamic — a hard requirement for a
  role-assignable group.

## What this does not show

Whether `adm-jsmith`'s earlier refusal was a missing OAuth consent, a role-based denial
(`Privileged Role Administrator` required, `User Administrator` held), or both. Not isolated.
Retesting the identical call as `adm-jsmith` after tenant-wide consent is granted would separate
the two causes; not done in this session.
