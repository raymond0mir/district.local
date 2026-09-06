# The P2 trial window, Captured

Retires the Recalled trial clock carried in `CARRYOVER.md` since 2026-09-04.

Command: `GET https://graph.microsoft.com/beta/directory/subscriptions`
Host: Graph Explorer, tenant, signed in as the native Global Administrator
Timestamp: 2026-09-06, same session as `01-preflight-and-dc01-standing-state.md`

```json
{
    "@odata.context": "https://graph.microsoft.com/beta/$metadata#directory/subscriptions",
    "value": [
        {
            "createdDateTime": "2026-09-04T00:00:00Z",
            "commerceSubscriptionId": "0f92f719-16e2-4b5e-b054-7487694456fc",
            "id": "8232b18e-81aa-4b55-ae50-c7f456acf665",
            "isTrial": true,
            "nextLifecycleDateTime": "2026-10-04T00:00:00Z",
            "ocpSubscriptionId": "0f92f719-16e2-4b5e-b054-7487694456fc",
            "skuId": "84a661c4-e949-4bd2-a560-ed7766fcaf2b",
            "skuPartNumber": "AAD_PREMIUM_P2",
            "status": "Enabled",
            "totalLicenses": 100,
            "ownerTenantId": null,
            "ownerId": null,
            "ownerType": null,
            "serviceStatus": [
                {
                    "servicePlanId": "113feb6c-3fe4-4440-bddc-54d774bf0318",
                    "servicePlanName": "EXCHANGE_S_FOUNDATION",
                    "servicePlanType": "Exchange",
                    "provisioningStatus": "Success",
                    "appliesTo": "Company"
                },
                {
                    "servicePlanId": "932ad362-64a8-4783-9106-97849a1a30b9",
                    "servicePlanName": "ADALLOM_S_DISCOVERY",
                    "servicePlanType": "Adallom",
                    "provisioningStatus": "Success",
                    "appliesTo": "User"
                },
                {
                    "servicePlanId": "8a256a2b-b617-496d-b51b-e76466e88db0",
                    "servicePlanName": "MFA_PREMIUM",
                    "servicePlanType": "MultiFactorService",
                    "provisioningStatus": "Success",
                    "appliesTo": "User"
                },
                {
                    "servicePlanId": "41781fb2-bc02-4b7c-bd55-b576c07bb09d",
                    "servicePlanName": "AAD_PREMIUM",
                    "servicePlanType": "AADPremiumService",
                    "provisioningStatus": "Success",
                    "appliesTo": "User"
                },
                {
                    "servicePlanId": "eec0eb4f-6444-4f95-aba0-50c24d67f998",
                    "servicePlanName": "AAD_PREMIUM_P2",
                    "servicePlanType": "AADPremiumService",
                    "provisioningStatus": "Success",
                    "appliesTo": "User"
                }
            ]
        }
    ]
}
```

The trial started 2026-09-04T00:00:00Z. `nextLifecycleDateTime` is 2026-10-04T00:00:00Z.
The estimate carried in carryover, about 2026-10-04, was correct. It is no longer Recalled.
100 licences are available, so seat count does not constrain B4.
