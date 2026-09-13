# Lab-AI-Agent-CLI exists, and Graph confirms every property the portal claimed

The registration was built in the Entra admin center, so the build itself is **Recalled**. These two
reads make the resulting state Captured. Bracket close: `Sun Sep 13 00:52:17 UTC 2026`, `date -u` on
the Mac Mini.

The portal account chip was visible in the screenshot of the build. That identity is deliberately
unpublished, per `CLAUDE.md`. It is not recorded here. The signing identity for the reads below is
the same native Global Administrator object id used throughout this exercise.

---

## Capture 1 — the application registration

```
Command: GET https://graph.microsoft.com/v1.0/applications(appId='388b9dd8-d98f-46f3-8eed-4418346e5673')?$select=id,appId,displayName,signInAudience,isFallbackPublicClient,createdDateTime,publicClient,requiredResourceAccess
Host:    Graph Explorer, browser on the Mac Mini
UTC:     before 2026-09-13T00:52:17Z
Signing identity: the native Global Administrator, 6ca413e3-06ff-4704-ab36-1348bb7387c8
```

```json
{
    "id": "e15012f9-b153-46df-afc9-ce63df4f29ee",
    "appId": "388b9dd8-d98f-46f3-8eed-4418346e5673",
    "displayName": "Lab-AI-Agent-CLI",
    "signInAudience": "AzureADMyOrg",
    "isFallbackPublicClient": true,
    "createdDateTime": "2026-09-13T00:46:37Z",
    "publicClient": {
        "redirectUris": []
    },
    "requiredResourceAccess": [
        {
            "resourceAppId": "00000003-0000-0000-c000-000000000000",
            "resourceAccess": [
                {
                    "id": "e1fe6dd8-ba31-4d61-89e7-88639da4683d",
                    "type": "Scope"
                }
            ]
        }
    ]
}
```

## Capture 2 — the service principal

```
Command: GET https://graph.microsoft.com/v1.0/servicePrincipals(appId='388b9dd8-d98f-46f3-8eed-4418346e5673')?$select=id,appId,displayName,servicePrincipalType,accountEnabled
Host:    Graph Explorer, browser on the Mac Mini
UTC:     before 2026-09-13T00:52:17Z
Signing identity: the native Global Administrator, 6ca413e3-06ff-4704-ab36-1348bb7387c8
```

```json
{
    "id": "4c43a528-ba33-40b0-8821-c8643587f351",
    "appId": "388b9dd8-d98f-46f3-8eed-4418346e5673",
    "displayName": "Lab-AI-Agent-CLI",
    "servicePrincipalType": "Application",
    "accountEnabled": true
}
```

---

## What the two captures establish

**Three identifiers, three jobs.** `appId` `388b9dd8` is the client id the device code request
sends. `id` `e15012f9` is the application object, and the teardown `DELETE` addresses that one.
`id` `4c43a528` is the service principal, a separate object with its own id. A reader who treats
"the app" as one object will address the wrong one.

**The portal created both objects.** The registration and the service principal exist together. A
`POST /applications` through Graph creates only the first, and a sign-in against an application with
no service principal fails for a reason that does not mention the missing object. The portal hides
that distinction by doing both silently.

**The client is public, and scoped to one delegated permission.** `isFallbackPublicClient: true`
permits device code flow. `publicClient.redirectUris` is empty. `signInAudience: AzureADMyOrg` keeps
it single tenant. `requiredResourceAccess` declares one resource, Microsoft Graph
(`00000003-0000-0000-c000-000000000000`), and one entry of `type: Scope`, which is delegated rather
than an application role.

**The declared permission id is `e1fe6dd8-ba31-4d61-89e7-88639da4683d`, and its name is Recalled.**
The portal displayed it as `User.Read`. This response does not name it. The device code token's own
`scp` claim prints the name in plain text, and that is where the name becomes Captured. The id was
never written from memory; it came out of the tenant.

**No consent exists yet.** Not proven by these two reads. `oauth2PermissionGrants` for the service
principal is the read that proves it, and it is the baseline the sign-in is measured against.
