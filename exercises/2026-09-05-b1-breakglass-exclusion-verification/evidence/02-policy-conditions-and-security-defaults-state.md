# Policy conditions, and Security Defaults still enabled

Command 1: GET https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies?$select=id,displayName,state,conditions,grantControls
Command 2: GET https://graph.microsoft.com/v1.0/policies/identitySecurityDefaultsEnforcementPolicy
Host: Graph Explorer, signed in as the current break-glass Global Administrator
UTC timestamp: 2026-09-05T16:08:17Z (host `date -u`, Proxmox console, same session)

HTTP status codes not captured. Both calls returned full response bodies.
No redaction applied. Neither response contains an identity beyond the object ID already retained
in evidence file 01.

## Command 1: the three policies

All three return `"state": "enabledForReportingButNotEnforced"`.
All three return `"excludeUsers": ["6ca413e3-06ff-4704-ab36-1348bb7387c8"]`, that ID alone.
All three return `"includeUsers": ["All"]` and `"includeApplications": ["All"]`.
All three return `platforms`, `locations`, `devices`, `clientApplications`, `authenticationFlows`,
and `insiderRiskLevels` as null, and `userRiskLevels`, `signInRiskLevels`,
`servicePrincipalRiskLevels`, `excludeApplications`, `includeGroups`, `excludeGroups`,
`includeRoles`, and `excludeRoles` as empty arrays.

They differ in two fields:

| id       | displayName                                | clientAppTypes                      | builtInControls                      |
|----------|--------------------------------------------|-------------------------------------|--------------------------------------|
| 365bdd23 | B1 - Require MFA for all users             | ["all"]                             | ["mfa"]                              |
| 75882b6a | B1 - Block legacy authentication           | ["exchangeActiveSync", "other"]     | ["block"]                            |
| d9a6a116 | B1 - Require compliant or hybrid joined... | ["all"]                             | ["compliantDevice","domainJoinedDevice"] |

`grantControls.operator` is "OR" on all three. `authenticationStrength` is null on all three.

## What this proves, combined with evidence file 01

**365bdd23 and d9a6a116: the break-glass exclusion is verified.** The 2026-09-04T14:19:38Z sign-in
was an interactive browser sign-in to Graph Explorer by object ID 6ca413e3. Against these two
policies it matched every condition: user (All), application (All), and client app type (all). No
platform, location, device, or risk condition exists to fail. The policies returned
`reportOnlyNotApplied`. The exclusion array is the only term that can produce that result.

**75882b6a: the exclusion is configured but not verified.** `clientAppTypes` is
["exchangeActiveSync", "other"], which excludes browser and modern-auth clients. The sign-in in
evidence 01 could not match this policy whether or not the account was excluded. Its
`reportOnlyNotApplied` is fully explained by the client app type condition. No browser or modern
client sign-in can ever verify this policy's exclusion. A legacy-auth attempt is required.

> **RETRACTED, same session.** The last two sentences of this paragraph are wrong. Entra evaluates
> the user condition before the client app type, so the exclusion short-circuits evaluation and is
> visible on a browser sign-in. Evidence file 06 carries the machine output and the full
> correction. The rest of this paragraph stands.

**One alternative hypothesis remains open for all three.** These results are also consistent with
report-only policies never applying to any user in this tenant. Ruling that out needs one sign-in
by a non-excluded user returning `reportOnlySuccess` or `reportOnlyFailure`. See evidence file 03.

## Command 2: Security Defaults

    "id": "00000000-0000-0000-0000-000000000005",
    "displayName": "Security Defaults",
    "isEnabled": true,
    "controlTypes": [],
    "securityDefaultsUpsell": null

Security Defaults is enabled in this tenant as of 2026-09-05. Three Conditional Access policies in
`enabledForReportingButNotEnforced` state exist beside it, created through Graph on 2026-09-04.

Two consequences follow.

1. Every MFA prompt this tenant has issued comes from Security Defaults. Evidence file 01 shows
   `Security Defaults` with `result: success` and `enforcedGrantControls: ["Mfa"]` on every sign-in
   listed. None of the three CA policies has enforced anything at any time.
2. Security Defaults accepts no exclusions. It applies to the break-glass account as well. The
   break-glass exclusion has effect only after a CA policy enforces, and a CA policy can enforce
   only after Security Defaults is disabled. Between those two acts the tenant has no MFA floor.
