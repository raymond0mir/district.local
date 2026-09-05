# B1 step 1 — verifying a break-glass exclusion before enforcement

## What I set out to do

Three Conditional Access policies had been running report-only in this tenant since 2026-09-04,
each excluding a break-glass Global Administrator by object ID. The exclusion had never been
verified. The prior session recorded that a sign-in by that account produced no log entry, called
it unexplained, and stopped. The hypothesis for this exercise: the missing entry has an
identifiable cause, and the exclusion can be proven from the sign-in log without enforcing
anything.

## The setup

The lab slice is the Entra tenant plus VM 101 (`win11-client01`, `DESKTOP-O860UU9`), an
Entra-joined Windows 11 client. No domain controller was touched. All Graph work ran in Graph
Explorer, signed in as the current break-glass account, whose identity stays out of this repo.

Pre-flight, host shell, 2026-09-05T16:17:01Z
(`evidence/00-lab-state-preflight.txt`):

- Thin pool `data`: Data% **61.62**, Meta% **3.27**. The 85 stop gate is not reached.
- Memory: 15Gi total, **10Gi available**.
- VM 100 (DC01) stopped, VM 101 stopped, VM 102 stopped, VM 104 (pfSense) running.

The exercise date comes from `date -u`, which returned 2026-09-05T16:08:17Z. `EXPOSURES.md`
records a one-day naming offset in this repo caused by using the host's local clock instead.

## What I did

1. Read the break-glass account's own object ID and its sign-in log on v1.0.

       GET https://graph.microsoft.com/v1.0/me?$select=id,userPrincipalName
       GET https://graph.microsoft.com/v1.0/auditLogs/signIns?$top=20

2. Read the three policies in full, and the Security Defaults state.

       GET https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies?$select=id,displayName,state,conditions,grantControls
       GET https://graph.microsoft.com/v1.0/policies/identitySecurityDefaultsEnforcementPolicy

3. Read `jsmith` to decide where a password reset would have to happen.

       GET https://graph.microsoft.com/v1.0/users/03b0f0f4-1230-42c1-983c-9bb5ecb1a2c8?$select=id,userPrincipalName,accountEnabled,onPremisesSyncEnabled,onPremisesSamAccountName,onPremisesDomainName,onPremisesLastSyncDateTime,lastPasswordChangeDateTime

4. Started VM 101 and signed in as `jsmith` with a Windows Hello for Business PIN, then opened
   Edge to `https://myapps.microsoft.com`. No password was used.

       qm start 101

5. Queried the sign-in log for `jsmith` on v1.0, then on beta for non-interactive events, then by
   time floor across both streams.

       GET https://graph.microsoft.com/beta/auditLogs/signIns?$filter=createdDateTime ge 2026-09-05T16:10:00Z&$top=25
       GET https://graph.microsoft.com/beta/auditLogs/signIns?$filter=createdDateTime ge 2026-09-05T16:10:00Z and signInEventTypes/any(t: t eq 'nonInteractiveUser')&$top=25

6. Re-read the 2026-09-04 break-glass sign-in on beta, by id.

       GET https://graph.microsoft.com/beta/auditLogs/signIns/3388ca4e-566a-4c7c-bd5d-fd8fcb600f00

No policy was created, modified, or enforced. No account was changed. No password was reset.

## Where Raymond was consulted

**Which exercise to run.** I offered four: this one, an AD CS and PKI build, PIM and entitlement
management, and custom roles with administrative units. He chose B1 step 1. It is the item gating
enforcement inside a running 30-day P2 trial.

**How to produce a non-excluded sign-in.** The contrast test needed one sign-in by a user who is
not excluded. `jsmith` is the only other account with a registered MFA method, and its password
was not to hand. He said:

> "lets reset jsmith"

I pushed back after reading `onPremisesSyncEnabled: true`. A synced account's password is mastered
on DC01, so the reset would need DC01 started, VM 102 started to carry the hash, a RAM rebalance to
fit both on a host `EXPOSURES.md` records as over-committed, and a typed secret with no TTY
available on any path into DC01. I proposed VM 101's Windows Hello PIN instead, which needs no
password at all and produces a device-joined sign-in that exercises the device policy properly. He
took it and reported:

> "logged in as jsmith with the pin on 101, successfully logged into myapps"

**Redaction.** The pastes carried the break-glass UPN and display name, which the portfolio rules
keep out of the repo, and also a residential IP address with geocoordinates. I extended redaction
to the IP and coordinates on my own judgment and flagged it in session. He did not object. The
object ID is retained, because an exclusion claim cannot be checked without it.

## What the box said

**The prior session's premise was wrong. The log had populated.** Two break-glass sign-ins postdate
all three policies, at 2026-09-04T14:19:33Z and 14:19:38Z, sharing one correlation ID
(`evidence/01-breakglass-signins-after-policy-creation.md`). The policies were created at
14:10:14Z, 14:11:55Z, and 14:12:50Z.

**On v1.0 the result is ambiguous.** All three policies returned `reportOnlyNotApplied`. That value
means the policy was evaluated in report-only mode and did not apply. It does not name the cause.

**The policy definitions narrow it** (`evidence/02-policy-conditions-and-security-defaults-state.md`).
All three scope `includeUsers: ["All"]` and `includeApplications: ["All"]`, with `platforms`,
`locations`, `devices` and every risk array null or empty, and `excludeUsers` holding one object ID
and nothing else.

