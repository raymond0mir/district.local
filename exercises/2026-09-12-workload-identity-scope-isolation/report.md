# Workload identity scope isolation: the token is the boundary, the registration is not

## What I set out to do

Test whether an access token bounds a client below the rights of the human who signed in. The plan
was to register an application restricted to one delegated scope, authenticate a privileged user
through the device code flow, and show that Microsoft Graph refuses a directory read the user is
otherwise permitted to make. `CURRICULUM.md`'s Exercise C3 states the hypothesis as "an app
registration restricted to one delegated scope produces an access token that Microsoft Graph
enforces, regardless of the signed-in user's own administrative rights."

Half of that is right. The premise in the first clause is wrong, and proving it wrong turned out to
be the more useful result.

## The setup

The `district.local` tenant, chosen over a throwaway tenant so the test would run against a directory
already carrying PIM, Conditional Access and Entra Connect state. No VM was involved; this exercise is
entirely tenant-side. Tools were Graph Explorer in a browser and Terminal, both on the Mac Mini.

Pre-flight, read before anything was created:

- The tenant's authorization policy and its full application inventory
  (`evidence/01-tenant-authorization-policy-and-application-baseline.md`). `allowedToCreateApps` is
  `true`, so any member can register a workload identity here without an administrator.
  `allowedToReadOtherUsers` is `true`, which matters because it means a directory read refusal cannot
  be blamed on the human by default.
- Conditional Access state, read from `exercises/2026-09-05-b1-security-defaults-transition/`. MFA for
  all users is `enabled` and `adm-jsmith` is not excluded, so the sign-in would be challenged. Block
  legacy authentication is `enabled` but scoped to `exchangeActiveSync` and `other`, and device code
  flow is neither. No policy carries an `authenticationFlows` condition.

Two accounts, two jobs. The native Global Administrator (`6ca413e3`) registered the application and
ran every validation read. `adm-jsmith` (`03ee6546`) signed into the device code client. A plain
member account would have made the negative test meaningless, because a refusal only carries
information when the human could otherwise have succeeded.

## What I did

1. Read the tenant baseline and the application inventory.
2. Tried to read the tenant's permission grant policies, to learn what a member may consent to. Three
   attempts, three refusals. See "What broke, and why".
3. Decoded Graph Explorer's own access token to establish who was signed in and what scopes the token
   carried (`evidence/03-graph-explorer-token-decoded.md`).
4. Registered `Lab-AI-Agent-CLI` in the Entra admin center: single tenant, no redirect URI, public
   client flows enabled, one delegated permission, no admin consent. The portal build is Recalled.
5. Made it Captured with two Graph reads
   (`evidence/06-lab-ai-agent-cli-registered-and-verified.md`):

   ```
   GET https://graph.microsoft.com/v1.0/applications(appId='388b9dd8-d98f-46f3-8eed-4418346e5673')?$select=id,appId,displayName,signInAudience,isFallbackPublicClient,createdDateTime,publicClient,requiredResourceAccess
   GET https://graph.microsoft.com/v1.0/servicePrincipals(appId='388b9dd8-d98f-46f3-8eed-4418346e5673')?$select=id,appId,displayName,servicePrincipalType,accountEnabled
   ```

6. Ran the device code flow requesting `https://graph.microsoft.com/User.Read`, then called
   `GET /v1.0/me`, `GET /v1.0/users?$top=3` and `GET /v1.0/directoryRoles` with the resulting token
   (`evidence/07-device-code-token-bounds-the-signed-in-user.md`).
7. Attempted a paired control by signing Graph Explorer in as `adm-jsmith`. It failed; see below.
8. Ran the flow a second time requesting `https://graph.microsoft.com/User.ReadBasic.All`, changing
   one variable and nothing else
   (`evidence/10-one-variable-changed-and-the-refusal-became-a-success.md`).
9. Read the consent grant and the application registration side by side
   (`evidence/11-the-grant-grew-and-the-registration-did-not.md`).

Every HTTP call in steps 6 and 8 ran inside one script, so the access token never reached a file, a
screen, or a chat window. Secrets were passed to `curl` on stdin rather than on the command line, so
no token appeared in the process list.

