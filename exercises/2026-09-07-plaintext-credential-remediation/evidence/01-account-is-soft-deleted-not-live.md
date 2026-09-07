# The exposed account is soft-deleted, not live

All reads run in Graph Explorer from the Mac Mini. Timestamps come from the API's own
`innerError.date` where returned. The two successful reads returned no timestamp; they ran in the
same session, immediately after the 17:52:54Z read.

## Read 1 — lookup by UPN with signInActivity (failed)

    GET https://graph.microsoft.com/v1.0/users/breakglassrotationverify@raytakosharkygmail.onmicrosoft.com?$select=id,userPrincipalName,accountEnabled,userType,creationType,onPremisesSyncEnabled,createdDateTime,signInActivity
    Host: Graph Explorer
    2026-09-07T17:51:31Z

```json
{
    "error": {
        "code": "400",
        "message": "Get By Key only supports UserId and the key has to be a valid Guid",
        "innerError": {
            "date": "2026-09-07T17:51:31",
            "request-id": "0dccb1c5-41f9-4736-baf4-9643f3f2898c",
            "client-request-id": "bb226f92-452f-e0da-f7e6-92a55ec1652d"
        }
    }
}
```

Cause: `signInActivity` in `$select` forces Graph to resolve the key as a GUID. The UPN then fails
at the key parser. This error does not describe the account's state.

## Read 2 — lookup by UPN without signInActivity (failed)

    GET https://graph.microsoft.com/v1.0/users/breakglassrotationverify@raytakosharkygmail.onmicrosoft.com?$select=id,userPrincipalName,accountEnabled,userType,creationType,onPremisesSyncEnabled,createdDateTime
    Host: Graph Explorer
    2026-09-07T17:52:15Z

```json
{
    "error": {
        "code": "Request_ResourceNotFound",
        "message": "Resource 'breakglassrotationverify@raytakosharkygmail.onmicrosoft.com' does not exist or one of its queried reference-property objects are not present.",
        "innerError": {
            "date": "2026-09-07T17:52:15",
            "request-id": "05112fc8-3508-4b9e-8a72-5aae94142277",
            "client-request-id": "1377c9fa-60a1-bba4-3792-5b7aae1d6bd7"
        }
    }
}
```

The UPN string matches the one captured at
`exercises/2026-09-03-breakglass-rotation/evidence/02-role-assignment-and-verification.md:78`
exactly. The string is correct. The object is not in `/users`.

## Read 3 — lookup by object id (failed)

    GET https://graph.microsoft.com/v1.0/users/84360e8b-3321-4e37-b9ec-10fccd0263b8?$select=id,userPrincipalName,accountEnabled,userType,createdDateTime
    Host: Graph Explorer
    2026-09-07T17:52:54Z

```json
{
    "error": {
        "code": "Request_ResourceNotFound",
        "message": "Resource '84360e8b-3321-4e37-b9ec-10fccd0263b8' does not exist or one of its queried reference-property objects are not present.",
        "innerError": {
            "date": "2026-09-07T17:52:54",
            "request-id": "e97377c4-6991-459e-b499-9eaf74cdabd4",
            "client-request-id": "99447dd4-6b1d-3222-dc78-a52192713956"
        }
    }
}
```

The object id comes from
`exercises/2026-09-03-breakglass-rotation/evidence/02-role-assignment-and-verification.md:91`.

## Read 4 — deleted items (succeeded)

    GET https://graph.microsoft.com/v1.0/directory/deletedItems/microsoft.graph.user?$select=id,userPrincipalName,accountEnabled,deletedDateTime
    Host: Graph Explorer
    2026-09-07, same session as read 3

```json
{
    "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users(id,userPrincipalName,accountEnabled,deletedDateTime)",
    "value": [
        {
            "id": "84360e8b-3321-4e37-b9ec-10fccd0263b8",
            "userPrincipalName": "84360e8b33214e37b9ec10fccd0263b8breakglassrotationverify@raytakosharkygmail.onmicrosoft.com",
            "accountEnabled": true,
            "deletedDateTime": "2026-09-03T15:02:45Z"
        }
    ]
}
```

This proves four things:

- The account was soft-deleted 2026-09-03T15:02:45Z, the same day it was created.
- It is the only soft-deleted user in the tenant.
- Its `accountEnabled` value is `true`, and that value grants no sign-in. A soft-deleted user
  cannot authenticate.
- Graph prefixed the object id onto the UPN at delete time. That is why every lookup by the
  original UPN returns `Request_ResourceNotFound`.

Soft-deleted users are restorable for 30 days. Automatic permanent purge falls about
2026-10-03.

## Read 5 — remaining accounts matching "breakglass" (succeeded)

    GET https://graph.microsoft.com/v1.0/users?$filter=startswith(userPrincipalName,'breakglass')&$select=id,userPrincipalName,accountEnabled
    Host: Graph Explorer
    2026-09-07, same session as read 3

```json
{
    "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users(id,userPrincipalName,accountEnabled)",
    "value": [
        {
            "id": "de938dc8-feb7-4140-9a01-8e32649b8fd6",
            "userPrincipalName": "breakglass@raytakosharkygmail.onmicrosoft.com",
            "accountEnabled": false
        }
    ]
}
```

The one live match is the old `breakglass@` account, and it is disabled. This agrees with the
existing record that it is rotated out.
