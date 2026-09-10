# `User Administrator` assigned to `PIM-UserAdmin-Pilot`, standing

## The assignment

Command: `POST https://graph.microsoft.com/v1.0/roleManagement/directory/roleAssignments`
Body:
```json
{
    "principalId": "3265375f-23f9-4d3f-81d3-15370199bc8a",
    "roleDefinitionId": "fe930be7-5e62-47db-91af-98c3a49a38b1",
    "directoryScopeId": "/"
}
```
Host: Graph Explorer, tenant, signed in as the native Global Administrator (break-glass).
Timestamp: not independently captured; same session as `evidence/01`.

```json
{
    "id": "5wuT_mJe20eRr5jDpJo4sV83ZTL5Iz9NgdMVNwGZvIo-1",
    "principalId": "3265375f-23f9-4d3f-81d3-15370199bc8a",
    "principalOrganizationId": "e0b13496-83d1-4721-8bf9-f965f676106f",
    "directoryScopeId": "/",
    "roleDefinitionId": "fe930be7-5e62-47db-91af-98c3a49a38b1"
}
```

## What this shows

- `201 Created` with a real assignment `id` — this is a standing, active assignment, not an
  eligible one. `PIM-UserAdmin-Pilot` now holds `User Administrator` tenant-wide (`directoryScopeId:
  "/"`), permanently, matching the PIM-for-Groups pattern Microsoft documents: the group holds
  the role standing; PIM governs just-in-time *membership* in the group, not the group's own role.
- `roleDefinitionId` reused from B4's `evidence/09`, not re-derived from memory.
- This is now the second live path to `User Administrator` in this tenant, alongside B4's direct
  eligible assignment on `adm-jsmith` (`exercises/2026-09-06-b4-pim-eligible-role/evidence/08-eligibility-granted.md`).
  Left in place deliberately — Raymond's decision, `evidence-log.md`'s consultation section —
  tracked in `CARRYOVER.md` as a pre-teardown cleanup item, not fixed here.