## Where Raymond was consulted

- **Which tenant runs this.** `CURRICULUM.md` schedules the question and does not answer it. Claude
  recommended `district.local`, because a throwaway tenant isolates the test and produces no contrast
  with the rest of the lab. Raymond: "lets use our tenant". He accepted the cost, one application
  object and one service principal in a tenant under audit.
- **Which account signs into the client.** Claude recommended `adm-jsmith` with its User Administrator
  role activated. Raymond: "good for adm-jsmith", and he confirmed he could activate the role.
- **Dropping the PIM activation from the first run.** Claude changed the agreed design and said so
  before the run, not after. `allowedToReadOtherUsers: true` already made the refusal attributable to
  the token, and activation costs an approval round trip through a second browser session. The
  activated run is still owed.
- **Moving the build into the portal.** After three refused reads and a permissions panel that would
  not load, Raymond: "i have feeling we are stucking on graph, cant we just do this shit clicking
  around entra then validate in graph after?" He was right, and the repository already prescribes that
  pattern: a portal action is Recalled, and a Graph read after it makes the claim Captured.

## What the box said

The two runs, fifteen minutes apart, with the scope as the only difference:

| | Run 1, 01:07:50Z | Run 2, 01:22:28Z |
|---|---|---|
| Client `appid` | `388b9dd8` | `388b9dd8` |
| Signed-in `oid` | `03ee6546` | `03ee6546` |
| `wids` | `b79fbf4d` only | `b79fbf4d` only |
| `scp` | `User.Read profile openid email` | `User.Read User.ReadBasic.All profile openid email` |
| `GET /v1.0/me` | 200 | 200 |
| `GET /v1.0/users?$top=3` | **403** | **200** |
| `GET /v1.0/directoryRoles` | 403 | 403 |

The refusal, in full:

```
GET https://graph.microsoft.com/v1.0/users?$top=3
HTTP 403
{"error":{"code":"Authorization_RequestDenied","message":"Insufficient privileges to complete the operation.",
 "innerError":{"date":"2026-09-13T01:07:50","request-id":"a751c943-d15b-4342-8aa2-b3ba73c13ed7"}}}
```

The consent grant, after both runs, beside the registration read at the same time:

```json
{ "consentType": "Principal", "principalId": "03ee6546-...", "scope": " User.Read User.ReadBasic.All" }
```

```json
{ "displayName": "Lab-AI-Agent-CLI",
  "requiredResourceAccess": [ { "resourceAppId": "00000003-0000-0000-c000-000000000000",
    "resourceAccess": [ { "id": "e1fe6dd8-ba31-4d61-89e7-88639da4683d", "type": "Scope" } ] } ] }
```

Three things follow from those two bodies.

**The token is the boundary.** `adm-jsmith` held no directory role in either run. Graph enforced the
token, not the person, and the boundary moved by exactly one permission rather than collapsing:
`directoryRoles` stayed refused.

**The registration is not the boundary.** Nobody edited `Lab-AI-Agent-CLI` between the runs. It
declares one delegated permission and it still declares one. The client asked the token endpoint for a
second scope, an ordinary member consented, and the token carried it. A declared permission list drives
the consent prompt and the portal's admin-consent button. It is not a runtime ceiling.

**The growth is invisible where an administrator looks.** Entra amended the existing grant rather than
creating a second one; the grant id is byte-identical across
`evidence/08-user-consent-recorded-as-principal.md` and `evidence/11-...`. A control that counts
consent grants sees one before and one after. The change is inside a space-delimited string, on an
object with no per-scope timestamp, while the API permissions blade an administrator reviews still
reads one permission.

That is this lab's permission-sprawl thesis at the workload layer: access that widens without anyone
with authority acting, and without the interface that represents it changing.

## What broke, and why

