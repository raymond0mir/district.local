Command (verbatim):
```
GET https://graph.microsoft.com/v1.0/policies/identitySecurityDefaultsEnforcementPolicy
GET https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies
```
Host: Graph Explorer, run by Raymond.
UTC timestamp: response pasted 2026-09-05, exact request time not separately captured.

Security Defaults: `isEnabled: true`.

Three CA policies, all `state: "enabledForReportingButNotEnforced"`:
- `365bdd23-d0e0-49a7-8131-f63b98ea6115` — "B1 - Require MFA for all users (report-only)".
  All apps, all client app types, grant `mfa`.
- `75882b6a-a9ba-4d97-bbb4-72d29277ebf4` — "B1 - Block legacy authentication (report-only)".
  Client app types `exchangeActiveSync`, `other`. Grant `block`.
- `d9a6a116-0c05-4894-af2c-a2990ef44593` — "B1 - Require compliant or hybrid joined device
  (report-only)". All apps, all client app types. Grant `compliantDevice` OR
  `domainJoinedDevice`.

All three exclude the same single user object id, `6ca413e3-06ff-4704-ab36-1348bb7387c8`
(break-glass account, per the prior exercise's verification). No fourth policy object exists.

Full JSON responses held in the session transcript, not reproduced here.
