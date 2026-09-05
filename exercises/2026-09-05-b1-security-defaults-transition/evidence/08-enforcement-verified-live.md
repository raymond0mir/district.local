Command (verbatim):
```
GET https://graph.microsoft.com/beta/auditLogs/signIns?$top=8&$orderby=createdDateTime desc
```
Host: Graph Explorer, run by Raymond, after a fresh logout/login on VM 101.

Five new entries, `createdDateTime` 2026-09-05T19:02:04Z through 19:02:35Z, all
`userPrincipalName: jsmith@raytakosharkygmail.onmicrosoft.com`, all `conditionalAccessStatus:
"success"` at the top level (the pre-enforcement entries all read `"notApplied"`).

`appliedConditionalAccessPolicies` on each: three entries, not four. `SecurityDefaults` no
longer appears at all.
- `365bdd23` (MFA for all users): `result: "success"`. Previously `reportOnlySuccess`.
- `75882b6a` (block legacy auth): `result: "notApplied"`. Previously
  `reportOnlyNotApplied`. Genuinely evaluated now; not triggered because this is a browser
  client, not a legacy-auth client. The block itself remains unexercised against a real
  legacy-auth attempt.
- `d9a6a116` (compliant or hybrid device): `result: "reportOnlyFailure"`. Unchanged, held in
  report-only as planned.

No separate failed entry appears for the wrong-PIN attempt Raymond reported. Consistent with
the hypothesis in this exercise's chat record: a failed local PIN unlock may never produce an
assertion submitted to Entra, so it may not generate a sign-in log entry at all. Not
independently confirmed against Microsoft documentation this session.

Finding: enforcement is real, not just a policy object reporting `state: "enabled"`. Security
Defaults is confirmed absent from CA evaluation on a live sign-in. The two enforced policies
behave as designed. `d9a6a116` correctly remains report-only.
