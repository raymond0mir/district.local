# The unfiltered audit window: what the log shows, and what it does not

## Capture header

```
command: GET https://graph.microsoft.com/v1.0/auditLogs/directoryAudits
             ?$filter=activityDateTime ge 2026-09-10T02:00:00Z
host:    Mac Mini, Graph Explorer, signed in as the tenant break-glass account (6ca413e3)
utc:     approximately 2026-09-10T14:52Z
```

The target filter was removed, so this covers every directory audit event in the tenant from
02:00:00Z to the time of the read. **Captured.**

**Redactions.** Public IP addresses are replaced with `[redacted]` throughout. One Apple push
notification token in a `StrongAuthenticationPhoneAppDetail` value is replaced with
`[redacted device token]`. The current tenant Global Administrator is referred to by object id
`6ca413e3` and never by account name, per the decision of 2026-09-03. Nothing else is removed.

## 1. The refused action produced no event. Confirmed.

`evidence/12` found no audit record for the 02:30Z password-reset refusal, and scoped that claim to
a query filtered on one target resource. This read removes the filter.

Across the whole tenant, the events nearest 02:30Z are:

| UTC | Service | Activity | Actor |
| --- | --- | --- | --- |
| 02:30:25.24 | B2C | Validate user authentication | `adm-jsmith` |
| 02:31:48.32 | B2C | Validate user authentication | `adm-jsmith` |
| 02:32:45.05 | PIM | Add member to role requested (PIM activation) | `adm-jsmith` |

**No `UserManagement` event, no failure row, nothing naming `dumbuser2`.** The refusal is absent
from the directory audit log entirely, not merely absent from a filtered view.

Two token validations bracket the refusal. The session was live and the platform recorded that the
token was valid. It did not record that the account tried to do something and was stopped.

**The finding holds at tenant scope.** An account can probe the boundaries of its own privilege
through the Entra portal and leave no entry in `directoryAudits`. Only successful changes are
recorded. A defender watching this log sees what an administrator did and is blind to what that
administrator attempted.

## 2. PIM alerts on its own recommended architecture, every two hours

Five events carry `AuditType: RoleElevatedOutsidePimAlert` and
`activityDisplayName: "Add member to role outside of PIM (permanent)"`.

| UTC | Interval since previous |
| --- | --- |
| 03:17:42.10 | — |
| 05:24:00.52 | 2h 06m 18s |
| 07:42:14.63 | 2h 18m 14s |
| 09:40:42.17 | 1h 58m 28s |
| 12:06:34.86 | 2h 25m 52s |

Every one names the same two objects: the `User Administrator` role
(`fe930be7-5e62-47db-91af-98c3a49a38b1`) and the group `PIM-UserAdmin-Pilot`
(`3265375f-23f9-4d3f-81d3-15370199bc8a`). Every one is attributed to `6ca413e3`, the account that
created the assignment. Each carries a distinct `RoleAssignmentRequestId` and a `StartTime`
matching its own `activityDateTime`.

**These are alerts, not assignments.** The `AuditType` names them as such, no `Core Directory`
"Add member to role" event accompanies any of them, and the underlying assignment was made once, on
2026-09-09. PIM re-detects the same condition on a roughly two-hourly scan and writes a fresh audit
row each time.

**The condition PIM is alerting on is the architecture Microsoft documents for PIM for Groups.** A
role-assignable group holds the directory role as a permanent, standing assignment. PIM then governs
membership of that group rather than the role itself. That permanent role assignment is, from the
alert engine's point of view, a role assigned outside PIM.

The control flags its own recommended design pattern as a violation, indefinitely, on a two-hour
cycle.

**The consequence is alert fatigue by construction.** A defender who adopts PIM for Groups inherits
a recurring alert that is correct in mechanism and wrong in meaning. The rational response is to
suppress it. Once suppressed, a genuine out-of-PIM role assignment produces the same signal and
lands in the same ignored bucket.

