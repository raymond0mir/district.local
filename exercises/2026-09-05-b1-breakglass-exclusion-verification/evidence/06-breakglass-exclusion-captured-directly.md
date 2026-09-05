# The break-glass exclusion, Captured directly

Command: GET https://graph.microsoft.com/beta/auditLogs/signIns/3388ca4e-566a-4c7c-bd5d-fd8fcb600f00
Host: Graph Explorer, signed in as the current break-glass Global Administrator
UTC timestamp: read 2026-09-05, session host clock 2026-09-05T16:17:01Z; the record itself is
2026-09-04T14:19:38Z

HTTP status code not captured. A full single-entity response body was returned.
Redactions applied: `userDisplayName`, `userPrincipalName`, `signInIdentifier`, `ipAddress`, and
`location.geoCoordinates`. The object ID is retained; the exclusion claim cannot be checked
without it.

## Why beta and not v1.0

Evidence file 01 read this same sign-in on v1.0. That response carries `result` but not
`conditionsSatisfied`, `conditionsNotSatisfied`, `includeRulesSatisfied`, or
`excludeRulesSatisfied`. On v1.0 the exclusion can only be inferred from the policy definition.
On beta the log states it.

## The record

    "id": "3388ca4e-566a-4c7c-bd5d-fd8fcb600f00",
    "createdDateTime": "2026-09-04T14:19:38Z",
    "userDisplayName": "<break-glass display name, redacted>",
    "userPrincipalName": "<break-glass UPN, redacted>",
    "userId": "6ca413e3-06ff-4704-ab36-1348bb7387c8",
    "appDisplayName": "Graph Explorer",
    "clientAppUsed": "Browser",
    "isInteractive": true,
    "signInEventTypes": ["interactiveUser"],
    "authenticationRequirement": "multiFactorAuthentication",
    "conditionalAccessStatus": "notApplied",
    "status": { "errorCode": 0, "failureReason": "Other.",
                "additionalDetails": "MFA requirement satisfied by claim in the token" },
    "deviceDetail": { "operatingSystem": "MacOs", "browser": "Firefox 155.0",
                      "isCompliant": false, "isManaged": false, "trustType": null }

All three B1 policies return identically shaped evaluations:

    {
      "id": "365bdd23-d0e0-49a7-8131-f63b98ea6115",
      "displayName": "B1 - Require MFA for all users (report-only)",
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
    }

`75882b6a` (Block legacy authentication) and `d9a6a116` (Require compliant or hybrid joined device)
return the same three values: `conditionsNotSatisfied: "users"`, the same `includeRulesSatisfied`
pair, and the same single `excludeRulesSatisfied` entry naming `userId`.

`Security Defaults` on the same record returns `result: "success"`,
`conditionsNotSatisfied: "none"`, and `excludeRulesSatisfied: []`.

## What this Captures

The break-glass account's exclusion from all three report-only Conditional Access policies is
verified by machine output. For each policy the log states that the user condition was not
satisfied and that a `userId` exclude rule was satisfied. The include rules were satisfied first
(`allApps`, `allUsers`), so the exclusion, not a scoping gap, is what stopped each policy.

This closes the open item carried from
`exercises/2026-09-04-b1-security-defaults-and-ca-report-only` and from `CARRYOVER.md`.

## Correction: Claude's own error, caught this session

Evidence file 02 states that policy `75882b6a`'s exclusion could not be verified by any browser or
modern client sign-in, because `clientAppTypes` is `["exchangeActiveSync", "other"]` and would
always fail the condition first. That reasoning is wrong. Entra evaluated the user condition first,
and the exclusion short-circuited evaluation before the client app type was reached.

The two records prove the ordering:

| record                          | policy 75882b6a `conditionsNotSatisfied` | `excludeRulesSatisfied` |
|---------------------------------|------------------------------------------|-------------------------|
| break-glass, 2026-09-04T14:19:38Z | users                                  | userId                  |
| jsmith, 2026-09-05T16:19:xxZ      | clientType                             | []                      |

Same policy, same client app type, different outcome, and the difference is the exclusion. All
three exclusions are verified, not two. Evidence file 02 carries a pointer to this correction.

## Supporting field

    "authenticationRequirementPolicies": [
        { "requirementProvider": "securityDefaults", "detail": "Security Defaults" }
    ]

The MFA requirement on this sign-in came from Security Defaults. This is independent support for
evidence file 02's reading that no CA policy in this tenant has ever enforced a control.

## Observation, not chased

`tokenProtectionStatusDetails` returns `signInSessionStatus: "none"` with
`signInSessionStatusCode: 1002`. Microsoft's token protection documentation lists 1002 as unbound
for lack of device state. The break-glass account signs in from an unregistered Mac in Firefox,
which is consistent. Not investigated.
