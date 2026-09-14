# Corrected full captures, superseding the compressed renderings in evidence 01, 02 and 03

Command: the three reads already named in `evidence/01`, `evidence/02` and `evidence/03`. No new read was performed.
Host: Graph Explorer on the Mac Mini, signed in as the native Global Administrator (`6ca413e3`)
UTC: captures taken 2026-09-14T14:59:06Z and 2026-09-14T15:05:51Z. This file written 2026-09-14, after the exercise was committed and pushed.

## Why this file exists

Evidence 01, 02 and 03 rendered the captured responses in a compressed form. Claude shortened them
to make them read more easily. This repository does not allow that: a capture block holds machine
output, unedited except for redactions that are named in place.

Those three files are closed evidence and `validate.py` refuses modification of them, which is the
correct behavior. An added file is the sanctioned route, so the complete output is recorded here and
the compressed blocks in 01, 02 and 03 are superseded by it.

**What was compressed, itemised:**

1. **Truncated GUIDs.** Conditional Access policy ids were written as `"365bdd23-..."`,
   `"75882b6a-..."` and `"d9a6a116-..."`, and a user object id as `"03ee6546-..."`, in evidence 01
   and 03.
2. **Reduced `appliedConditionalAccessPolicies` blocks.** Records 2, 3 and 4 of evidence 01, and all
   four records of evidence 03, dropped `enforcedGrantControls`, `enforcedSessionControls`,
   `sessionControlsNotSatisfied`, `authenticationStrength`, `includeRulesSatisfied` and
   `excludeRulesSatisfied`.
3. **A summarised value.** Evidence 01 record 3 replaced the `Oauth Scope Info` value with the text
   `[same 26-scope list as record 2, verbatim in the response]`.
4. **An ellipsized value.** Evidence 01 record 3 wrote `"Mozilla/5.0 ... Firefox/155.0"`.
5. **Dropped `modifiedProperties` and `additionalDetails`.** Five of the seven `directoryAudits`
   events in evidence 02 lost entries, including every `ServicePrincipal.*` property and every
   `TargetId.ServicePrincipalNames` value.
6. **Compressed record blocks.** The four Graph Explorer records in evidence 03 were written as
   one-line summaries rather than as returned.
7. **A broken path reference.** Evidence 01 cites
   `exercises/2026-09-05-b1-breakglass-exclusion-verification/evidence/01-...`. The real path is
   `exercises/2026-09-05-b1-breakglass-exclusion-verification/evidence/01-breakglass-signins-after-policy-creation.md`.

None of the seven changed a finding. Every claim in the report survives this file unchanged. The
defect is in how the evidence was presented, not in what it showed, and it is recorded because a
capture that has been tidied is no longer a capture.

## Redaction set, unchanged from evidence 01, 02 and 03

- `ipAddress` on sign-in records, and every `location` object. They identify a private residence.
- `userDisplayName` and `userPrincipalName` of principal `6ca413e3`, replaced with `<GA>`. The
  current tenant Global Administrator's name may not appear in an artifact.
- One `StrongAuthenticationPhoneAppDetail` value holding an Apple push credential for a personal
  handset, and one `User.PUID`.
- `initiatedBy.user.ipAddress` on audit events is **kept**. Those are Microsoft service addresses
  and not the operator's, which is itself a finding.

## The Conditional Access block, written once

Every sign-in record below carries `appliedConditionalAccessPolicies` with the same three policies
and the same property set. The three policy ids in full:

```
365bdd23-d0e0-49a7-8131-f63b98ea6115   B1 - Require MFA for all users (report-only)
75882b6a-a9ba-4d97-bbb4-72d29277ebf4   B1 - Block legacy authentication (report-only)
d9a6a116-0c05-4894-af2c-a2990ef44593   B1 - Require compliant or hybrid joined device (report-only)
```

Per-record `result`, `conditionsSatisfied`, `conditionsNotSatisfied`, `includeRulesSatisfied` and
`excludeRulesSatisfied` values are given with each record. `enforcedSessionControls`,
`sessionControlsNotSatisfied` and `authenticationStrength` were returned as `[]`, `[]` and `null`
respectively on every one of the twelve records across both reads, with no exception.
`enforcedGrantControls` was `["Mfa"]`, `["Block"]` and `["RequireCompliantDevice"]` for the three
policies in that order, on every record.

## Read A, beta non-interactive stream, complete

`GET https://graph.microsoft.com/beta/auditLogs/signIns?$filter=signInEventTypes/any(t: t eq 'nonInteractiveUser') and createdDateTime ge 2026-09-13T00:55:00Z and createdDateTime le 2026-09-13T01:35:00Z&$top=50`

Four records. The Conditional Access results per record:

