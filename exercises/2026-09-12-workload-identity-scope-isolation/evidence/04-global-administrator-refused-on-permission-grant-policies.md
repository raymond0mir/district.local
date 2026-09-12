# Global Administrator, holding Directory.Read.All, is refused the permission grant policy list

```
Command: GET https://graph.microsoft.com/v1.0/policies/permissionGrantPolicies
Host:    Graph Explorer, browser on the Mac Mini
UTC:     2026-09-12T16:57:13Z, from the response body's innerError.date
Signing identity: the native Global Administrator, 6ca413e3-06ff-4704-ab36-1348bb7387c8,
                  Captured in evidence/03-graph-explorer-token-decoded.md
```

```json
{
    "error": {
        "code": "Authorization_RequestDenied",
        "message": "Insufficient privileges to complete the operation.",
        "innerError": {
            "date": "2026-09-12T16:57:13",
            "request-id": "b5fc9be7-ee47-40c5-8c8c-ac9e9928f76c",
            "client-request-id": "7503f1a5-9674-7304-ec9d-0710686b66c8"
        }
    }
}
```

**The path parsed.** A malformed segment on this same endpoint returns `400 BadRequest` naming the
segment, observed at 16:55:27Z after a paste landed beside stale address bar text. This response is
`403`, so the request reached authorization. The earlier `400` is Recalled; it was read from a
screenshot.

---

## What this shows

The same token, in the same minute, reads other endpoints without error. Capture 01 read
`policies/authorizationPolicy` with `Policy.Read.All` and `applications` with `Application.Read.All`.
Both returned bodies. This call is refused.

The difference is not the human. The signed-in account holds Global Administrator, Captured in the
`wids` claim. The difference is the token's scope list. `scp` carries `Policy.Read.All`,
`Directory.Read.All` and 23 other scopes. It does not carry `Policy.Read.PermissionGrant`.

**This is the exercise's own hypothesis, arriving before the exercise built anything.** C3 set out to
show that an access token bounds a client below the rights of the human who signed in. A Global
Administrator refused on a directory read, by a token that lacks one scope, is that claim with the
highest-privileged account in the tenant standing in for the test subject.

## What is not yet proven

The positive control is missing. Consenting `Policy.Read.PermissionGrant` and receiving `200` on this
same URL would close it. Until then, one alternative explanation survives: that the endpoint requires
something else this account lacks.

Microsoft Learn weakens that alternative but does not remove it. `GET /policies/permissionGrantPolicies`
lists `Policy.Read.PermissionGrant` as least privileged and `Policy.ReadWrite.PermissionGrant` as
higher privileged. `GET /policies/permissionGrantPolicies/{id}/includes` lists
`Policy.Read.PermissionGrant` as least privileged and **`Directory.Read.All`** as higher privileged.
The token holds `Directory.Read.All`, and the `includes` reads at 16:35:05Z and 16:35:33Z were
refused as well. Either the documented alternative does not work on that path, or both refusals share
a cause the documentation does not describe.

## Blocker on the positive control

Graph Explorer's permissions panel does not load. It renders "Retry again" with an empty list, before
and after a search for `policy`, and after a page reload. No scope can be consented through the tool
while that persists. Observed in two screenshots, so this blocker is Recalled.
