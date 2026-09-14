# The detection half: a device code flow writes four records, and the one named "Consent" hides the change

## What I set out to do

`exercises/2026-09-12-workload-identity-scope-isolation` proved that an access token bounds a client
below the rights of the human who signed in, and that the application registration does not. It
never asked what the tenant recorded while that happened. This exercise asks whether a defender
reading the tenant's own logs can see a device code sign-in, name the client and the flow, and see a
consent grant widen.

C3 concluded that the widening is invisible where an administrator looks. That is half right, and
the half that is wrong is the more useful result.

## The setup

The `district.local` tenant. No VM was involved. The events under test were already written: two
device code runs on 2026-09-13, at 01:07:50Z and 01:22:28Z, by `adm-jsmith` (`03ee6546`) through
`Lab-AI-Agent-CLI` (appId `388b9dd8`, service principal `4c43a528`).

Pre-flight, read before anything else:

- **The signing identity, from Graph rather than from the account chip.** `GET /v1.0/me?$select=id`
  returned `6ca413e3`, the native Global Administrator. C3 lost a control by reading an account chip
  instead. `id` alone was selected, because this repository does not publish that account's name.
- **The licence, because the endpoint is gated on it.** `GET /v1.0/subscribedSkus` returned
  `AAD_PREMIUM_P2`, `capabilityStatus` `Enabled`, one unit consumed of one hundred.

**Why this exercise ran now.** The P2 trial ends about 2026-10-04. `auditLogs/signIns` is gated on
it. The events were already written and cannot be recaptured after the endpoint closes. That
reasoning turned out to understate the problem: one of the questions asked here had already expired,
and the exercise found that out by asking.

The scope was not a blocker. C3 was stopped by a permissions panel that would not load, but
`AuditLog.Read.All` appears in five prior captures in this repository, so it was already consented.

## What I did

1. Confirmed the signing identity and the licence.
2. Read the non-interactive sign-in stream on `beta`, filtered to
   `signInEventTypes/any(t: t eq 'nonInteractiveUser')` over a window bracketing both runs.
3. Read `directoryAudits` on `v1.0` over the same window.
4. Wrote `evidence/01` and `evidence/02` from those two responses, **while the interactive read was
   still outstanding**. See "What broke, and why".
5. Read the interactive sign-in stream on `v1.0` over the same window. It disproved a claim in
   `evidence/01`, which is struck in place and corrected there.
6. Read `P2P Server`'s service principal and application object, to close a provenance question C3
   opened.
7. Read `directoryAudits` three ways for `P2P Server`. All three returned empty.

The two sign-in reads used the same time window and differed only in the stream:

```
GET https://graph.microsoft.com/beta/auditLogs/signIns?$filter=signInEventTypes/any(t: t eq 'nonInteractiveUser') and createdDateTime ge 2026-09-13T00:55:00Z and createdDateTime le 2026-09-13T01:35:00Z&$top=50
GET https://graph.microsoft.com/v1.0/auditLogs/signIns?$filter=createdDateTime ge 2026-09-13T00:55:00Z and createdDateTime le 2026-09-13T01:35:00Z&$top=50
```

## Where Raymond was consulted

- **Which work to run against the closing trial.** Claude audited what was open across the
  repository and found four questions in three exercises gated on the audit endpoints, with twenty
  days left. Raymond: "lets do the audit log reads before the trial ends". The alternative was an
  Okta exercise he had raised the same day, which has no deadline.
- **The redaction set, flagged before any file was written.** The pasted responses carried the
  current Global Administrator's display name and UPN, an Apple push notification token for a
  personal handset, a `User.PUID`, a source IP address and geocoordinates for a private residence.
  The first is forbidden by `CLAUDE.md`. The IP and location follow precedent set in
  `exercises/2026-09-05-b1-breakglass-exclusion-verification`. The push token and the PUID are new
  cases. All are marked in place in the evidence files.
- **Whether to keep chasing `P2P Server` after three empty audit reads.** Claude recommended parking
  it: the exercise's four primary questions were answered, and the remaining question was why the
  audit window is empty, which changes nothing in the lab. Raymond: "park it, write the report".
- **The tenant domain.** It embeds Raymond's personal email local-part and appears in every capture.
  It is already throughout the repository, so it was left as captured. The decision is recorded, not
  closed.

## What the box said

**A device code flow writes four records across three surfaces, in a fixed order.**

