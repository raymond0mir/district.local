# The eligible account is licensed, and every group in the tenant is synced

## `adm-jsmith` read-back

Command: `GET https://graph.microsoft.com/v1.0/users/03ee6546-f113-4ec5-ba9d-e57381b0c928?$select=displayName,userPrincipalName,accountEnabled,usageLocation,assignedLicenses,assignedPlans,onPremisesSyncEnabled`
Host: Graph Explorer, tenant, signed in as the native Global Administrator
Timestamp: 2026-09-06, same session as `01-preflight-and-dc01-standing-state.md`

```json
{
    "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users(displayName,userPrincipalName,accountEnabled,usageLocation,assignedLicenses,assignedPlans,onPremisesSyncEnabled)/$entity",
    "displayName": "Admin - John Smith",
    "userPrincipalName": "adm-jsmith@raytakosharkygmail.onmicrosoft.com",
    "accountEnabled": true,
    "usageLocation": "US",
    "onPremisesSyncEnabled": null,
    "assignedLicenses": [
        {
            "disabledPlans": [],
            "skuId": "84a661c4-e949-4bd2-a560-ed7766fcaf2b"
        }
    ],
    "assignedPlans": [
        {
            "assignedDateTime": "2026-09-06T17:18:32Z",
            "capabilityStatus": "Enabled",
            "service": "Adallom",
            "servicePlanId": "932ad362-64a8-4783-9106-97849a1a30b9"
        },
        {
            "assignedDateTime": "2026-09-06T17:18:32Z",
            "capabilityStatus": "Enabled",
            "service": "MultiFactorService",
            "servicePlanId": "8a256a2b-b617-496d-b51b-e76466e88db0"
        },
        {
            "assignedDateTime": "2026-09-06T17:18:32Z",
            "capabilityStatus": "Enabled",
            "service": "AADPremiumService",
            "servicePlanId": "eec0eb4f-6444-4f95-aba0-50c24d67f998"
        },
        {
            "assignedDateTime": "2026-09-06T17:18:32Z",
            "capabilityStatus": "Enabled",
            "service": "AADPremiumService",
            "servicePlanId": "41781fb2-bc02-4b7c-bd55-b576c07bb09d"
        }
    ]
}
```

`accountEnabled` true, `usageLocation` US, `onPremisesSyncEnabled` null. The account is
cloud-native. `AAD_PREMIUM_P2` is assigned, and `servicePlanId`
`eec0eb4f-6444-4f95-aba0-50c24d67f998` (`AAD_PREMIUM_P2`) reports `capabilityStatus` Enabled.
Licence assigned 2026-09-06T17:18:32Z.

## Group surface

Command: `GET https://graph.microsoft.com/v1.0/groups?$select=displayName,id,onPremisesSyncEnabled,securityEnabled,isAssignableToRole,mailEnabled`
Host: Graph Explorer, tenant, signed in as the native Global Administrator
Timestamp: 2026-09-06, same session

```json
{
    "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#groups(displayName,id,onPremisesSyncEnabled,securityEnabled,isAssignableToRole,mailEnabled)",
    "value": [
        {"displayName":"SG_admin_tier0_domain","id":"3da94cd2-9141-4c7f-92f3-f3ef802b66ad","onPremisesSyncEnabled":true,"securityEnabled":true,"isAssignableToRole":null,"mailEnabled":false},
        {"displayName":"DnsAdmins","id":"65ccdf0d-41b7-45f3-8eb1-59287baafb66","onPremisesSyncEnabled":true,"securityEnabled":true,"isAssignableToRole":null,"mailEnabled":false},
        {"displayName":"DHCP Users","id":"796bd20e-350e-4366-b19b-37e2ae22324b","onPremisesSyncEnabled":true,"securityEnabled":true,"isAssignableToRole":null,"mailEnabled":false},
        {"displayName":"SG_admin_tier2_desktop","id":"8221c338-4a89-4ac3-8759-68280dcc5261","onPremisesSyncEnabled":true,"securityEnabled":true,"isAssignableToRole":null,"mailEnabled":false},
        {"displayName":"DHCP Administrators","id":"9cfc86eb-2604-43fc-8600-5c7e61cf63a8","onPremisesSyncEnabled":true,"securityEnabled":true,"isAssignableToRole":null,"mailEnabled":false},
        {"displayName":"SG_Share_Site1_RW","id":"a9700e96-b8f9-49b4-a47a-2c2f3b6d70a1","onPremisesSyncEnabled":true,"securityEnabled":true,"isAssignableToRole":null,"mailEnabled":false},
        {"displayName":"SG_admin_tier1_helpdesk","id":"af739093-4956-4000-bbc5-e6aca29454cf","onPremisesSyncEnabled":true,"securityEnabled":true,"isAssignableToRole":null,"mailEnabled":false},
        {"displayName":"SG_Share_Site1_Read","id":"bb3a4718-7273-413b-8053-0accd78e6f22","onPremisesSyncEnabled":true,"securityEnabled":true,"isAssignableToRole":null,"mailEnabled":false},
        {"displayName":"DnsUpdateProxy","id":"e2ae3ac0-c5c8-4aae-895a-a7e53188a3e4","onPremisesSyncEnabled":true,"securityEnabled":true,"isAssignableToRole":null,"mailEnabled":false}
    ]
}
```

The response is reformatted to one object per line. No value is altered, added, or removed.

## What this shows

- Nine groups. Every one has `onPremisesSyncEnabled` true. The tenant holds no cloud-only group.
- Every group has `isAssignableToRole` null. The tenant holds no role-assignable group.
- `SG_admin_tier1_helpdesk` is the closest on-premises analogue to the User Administrator role
  chosen for this exercise. It is the target for the step 2 refusal.
- Consequence: PIM for Groups cannot govern anything in this tenant as built. Not one group
  qualifies. That is a property of how the tenant was populated, not a misconfiguration to fix.
