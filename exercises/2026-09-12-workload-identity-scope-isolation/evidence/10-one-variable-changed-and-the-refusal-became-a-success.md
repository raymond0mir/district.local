# Same client, same user, one scope different: 403 becomes 200

The paired control for `evidence/07-device-code-token-bounds-the-signed-in-user.md`. Everything is
held constant except the scope requested at the token endpoint.

```
Command: python3 <scratchpad>/device-code-run.py "https://graph.microsoft.com/User.ReadBasic.All"
Host:    Terminal on the Mac Mini
UTC:     2026-09-13T01:21:16Z to 2026-09-13T01:22:29Z
Client:  Lab-AI-Agent-CLI, appId 388b9dd8-d98f-46f3-8eed-4418346e5673
Signed in: adm-jsmith, oid 03ee6546-f113-4ec5-ba9d-e57381b0c928, no PIM role activated
```

## The two runs, side by side

| | Run 1, 01:07:50Z | Run 2, 01:22:28Z |
|---|---|---|
| Client `appid` | `388b9dd8` | `388b9dd8` |
| Signed-in `oid` | `03ee6546` | `03ee6546` |
| `wids` | `b79fbf4d` only | `b79fbf4d` only |
| `scp` | `User.Read profile openid email` | `User.Read User.ReadBasic.All profile openid email` |
| `GET /v1.0/me` | 200 | 200 |
| `GET /v1.0/users?$top=3` | **403** | **200** |
| `GET /v1.0/directoryRoles` | 403 | 403 |

Fifteen minutes apart. One difference in the token.

## Step 2 — the token response

```
2026-09-13T01:21:24Z  HTTP 400  error: authorization_pending
2026-09-13T01:22:28Z  HTTP 200, token issued
  token_type      : Bearer
  expires_in      : 5355
  scope returned  : profile openid email https://graph.microsoft.com/User.Read https://graph.microsoft.com/User.ReadBasic.All
  refresh_token   : absent
```

## Step 3 — decoded token claims

```json
{
  "aud": "https://graph.microsoft.com",
  "appid": "388b9dd8-d98f-46f3-8eed-4418346e5673",
  "app_displayname": "Lab-AI-Agent-CLI",
  "scp": "User.Read User.ReadBasic.All profile openid email",
  "roles": null,
  "wids": ["b79fbf4d-3ef9-4689-8143-76b194e85509"],
  "oid": "03ee6546-f113-4ec5-ba9d-e57381b0c928",
  "tid": "e0b13496-83d1-4721-8bf9-f965f676106f",
  "ver": "1.0",
  "iat": 1789262248,
  "exp": 1789267904
}
```

## Step 5 — the call that was refused fifteen minutes earlier

```
GET https://graph.microsoft.com/v1.0/users?$top=3
HTTP 200
```

Three users returned: `adm-jsmith`, `ajones`, `bhound`, with an `@odata.nextLink`. The same three the
Global Administrator's token returned in `evidence/09-...`.

## Step 6 — still refused

```
GET https://graph.microsoft.com/v1.0/directoryRoles
HTTP 403  Authorization_RequestDenied
```

`User.ReadBasic.All` does not reach directory roles. The boundary moved by exactly one permission,
not to everything.

---

## Findings

**1. The hypothesis is closed, on a paired observation.** The token is the boundary. One client, one
user, one endpoint, refused and then permitted, with the scope as the only variable. No role was
activated in either run; `wids` holds the non-guest marker alone both times.

**2. The application's declared permission list did not bound what the client could request, and
this is the more important result.** `Lab-AI-Agent-CLI` declares exactly one delegated permission,
`e1fe6dd8-ba31-4d61-89e7-88639da4683d`, Captured in `evidence/06-...`. Nobody edited the
registration between the runs. The client asked the token endpoint for `User.ReadBasic.All`, an
ordinary member consented, and the token carried it.

**The exercise's own hypothesis, as `CURRICULUM.md` words it, is wrong in its premise.** It reads:
"an app registration restricted to one delegated scope produces an access token that Microsoft Graph
enforces". Graph does enforce the token, which is the half that holds. But an app registration is not
restricted by its declared permission list. The list drives the consent experience and the portal's
admin-consent button. It is not a runtime ceiling.

**3. What actually bounds a delegated client is consent, plus what the tenant lets a user consent
to.** `adm-jsmith` holds no directory role and it widened this client's access on its own, twice, in
fifteen minutes, with no administrator and no change to any object an administrator reviews.

**4. This is the permission-sprawl thesis, at the workload layer, in miniature.** The registration's
API permissions blade still shows one permission. Nothing an administrator would look at has changed.
The consent grant behind it has grown. An application that looks scoped to one permission is not
evidence that it is.

**5. Token lifetime varies between runs.** Run 1: `expires_in` 4300, `exp` minus `iat` 4601 seconds.
Run 2: `expires_in` 5355, `exp` minus `iat` 5656 seconds. Same client, same user, different
lifetimes, and a constant 301-second gap between the two measures in both runs. Do not treat either
number as fixed.

## Not proven here

- That the consent grant object now records both scopes. Predicted, not read.
- That the application's `requiredResourceAccess` still declares one permission after both runs.
  Predicted, not read.
- Whether a scope requiring admin consent would also be obtainable this way. It would not be, by
  definition of admin consent, but that is reasoning, not a capture.