| Record | `365bdd23` | `75882b6a` | `d9a6a116` | `conditionsSatisfied` / `conditionsNotSatisfied` |
|---|---|---|---|---|
| `42a0215d` 01:22:28Z run 2 token | success | notApplied | reportOnlyFailure | `application,users` / `none`, except `75882b6a` which is `application,users` / `clientType` |
| `a8835a85` 01:16:38Z `<GA>` Graph Explorer | notApplied | notApplied | reportOnlyNotApplied | `application` / `users`, each with `excludeRulesSatisfied` `[{users, userId}]` |
| `79fe4851` 01:15:37Z adm-jsmith Graph Explorer | success | notApplied | reportOnlyFailure | `application,users` / `none`, except `75882b6a` which is `application,users` / `clientType` |
| `a7e6febd` 01:07:50Z run 1 token | success | notApplied | reportOnlyFailure | `application,users` / `none`, except `75882b6a` which is `application,users` / `clientType` |

`includeRulesSatisfied` on all four records, for all three policies, is:

```json
[ { "conditionalAccessCondition": "application", "ruleSatisfied": "allApps" },
  { "conditionalAccessCondition": "users", "ruleSatisfied": "allUsers" } ]
```

`excludeRulesSatisfied` is `[]` on records `42a0215d`, `79fe4851` and `a7e6febd`, and
`[ { "conditionalAccessCondition": "users", "ruleSatisfied": "userId" } ]` on all three policies of
record `a8835a85`.

**Record `79fe4851`'s `Oauth Scope Info`, written out in full** rather than cross-referenced as
evidence 01 did. It is byte-identical to record `a8835a85`'s:

```
["Application.Read.All","AuditLog.Read.All","Directory.Read.All","Directory.ReadWrite.All",
"IdentityRiskyUser.Read.All","openid","Policy.Read.All","Policy.ReadWrite.ConditionalAccess",
"PrivilegedAccess.ReadWrite.AzureAD","profile","RoleManagement.ReadWrite.Directory","User.Read",
"User.Read.All","User.ReadBasic.All","User.ReadWrite.All","UserAuthenticationMethod.Read",
"UserAuthenticationMethod.Read.All","email","AgentIdUser.ReadWrite.All",
"AgentIdUser.ReadWrite.IdentityParentedBy","Policy.ReadWrite.SecurityDefaults",
"PrivilegedAssignmentSchedule.Read.AzureADGroup","PrivilegedEligibilitySchedule.ReadWrite.AzureADGroup",
"RoleEligibilitySchedule.ReadWrite.Directory","RoleManagementPolicy.ReadWrite.Directory",
"User.EnableDisableAccount.All"]
```

**Record `79fe4851`'s `userAgent`, written out in full:**

```
Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:155.0) Gecko/20100101 Firefox/155.0
```

All other fields of the four records are as recorded in `evidence/01`, which reproduced them
without alteration.

## Read B, v1.0 interactive stream, complete

`GET https://graph.microsoft.com/v1.0/auditLogs/signIns?$filter=createdDateTime ge 2026-09-13T00:55:00Z and createdDateTime le 2026-09-13T01:35:00Z&$top=50`

Eight records. Every one carries `isInteractive` true, `riskDetail`, `riskLevelAggregated`,
`riskLevelDuringSignIn` and `riskState` all `none`, `riskEventTypes` and `riskEventTypes_v2` both
`[]`, `resourceDisplayName` `Microsoft Graph`, `resourceId` `00000003-0000-0000-c000-000000000000`,
`resourceTenantId` and `homeTenantId` both `e0b13496-83d1-4721-8bf9-f965f676106f`,
`servicePrincipalName` null, `ipAddress` `[redacted]`, `location` `[redacted: private residence]`,
and `userAgent` `Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:155.0) Gecko/20100101 Firefox/155.0`.

| id | time | user | app | `clientAppUsed` | `conditionalAccessStatus` | `errorCode` | `servicePrincipalId` |
|---|---|---|---|---|---|---|---|
| `dd79c411-e6d9-4d79-97b8-6a463c3eb000` | 01:22:26Z | `03ee6546` | Lab-AI-Agent-CLI | Mobile Apps and Desktop clients | success | 0 | `4c43a528-ba33-40b0-8821-c8643587f351` |
| `50175a48-3b5c-4e78-86f4-0105e7ac6e00` | 01:22:08Z | `03ee6546` | Lab-AI-Agent-CLI | Mobile Apps and Desktop clients | success | 65001 | `4c43a528-ba33-40b0-8821-c8643587f351` |
| `5beec047-646e-445d-9948-14b326630801` | 01:16:37Z | `6ca413e3` `<GA>` | Graph Explorer | Browser | notApplied | 0 | `14f143fa-ad1e-41fa-9771-e6aeb7ee4fa4` |
| `88b0e952-f6c3-487e-a3c5-6683cc728400` | 01:15:36Z | `03ee6546` | Graph Explorer | Browser | success | 0 | `14f143fa-ad1e-41fa-9771-e6aeb7ee4fa4` |
| `5beec047-646e-445d-9948-14b39a540801` | 01:15:34Z | `03ee6546` | Graph Explorer | Browser | success | 50140 | `14f143fa-ad1e-41fa-9771-e6aeb7ee4fa4` |
| `e889a0c1-c566-4744-a6bf-d89647fc6200` | 01:15:33Z | `03ee6546` | Graph Explorer | Browser | failure | 50097 | `14f143fa-ad1e-41fa-9771-e6aeb7ee4fa4` |
| `3d325160-4f8a-4daf-8056-56e3d8cd6100` | 01:07:46Z | `03ee6546` | Lab-AI-Agent-CLI | Mobile Apps and Desktop clients | success | 0 | `4c43a528-ba33-40b0-8821-c8643587f351` |
| `0287d5cf-0a1b-46aa-996f-27eab31eeb00` | 01:07:40Z | `03ee6546` | Lab-AI-Agent-CLI | Mobile Apps and Desktop clients | success | 65001 | `4c43a528-ba33-40b0-8821-c8643587f351` |

