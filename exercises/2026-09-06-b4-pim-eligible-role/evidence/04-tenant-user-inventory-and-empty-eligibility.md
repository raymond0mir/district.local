# Tenant user inventory, and the empty PIM eligibility surface

**Redaction.** The current native Global Administrator's `displayName` and `userPrincipalName`
are replaced with `[REDACTED]`, per the standing portfolio rule. Its object id
`6ca413e3-06ff-4704-ab36-1348bb7387c8` is kept, and matches
`03-active-directory-role-assignments.md`. No other value is altered.

## User inventory

Command: `GET https://graph.microsoft.com/v1.0/users?$select=displayName,userPrincipalName,onPremisesSyncEnabled,accountEnabled,id`
Host: Graph Explorer, tenant, signed in as the native Global Administrator
Timestamp: 2026-09-06, same session as `01-preflight-and-dc01-standing-state.md`

```json
{
    "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users(displayName,userPrincipalName,onPremisesSyncEnabled,accountEnabled,id)",
    "value": [
        {
            "displayName": "Alice Jones",
            "userPrincipalName": "ajones@raytakosharkygmail.onmicrosoft.com",
            "onPremisesSyncEnabled": true,
            "accountEnabled": true,
            "id": "adb0ee55-70ae-4f34-bb74-63c2642df9d9"
        },
        {
            "displayName": "bhound",
            "userPrincipalName": "bhound@raytakosharkygmail.onmicrosoft.com",
            "onPremisesSyncEnabled": true,
            "accountEnabled": false,
            "id": "1b39b0f8-1629-4241-807c-61ca6c36ac3d"
        },
        {
            "displayName": "bing bong",
            "userPrincipalName": "bingbong@raytakosharkygmail.onmicrosoft.com",
            "onPremisesSyncEnabled": true,
            "accountEnabled": true,
            "id": "a48dbe5c-330c-47f6-8654-edba373dc560"
        },
        {
            "displayName": "breakglass",
            "userPrincipalName": "breakglass@raytakosharkygmail.onmicrosoft.com",
            "onPremisesSyncEnabled": null,
            "accountEnabled": false,
            "id": "de938dc8-feb7-4140-9a01-8e32649b8fd6"
        },
        {
            "displayName": "dumb helpdesk",
            "userPrincipalName": "dumbhelpdesk1@raytakosharkygmail.onmicrosoft.com",
            "onPremisesSyncEnabled": true,
            "accountEnabled": true,
            "id": "9781c3ff-fd70-4492-8b68-3c44a00394d5"
        },
        {
            "displayName": "dumb user2",
            "userPrincipalName": "dumbuser2@raytakosharkygmail.onmicrosoft.com",
            "onPremisesSyncEnabled": true,
            "accountEnabled": true,
            "id": "11033cf6-328f-4a1a-b66d-82807b0f2acb"
        },
        {
            "displayName": "dumb user 3",
            "userPrincipalName": "dumbuser3@raytakosharkygmail.onmicrosoft.com",
            "onPremisesSyncEnabled": true,
            "accountEnabled": true,
            "id": "12a79785-0100-40fa-bb54-68a0493dfa1c"
        },
        {
            "displayName": "John Smith",
            "userPrincipalName": "jsmith@raytakosharkygmail.onmicrosoft.com",
            "onPremisesSyncEnabled": true,
            "accountEnabled": true,
            "id": "03b0f0f4-1230-42c1-983c-9bb5ecb1a2c8"
        },
        {
            "displayName": "Kareem Khan",
            "userPrincipalName": "khan@raytakosharkygmail.onmicrosoft.com",
            "onPremisesSyncEnabled": true,
            "accountEnabled": true,
            "id": "ffd8ba96-dd1b-4e81-8ef2-0f9808c6339d"
        },
        {
            "displayName": "Lab Admin",
            "userPrincipalName": "labadmin@raytakosharkygmail.onmicrosoft.com",
            "onPremisesSyncEnabled": null,
            "accountEnabled": false,
            "id": "dde25d37-4119-4217-9252-6b69d2798519"
        },
        {
            "displayName": "[REDACTED]",
            "userPrincipalName": "[REDACTED]@raytakosharkygmail.onmicrosoft.com",
            "onPremisesSyncEnabled": null,
            "accountEnabled": true,
            "id": "6ca413e3-06ff-4704-ab36-1348bb7387c8"
        },
        {
            "displayName": "Michael Lee",
            "userPrincipalName": "mlee@raytakosharkygmail.onmicrosoft.com",
            "onPremisesSyncEnabled": true,
            "accountEnabled": true,
            "id": "be30dc5f-8f31-4c4f-bcbc-7be6e23cf9bb"
        },
        {
            "displayName": "R M",
            "userPrincipalName": "raytakosharky_gmail.com#EXT#@raytakosharkygmail.onmicrosoft.com",
            "onPremisesSyncEnabled": null,
            "accountEnabled": false,
            "id": "888038b6-2970-46dc-9245-0dfa9a464939"
        },
        {
            "displayName": "svc-entraconnect",
            "userPrincipalName": "svc-entraconnect@raytakosharkygmail.onmicrosoft.com",
            "onPremisesSyncEnabled": true,
            "accountEnabled": true,
            "id": "da4c397e-f3b1-4ac2-97a9-11229c8f52cd"
        },
        {
            "displayName": "System Admin",
            "userPrincipalName": "sysadmin@raytakosharkygmail.onmicrosoft.com",
            "onPremisesSyncEnabled": true,
            "accountEnabled": true,
            "id": "05198b4f-e5a9-4fa9-a755-c57acc12eed8"
        }
    ]
}
```

## PIM eligibility, before enablement

Command: `GET https://graph.microsoft.com/beta/roleManagement/directory/roleEligibilitySchedules?$expand=principal,roleDefinition`
Host: Graph Explorer, tenant, signed in as the native Global Administrator
Timestamp: 2026-09-06, same session

Result: HTTP 200, `value` empty. Reported by Raymond as "empty value on 2nd result". The literal
body was not pasted, so the empty result is Recalled, not Captured. The 200 status is consistent
with a tenant that has no eligible role assignments.

## What this shows

- Fifteen user objects. Twelve are synced from `district.local`. Three are cloud-only.
- The tenant's original Global Administrator is present as an external member,
  `raytakosharky_gmail.com#EXT#@...`, and `accountEnabled` is **false**. It returned no row from
  `roleAssignments`. The open question in `03-active-directory-role-assignments.md` is answered
  as far as sign-in is concerned: that identity cannot sign in.
- `breakglass` and `labadmin`, both cloud-only, are disabled. `breakglass` is the account rotated
  out in `exercises/2026-09-03-breakglass-rotation`.
- The redacted account is the only enabled account holding an active Entra directory role.
- `sysadmin` is synced to Entra and enabled. The same object is a `Domain Admins` member on
  `district.local` with `adminCount` 1, per `01-preflight-and-dc01-standing-state.md`.
- `bhound` is synced and disabled, consistent with `EXPOSURES.md`.
- No object named `adm-jsmith` exists. The name is free.