| Step | Run 1 | Run 2 | Surface | Marker |
|---|---|---|---|---|
| Consent not yet granted | 01:07:40Z | 01:22:08Z | interactive sign-ins | `errorCode` 65001 |
| Consent written | 01:07:44Z | 01:22:12Z | `directoryAudits` | three events |
| Authentication succeeds | 01:07:46Z | 01:22:26Z | interactive sign-ins | `errorCode` 0 |
| Token redeemed | 01:07:50Z | 01:22:28Z | non-interactive sign-ins | `originalTransferMethod` |

The `correlationId` joins the streams. Run 1 carries `61805a6d` on its interactive pair and on its
token event. Run 2 carries `bae290c5` on both.

**Only one record names the flow, and the field that sounds like it does not.** On the token event:

```
"incomingTokenType": "none",
"authenticationProtocol": "none",
"originalTransferMethod": "deviceCodeFlow",
```

`v1.0` returns no `originalTransferMethod` property at all. The interactive records show
`clientAppUsed` `"Mobile Apps and Desktop clients"` and a Firefox `userAgent`, which describes any
desktop client.

**The sign-in log records the requested scope, and the two runs differ in it.** From
`authenticationProcessingDetails`:

```
run 1   "Oauth Scope Info"  ["User.Read","profile","openid","email"]
run 2   "Oauth Scope Info"  ["User.Read","User.ReadBasic.All","profile","openid","email"]
```

**One amended consent writes three audit events inside 13 milliseconds**, under one
`correlationId`. The event named `Consent to application` carries this:

```
ConsentAction.Permissions:
  "[[Id: KKVDTDO6...ruqpGZe4DE_HFTrqd5XOBsMko, ... ConsentType: Principal, Scope:  User.Read, ...]]
=> [[Id: KKVDTDO6...ruqpGZe4DE_HFTrqd5XOBsMko, ... ConsentType: Principal, Scope:  User.Read, ...]]"
```

`User.Read` on both sides of the arrow. The two events that do carry the change are named
`Add delegated permission grant` and `Remove delegated permission grant`, and both record:

```
DelegatedPermissionGrant.Scope
  oldValue  " User.Read"
  newValue  " User.Read User.ReadBasic.All"
```

**The same event type is accurate on a first consent.** Run 1's `Consent to application` reads
`"[] => [[... Scope:  User.Read ...]]"`. The defect belongs to amending an existing grant, which is
the case C3 proved an administrator cannot see anywhere else either.

**`initiatedBy` names a Microsoft service and carries the human underneath it**, on all six consent
events:

```json
"initiatedBy": { "app": null, "user": {
    "id": "03ee6546-f113-4ec5-ba9d-e57381b0c928",
    "displayName": "Azure ESTS Service",
    "userPrincipalName": "adm-jsmith@...",
    "ipAddress": "4.151.103.193" } }
```

`4.151.103.193` is a Microsoft address. The operator's address appears only in the sign-in log.

**`P2P Server` is a tenant-local registration, and it appeared three seconds after a device join.**

```
2026-09-04T00:35:33Z   VM 101 joins Entra
2026-09-04T00:35:35Z   application object   2c0ccf62-d781-449f-a32c-5eb0976db760
2026-09-04T00:35:36Z   service principal    505610fa-43e4-4e65-990e-364f5794827b
```

`appOwnerOrganizationId` is this tenant. `publisherDomain` is this tenant's own default domain.
`signInAudience` is `AzureADMyOrg`. `servicePrincipalNames` holds `urn:p2p_cert`. `tags` is empty.

**Three `directoryAudits` filters returned `"value": []`**: a ten-minute bracket, an object-id
filter, and the whole of 2026-09-04.

## What broke, and why

**Claude wrote a finding from one stream and called it a property of the flow.** `evidence/01`
stated that neither device code run appears in the interactive log. Four interactive records for
that client exist. The v1.0 read had been issued and had not come back, and the file was written
anyway, with the gap named only under "Not captured". An outstanding read is not a negative result.
Both affected claims are struck in place in `evidence/01`, corrected, and recorded in
`evidence-log.md`. Nothing was deleted.

The correction produced a narrower and better claim. "The flow is invisible in the interactive log"
was wrong. "The interactive log shows the sign-in and cannot tell you it was a device code flow" is
right, and it is the version a detection engineer can act on.