**Three attempts to read the tenant's consent policy were refused, and the cause is still open.**
`GET /policies/permissionGrantPolicies` and two `/includes` reads returned `403
Authorization_RequestDenied` to a Global Administrator whose token carried `Directory.Read.All`.
Microsoft Learn lists `Directory.Read.All` as the higher-privileged permission for the `/includes`
path. The token did not carry `Policy.Read.PermissionGrant`, the least-privileged one, and Graph
Explorer's permissions panel would not load, so it could not be consented. The positive control was
never obtained. See `evidence/04-global-administrator-refused-on-permission-grant-policies.md`. The
device code flow answered the underlying question anyway, and answered it better: `consentType:
Principal` proves a member consented without an administrator.

**Graph Explorer's address bar keeps its previous contents.** A paste landed beside stale text and
produced `.../permissionGrantPoliciess://graph.microsoft.com/`, which returned `400 BadRequest`
naming a segment nobody typed. A `400` there describes the typing, not the tenant.

**Python hung where `curl` did not.** `urllib.request.urlopen` blocked in `sock.connect(sa)` with no
timeout, on a host where `curl` reached the same endpoint in 0.6 seconds. The traceback named the
blocking call. Every HTTP call was moved to `curl` rather than diagnosed further.

**The paired control failed because the browser session never switched accounts.** Signing out of
Graph Explorer and signing back in re-authenticated the same account through browser SSO. The `/users`
read that was supposed to come from `adm-jsmith` came from the Global Administrator, and the token
decode is what caught it. See `evidence/09-control-attempt-failed-session-never-switched.md`. That
failure produced the better experiment: instead of changing the client and holding the user, change
the scope and hold both.

**Claude stated a cause from a single observation, and the next capture disproved it.**
`evidence/03-...` finding 4 concluded that `aud` carried Graph's GUID because `ver` was `1.0`. The
device code token is also `ver` `1.0` and carries `https://graph.microsoft.com`. Two tokens, one
version, two forms. The finding is struck in place and retracted in `evidence/07-...`.
`CURRICULUM.md`'s C3 entry carries the same error, sourced from the same external outline, and it is
disproven by this exercise's evidence.

**Claude designed two sequences around reading an account chip instead of capturing an identity.**
The first left the signing identity unrecorded across two evidence files, corrected later from a token
decode. The second produced the failed control above. The same lesson had to arrive twice in one
exercise.

**One baseline was lost.** The `oauth2PermissionGrants` read was requested before the first sign-in and
run after it, so it captures the grant's existence rather than its absence beforehand.

## What I'd do differently

Establish the signing identity from the token, before running anything that depends on it. A chip is a
screenshot; a token is evidence. Two failures in one exercise came from that single substitution.

State a mechanism only when a second observation can vary it. The `aud` claim had one data point and
got a causal explanation, which the next token removed.

Take the baseline before the state change, not after. The pre-consent read was cheap and is now
unrecoverable except through audit logs.

On this host, reach the network with `curl` from the start. The Python standard library's default of
blocking forever on connect is not something to discover mid-flow.

## Open questions

- What does the tenant log for a device code sign-in, and does the entry name the client app and the
  flow? This is the detection half of the loop and it is not started. `auditLogs/signIns` needs the P2
  trial, which ends about 2026-10-04.
- Does `directoryAudits` show two separate consent events for one amended grant? Finding 2 of
  `evidence/11-...` predicts it and does not capture it.
- What would `offline_access` change? Neither run received a refresh token, because neither asked. For
  an agent, that word is the difference between access that ends in 72 minutes and access that
  persists.
- Would a scope requiring admin consent be refused to `adm-jsmith` at sign-in? Reasoning says yes.
  No capture says so.
- What determines the `aud` form? Run 1 and run 2 named the resource by URL. A request naming it by
  GUID is the obvious next test.
- Does the same pair of runs behave differently with User Administrator activated through PIM? The
  activated pass is owed, and it is the maximal version of the negative test.
- Why is `GET /policies/permissionGrantPolicies` refused to a Global Administrator holding
  `Directory.Read.All`? Unresolved, and the positive control remains blocked by the permissions panel.
- Who created `P2P Server`, appId `004ad450-5909-445f-969a-d3798ab41880`, on 2026-09-04? Surfaced by
  the baseline read. No exercise records creating it.
