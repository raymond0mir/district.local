# The working administrator account, created

Command: `POST https://graph.microsoft.com/v1.0/users`
Host: Graph Explorer, tenant, signed in as the native Global Administrator
Timestamp: 2026-09-06, same session as `01-preflight-and-dc01-standing-state.md`

Request body, with the password redacted. Raymond typed the password directly into Graph
Explorer. It was never sent to Claude, and it is not recorded here.

```json
{
  "accountEnabled": true,
  "displayName": "Admin - John Smith",
  "mailNickname": "adm-jsmith",
  "userPrincipalName": "adm-jsmith@raytakosharkygmail.onmicrosoft.com",
  "usageLocation": "US",
  "passwordProfile": {
    "forceChangePasswordNextSignIn": true,
    "password": "[REDACTED]"
  }
}
```

Response:

```json
{
    "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users/$entity",
    "businessPhones": [],
    "displayName": "Admin - John Smith",
    "givenName": null,
    "jobTitle": null,
    "mail": null,
    "mobilePhone": null,
    "officeLocation": null,
    "preferredLanguage": null,
    "surname": null,
    "userPrincipalName": "adm-jsmith@raytakosharkygmail.onmicrosoft.com",
    "id": "03ee6546-f113-4ec5-ba9d-e57381b0c928"
}
```

The account is cloud-native. Object id `03ee6546-f113-4ec5-ba9d-e57381b0c928`.

The response does not echo `usageLocation` or `accountEnabled`, because the default `$select` on
a create response is narrow. Both need a read-back to be Captured. Do not infer them from the
request body.