`correlationId` by record: `dd79c411` and `50175a48` carry `bae290c5-0422-4859-9004-e12b7af9be12`.
`5beec047-...326630801` carries `01a09856-6318-788a-ab9e-915e146b9f0f`. `88b0e952`,
`5beec047-...39a540801` and `e889a0c1` carry `01a09855-6ea6-7186-ae80-e3b48c38d39d`. `3d325160` and
`0287d5cf` carry `61805a6d-2177-43cb-858c-f84fa8f73815`.

`status.failureReason` and `status.additionalDetails` in full:

```
dd79c411  "Other."  /  "MFA completed in Azure AD"
50175a48  "The user or administrator has not consented to use the application with ID
           '{identifier}'{namePhrase}. Send an interactive authorization request for this user and
           resource."  /  null
5beec047-...326630801  "Other."  /  null
88b0e952  "Other."  /  "MFA requirement satisfied by claim in the token"
5beec047-...39a540801  "This occurred due to 'Keep me signed in' interrupt when the user was
           signing in."  /  "This is an expected part of the login flow, where a user is asked if
           they want to remain signed into this browser to make further logins easier. For more
           details, see https://techcommunity.microsoft.com/t5/microsoft-entra/the-new-azure-ad-sign-in-and-keep-me-signed-in-experiences/td-p/128267"
e889a0c1  "Device authentication is required."  /  "This is not an error - this is an interrupt
           that triggers device authentication when required due to a Conditional Access policy or
           because the application or resource requested the device ID in a token. This code alone
           does not indicate a failure on your users part to sign in. The sign in logs may indicate
           that the device authentication challenge was passed succesfully or failed."
3d325160  "Other."  /  "MFA requirement satisfied by claim in the token"
0287d5cf  "The user or administrator has not consented to use the application with ID
           '{identifier}'{namePhrase}. Send an interactive authorization request for this user and
           resource."  /  "MFA completed in Azure AD"
```

`authenticationAppDeviceDetails` is non-null on exactly two records, `dd79c411` and `0287d5cf`, and
identical on both:

```json
{ "deviceId": "", "operatingSystem": "Ios", "clientApp": "Authenticator", "appVersion": "6.8.54" }
```

It is null on `50175a48`, `5beec047-...326630801`, `88b0e952`, `5beec047-...39a540801`, `e889a0c1`
and `3d325160`.

`deviceDetail` is `{ "deviceId": "", "displayName": "", "operatingSystem": "", "browser":
"Firefox 155.0", "isCompliant": false, "isManaged": false, "trustType": null }` on the four
Lab-AI-Agent-CLI records, and the same with `"operatingSystem": "MacOs"` on the four Graph Explorer
records.

Conditional Access results per record:

| id | `365bdd23` | `75882b6a` | `d9a6a116` |
|---|---|---|---|
| `dd79c411` | success | notApplied | reportOnlyFailure |
| `50175a48` | notApplied | notApplied | reportOnlyNotApplied |
| `5beec047-...326630801` | notApplied | notApplied | reportOnlyNotApplied |
| `88b0e952` | success | notApplied | reportOnlyFailure |
| `5beec047-...39a540801` | success | notApplied | reportOnlyFailure |
| `e889a0c1` | success | notApplied | reportOnlyFailure |
| `3d325160` | success | notApplied | reportOnlyFailure |
| `0287d5cf` | success | notApplied | reportOnlyFailure |

The v1.0 response returns `appliedConditionalAccessPolicies` entries with `id`, `displayName`,
`enforcedGrantControls`, `enforcedSessionControls` and `result` only. It carries no
`conditionsSatisfied`, `conditionsNotSatisfied`, `includeRulesSatisfied` or `excludeRulesSatisfied`.
That difference between v1.0 and beta is the standing gotcha recorded from
`exercises/2026-09-05-b1-breakglass-exclusion-verification`, and this capture confirms it again.

## What this file does not change

Every finding in `report.md` stands. The four-step sequence, `originalTransferMethod` as the only
field naming the flow, the `Oauth Scope Info` distinction between the two runs, the three audit
events, the `Consent to application` defect, the `Unassign` recording an addition, and the
`initiatedBy` correction are all unaffected. The complete records confirm each of them.
