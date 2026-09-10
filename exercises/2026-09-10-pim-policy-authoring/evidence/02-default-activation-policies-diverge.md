# Two untouched default PIM policies in the same tenant do not agree on MFA

Command: `GET https://graph.microsoft.com/v1.0/policies/roleManagementPolicies/DirectoryRole_e0b13496-83d1-4721-8bf9-f965f676106f_4219d0b2-c1b3-45cc-9a2d-87e345b43fdc?$expand=rules` (Exchange Administrator)
Command: `GET https://graph.microsoft.com/v1.0/policies/roleManagementPolicies/DirectoryRole_e0b13496-83d1-4721-8bf9-f965f676106f_c152bab8-faab-4563-afb6-4e375e31d122?$expand=rules` (Teams Administrator)
Host: Graph Explorer, tenant
Timestamp: 2026-09-10, UTC date only — exact time not captured, no host `date -u` paired with this
Graph read

Both `lastModifiedDateTime` are null and `lastModifiedBy` is empty. Every value below is a platform
default; neither policy has ever been touched in this tenant.

Both roles share these values:
- `Expiration_Admin_Eligibility`: `maximumDuration` `P365D`, `isExpirationRequired` false.
- `Expiration_Admin_Assignment`: `maximumDuration` `P180D`, `isExpirationRequired` false.
- `Enablement_Admin_Assignment`: `["Justification"]`.
- `Expiration_EndUser_Assignment`: `maximumDuration` `PT8H`, `isExpirationRequired` true.
- `Approval_EndUser_Assignment`: `isApprovalRequired` **false**, `primaryApprovers` empty,
  `approvalMode` `SingleStage`.
- `AuthenticationContext_EndUser_Assignment`: `isEnabled` false.

The one difference, and it is the self-activation MFA check:

- Exchange Administrator `Enablement_EndUser_Assignment.enabledRules`:
  `["MultiFactorAuthentication","Justification"]`.
- Teams Administrator `Enablement_EndUser_Assignment.enabledRules`: `["Justification"]` only.

Cross-checked against `exercises/2026-09-06-b4-pim-eligible-role/evidence/10-activation-policy-defaults.md`:
User Administrator's untouched default also carries
`["MultiFactorAuthentication","Justification"]`. Exchange Administrator matches that default.
Teams Administrator does not. **Teams Administrator can be self-activated today, tenant-wide, with
a typed justification and no MFA check and no approval.** This is not a misconfiguration anyone
made — the role has never been touched, per `lastModifiedDateTime: null` above — it is the
platform's own out-of-the-box default for this specific role.