**The same mistake was then avoided twice, deliberately.** `evidence/04` records what the
`P2P Server` objects are and stops before saying what created them, because the audit reads were
outstanding. `evidence/05` records three empty responses and states which of three candidate causes
they do and do not rule out.

**A standing rule in `references/gotchas.md` is wrong, and this exercise disproves it.** The rule
says a platform-initiated audit entry carries a null `userPrincipalName` and a null `ipAddress`, and
to read the null address as the signal. Six consent events here name `Azure ESTS Service` while
carrying a populated UPN and a populated address. The signal does not fire, and the populated
address is still not the actor's.

**Claude compressed captured output in three evidence files, and pushed them.** Conditional
Access policy ids were truncated, `appliedConditionalAccessPolicies` blocks were reduced to a few
properties, one scope list was replaced with a cross-reference, one `userAgent` was ellipsized, and
five of seven audit events lost `modifiedProperties` and `additionalDetails` entries. The motive was
readability. A capture block holds machine output, and a capture that has been tidied is no longer a
capture. The complete output is recorded in
`evidence/06-corrected-full-captures-superseding-01-02-03.md`, which itemises all seven compressions.
No finding changed.

**The first attempt to fix it was also wrong.** Claude rewrote the three closed evidence files in
place. `validate.py` refused with `evidence-modified`: an exercise holding a `report.md` is closed
and its evidence is frozen against modification, while added files are permitted. The in-place edits
were reverted and the correction was added as a new file, which is the route the tooling intends.

**Those two rules can conflict, and this exercise found the case.** `evidence/01` cites a path that
does not resolve. `CLAUDE.md` requires a wrong published claim to be corrected on the record rather
than by silent edit. `validate.py` forbids touching closed evidence at all. The broken reference is
therefore a standing ERROR that cannot be cleared in place. Recorded as a pending decision in
`CARRYOVER.md`; the correct path is named in `evidence/06`.

**Graph Explorer failed in four recorded ways during this work.** The stale response body fired a
third time, returning `#users/$entity` against an `applications` request; all three occurrences
returned that same body shape, which narrows the cause to the tool's own profile request reaching
the response pane. The address bar keeps its previous contents. The permissions panel will not
load. Signing out does not switch accounts. Raymond absorbed all four by hand, at two to three
attempts per read.

**One question expired before it was asked.** `P2P Server` appeared on 2026-09-04 and was first
noticed on 2026-09-12. By 2026-09-14 no audit record of it survived. The exercise that would have
named its creator was the exercise that created it, eight days earlier, and nothing captured it at
the time.

## What I'd do differently

Do not write an evidence file while a read that bears on its central claim is outstanding. Naming
the gap under "Not captured" is not a substitute for waiting. The gap was named and the claim was
written anyway.

Read both sign-in streams before drawing any conclusion about either. One stream is half an
authentication. The interactive and non-interactive records of one device code run describe
different legs of it and neither is the whole.

Capture the per-call UTC timestamp at the time, not the batch timestamp afterwards.
`evidence/04` and `evidence/05` carry a date and a lower bound instead of a time, and that is
unrecoverable.

Write down what a state change created, at the time it creates it. `P2P Server` cost nothing to
notice on 2026-09-04 and cannot be explained on 2026-09-14.

## Open questions

- Where is the `directoryAudits` retention boundary in this tenant? One read of the oldest surviving
  event settles it. The Entra admin center's Audit logs blade answers it without Graph Explorer, and
  it distinguishes a creation that wrote no event from a creation whose event has aged out.
- Did the Entra join of VM 101 create the two `P2P Server` objects? The three-second relationship is
  Captured and the causal claim is not. A second device join, watched live, would answer it and
  would also answer the retention question by producing a fresh event.
- What is `urn:p2p_cert` used for? The value is Captured. Its purpose is not established here.
- Does a `Consent to application` event report an amendment correctly in any tenant, or is the
  `User.Read => User.Read` body a general defect? One tenant, one observation.
- What does a **refused** consent write? Every event captured here has `result` `success`.
  `2026-09-09-pim-for-groups` asked the same question about a refused privileged action and it is
  still open.
- Would `offline_access` change the sign-in record? Carried from C3. Neither run requested a refresh
  token, so no record here shows what a persistent grant looks like.
- Does the stale-response-body defect reproduce against a signed-out session, or does it require the
  tool's own profile request? Three occurrences, one body shape, no test.
