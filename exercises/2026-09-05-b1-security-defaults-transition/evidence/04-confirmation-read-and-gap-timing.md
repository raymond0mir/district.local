Command (verbatim):
```
GET https://graph.microsoft.com/v1.0/policies/identitySecurityDefaultsEnforcementPolicy
GET https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies
date -u
```
Host: Graph Explorer (the two GETs) and the Proxmox host console (`date -u`), both run by
Raymond.
UTC timestamp: confirmation read pasted before 2026-09-05T18:43:14Z, the host's `date -u` at
the time of this capture.

Security Defaults: `isEnabled: false`. `securityDefaultsUpsell.dueDateTime`:
`2026-09-05T18:41:12.0818575Z`.

- `365bdd23` (MFA for all users): `state: "enabled"`, `modifiedDateTime`:
  `2026-09-05T18:41:28.6343692Z`.
- `75882b6a` (block legacy auth): `state: "enabled"`, `modifiedDateTime`:
  `2026-09-05T18:41:42.6392666Z`.
- `d9a6a116` (compliant or hybrid device): `state: "enabledForReportingButNotEnforced"`,
  unchanged, no `modifiedDateTime`. Held in report-only as planned.

Finding: the two CA policies enabled 14 seconds apart (18:41:28 to 18:41:42), read from their
own `modifiedDateTime` fields, a reliable server-recorded value. The Security Defaults object
carries no `modifiedDateTime` of its own. Its `securityDefaultsUpsell.dueDateTime`
(18:41:12) is offered here as a plausible proxy for the disable moment, about 16 seconds
before the first CA policy landed, but this field's exact semantics were not independently
confirmed against Microsoft documentation this session. Labeled a proxy, not a confirmed
timestamp.

If the proxy holds, the tenant carried zero MFA enforcement for approximately 16 seconds,
between Security Defaults going off and the first CA policy enforcing. `jsmith` and VM 101
made no sign-in attempt during this window; no sign-in exists to test against it.
