# The default activation policy for User Administrator, before any change

Command: `GET https://graph.microsoft.com/v1.0/policies/roleManagementPolicies/DirectoryRole_e0b13496-83d1-4721-8bf9-f965f676106f_6710deb2-862a-4457-95cb-a7b2dd297ca0/rules`
Host: Graph Explorer, tenant, signed in as the native Global Administrator
Timestamp: 2026-09-06, same session as `01-preflight-and-dc01-standing-state.md`

`evidence/09` captures this policy's `lastModifiedDateTime` as null. Every value below is a
platform default, not a prior choice made in this tenant.

The response is reformatted to one rule object per line. Every field, value, and rule is present.
Nothing is dropped, added, or altered. The `@odata.context` and `@microsoft.graph.tips` lines are
omitted, and are noted here rather than removed silently.

```json
{"@odata.type":"#microsoft.graph.unifiedRoleManagementPolicyExpirationRule","id":"Expiration_Admin_Eligibility","isExpirationRequired":false,"maximumDuration":"P365D","target":{"caller":"Admin","operations":["all"],"level":"Eligibility","inheritableSettings":[],"enforcedSettings":[]}}
{"@odata.type":"#microsoft.graph.unifiedRoleManagementPolicyEnablementRule","id":"Enablement_Admin_Eligibility","enabledRules":[],"target":{"caller":"Admin","operations":["all"],"level":"Eligibility","inheritableSettings":[],"enforcedSettings":[]}}
{"@odata.type":"#microsoft.graph.unifiedRoleManagementPolicyNotificationRule","id":"Notification_Admin_Admin_Eligibility","notificationType":"Email","recipientType":"Admin","notificationLevel":"All","isDefaultRecipientsEnabled":true,"notificationRecipients":[],"target":{"caller":"Admin","operations":["all"],"level":"Eligibility","inheritableSettings":[],"enforcedSettings":[]}}
{"@odata.type":"#microsoft.graph.unifiedRoleManagementPolicyNotificationRule","id":"Notification_Requestor_Admin_Eligibility","notificationType":"Email","recipientType":"Requestor","notificationLevel":"All","isDefaultRecipientsEnabled":true,"notificationRecipients":[],"target":{"caller":"Admin","operations":["all"],"level":"Eligibility","inheritableSettings":[],"enforcedSettings":[]}}
{"@odata.type":"#microsoft.graph.unifiedRoleManagementPolicyNotificationRule","id":"Notification_Approver_Admin_Eligibility","notificationType":"Email","recipientType":"Approver","notificationLevel":"All","isDefaultRecipientsEnabled":true,"notificationRecipients":[],"target":{"caller":"Admin","operations":["all"],"level":"Eligibility","inheritableSettings":[],"enforcedSettings":[]}}
{"@odata.type":"#microsoft.graph.unifiedRoleManagementPolicyExpirationRule","id":"Expiration_Admin_Assignment","isExpirationRequired":false,"maximumDuration":"P180D","target":{"caller":"Admin","operations":["all"],"level":"Assignment","inheritableSettings":[],"enforcedSettings":[]}}
{"@odata.type":"#microsoft.graph.unifiedRoleManagementPolicyEnablementRule","id":"Enablement_Admin_Assignment","enabledRules":["Justification"],"target":{"caller":"Admin","operations":["all"],"level":"Assignment","inheritableSettings":[],"enforcedSettings":[]}}
{"@odata.type":"#microsoft.graph.unifiedRoleManagementPolicyNotificationRule","id":"Notification_Admin_Admin_Assignment","notificationType":"Email","recipientType":"Admin","notificationLevel":"All","isDefaultRecipientsEnabled":true,"notificationRecipients":[],"target":{"caller":"Admin","operations":["all"],"level":"Assignment","inheritableSettings":[],"enforcedSettings":[]}}
{"@odata.type":"#microsoft.graph.unifiedRoleManagementPolicyNotificationRule","id":"Notification_Requestor_Admin_Assignment","notificationType":"Email","recipientType":"Requestor","notificationLevel":"All","isDefaultRecipientsEnabled":true,"notificationRecipients":[],"target":{"caller":"Admin","operations":["all"],"level":"Assignment","inheritableSettings":[],"enforcedSettings":[]}}
{"@odata.type":"#microsoft.graph.unifiedRoleManagementPolicyNotificationRule","id":"Notification_Approver_Admin_Assignment","notificationType":"Email","recipientType":"Approver","notificationLevel":"All","isDefaultRecipientsEnabled":true,"notificationRecipients":[],"target":{"caller":"Admin","operations":["all"],"level":"Assignment","inheritableSettings":[],"enforcedSettings":[]}}
{"@odata.type":"#microsoft.graph.unifiedRoleManagementPolicyExpirationRule","id":"Expiration_EndUser_Assignment","isExpirationRequired":true,"maximumDuration":"PT8H","target":{"caller":"EndUser","operations":["all"],"level":"Assignment","inheritableSettings":[],"enforcedSettings":[]}}
{"@odata.type":"#microsoft.graph.unifiedRoleManagementPolicyEnablementRule","id":"Enablement_EndUser_Assignment","enabledRules":["MultiFactorAuthentication","Justification"],"target":{"caller":"EndUser","operations":["all"],"level":"Assignment","inheritableSettings":[],"enforcedSettings":[]}}
{"@odata.type":"#microsoft.graph.unifiedRoleManagementPolicyApprovalRule","id":"Approval_EndUser_Assignment","target":{"caller":"EndUser","operations":["all"],"level":"Assignment","inheritableSettings":[],"enforcedSettings":[]},"setting":{"isApprovalRequired":false,"isApprovalRequiredForExtension":false,"isRequestorJustificationRequired":true,"approvalMode":"SingleStage","approvalStages":[{"approvalStageTimeOutInDays":1,"isApproverJustificationRequired":true,"escalationTimeInMinutes":0,"isEscalationEnabled":false,"primaryApprovers":[],"escalationApprovers":[]}]}}
{"@odata.type":"#microsoft.graph.unifiedRoleManagementPolicyAuthenticationContextRule","id":"AuthenticationContext_EndUser_Assignment","isEnabled":false,"claimValue":null,"target":{"caller":"EndUser","operations":["all"],"level":"Assignment","inheritableSettings":[],"enforcedSettings":[]}}
{"@odata.type":"#microsoft.graph.unifiedRoleManagementPolicyNotificationRule","id":"Notification_Admin_EndUser_Assignment","notificationType":"Email","recipientType":"Admin","notificationLevel":"All","isDefaultRecipientsEnabled":true,"notificationRecipients":[],"target":{"caller":"EndUser","operations":["all"],"level":"Assignment","inheritableSettings":[],"enforcedSettings":[]}}
{"@odata.type":"#microsoft.graph.unifiedRoleManagementPolicyNotificationRule","id":"Notification_Requestor_EndUser_Assignment","notificationType":"Email","recipientType":"Requestor","notificationLevel":"All","isDefaultRecipientsEnabled":true,"notificationRecipients":[],"target":{"caller":"EndUser","operations":["all"],"level":"Assignment","inheritableSettings":[],"enforcedSettings":[]}}
{"@odata.type":"#microsoft.graph.unifiedRoleManagementPolicyNotificationRule","id":"Notification_Approver_EndUser_Assignment","notificationType":"Email","recipientType":"Approver","notificationLevel":"All","isDefaultRecipientsEnabled":true,"notificationRecipients":[],"target":{"caller":"EndUser","operations":["all"],"level":"Assignment","inheritableSettings":[],"enforcedSettings":[]}}
```

## What the defaults already do

- `Expiration_EndUser_Assignment`: `isExpirationRequired` true, `maximumDuration` PT8H. An
  activation cannot be permanent. Time-bounding is on by default.
- `Enablement_EndUser_Assignment`: `MultiFactorAuthentication` and `Justification`. An activation
  demands both by default.

## What the defaults do not do

- `Approval_EndUser_Assignment`: `isApprovalRequired` **false**. `primaryApprovers` is empty.
  No human approves an activation.
- `AuthenticationContext_EndUser_Assignment`: `isEnabled` false. Activation is not tied to a
  Conditional Access authentication context.
- `Expiration_Admin_Assignment`: `isExpirationRequired` false, `maximumDuration` P180D. An
  administrator can still create a standing active assignment through PIM.
- `Expiration_Admin_Eligibility`: `isExpirationRequired` false, `maximumDuration` P365D. This is
  why the permanent eligibility in `evidence/08` was accepted.

## The finding

The platform ships just-in-time behavior on, and human approval off. A tenant that enables PIM
and changes nothing gets bounded, MFA-gated, self-justified activation with no second person in
the loop. The activation record will show who asked and why. It will not show that anyone agreed.

That distinction is the difference between an audit trail and a control.
