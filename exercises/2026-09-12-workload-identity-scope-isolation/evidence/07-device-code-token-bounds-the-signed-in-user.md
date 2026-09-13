# The device code token refuses what its user is permitted to do

One run of `device-code-run.py`, which performs the device code flow and three Graph calls in one
process. The access token was never written to a file, a screen, or a chat window. Every HTTP call
went through `curl`, with secrets passed on stdin rather than on the command line, so no token
appeared in the process list.

```
Command: python3 <scratchpad>/device-code-run.py
Host:    Terminal on the Mac Mini
UTC:     2026-09-13T01:02:05Z to 2026-09-13T01:07:51Z
Client:  Lab-AI-Agent-CLI, appId 388b9dd8-d98f-46f3-8eed-4418346e5673
Signed in: adm-jsmith, oid 03ee6546-f113-4ec5-ba9d-e57381b0c928, no PIM role activated
```

## Step 1 — device code request

```
POST https://login.microsoftonline.com/e0b13496-83d1-4721-8bf9-f965f676106f/oauth2/v2.0/devicecode
HTTP 200
{
  "user_code": "BMS4RWVV8",
  "verification_uri": "https://login.microsoft.com/device",
  "expires_in": 900,
  "interval": 5
}
```

## Step 2 — polling

```
2026-09-13T01:02:12Z  HTTP 400  error: authorization_pending
2026-09-13T01:07:50Z  HTTP 200, token issued
  token_type      : Bearer
  expires_in      : 4300
  scope returned  : profile openid email https://graph.microsoft.com/User.Read
  refresh_token   : absent
```

## Step 3 — decoded token claims

```json
{
  "aud": "https://graph.microsoft.com",
  "appid": "388b9dd8-d98f-46f3-8eed-4418346e5673",
  "app_displayname": "Lab-AI-Agent-CLI",
  "scp": "User.Read profile openid email",
  "roles": null,
  "wids": [
    "b79fbf4d-3ef9-4689-8143-76b194e85509"
  ],
  "oid": "03ee6546-f113-4ec5-ba9d-e57381b0c928",
  "tid": "e0b13496-83d1-4721-8bf9-f965f676106f",
  "ver": "1.0",
  "iat": 1789261370,
  "exp": 1789265971
}
```

## Step 4 — positive control

```
GET https://graph.microsoft.com/v1.0/me
HTTP 200
{
  "displayName": "Admin - John Smith",
  "userPrincipalName": "adm-jsmith@raytakosharkygmail.onmicrosoft.com",
  "id": "03ee6546-f113-4ec5-ba9d-e57381b0c928"
}
```

## Step 5 — negative test, other users

```
GET https://graph.microsoft.com/v1.0/users?$top=3
HTTP 403
{
  "error": {
    "code": "Authorization_RequestDenied",
    "message": "Insufficient privileges to complete the operation.",
    "innerError": { "date": "2026-09-13T01:07:50", "request-id": "a751c943-d15b-4342-8aa2-b3ba73c13ed7" }
  }
}
```

## Step 6 — negative test, directory roles

```
GET https://graph.microsoft.com/v1.0/directoryRoles
HTTP 403
{
  "error": {
    "code": "Authorization_RequestDenied",
    "message": "Insufficient privileges to complete the operation.",
    "innerError": { "date": "2026-09-13T01:07:51", "request-id": "469bf36e-3c74-4422-8b37-ccea367a28cf" }
  }
}
```

---

## Findings

**1. The hypothesis holds, with one control still owed.** A token carrying `User.Read` read the
signed-in user's own profile and was refused two directory reads. The positive control passed at the
same second as both refusals, so the client, the network and the token were all working when the
refusals happened. The tenant permits this user to read other users:
`defaultUserRolePermissions.allowedToReadOtherUsers` is `true`, Captured in
`evidence/01-tenant-authorization-policy-and-application-baseline.md`. The refusal therefore does not
come from the directory's view of the human. **The control still owed is a demonstration of the same
account succeeding on `/users` through a client holding a broader scope.** Until that runs, the claim
rests on the tenant policy rather than on a paired observation.

**2. `User.Read` is now Captured by name.** `scp` prints `User.Read profile openid email`. The
application declared permission id `e1fe6dd8-ba31-4d61-89e7-88639da4683d` and the consent record
stores `" User.Read"`. The name was Recalled off the portal until this claim printed it.

**3. `openid`, `profile` and `email` arrived without being requested.** The scope sent was
`https://graph.microsoft.com/User.Read` alone. Three OpenID Connect scopes were added by the
platform. A reviewer auditing what a client holds must read the token, not the app's declared
permission list; the two differ, and they differ in the permissive direction.

**4. No refresh token was issued, because `offline_access` was not requested.** The access token is
the whole of this client's access. It expires and the client stops, with no silent renewal. For an
agent or a CLI, `offline_access` is the difference between access that ends and access that persists,
and it is one word in a scope string.

**5. `wids` carries the non-guest marker alone, which independently confirms capture 05.** This
account holds no directory role at this moment, and its `wids` holds exactly
`b79fbf4d-3ef9-4689-8143-76b194e85509`. The Global Administrator's token in capture 03 held that
value plus the Global Administrator role template id. A role-holder and a role-less account differ by
the role entry; the marker is constant.

**6. Two refusals with different causes return the same code.** `Authorization_RequestDenied` here is
a scope refusal. The same code was returned to a Global Administrator on
`policies/permissionGrantPolicies` in `evidence/04-...`, where the cause was not established. The code
carries no information about which boundary stopped the call.

**7. The token lifetime is about 72 minutes, and `expires_in` disagrees with the claims.**
`expires_in` reports 4300 seconds. `exp` minus `iat` is 4601 seconds, about five minutes longer,
which is the usual clock-skew allowance. Do not compute a deadline from one of them and compare it to
the other. Capture 03's Graph Explorer token ran 24.08 hours. Same tenant, same user population,
very different lifetimes, which weakens nothing and explains nothing on its own; the Continuous
Access Evaluation hypothesis in capture 03 remains unverified.

## Correction — `aud` does not follow `ver`

**`evidence/03-graph-explorer-token-decoded.md`, finding 4, is wrong and is retracted here.** It read
`aud` `00000003-0000-0000-c000-000000000000` alongside `ver` `1.0` and concluded that "`ver` says
why". This token has `ver` `1.0` and `aud` `https://graph.microsoft.com`. Two tokens, the same token
version, the same resource, two different `aud` forms. The token version does not determine the
`aud` form.

**`CURRICULUM.md`'s Exercise C3 entry carries the same error and it is disproven.** Step 6 of that
entry states that "a v1-formatted token carries Graph's GUID, not the URL, even when requested from
the v2.0 endpoint". This capture is a v1-formatted token from the v2.0 endpoint carrying the URL.

Not established: what does determine the form. This request identified the resource by URL, in
`scope=https://graph.microsoft.com/User.Read`. A request that names the resource by GUID is the
obvious next test, and it has not been run.
