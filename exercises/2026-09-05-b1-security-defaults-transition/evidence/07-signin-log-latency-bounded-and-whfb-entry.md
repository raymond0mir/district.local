Command (verbatim):
```
GET https://graph.microsoft.com/beta/auditLogs/signIns?$top=5&$orderby=createdDateTime desc
date -u
```
Host: Graph Explorer and the Proxmox host console, both run by Raymond.

New entry present: `id: 55091a61-0c10-4ffd-8907-b9bdb9654100`, `createdDateTime:
2026-09-05T18:46:29Z`, `userPrincipalName: jsmith@raytakosharkygmail.onmicrosoft.com`,
`appDisplayName: "Windows Sign In"`. `status.errorCode: 50013`, "Assertion failed signature
validation." Same failure pattern as the prior exercise's contrast sign-in
(`a6709b24`, 2026-09-05T16:19:26Z). `appliedConditionalAccessPolicies: []` — CA is not
evaluated on this failed pre-authentication step.

`date -u` at the time of this read: 2026-09-05T18:57:21Z.

Finding: write latency is now bounded, not unmeasured. The entry did not exist at the
2026-09-05T18:51:33Z read (evidence/06). It existed by this read, at or before
2026-09-05T18:57:21Z. Latency for this event: at least 5 minutes 4 seconds, at most 10
minutes 52 seconds. This closes the "unmeasured" state of the standing exposure with a real
bound, though not an exact figure.

An unrelated Graph Explorer response was returned once during this retry sequence: a
`/users/{id}` lookup resolving the object id excluded from all three CA policies to a display
name and UPN. That identity is not recorded in this file or elsewhere in the repo, consistent
with the skill's rule against publishing the tenant Global Administrator's identity. Cause of
the mismatched query not established; noted for completeness, not investigated further this
session.
