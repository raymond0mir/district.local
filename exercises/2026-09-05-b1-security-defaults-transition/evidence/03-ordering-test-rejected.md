Command (verbatim):
```
PATCH https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies/75882b6a-a9ba-4d97-bbb4-72d29277ebf4
Body: {"state": "enabled"}
```
Host: Graph Explorer, run by Raymond.
UTC timestamp: 2026-09-05T18:39:37Z (from the error body's `date` field).

```
{
    "error": {
        "code": "BadRequest",
        "message": "Security Defaults is enabled in the tenant. You must disable Security defaults before enabling a Conditional Access policy.",
        "innerError": {
            "date": "2026-09-05T18:39:37",
            "request-id": "2a401101-810b-4431-bae4-3e29ac10105d",
            "client-request-id": "a185695b-34bf-8273-9dbe-4fe17506b2bb"
        }
    }
}
```

Finding: the platform rejects enabling a CA policy while Security Defaults is on, at the API
level, in this tenant. A zero-gap transition is not possible here. Security Defaults must be
disabled first. A real gap exists between that act and CA enforcement taking effect.
