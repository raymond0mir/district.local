# Workload identity scope isolation: device code flow, audited at the token — evidence log

Exercise C3, `CURRICULUM.md`. Opened 2026-09-12T16:04:19Z, from `date -u` on the Mac Mini.

**Hypothesis.** An app registration restricted to one delegated scope produces an access token
that Microsoft Graph enforces, whatever administrative rights the signed-in user holds. The token
is the boundary, not the human.

## Captured

- **The tenant's authorization policy, and the application inventory before this exercise.** Four
  application registrations exist and none is `Lab-AI-Agent-CLI`. `allowedToCreateApps` is `true`,
  so any member account in this tenant can register a workload identity without an administrator.
  `allowedToCreateTenants` and `allowedToReadOtherUsers` are also `true`. User consent is not
  switched off; two `ManagePermissionGrantsForSelf` policies are assigned.
  `evidence/01-tenant-authorization-policy-and-application-baseline.md`.
- **Both permission grant policy reads refused at 403 `Authorization_RequestDenied`**, 28 seconds
  apart. The code names neither cause. `evidence/02-permission-grant-policy-reads-refused.md`.
- **Graph Explorer's own access token, decoded.** Signing identity is the native Global
  Administrator, `6ca413e3`, with the Global Administrator role template id in `wids`. `aud` carries
  Graph's GUID and `ver` is `1.0`, as C3 predicted. The token lifetime is 24.08 hours. `scp` holds
  `Directory.Read.All` and not `Policy.Read.PermissionGrant`.
  `evidence/03-graph-explorer-token-decoded.md`.
- **The Global Administrator is refused `GET /policies/permissionGrantPolicies` at 403**, holding a
  token with `Directory.Read.All` and without `Policy.Read.PermissionGrant`. The path parsed; a
  malformed path on the same endpoint returns 400.
  `evidence/04-global-administrator-refused-on-permission-grant-policies.md`.
- **`b79fbf4d-3ef9-4689-8143-76b194e85509` is not a directory role**, and `roleDefinitions` returns
  `Request_ResourceNotFound` for it under a Global Administrator's token. Entra sends it in `wids`
  for every non-guest account. Closes an open question carried since 2026-09-09.
  `evidence/05-wids-b79fbf4d-is-not-a-role.md`.
- **`Lab-AI-Agent-CLI` exists as two objects, and Graph confirms every property the portal claimed.**
  Application `e15012f9`, service principal `4c43a528`, client id `388b9dd8`. Single tenant, public
  client, no redirect URI, one declared delegated scope.
  `evidence/06-lab-ai-agent-cli-registered-and-verified.md`.
- **The device code token refuses what its user is permitted to do.** `scp` `User.Read`, `GET /me`
  returns 200, `GET /users` and `GET /directoryRoles` both return 403, all inside the same second.
  `evidence/07-device-code-token-bounds-the-signed-in-user.md`.
- **The consent is user consent.** `consentType: Principal`, granted by `adm-jsmith` for
  `" User.Read"` alone, with no administrator involved.
  `evidence/08-user-consent-recorded-as-principal.md`.
- **The paired control failed: Graph Explorer's sign-out did not switch accounts.** The `/users` read
  intended for `adm-jsmith` came from the Global Administrator, proven by a token decode.
  `evidence/09-control-attempt-failed-session-never-switched.md`.
- **Same client, same user, one scope different: 403 became 200.** Run 2 requested
  `User.ReadBasic.All`, an ordinary member consented, and `GET /users` succeeded where it had been
  refused fifteen minutes earlier. `directoryRoles` stayed refused.
  `evidence/10-one-variable-changed-and-the-refusal-became-a-success.md`.
- **The consent grant grew to two scopes while the registration still declares one**, and Entra
  amended the existing grant rather than creating a second. The grant id is identical across captures
  08 and 11. `evidence/11-the-grant-grew-and-the-registration-did-not.md`.

## Not captured, and why

- **What each assigned `ManagePermissionGrantsForSelf` policy admits.** Three reads were refused,
  and Graph Explorer's permissions panel will not load, so `Policy.Read.PermissionGrant` cannot be
  consented in the tool. The question is left to the device code sign-in, which answers it
  empirically. Stopped deliberately after one retry.
- **The positive control on the 403.** Consenting `Policy.Read.PermissionGrant` and getting `200`
  on the same URL would close capture 04's remaining alternative explanation. The broken panel
  blocks it.
- ~~The paired control for capture 07.~~ **Captured 2026-09-13 in capture 10**, by changing the scope
  and holding the client and the user constant, after the client-swap version failed in capture 09.
- **`directoryAudits` evidence that one amended grant produces two consent events.** Predicted in
  capture 11, not read.
- **The sign-in log entry for either device code run.** Not started. It is the detection half of the
  loop, and `auditLogs/signIns` needs the P2 trial, which ends about 2026-10-04.
- **The pre-consent baseline.** The `oauth2PermissionGrants` read ran after the sign-in, not before.
  Capture 08 records the gap.
- **Whether the access token was pasted into the jwt.ms tab open beside Graph Explorer.** Asked
  twice, unanswered at the time of writing. The record says not established.
- **Whether this tenant issues Continuous Access Evaluation tokens.** The 24.08-hour lifetime in
  capture 03 is consistent with CAE and proves nothing by itself.

## Where Raymond was consulted

- **Which tenant runs this exercise. Asked 2026-09-12. Answered the same day: the `district.local`
  tenant.** `CURRICULUM.md` schedules this question and does not decide it. Claude recommended
  `district.local`, because the exercise tests scope isolation against a directory that already
  carries PIM, Conditional Access and Entra Connect state. A throwaway tenant isolates the test and
  produces no contrast. Raymond: "lets use our tenant". Cost accepted: one application object and
  one service principal added to a tenant under audit, to be removed at teardown.