This is a detection failure created by following the vendor's own guidance, and it is not visible
until the alerts start arriving.

## 3. Early deactivation was refused

```
activityDisplayName: "Process role removal request"
activityDateTime:    2026-09-10T02:54:42.811766Z
result:              failure
resultReason:        ActiveDurationTooShort
AuditType:           CreateRoleRemovalRequest
initiatedBy:         6ca413e3
target:              Member role on PIM-UserAdmin-Pilot, for adm-jsmith
```

The activation completed at 02:50:59.855945Z. The removal was attempted at 02:54:42.811766Z, 3
minutes 43 seconds later, and PIM refused it.

**PIM enforces a minimum active duration before an activation can be deactivated.** The elapsed
time here is under five minutes. The exact threshold is not established by this capture and no
figure is claimed.

The operational consequence is direct: an administrator who activates by mistake cannot immediately
undo it. The privilege stays live until the minimum elapses or the window expires. A control
designed to limit standing privilege has a floor below which it will not shorten that privilege.

This belongs in `references/gotchas.md`.

## 4. Both activations expired on their own. The carryover item closes.

`CARRYOVER.md` recorded that a stray activation of B4's direct `User Administrator` eligibility was
approved in error at about 02:42Z, and that "deactivation unconfirmed, expires on its own". This
read settles it.

| UTC | Activity | Actor | Target |
| --- | --- | --- | --- |
| 04:42:10.95 | Remove member from role (PIM activation expired) | `Azure AD PIM` (`9dfd627f`) | `User Administrator`, direct |
| 04:42:05.70 | Remove member from role | `MS-PIM` (`bdefcbb6`) | `User Administrator`, direct |
| 04:51:00.99 | Remove member from role (PIM activation expired) | `Azure AD PIM` (`9dfd627f`) | Member role, `PIM-UserAdmin-Pilot` |
| 04:50:54.34 | Remove member from group | `MS-PIM` (`bdefcbb6`) | `PIM-UserAdmin-Pilot` |

Both carry `AuditType: RemoveActivatedRole` and `ActionType: Revoke`. Neither was initiated by a
human. **Neither activation was deactivated. Both expired.** The stray direct activation ran its
full two hours, from 02:42:04 to 04:42:10.

Section 3 explains why the group activation was not cut short: the one attempt to remove it early
was refused.

The group path also shows the two-layer mechanism plainly. `MS-PIM` removes the user from the group
in `Core Directory` at 04:50:54, and PIM records the role removal at 04:51:00. Group membership is
the thing PIM manipulates; the role follows from it.

## 5. `evidence/05` moves from Recalled to Captured

```
activityDisplayName: "Update role setting in PIM"
activityDateTime:    2026-09-10T02:23:09.790418Z
AuditType:           UpdatePolicy
initiatedBy:         6ca413e3
resultReason:        "Setting changes in this session: Maximum activation duration updated to
                      02:00:00. CustomExtension_PreApproval_EndUser_Assignment added:  ().
                      CustomExtension_PostApproval_EndUser_Assignment added:  (). MFA on
                      activation requirement enabled. Approval enabled with approvers
                      [redacted]. MFA on active assignment requirement enabled."
```

`evidence/05` recorded the hardened member policy from portal screenshots and labelled it Recalled.
It stated the save time as 2026-09-10T02:23:09Z. This event carries the same timestamp to the
second and enumerates the changes.

**The policy hardening is now Captured.** Two-hour maximum, MFA on activation, approval required
with a single approver, MFA on active assignment. `evidence/05` should cite this file.

The approver name is the current Global Administrator's account and is redacted here. That the
single approver is also the tenant's only working administrator was already stated as a limitation
in `evidence/05`, and this capture confirms it rather than softening it.

## 6. `evidence/06`'s MFA explanation moves from documentation to evidence

Both `CreateRequestRoleActivation` events carry:

```
IsAuthenticatedWithMfa:     True
IsActivationRequireApproval: true
```

