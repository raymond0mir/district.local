# The unidentified wids value is not a directory role, and the lab proves it

Closes an open question carried since 2026-09-09 in
`exercises/2026-09-09-pim-for-groups/report.md`.

```
Command: GET https://graph.microsoft.com/v1.0/roleManagement/directory/roleDefinitions/b79fbf4d-3ef9-4689-8143-76b194e85509
Host:    Graph Explorer, browser on the Mac Mini
UTC:     2026-09-12T16:59:35Z, from the response body's innerError.date
Signing identity: the native Global Administrator, 6ca413e3-06ff-4704-ab36-1348bb7387c8
```

```json
{
    "error": {
        "code": "Request_ResourceNotFound",
        "message": "Resource 'b79fbf4d-3ef9-4689-8143-76b194e85509' does not exist or one of its queried reference-property objects are not present.",
        "innerError": {
            "date": "2026-09-12T16:59:35",
            "request-id": "bbde1749-1a74-4723-97d3-b35517c478a2",
            "client-request-id": "a36174b2-5375-34ce-ac19-93c5c82143cb"
        }
    }
}
```

---

## The answer

`b79fbf4d-3ef9-4689-8143-76b194e85509` is not a directory role definition. Microsoft Entra sends it
in `wids` for every non-guest account in a tenant, and it refers to no administrator role. Source:
Microsoft Learn, "Secure an ASP.NET Core Blazor Web App with OpenID Connect", Application roles
section, which states it in those terms; the same sentence appears in the Blazor WebAssembly groups
and roles article. That is documentation, not a lab capture.

**The lab capture is the independent half.** `roleDefinitions` holds every built-in and custom role
definition in the tenant, and a Global Administrator's token asking it for this id gets
`Request_ResourceNotFound`. A value that named a role would resolve there. The two sources agree by
different routes.

## Why the question arose twice

`exercises/2026-09-09-pim-for-groups` found this value on `adm-jsmith`. Capture 03 found it on the
native Global Administrator. Two accounts with very different privilege carried the same value, which
is what made it look like a role worth identifying. The explanation is the opposite of privilege:
both accounts are members of the tenant rather than guests, and that is the only thing the value
reports.

## The reading error it was inviting

A reader who treats `wids` as a list of administrator roles counts two roles for this account and one
for `adm-jsmith`, and concludes the Global Administrator holds an extra unnamed privilege. The
account holds one directory role, `62e90394-69f5-4237-9190-012177145e10`. Read `wids` as
"directly assigned directory roles, plus a fixed member marker", and check any unfamiliar value
against `roleDefinitions` before naming it.