**The contrast case settles whether the policies work at all**
(`evidence/05-non-excluded-user-contrast-jsmith.md`). `jsmith`'s VM 101 sign-in returned, on every
evaluated event:

| policy | result | conditionsNotSatisfied |
|---|---|---|
| 365bdd23 Require MFA for all users | `reportOnlySuccess` | none |
| d9a6a116 Require compliant or hybrid joined device | `reportOnlyFailure` | none |
| 75882b6a Block legacy authentication | `reportOnlyNotApplied` | clientType |

**The beta endpoint states the exclusion outright**
(`evidence/06-breakglass-exclusion-captured-directly.md`). Re-reading the same 2026-09-04 sign-in
on beta returns, for all three policies:

    "result": "reportOnlyNotApplied",
    "conditionsSatisfied": "application",
    "conditionsNotSatisfied": "users",
    "includeRulesSatisfied": [
        { "conditionalAccessCondition": "application", "ruleSatisfied": "allApps" },
        { "conditionalAccessCondition": "users", "ruleSatisfied": "allUsers" }
    ],
    "excludeRulesSatisfied": [
        { "conditionalAccessCondition": "users", "ruleSatisfied": "userId" }
    ]

The include rules were satisfied first. A `userId` exclude rule then stopped each policy. The
exclusion is verified on all three, by machine output, without enforcing anything.

**Security Defaults is still enabled.** `isEnabled: true`, and the break-glass record names its
requirement provider directly:

    "authenticationRequirementPolicies": [
        { "requirementProvider": "securityDefaults", "detail": "Security Defaults" }
    ]

Every MFA prompt this tenant has issued comes from Security Defaults. No CA policy has ever
enforced a control here.

**A failed sign-in never reaches Conditional Access**
(`evidence/04-failed-signin-bypasses-conditional-access.md`). Four errorCode 50126 attempts all
returned `appliedConditionalAccessPolicies: []`. Credential validation runs first. An exclusion
cannot be tested with a sign-in that fails.

## What broke, and why

**I asserted something the log then disproved.** In `evidence/02` I wrote that policy 75882b6a's
exclusion could never be verified by a browser or modern client sign-in, because its
`clientAppTypes` condition is `["exchangeActiveSync", "other"]` and would always fail first. That
is wrong. Entra evaluates the user condition before the client app type, so the exclusion
short-circuits evaluation. The two records prove the ordering:

| record | 75882b6a `conditionsNotSatisfied` | `excludeRulesSatisfied` |
|---|---|---|
| break-glass, 2026-09-04T14:19:38Z | users | userId |
| jsmith, 2026-09-05T16:19:36Z | clientType | [] |

Same policy, same client app type, different outcome, and the difference is the exclusion. All
three exclusions are verified, not two. `evidence/02` carries an inline retraction.

**I sent a command against the wrong API version.** I asked for the non-interactive query on
`v1.0`. Microsoft's documentation states v1.0 returns interactive user sign-ins and successful
federated sign-ins only. Caught before the command ran, corrected to `beta`.

**The 2026-09-04 conclusion came from one read.** The successful VM 101 sign-in was also missing
from a read taken minutes after it happened, then present in a later read. The same shape produced
the prior session's "unexplained" verdict. A single empty read is not a finding.

**Two dead ends cost real time.** Four failed password attempts against `jsmith` from a Mac browser
produced nothing usable, because a failed sign-in bypasses Conditional Access entirely. Then the
successful sign-in did not appear in the interactive log, because desktop single sign-on issues
tokens through the primary refresh token and lands in the non-interactive stream. Neither dead end
was wasted: both are now Captured findings.

## What I'd do differently

Read the beta endpoint first. Every ambiguity in this exercise came from v1.0 omitting
`conditionsSatisfied`, `conditionsNotSatisfied`, `includeRulesSatisfied`, and
`excludeRulesSatisfied`. The first two hours reasoned toward a conclusion the beta schema states in
one field. For any Conditional Access question, beta is the correct endpoint.

Establish the log's write latency before treating an empty read as evidence. Two sessions now have
drawn conclusions from a single query returning nothing.

Test the exclusion with a successful sign-in from the start. The four failed password attempts were
never going to produce a Conditional Access evaluation.

## Open questions

- What the sign-in log's write latency actually is. Both the 2026-09-04 case and this one point at
  it, and neither measured it.
- Whether policy 75882b6a blocks a real legacy-auth client. Its exclusion is verified. Its control
  has never been exercised.
- Whether `d9a6a116` should enforce at all in its current form. `jsmith`'s Entra-joined,
  non-compliant device returned `reportOnlyFailure`, meaning enforcement would block the lab's only
  working client. `domainJoinedDevice` means hybrid joined, which VM 101 is not.
- The order of operations for the Security Defaults transition. Disabling Security Defaults before
  a CA policy enforces leaves the tenant with no MFA floor. The window's length has not been
  planned.
- One non-interactive entry at 2026-09-05T16:19:50Z returned an empty policy array while sibling
  entries in the same second carried the full array. Cause unknown.
- The app `Enterprise Dashboard Project` (`3a4d129e-7f50-4e0d-a7fd-033add0a29f4`) acquires tokens
  on VM 101 under `jsmith`. Microsoft owns the app registration. The display name is unexplained.
- VM 101's clock runs UTC, not the host's America/Los_Angeles.
- Whether to onboard more of the restamped accounts for broader report-only telemetry. Undecided
  since 2026-09-04.
