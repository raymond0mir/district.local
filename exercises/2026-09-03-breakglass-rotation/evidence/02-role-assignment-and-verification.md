# Assign Global Administrator, then verify from the new account's own token

## Role lookup

Command: `GET https://graph.microsoft.com/v1.0/directoryRoles?$filter=displayName eq 'Global Administrator'`
Host: Graph Explorer, signed in as `breakglass@raytakosharkygmail.onmicrosoft.com`

```json
{
    "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#directoryRoles",
    "value": [
        {
            "id": "38d63b66-2238-4a84-bc42-2ad7d1d33418",
            "deletedDateTime": null,
            "description": "Can manage all aspects of Microsoft Entra ID and Microsoft services that use Microsoft Entra identities.",
            "displayName": "Global Administrator",
            "roleTemplateId": "62e90394-69f5-4237-9190-012177145e10"
        }
    ]
}
```

`roleTemplateId` matches Microsoft's well-known, tenant-invariant Global Administrator template
GUID (`62e90394-69f5-4237-9190-012177145e10`) — confirms this is genuinely that role, not a
custom role sharing the display name.

## Role assignment

Command: `POST https://graph.microsoft.com/v1.0/directoryRoles/38d63b66-2238-4a84-bc42-2ad7d1d33418/members/$ref`
Host: Graph Explorer, signed in as `breakglass@raytakosharkygmail.onmicrosoft.com`

Body:
```json
{
  "@odata.id": "https://graph.microsoft.com/v1.0/directoryObjects/6ca413e3-06ff-4704-ab36-1348bb7387c8"
}
```

Response: `204 No Content`.

## Verification 1 — new account's own token confirms membership

Command: `GET https://graph.microsoft.com/v1.0/me/memberOf?$select=displayName,id`
Host: Graph Explorer, signed in as the new (renamed) account itself — first interactive sign-in,
required accepting a first-run consent prompt.

```json
{
    "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#directoryObjects(displayName,id)",
    "value": [
        {
            "@odata.type": "#microsoft.graph.directoryRole",
            "displayName": "Global Administrator",
            "id": "38d63b66-2238-4a84-bc42-2ad7d1d33418"
        }
    ]
}
```

Same role id as the assignment step — self-attested from the new account's own session, not
re-read from the old admin's view of it.

## Verification 2 — privilege actually exercised, not just claimed in a token

A role claim in `/me/memberOf` proves the assignment exists, not that it works end-to-end. Tested
by having the new account perform an action that genuinely requires an administrative role:
creating, then deleting, a throwaway user object.

Command: `POST https://graph.microsoft.com/v1.0/users`
Host: Graph Explorer, signed in as the new account.

Body:
```json
{
  "accountEnabled": true,
  "displayName": "breakglass-rotation-verify",
  "mailNickname": "breakglassrotationverify",
  "userPrincipalName": "breakglassrotationverify@raytakosharkygmail.onmicrosoft.com",
  "passwordProfile": {
    "forceChangePasswordNextSignIn": true,
    "password": "TempV3rify!Throwaway2026"
  }
}
```

Response: `201 Created`

```json
{
    "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users/$entity",
    "id": "84360e8b-3321-4e37-b9ec-10fccd0263b8",
    "businessPhones": [],
    "displayName": "breakglass-rotation-verify",
    "givenName": null,
    "jobTitle": null,
    "mail": null,
    "mobilePhone": null,
    "officeLocation": null,
    "preferredLanguage": null,
    "surname": null,
    "userPrincipalName": "breakglassrotationverify@raytakosharkygmail.onmicrosoft.com"
}
```

Cleanup — `DELETE https://graph.microsoft.com/v1.0/users/84360e8b-3321-4e37-b9ec-10fccd0263b8`,
still as the new account. Response: `204 No Content`.

**Conclusion:** the new account can both create and delete directory objects — real Global
Administrator capability confirmed from its own session, before the old account's privilege was
touched. This is the point at which it's safe to de-privilege the old account.