- **Which account signs into the device code client. Asked 2026-09-12. Answered the same day:
  `adm-jsmith` (`03ee6546`), with its User Administrator role activated through PIM.** Claude
  recommended it over a plain member account, because a refusal only carries meaning when the
  signed-in human could otherwise succeed. Raymond: "good for adm-jsmith", and he confirmed he can
  activate the role when the negative test runs. The native Global Administrator (`6ca413e3`)
  registers the app and grants consent, and never signs into the client. It is excluded from the
  MFA Conditional Access policy, so a sign-in by it would skip MFA and would not represent a normal
  administrator.

- **Dropping the PIM activation from the first run. Changed by Claude, stated before the run.** The
  entry above records User Administrator activated through PIM as the agreed design. That activation
  did not happen in either run, and both tokens carry `wids` `b79fbf4d` alone, with no directory
  role. Claude changed the design and said so before running, not after: `allowedToReadOtherUsers`
  is `true`, so the refusal was already attributable to the token rather than to the human, and the
  activation costs an approval round trip through a second browser session. **The activated pass is
  still owed**, and it is the maximal version of the negative test.
  `evidence/07-device-code-token-bounds-the-signed-in-user.md`.

## Corrections

- **The signing identity of captures 01 and 02 was recorded as not captured, and it is now
  Captured.** Claude wrote the sequence with a step that read the Graph Explorer account chip, and
  did not stop when the answer came back missing. The token decode closed the gap afterward. Both
  files are corrected on the record, not silently. The correct order is to establish the signing
  identity before the reads, not after.
- **Claude's decode command failed on its first run, and the cause was not the one C3 predicted.**
  The curriculum warns that base64url characters break a naive decode. This failure was earlier
  than that: the clipboard did not hold a JWT, and the traceback pointed at base64 anyway. A
  guarded script now reports the clipboard length and segment count before it decodes. Check what
  you decoded before you trust what it says.

## Pre-flight read from the record, 2026-09-12

Conditional Access will not block a device code sign-in, and it will demand MFA of `adm-jsmith`.
Read from `exercises/2026-09-05-b1-security-defaults-transition/evidence/04-confirmation-read-and-gap-timing.md`:
`365bdd23` (MFA for all users) is `enabled`, `75882b6a` (block legacy auth) is `enabled` and scoped
to `exchangeActiveSync` and `other`, and `d9a6a116` (compliant or hybrid device) is still
`enabledForReportingButNotEnforced`. Device code flow is not a legacy client, so `75882b6a` does not
catch it. No policy carries an `authenticationFlows` condition, read from the three creation
captures in `exercises/2026-09-04-b1-security-defaults-and-ca-report-only/evidence/`. Only the
break-glass account is excluded from `365bdd23`. This is a read of prior evidence, not a fresh
capture; a live re-read is owed if a sign-in behaves differently.

## Open questions

- Does the tenant's user-consent policy refuse the device code flow before the app's own scope
  matters? `AADSTS65001` at sign-in would answer yes. Sequence 1 reads the policy first.
- ~~Does `aud` carry Graph's GUID or its URL? The manifest's `accessTokenAcceptedVersion` decides
  this.~~ **Answered and the premise was wrong, 2026-09-13.** Both forms appeared in this exercise on
  `ver` `1.0` tokens. What determines the form is not established. This request named the resource by
  URL in its scope string; a request naming it by GUID is the obvious next test.
- What does the tenant log for a device code sign-in, and does the log name the client app? The P2
  trial admits `auditLogs/signIns` until about 2026-10-04. This is the detection half of the loop and
  it is not started.
- Does requesting `offline_access` change what this client can do after the token expires, and what
  does a refresh token look like in the tenant's own records?
- Would a scope requiring admin consent be refused to `adm-jsmith` at sign-in? Capture 08 answers the
  consent question for `User.Read` only.
- **Who created `P2P Server`, appId `004ad450-5909-445f-969a-d3798ab41880`, on
  2026-09-04T00:35:35Z?** No exercise in `exercises/` records creating it. Its provenance is not
  captured, and a first-party explanation for it is Recalled, not established. One
  `auditLogs/directoryAudits` read filtered on the object settles it, and the P2 trial that admits
  that endpoint ends 2026-10-04. This is the permission-sprawl pattern inside the lab's own tenant:
  an application object nobody's record accounts for.

## Not started

**This section is retired, 2026-09-14.** It recorded a mid-exercise pause on 2026-09-12 and was not
updated when the exercise resumed on 2026-09-13. Two of its three items completed. The section is
kept on the record rather than deleted, under the standing rule against silent edits.

~~Paused at Raymond's request, 2026-09-12, before the app registration.~~

- ~~Resolving the 403.~~ **Still open, and recorded elsewhere.** Two candidates remain: the
  least-privileged scope is genuinely required, or Graph Explorer returned a stale body. "Not
  captured, and why" already carries this as the blocked positive control. It is not a Not-started
  item.
- ~~The app registration itself.~~ **Completed 2026-09-12.** Built in the Entra admin center at
  Raymond's direction: "cant we just do this shit clicking around entra then validate in graph
  after?" The portal action was Recalled, and the Graph reads after it made the claim Captured.
  `evidence/06-lab-ai-agent-cli-registered-and-verified.md`.
- ~~The device code request, the token decode, and the positive and negative Graph calls.~~
  **Completed 2026-09-13, across two runs fifteen minutes apart.**
  `evidence/07-device-code-token-bounds-the-signed-in-user.md`,
  `evidence/10-one-variable-changed-and-the-refusal-became-a-success.md`.