`evidence/06` recorded that no MFA prompt appeared at activation despite the policy requiring Azure
MFA, and explained it by citing Microsoft's documentation on sessions that already satisfied MFA.
That was a documented explanation applied to an observation, not a measurement.

**The platform recorded the MFA claim as satisfied at request time.** The explanation is now
supported by the tenant's own log. `evidence/06`'s conclusion stands: the setting is a claim check,
not a step-up prompt.

Corroborating, at 14:17:03.38Z, one minute before the activation request, the
`Azure MFA StrongAuthenticationService` updated `adm-jsmith`'s
`StrongAuthenticationPhoneAppDetail`, moving `LastAuthenticatedTimestamp` to
`2026-09-10T14:17:03.19Z`. The device is named `iPhone`, running Authenticator 6.8.53. Its push
token is `[redacted device token]`. The MFA that satisfied the claim happened at sign-in, 1 minute
50 seconds before the request, and not at elevation.

## 7. This session created two standing tenant-wide consent grants

Two service principals now hold admin-consented delegated permissions with
`ConsentType: AllPrincipals`.

**Graph Explorer** (`14f143fa-ad1e-41fa-9771-e6aeb7ee4fa4`), consented 14:40:16.62Z by `6ca413e3`.
The grant was replaced wholesale — a `Remove delegated permission grant` at 14:40:16.55 followed by
an `Add delegated permission grant` at 14:40:16.55, adding one scope to an existing list. The
resulting scope set includes:

```
Directory.ReadWrite.All   RoleManagement.ReadWrite.Directory
User.ReadWrite.All        PrivilegedAccess.ReadWrite.AzureAD
User.EnableDisableAccount.All   Policy.ReadWrite.ConditionalAccess
RoleEligibilitySchedule.ReadWrite.Directory
PrivilegedEligibilitySchedule.ReadWrite.AzureADGroup
RoleManagementPolicy.ReadWrite.Directory
AuditLog.Read.All   Policy.ReadWrite.SecurityDefaults
UserAuthenticationMethod.Read.All   IdentityRiskyUser.Read.All
```

**Microsoft Graph Command Line Tools** (`8036494e-7886-4bf1-91e2-9c33b9e503c2`), consented
02:00:33.65Z by `6ca413e3`, during the `Connect-MgGraph` attempts recorded in `evidence/09`. Scopes:
`Group.ReadWrite.All`, `RoleManagement.ReadWrite.Directory`,
`PrivilegedEligibilitySchedule.ReadWrite.AzureADGroup`, `RoleManagementPolicy.ReadWrite.AzureADGroup`.

**`AllPrincipals` means the consent covers every user in the tenant, not the administrator who
granted it.** Any account that signs into either application receives a token carrying these scopes.
What that account can then do is still bounded by its directory roles, so this is not a privilege
escalation on its own. It is a permanent widening of the surface through which privilege can be
exercised, granted for a single query and never scheduled for removal.

**This exercise produced the pattern it was written to study.** A real requirement appeared: read
the PIM assignment schedule. The remedy was a tenant-wide standing grant. It took one click, it was
justified, and nothing in the process asked when it should end. That is the same shape as the
reporting-role problem in `evidence/09` section D, and it happened for real rather than as a
scenario.

Both grants belong in `EXPOSURES.md`.

## Two values not explained

`wids` on `adm-jsmith`'s activation requests reads `b79fbf4d-3ef9-4689-8143-76b194e85509` alone. On
`6ca413e3`'s events it reads `62e90394-69f5-4237-9190-012177145e10,b79fbf4d-3ef9-4689-8143-76b194e85509`.
The first of that pair is the Global Administrator role template. The second appears on both
accounts and its role is not identified here. No claim is made.

The `Access Reviews` service writes a parallel record of every PIM approval, as `Create request` and
`Request approved` events under `AADERM_` identifiers, alongside PIM's own. Why approval traffic is
duplicated into the Access Reviews service is not established.
