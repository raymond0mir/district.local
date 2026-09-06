# PIM for Groups cannot reach this tenant's groups, and the refusal names why

## The attempt

Command: `PATCH https://graph.microsoft.com/v1.0/groups/af739093-4956-4000-bbc5-e6aca29454cf`
Body: `{ "isAssignableToRole": true }`
Target: `SG_admin_tier1_helpdesk`, synced from `district.local`
Host: Graph Explorer, tenant, signed in as the native Global Administrator
Timestamp: 2026-09-06T17:23:09, from the error's `innerError.date`

```json
{
    "error": {
        "code": "Request_BadRequest",
        "message": "Value for IsAssignableToRole cannot be updated for groups assignable to role.",
        "innerError": {
            "date": "2026-09-06T17:23:09",
            "request-id": "801839ba-8315-413f-8bfb-67c0db0fcf63",
            "client-request-id": "f8af64a2-40e6-b0e4-992e-a82f210c86ab"
        }
    }
}
```

## What this shows

- The refusal is an immutability refusal. `isAssignableToRole` cannot be changed after a group
  exists.
- The refusal is **not** the external-service-mastering refusal. Both were plausible before the
  attempt. Entra returned the immutability one. This file does not claim which check ran first,
  because the response does not say.
- The message reads "for groups assignable to role", while `06` captures this group's
  `isAssignableToRole` as null. The message wording does not match the object's state. Treat the
  message as a generic immutability string, not as a statement about this group.

## Why this closes the question rather than opening it

`06` captures that all nine groups in the tenant are synced and all have `isAssignableToRole`
null. This capture shows the property cannot be set after creation. Together: no existing group
in this tenant can ever be brought under PIM for Groups. Governing a group here requires creating
a new cloud-only role-assignable group, which is a different design, not a repair.

The on-premises `Domain Admins` grant that `01` captures therefore has no PIM equivalent
available to it. That is the exercise's central contrast, and it is now Captured rather than
argued from documentation.
