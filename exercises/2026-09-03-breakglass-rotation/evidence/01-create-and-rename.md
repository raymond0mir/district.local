# Create new emergency-access account, then rename off the example values

Command: `POST https://graph.microsoft.com/v1.0/users`
Host: Graph Explorer, signed in as `breakglass@raytakosharkygmail.onmicrosoft.com`
Timestamp (UTC): 2026-09-03T14:52:xx (from the error response's own `date` field on the first attempt)

## First attempt — rejected

Request body used a UPN local-part containing an invalid character (exact string not
captured — this failed before the account existed, so nothing to redact).

Response: `400 Bad Request`

```json
{
    "error": {
        "code": "Request_BadRequest",
        "message": "Property userPrincipalName is invalid.",
        "details": [
            {
                "code": "InvalidCharacter",
                "message": "Property userPrincipalName is invalid.",
                "target": "userPrincipalName",
                "blockedWord": "",
                "prefix": "",
                "suffix": ""
            }
        ],
        "innerError": {
            "date": "2026-09-03T14:52:58",
            "request-id": "0c267479-cce6-474f-b813-5d5d0ce785dd",
            "client-request-id": "1915dd97-7a13-0c17-ad44-95eceb3b8837"
        }
    }
}
```

## Second attempt — succeeded, but with placeholder-obvious values

Raymond fell back to the example `displayName`/`mailNickname`/UPN pattern suggested during
planning (`Emergency Access 2` / `emergencyaccess2@...`) to get unblocked past the character
error, not as a deliberate naming choice.

Response: `201 Created`

```json
{
    "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users/$entity",
    "id": "6ca413e3-06ff-4704-ab36-1348bb7387c8",
    "businessPhones": [],
    "displayName": "Emergency Access 2",
    "givenName": null,
    "jobTitle": null,
    "mail": null,
    "mobilePhone": null,
    "officeLocation": null,
    "preferredLanguage": null,
    "surname": null,
    "userPrincipalName": "[REDACTED-EXAMPLE-UPN]"
}
```

`userPrincipalName` above is redacted in this file even though the literal value at this point
(`emergencyaccess2@raytakosharkygmail.onmicrosoft.com`) was itself just the example text, not a
secret — kept consistent with the redaction convention applied to every later state of this
object, so no step in this file reads differently from the rest.

**Why this is a real finding, not just a typo:** the failure mode here isn't the syntax error —
it's that hitting a validation error mid-setup created pressure to fall back to convenient values,
and those convenient values (`Emergency Access 2`) directly defeated the purpose of the exercise:
a break-glass account's name should not announce itself to anyone browsing the tenant's user
list. Caught before the account was ever granted a role, but worth keeping as a caution against
example values leaking into real state under time pressure.

## Corrective rename

Command: `PATCH https://graph.microsoft.com/v1.0/users/6ca413e3-06ff-4704-ab36-1348bb7387c8`
Host: Graph Explorer, signed in as `breakglass@raytakosharkygmail.onmicrosoft.com`

Request body (values redacted; Raymond chose an ordinary-sounding name and did not disclose it in
chat as text — it appeared incidentally in a screenshot):

```json
{
  "userPrincipalName": "[REDACTED-NEW-BREAKGLASS-UPN]",
  "displayName": "[REDACTED-NEW-BREAKGLASS-DISPLAYNAME]"
}
```

Response: `204 No Content`, response preview `{}` — matches Graph's documented behavior for a
successful `PATCH` on a `user` resource.

**Object id is stable across the rename:** `6ca413e3-06ff-4704-ab36-1348bb7387c8` — same object,
identity metadata changed, no new soft-deleted object left behind by this step.
