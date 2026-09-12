# Graph Explorer's own access token, decoded

```
Command: python3 <scratchpad>/decode-token.py, reading the clipboard
Host:    Terminal on the Mac Mini
UTC:     token iat 2026-09-12T16:25:16Z, exp 2026-09-13T16:30:16Z, both from the payload
```

The script prints non-secret claims only. It prints no name claim, no UPN claim, and no part of the
token. The token itself never entered a file, a chat window, or a web page.

```
clipboard characters: 3428
dot-separated segments: 3
looks like a JWT: True
header alg: RS256  typ: JWT

{
  "aud": "00000003-0000-0000-c000-000000000000",
  "appid": "de8bc8b5-d9f9-48b1-a8ad-b748da725064",
  "app_displayname": "Graph Explorer",
  "scp": "AgentIdUser.ReadWrite.All AgentIdUser.ReadWrite.IdentityParentedBy AuditLog.Read.All Directory.Read.All Directory.ReadWrite.All IdentityRiskyUser.Read.All openid Policy.Read.All Policy.ReadWrite.ConditionalAccess Policy.ReadWrite.SecurityDefaults PrivilegedAccess.ReadWrite.AzureAD PrivilegedAssignmentSchedule.Read.AzureADGroup PrivilegedEligibilitySchedule.ReadWrite.AzureADGroup profile RoleEligibilitySchedule.ReadWrite.Directory RoleManagement.ReadWrite.Directory RoleManagementPolicy.ReadWrite.Directory User.EnableDisableAccount.All User.Read User.Read.All User.ReadBasic.All User.ReadWrite.All UserAuthenticationMethod.Read UserAuthenticationMethod.Read.All email Application.Read.All",
  "roles": null,
  "wids": [
    "62e90394-69f5-4237-9190-012177145e10",
    "b79fbf4d-3ef9-4689-8143-76b194e85509"
  ],
  "oid": "6ca413e3-06ff-4704-ab36-1348bb7387c8",
  "tid": "e0b13496-83d1-4721-8bf9-f965f676106f",
  "ver": "1.0",
  "iat": 1789230316,
  "exp": 1789317016
}
```

---

## Findings

**1. The signing identity is Captured, and it is the native Global Administrator.** `oid`
`6ca413e3-06ff-4704-ab36-1348bb7387c8` is the account `verified-claims.md` already records as the
tenant's native Global Administrator. `wids` carries `62e90394-69f5-4237-9190-012177145e10`, the
Global Administrator role template id, already Confirmed in the ledger from
`exercises/2026-09-06-b4-pim-eligible-role`. Captures 01 and 02 are corrected from Recalled to
Captured on this evidence.

**2. A role template id in `wids` is still unidentified, and this is the second time it has
appeared.** `b79fbf4d-3ef9-4689-8143-76b194e85509` is an open question in
`exercises/2026-09-09-pim-for-groups/report.md`, where it appeared on `adm-jsmith`. It now appears
on the Global Administrator as well. Two accounts, different privilege, same value.

**3. The token carried `Directory.Read.All` when both permission-grant reads were refused.** The
token was issued at 16:25:16Z. The refusals are stamped 16:35:05Z and 16:35:33Z, inside this
token's validity. Microsoft Learn lists `Directory.Read.All` as the higher-privileged permission
for `GET /policies/permissionGrantPolicies/{id}/includes`, with `Policy.Read.PermissionGrant` as
least privileged. The signed-in user also holds Global Administrator. **The documented alternative
did not admit the call.** `scp` does not carry `Policy.Read.PermissionGrant`. Unresolved: whether
consenting the least-privileged scope admits it, and therefore whether the documented
higher-privileged alternative is wrong for this path.

**4. `aud` carries Microsoft Graph's GUID, not its URL, and `ver` says why.** `aud` is
`00000003-0000-0000-c000-000000000000` and `ver` is `1.0`. `CURRICULUM.md`'s C3 entry predicted this
form and named the cause, the app manifest's `accessTokenAcceptedVersion`. The prediction holds for
Graph Explorer's own client. The device code client's own token is a separate read.

**5. The token lifetime is 24.08 hours, not the usual hour.** `exp` minus `iat` is 86,700 seconds.
A long lifetime of this shape is associated with Continuous Access Evaluation, which trades a
longer token for near-real-time revocation. **That attribution is not verified.** No capture in this
repository establishes whether this tenant issues CAE tokens. It matters for the exercise: token
lifetime and revocability are the controls that bound a workload identity after consent is granted.

## Not proven here

- Why the refusal happened. Finding 3 states the contradiction and does not resolve it.
- What `b79fbf4d-3ef9-4689-8143-76b194e85509` is.
- Whether CAE explains the lifetime.
