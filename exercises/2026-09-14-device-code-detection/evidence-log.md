# The detection half: what the tenant recorded for two device code runs — evidence log

Opened 2026-09-14T14:54:02Z, from `date -u` on the Mac Mini.

**Hypothesis.** `exercises/2026-09-12-workload-identity-scope-isolation` proved the token is the
boundary and the registration is not. It never asked what the tenant recorded while that happened.
This exercise asks whether a defender reading the tenant's own logs can see a device code sign-in,
name the client and the flow, and see a consent grant widen. C3's finding says the widening is
invisible where an administrator looks. If it is also invisible in the audit surface, the exposure
is larger than C3 recorded.

**Why now.** The P2 trial ends about 2026-10-04. `auditLogs/signIns` is gated on it. The events are
already written and cannot be recaptured after the endpoint closes.

## The events under test, from the C3 record

| | Run 1 | Run 2 |
|---|---|---|
| Token issued | 2026-09-13T01:07:50Z | 2026-09-13T01:22:28Z |
| Client `appId` | `388b9dd8-d98f-46f3-8eed-4418346e5673` | same |
| Signed-in `oid` | `03ee6546` (`adm-jsmith`) | same |
| `scp` | `User.Read` | `User.Read User.ReadBasic.All` |
| Consent | `consentType: Principal` | grant amended in place, id unchanged |

Sources: `exercises/2026-09-12-workload-identity-scope-isolation/evidence/07-device-code-token-bounds-the-signed-in-user.md`,
`exercises/2026-09-12-workload-identity-scope-isolation/evidence/10-one-variable-changed-and-the-refusal-became-a-success.md`,
`exercises/2026-09-12-workload-identity-scope-isolation/evidence/11-the-grant-grew-and-the-registration-did-not.md`.

## Questions this exercise must answer

1. Does a device code sign-in appear in the interactive stream, the non-interactive stream, both, or
   neither?
2. Does the entry name the client application and the authentication flow?
3. Does `directoryAudits` write one consent event or two for one amended `oauth2PermissionGrant`?
4. Does any record distinguish run 2's wider scope from run 1's?

## Captured

- **A device code flow writes to both sign-in streams, in a fixed four-step order.** Interactive
  `errorCode` 65001, then three `directoryAudits` consent events, then interactive `errorCode` 0,
  then the non-interactive token redemption. Run 1 spans 01:07:40Z to 01:07:50Z; run 2 spans
  01:22:08Z to 01:22:28Z. The `correlationId` joins the streams.
  `evidence/03-the-interactive-stream-holds-the-flow-and-cannot-name-it.md`.
- **Only the non-interactive token event names the flow, and only on `beta`.**
  `originalTransferMethod` reads `"deviceCodeFlow"` there. `authenticationProtocol` and
  `incomingTokenType` both read `"none"`. v1.0 returns no such property at all, so the interactive
  records show a successful sign-in to a named application and nothing about the flow.
  `evidence/01-device-code-lands-in-the-non-interactive-stream.md` and `evidence/03`.
- **`userAgent` differs between the two streams for one run.** Firefox on the interactive records,
  `curl/8.7.1` on the token event. That split is the device code flow itself. `evidence/01`, `03`.
- **MFA was completed interactively on both runs, and the token event inherited it.**
  `"MFA completed in Azure AD"` with the iOS Authenticator named, then `"Previously satisfied"` on
  the redemption. `evidence/03`.
- **`errorCode` 65001 opens every run and is not an incident.** It reads "the user or administrator
  has not consented", four seconds before the consent is written. `evidence/03`.
- **The sign-in log records the requested scope, and the two runs differ in it.**
  `authenticationProcessingDetails` carries `Oauth Scope Info`: run 1 `User.Read`, run 2
  `User.Read` plus `User.ReadBasic.All`. Same file.
- **Conditional Access evaluated the device code sign-in, and the block-legacy-authentication
  policy did not apply.** `75882b6a` returns `notApplied` with `conditionsNotSatisfied`
  `clientType`. C3 asserted this from reasoning; it is now Captured. `d9a6a116` returns
  `reportOnlyFailure` on both runs. Same file.
- **A third device code redemption exists that C3 never recorded.** `adm-jsmith` into Graph
  Explorer at 01:15:37Z, `originalTransferMethod` `deviceCodeFlow`, sharing run 1's `sessionId`.
  Same file.
- **One amended consent writes three `directoryAudits` events in 13 milliseconds, and the event
  named `Consent to application` shows no change.** Its `ConsentAction.Permissions` reads
  `Scope:  User.Read` on both sides of the `=>`. The change appears only in
  `Add delegated permission grant` and `Remove delegated permission grant`.
  `evidence/02-three-audit-events-and-the-one-named-consent-hides-the-widening.md`.
- **The same event type reports a first consent correctly and an amendment incorrectly.** Run 1's
  `Consent to application` reads `[] => [... User.Read ...]`. Run 2's does not. Same file.
- **An `Unassign` operation recorded an addition.** `Remove delegated permission grant` carries the
  same scope growth as the `Assign` event beside it. Same file.
- **`initiatedBy.user.displayName` names `Azure ESTS Service` while `id` and `userPrincipalName`
  name `adm-jsmith`, and `ipAddress` is a Microsoft address.** Same file.
