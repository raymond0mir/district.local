# B1 Security Defaults Transition

## What I set out to do

B1's three Conditional Access policies had run in report-only mode since 2026-09-04, alongside
Security Defaults, the tenant's only actual MFA control. This exercise tested whether the
transition to real enforcement could happen with no gap in MFA coverage, and if not, executed
the transition while minimizing that gap and deciding the disposition of the one policy known
to fail against the lab's only client.

## The setup

Tenant: `district.local`'s Entra ID tenant, Microsoft Entra ID P2 trial active. Client: VM 101
(`win11-client01`), Azure AD joined, signed in as `jsmith`. Pre-flight, 2026-09-05T18:25:14Z:
pool Data% 64.74, under the 85% gate. VM 100 (DC01) unexpectedly running — Raymond had started
it manually without logging a session; not a system anomaly. A second pre-flight before
touching VM 101, 2026-09-05T18:45:01Z: pool Data% 66.28, available memory risen to 4.6Gi from
1.2Gi with no host action taken in between, cause not investigated.

## What I did

1. Read current state: Security Defaults `isEnabled: true`; all three CA policies
   `enabledForReportingButNotEnforced`.
2. Tested the ordering question directly by attempting to enable `75882b6a` (block legacy
   auth) while Security Defaults was still on. Entra rejected it with `BadRequest`.
3. Decided to hold `d9a6a116` (compliant or hybrid device) in report-only, since it has a
   confirmed `reportOnlyFailure` against VM 101 and would guarantee breaking it.
4. Disabled Security Defaults, then enabled `365bdd23` (MFA for all users) and `75882b6a`
   (block legacy auth), back to back.
5. Confirmed the new state by reading the policies again. Measured the gap between the two
   enable actions at 14 seconds, from their own `modifiedDateTime` fields.
6. Started VM 101 and signed in as `jsmith` to verify enforcement live.
7. Measured the sign-in log's write latency directly, since two prior exercises had each drawn
   a conclusion from a single empty read of this log.
8. Confirmed enforcement on a live sign-in: `conditionalAccessStatus: "success"`, Security
   Defaults absent from evaluation, `365bdd23` and `75882b6a` genuinely evaluated, `d9a6a116`
   correctly still report-only.

## Where Raymond was consulted

- Asked whether VM 100's unexpected running state was a known start. He said: "i started it
  manually, forgot to log a session here."
- Asked to confirm the session's overall direction before any state change. He said: "design
  and execute if the plan closes clean."
- Asked to confirm the ordering test specifically, since it is a live security-posture change
  even at low risk. He said: "go ahead."
- Proposed holding `d9a6a116` in report-only rather than enforcing it immediately, since
  enforcing it would guarantee breaking VM 101's access. He confirmed the finalized
  enforcement sequence with "go ahead."
- Asked whether to verify enforcement live now, which required starting VM 101, or defer it.
  He said: "verify now."

## What the box said

Ordering test, 2026-09-05T18:39:37Z:
```
"message": "Security Defaults is enabled in the tenant. You must disable Security defaults
before enabling a Conditional Access policy."
```

Post-enforcement policy state: `365bdd23.state = "enabled"`, `modifiedDateTime =
2026-09-05T18:41:28.6343692Z`. `75882b6a.state = "enabled"`, `modifiedDateTime =
2026-09-05T18:41:42.6392666Z`. `d9a6a116.state` unchanged, `"enabledForReportingButNotEnforced"`.

Live verification sign-in, 2026-09-05T19:02:04Z–19:02:35Z: `conditionalAccessStatus:
"success"`. `appliedConditionalAccessPolicies` carries three entries, not four — Security
Defaults no longer appears. `365bdd23` result `"success"`. `75882b6a` result `"notApplied"`
(genuinely evaluated; this client is not a legacy-auth client). `d9a6a116` result
`"reportOnlyFailure"`, unchanged.

## What broke, and why

The assumed zero-gap transition does not exist in this tenant. Entra's API rejects enabling a
CA policy while Security Defaults is on, at the platform level, not just in portal UI
guidance. This forced a real, if brief, gap in MFA coverage rather than the clean handoff the
initial plan hoped for.

The sign-in log's write latency was far larger than either of the two prior exercises had
assumed. A sign-in at 18:46:29Z had not appeared by 18:51:33Z (5m4s later) and had appeared by
18:57:21Z (at most 10m52s later). Two earlier sessions each treated a single empty read as
meaningful; this session measured the gap instead of repeating that error.

One retry in that measurement loop returned a mismatched response: a `/users/{id}` lookup
instead of the requested sign-in log query. It resolved the object id excluded from all three
CA policies to a display name and UPN. Cause not established. That identity is not recorded in
this repo, consistent with the standing rule against publishing the tenant Global
Administrator's identity.

A plain desktop unlock on VM 101 produced only a pre-authentication Windows Hello for Business
failure with no CA evaluation — not the CA-evaluated entries needed for verification. Those
only appeared after Raymond opened a browser and interacted with a Microsoft resource
directly, matching the pattern from the prior exercise's contrast sign-in.

## What I'd do differently

Pair each Graph action with a `date -u` capture at the moment of execution, not after the
fact, to get a tighter latency bound than the several-minute window this session established.

Ask for the browser-based verification step earlier, rather than assuming a desktop unlock
alone would generate CA-evaluated log entries.

## Open questions

- Cause of the mismatched `/users/{id}` response during the latency retry loop. Not
  investigated this session.
- Whether a failed local Windows Hello PIN unlock ever reaches the sign-in log at all. No
  failed entry appeared for Raymond's deliberate wrong-PIN attempt; not confirmed against
  documentation.
- The exact semantics of `securityDefaultsUpsell.dueDateTime` as a disable-action timestamp.
  Used as a plausible proxy this session, not confirmed against Microsoft documentation.
- `75882b6a`'s block remains unexercised against a real legacy-auth attempt. Its
  `notApplied` result this session reflects a non-legacy client, not a tested block.
- `d9a6a116`'s disposition: Intune enrollment, grant change, or narrower scope. Still
  undecided, deliberately deferred this session.
