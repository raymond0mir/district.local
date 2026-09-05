# Contrast test: a non-excluded user gets real report-only results

Command 1: GET https://graph.microsoft.com/beta/auditLogs/signIns?$filter=createdDateTime ge 2026-09-05T16:10:00Z&$top=25
Command 2: GET https://graph.microsoft.com/beta/auditLogs/signIns?$filter=createdDateTime ge 2026-09-05T16:10:00Z and signInEventTypes/any(t: t eq 'nonInteractiveUser')&$top=25
Host: Graph Explorer, signed in as the current break-glass Global Administrator
UTC timestamp: entries carry their own UTC times; host clock read 2026-09-05T16:17:01Z earlier in session

HTTP status codes not captured. Both calls returned full response bodies.
Redactions applied: `ipAddress` and `location.geoCoordinates`. jsmith's UPN and display name retained.

## How the sign-in was produced

VM 101 was started. jsmith signed in at the Windows lock screen with a Windows Hello for Business
PIN, then opened Edge to https://myapps.microsoft.com. The My Apps dashboard rendered signed in as
jsmith. No password was used and no password reset was performed. See evidence file 03 for why the
password path was rejected.

## Command 1 returned only the earlier failures

Four entries, all `2026-09-05T16:15:12Z` to `16:15:37Z`, all errorCode 50126, all from the Mac
Mini in Firefox, all with `signInEventTypes: ["interactiveUser"]` and an empty
`appliedConditionalAccessPolicies` array. The VM 101 sign-in is not in the interactive stream.

The beta schema adds a field v1.0 does not carry. On each failure:

    "authenticationDetails": [
        {
            "authenticationStepDateTime": "2026-09-05T16:15:37Z",
            "authenticationMethod": "Password",
            "authenticationMethodDetail": "Password Hash Sync",
            "succeeded": false,
            "authenticationStepResultDetail": "Invalid username or password or Invalid on-premise
                                               username or password."
        }
    ]

`authenticationMethodDetail: "Password Hash Sync"` confirms from the tenant side that jsmith's
password is validated against a synced hash, which matches evidence file 03's Graph read of
`onPremisesSyncEnabled`.

## Command 2 returned the VM 101 sign-in, and it settles the question

Twelve non-interactive entries between `2026-09-05T16:19:36Z` and `16:19:56Z`, all from
DESKTOP-O860UU9 (`deviceId` 7b564046-16ba-4d3d-8baf-6745b6e93267, `trustType: "Azure AD joined"`,
`isCompliant: false`, `isManaged: false`), all `incomingTokenType: "primaryRefreshToken"`, all
sharing `sessionId` 0089f86a-40bd-6b61-168c-1022467e8012.

Every entry that carries a policy array returns the same three results:

| policy id | displayName                                | result                | conditionsSatisfied | conditionsNotSatisfied | excludeRulesSatisfied |
|-----------|--------------------------------------------|-----------------------|---------------------|------------------------|-----------------------|
| 365bdd23  | B1 - Require MFA for all users              | reportOnlySuccess     | application,users   | none                   | []                    |
| d9a6a116  | B1 - Require compliant or hybrid joined dev | reportOnlyFailure     | application,users   | none                   | []                    |
| 75882b6a  | B1 - Block legacy authentication            | reportOnlyNotApplied  | application,users   | clientType             | []                    |

`Security Defaults` also appears on each with `result: "success"`.

## Findings

**1. Report-only policies do apply to users in this tenant.** The alternative hypothesis recorded
in evidence file 02, that these policies never apply to anyone, is disproved. One sign-in produced
both a `reportOnlySuccess` and a `reportOnlyFailure`.

**2. Policy 75882b6a's non-application is machine-attributed to the client app type.** Evidence
file 02 reached that conclusion by reading the policy conditions. The log now states it directly:
`conditionsNotSatisfied: "clientType"`. The exclusion is not what stopped that policy for jsmith,
and by the same mechanism it was not what stopped it for the break-glass account.

**3. `reportOnlyFailure` on d9a6a116 is the expected result and it is a real signal.** VM 101 is
Azure AD joined, not hybrid joined, and not compliant. The policy grants on `compliantDevice` or
`domainJoinedDevice`. Neither is satisfied. If this policy were enforced today, this device would
be blocked. That is the report-only telemetry CURRICULUM.md step 5 asks for, produced by one
sign-in.

**4. The beta endpoint carries `excludeRulesSatisfied`; v1.0 does not.** For jsmith the array is
empty on all three policies, which is correct for a user who is not excluded. This field is the
direct evidence for an exclusion claim. See evidence file 06.

## Observations, not chased

- One entry at `16:19:50Z` (appId ecd6b820, resource `OCaaS Client Interaction Service`) returned
  `appliedConditionalAccessPolicies: []` while sibling entries in the same second carried the full
  array. Cause not investigated.
- `M365ChatClient` at `16:19:54Z` returned errorCode 500014, service principal for the resource is
  disabled. Not investigated.
- Twelve token acquisitions in twenty seconds, to Edge Sync, Microsoft Text Understanding,
  Microsoft People Cards Service, Olympus, OCaaS Client Interaction Service, Windows Store for
  Business, Microsoft Device Directory Service, Microsoft Activity Feed Service, and Microsoft
  Graph. One user opening one browser tab produced all of it, under the user's identity, none of
  it visible in the interactive sign-in log.
