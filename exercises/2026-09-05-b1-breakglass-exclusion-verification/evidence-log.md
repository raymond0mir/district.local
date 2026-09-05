# B1 step 1 — break-glass exclusion verification — evidence log

Exercise date derived from the host clock: `date -u` returned 2026-09-05T16:08:17Z.

## Captured

- **Lab state pre-flight.** Thin pool Data% 61.62, Meta% 3.27, 10Gi available, VMs 100/101/102
  stopped and VM 104 running at 16:17:01Z. Pool is below the 85 stop gate.
  `evidence/00-lab-state-preflight.txt`
- **The break-glass sign-in log did populate after the policies were created.** Two entries at
  2026-09-04T14:19:33Z and 14:19:38Z, both carrying all three B1 policies. Also: a failed sign-in
  returns an empty policy array, and the successful VM 101 sign-in is absent from the interactive
  stream. `evidence/01-breakglass-signins-after-policy-creation.md`
- **All three policies scope all users and all cloud apps, exclude one object ID, and run
  report-only. Security Defaults is still enabled** (`isEnabled: true`).
  `evidence/02-policy-conditions-and-security-defaults-state.md`
- **jsmith is a synced account** (`onPremisesSyncEnabled: true`, `onPremisesDomainName:
  district.local`), so its password is mastered on DC01, not in Entra.
  `evidence/03-jsmith-is-a-synced-account.md`
- **A failed sign-in is never evaluated by Conditional Access.** Four errorCode 50126 attempts,
  all with `appliedConditionalAccessPolicies: []`.
  `evidence/04-failed-signin-bypasses-conditional-access.md`
- **A non-excluded user gets real report-only results.** jsmith's VM 101 sign-in returns
  `reportOnlySuccess` on the MFA policy, `reportOnlyFailure` on the device policy, and
  `reportOnlyNotApplied` with `conditionsNotSatisfied: "clientType"` on the legacy-auth policy.
  `evidence/05-non-excluded-user-contrast-jsmith.md`
- **The break-glass exclusion, stated by the log.** All three policies return
  `conditionsNotSatisfied: "users"` and `excludeRulesSatisfied: [{users, userId}]`.
  `evidence/06-breakglass-exclusion-captured-directly.md`

## Not captured, and why

- **HTTP status codes.** Graph Explorer returned response bodies. The status line was not pasted
  for any call. Every Graph evidence file in this exercise says so in its header.
- **The exact time of the VM 101 PIN sign-in at the lock screen.** Only the resulting token
  acquisitions at 16:19:36Z onward are Captured. The lock-screen event itself was not read.
- **The P2 trial start timestamp.** Still Recalled, carried forward from 2026-09-04. Blocker: it
  was never captured when the trial started, and no read since has surfaced it.
- **Policy 75882b6a against a real legacy-auth client.** The exclusion is verified, but the
  policy's blocking behaviour is not. No legacy-auth sign-in has ever been attempted in this
  tenant.
- **Sign-in log write latency.** The VM 101 sign-in was absent from a read taken minutes after it
  happened and present in a later read. The interval was not measured.

## Where Raymond was consulted

- **Which exercise to run.** Offered four: B1 step 1, AD CS and PKI, PIM and entitlement
  management, custom roles and administrative units. He chose B1 step 1. Reason not stated; it is
  the item gating enforcement inside the P2 trial window.
- **How to produce a non-excluded sign-in.** He said "lets reset jsmith". Claude pushed back after
  reading `onPremisesSyncEnabled: true`, on the grounds that a synced account's reset needs DC01
  and VM 102 running, a RAM rebalance, and a typed secret with no TTY available. Claude proposed
  the VM 101 Windows Hello PIN path instead, which needs no password. He took it and reported:
  "logged in as jsmith with the pin on 101, successfully logged into myapps".
- **Redaction of the paste.** Claude applied redaction of the break-glass UPN and display name per
  the portfolio rule, and extended it to the public IP address and geocoordinates on its own
  judgment, flagging the extension in session. He did not object.

## Corrections

- **Claude's own error, caught and retracted the same session.** Evidence file 02 states that no
  browser or modern client sign-in could ever verify policy 75882b6a's exclusion, because its
  `clientAppTypes` condition would always fail first. Evidence file 06 disproves it: Entra
  evaluates the user condition before the client app type, and the exclusion short-circuits
  evaluation. The break-glass record shows `conditionsNotSatisfied: "users"` on that policy, while
  jsmith's shows `conditionsNotSatisfied: "clientType"`. Evidence file 02 carries an inline
  retraction pointing here. No ledger row is retired, because the wrong claim never reached the
  ledger.
- **`CARRYOVER.md` was stale on git state.** It recorded the 2026-09-04 evidence, report, ledger
  and exposures updates as uncommitted. `git status` was clean at commit `1bd8c3c`. Stated at
  session start.
- **`CARRYOVER.md`'s Lab state was Recalled, not Captured.** It carried the 09-04 readings
  forward. Treated as Recalled until the pre-flight ran.
- **The first command block named the wrong Graph endpoint.** Claude asked for the non-interactive
  query on `v1.0`. Microsoft's documentation states v1.0 returns interactive user sign-ins and
  successful federated sign-ins only. Corrected to `beta` before the command was run.

## Open questions

- What the write latency on the sign-in log actually is. The VM 101 sign-in was missing from one
  read and present in a later one. The 2026-09-04 session concluded "no entry, unexplained" from a
  single read. Both point at latency, and neither measured it.
- Whether policy 75882b6a blocks a real legacy-auth client. Its exclusion is verified; its control
  is not.
- One non-interactive entry at 2026-09-05T16:19:50Z (appId ecd6b820, resource `OCaaS Client
  Interaction Service`) returned an empty `appliedConditionalAccessPolicies` array while sibling
  entries in the same second carried the full array. Cause unknown.
- `M365ChatClient` returned errorCode 500014 at 16:19:54Z, service principal for the resource
  disabled. Not investigated.
- The app `Enterprise Dashboard Project`, appId `3a4d129e-7f50-4e0d-a7fd-033add0a29f4`, acquires
  tokens for `Microsoft News Feed` and Microsoft Graph on VM 101. Its `appOwnerTenantId` is
  Microsoft's, so it is not a planted object, but the display name is unexplained.
- VM 101's clock reads UTC, not America/Los_Angeles. `EXPOSURES.md` records a dated-artifact
  offset from clock differences. Not chased.
- Whether the other eight restamped accounts should be onboarded to produce broader report-only
  telemetry. Carried forward from 2026-09-04, still undecided.

## Not started

- CURRICULUM.md B1 step 4, letting report-only run and gathering real sign-in volume. One user's
  single session is now Captured; that is not volume.
- CURRICULUM.md B1 step 6, enforcement. Blocked on the Security Defaults transition, which is now
  the named next gate.
- The fourth policy, phishing-resistant auth against Salesforce. Still blocked on certificate-based
  authentication and a trusted certificate authority, both absent.
- `A3-nongallery-test` app object. Still undecided, delete or keep.
