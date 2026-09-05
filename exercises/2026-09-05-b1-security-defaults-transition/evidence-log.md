# B1 Security Defaults transition — evidence log

## Captured

- Pre-flight host state, 2026-09-05T18:25:14Z. Pool Data% 64.74, under the 85% gate.
  `evidence/01-preflight-and-vm100-state-discrepancy.md`.
- Fresh policy state read: Security Defaults `isEnabled: true`, all three CA policies
  `enabledForReportingButNotEnforced`. `evidence/02-current-policy-state-fresh-read.md`.
- Ordering test: Entra rejects enabling a CA policy while Security Defaults is on
  (`BadRequest`, 2026-09-05T18:39:37Z). A zero-gap transition is not possible in this tenant.
  `evidence/03-ordering-test-rejected.md`.
- Security Defaults disabled; `365bdd23` and `75882b6a` enforced; `d9a6a116` held report-only
  as planned. Gap between the two CA policies: 14 seconds, from their own `modifiedDateTime`
  fields. `evidence/04-confirmation-read-and-gap-timing.md`.
- Sign-in log write latency, previously unmeasured, now bounded at 5m4s to 10m52s for this
  event. `evidence/06-signin-log-latency-measurement.md`,
  `evidence/07-signin-log-latency-bounded-and-whfb-entry.md`.
- Enforcement verified live: `conditionalAccessStatus: "success"`, Security Defaults absent
  from evaluation, `365bdd23` and `75882b6a` genuinely evaluated (not report-only), `d9a6a116`
  correctly still report-only. `evidence/08-enforcement-verified-live.md`.
- Session close: VM 100, 101, 102 stopped; VM 104 running. Matches the lab's standard opening
  state. `evidence/09-session-close-vm-state-confirmed.md`.

## Not captured, and why

- The exact semantics of `securityDefaultsUpsell.dueDateTime` as a disable-action timestamp.
  Used as a proxy, not confirmed against documentation.
- Whether a failed local Windows Hello PIN unlock ever reaches the sign-in log. No failed
  entry appeared for Raymond's deliberate wrong-PIN attempt, consistent with it not reaching
  Entra, but not confirmed against documentation.

## Where Raymond was consulted

- Asked whether VM 100's unexpected running state was a known, out-of-band start. Raymond
  said he started it manually and did not log the session.
- Asked to confirm the overall session direction before any state change. Raymond said
  "design and execute if the plan closes clean."
- Asked to confirm the ordering test on `75882b6a` specifically, since it is a live
  security-posture change. Raymond said "go ahead."
- Proposed holding `d9a6a116` in report-only rather than enforcing it, since it would
  guarantee blocking VM 101. Raymond confirmed the finalized three-step enforcement sequence
  with "go ahead."
- Asked whether to verify enforcement live now (requiring VM 101 up) or defer it. Raymond
  said "verify now."

## Corrections

- Carryover recorded VM 100 stopped as of 2026-09-05T16:51:16Z. The 2026-09-05T18:25:14Z
  pre-flight read shows VM 100 running. Resolved: a manual, untracked start by Raymond.

## Open questions

- Cause of one mismatched Graph Explorer response during the latency retry loop: a
  `/users/{id}` lookup returned instead of the requested sign-in log query. It resolved the
  object id excluded from all three CA policies to a display name and UPN, not recorded in
  this file per the skill's rule against publishing the tenant Global Administrator's
  identity. Not investigated further this session.

## Not started

- A real legacy-auth sign-in attempt against `75882b6a`. Its block remains unexercised.
- The `d9a6a116` resolution decision (Intune enrollment, grant change, or narrower scope).