- **`P2P Server` is a tenant-local registration, not a Microsoft first-party object, and it appeared
  three seconds after VM 101's Entra join.** `appOwnerOrganizationId` this tenant, `publisherDomain`
  this tenant's default domain, `signInAudience` `AzureADMyOrg`, `servicePrincipalNames` holding
  `urn:p2p_cert`, `tags` empty. `evidence/04-p2p-server-is-a-tenant-local-registration.md`.
- **No `directoryAudits` record for 2026-09-04 survives as of 2026-09-14.** Three filters returned
  empty, including the whole day, on a day that carried four audit-writing actions. The empty result
  is evidence about retention. `evidence/05-no-audit-record-of-p2p-server-survives-today.md`.

## Not captured, and why

- ~~The v1.0 interactive sign-in read.~~ **Captured 2026-09-14 in `evidence/03`**, and it disproved
  the claim this entry was written to support. See Corrections.
- **`P2P Server`'s provenance.** Needs its object id first, then a `targetResources` filter. A
  different thread, queued inside the same trial window.
- **Whether a refused privileged action appears in any sign-in stream.** Carried from
  `2026-09-09-pim-for-groups` and not addressed by this window.

## Where Raymond was consulted

- **The redaction set for these two captures.** Flagged 2026-09-14 before either file was written.
  The Global Administrator's display name and UPN, the operator's IP address, and every `location`
  object are redacted under standing rules and existing precedent. An Apple push notification token
  for a personal handset and a `User.PUID` are redacted as new cases. His decision is recorded in
  the next session turn.

## Corrections

- **Claude wrote a finding from one stream and called it a property of the flow, and the missing
  read disproved it.** `evidence/01` stated that neither device code run appears in the interactive
  log. Four interactive records for that client exist. The error was available to catch at the
  time: the v1.0 read had been issued and its response had not come back, and the file was written
  anyway with the gap named only in "Not captured". The rule this breaks is the repository's own —
  an outstanding read is not a negative result. Both affected claims in `evidence/01` are struck in
  place and corrected, not deleted.
- **A second claim in `evidence/01` was too wide rather than wrong.** It read the token event's
  `"Previously satisfied"` as proof that no MFA prompt occurred. `evidence/03` shows the prompt one
  leg earlier. Narrowed in place.
- **Claude compressed captured output in evidence 01, 02 and 03, and the files were committed and
  pushed before it was caught.** Seven kinds of compression, itemised in
  `evidence/06-corrected-full-captures-superseding-01-02-03.md`: truncated GUIDs, reduced
  Conditional Access blocks, one summarised scope list, one ellipsized `userAgent`, dropped
  `modifiedProperties` and `additionalDetails`, compressed record blocks, and one broken path
  reference. The motive was readability, and it is not a permitted motive. No finding changed.
- **The first repair attempt broke a second rule.** Claude rewrote the three closed evidence files
  in place. `validate.py` refused with `evidence-modified`. An exercise with a `report.md` is
  closed, its evidence is frozen, and added files are the sanctioned route. The edits were reverted
  and `evidence/06` was added instead.
- **The two rules conflict for one case, and it is now open.** `evidence/01` holds a path that does
  not resolve. It cannot be corrected in place, so `validate.py` carries a standing
  `reference-missing` ERROR. `evidence/06` states the correct path. Raymond's decision, recorded in
  `CARRYOVER.md`.

- **The stale-response-body defect fired a third time, and the body was `#users/$entity` again.**
  `GET /v1.0/applications(appId='004ad450-5909-445f-969a-d3798ab41880')` returned the signed-in
  user's own object, with `@odata.context` `#users/$entity`. That context cannot be produced by an
  `applications` request. The two prior occurrences, on 2026-09-09 and 2026-09-10, also returned
  `#users/$entity` in place of a `roleManagementPolicies` read. Three occurrences, one body shape.
  The stale body is not arbitrary: it is the shape Graph Explorer fetches to render its own account
  chip. That narrows the cause from "unknown" to "the tool's own profile request is reaching the
  response pane", which is a hypothesis this exercise has not tested. Not captured as an evidence
  file; recorded here and owed to `references/gotchas.md`. Response discarded, re-run requested.

- **A standing gotcha does not hold, and this exercise disproves it.**
  `references/gotchas.md` says a platform-initiated audit entry names a non-human actor with a null
  `userPrincipalName` and a null `ipAddress`, and to read the null `ipAddress` as the signal. Six
  consent events here name `Azure ESTS Service` as `initiatedBy.user.displayName` while carrying a
  populated `userPrincipalName` and a populated `ipAddress`. The signal does not fire, and the
  populated address is a Microsoft service address rather than the actor's. The rule is narrower
  than it was written.

## Open questions

- Carried from C3 and not yet addressed here: who created `P2P Server`, appId
  `004ad450-5909-445f-969a-d3798ab41880`, on 2026-09-04T00:35:35Z. It needs the same endpoint and the
  same trial window, so it is queued behind the four questions above.

## Not started

- **The retention boundary read.** One read of the oldest surviving `directoryAudits` event fixes
  it. Parked at Raymond's direction on 2026-09-14 after three empty responses and four Graph
  Explorer defects in one session: "park it, write the report". The Entra admin center's Audit logs
  blade answers it without Graph Explorer.
- **Whether the Entra join created the `P2P Server` objects.** A second device join, watched live,
  answers this and the retention question together. Not attempted.
