# Both permission grant policy reads return 403, and the refusal is ambiguous

```
Bracket open:  Sat Sep 12 16:34:54 UTC 2026   (date -u, Mac Mini)
Bracket close: Sat Sep 12 16:36:09 UTC 2026   (date -u, Mac Mini)
```

**Signing identity: the native Global Administrator, `6ca413e3-06ff-4704-ab36-1348bb7387c8`.**
~~Not recorded.~~ **Corrected 2026-09-12, same session**, from the token in force at the time. See
`evidence/03-graph-explorer-token-decoded.md`. That capture changes what this refusal means: the
token carried `Directory.Read.All`, which Microsoft Learn documents as sufficient for this endpoint,
and the signed-in account holds Global Administrator. The refusal is not explained by either.

---

## Capture 1

```
Command: GET https://graph.microsoft.com/v1.0/policies/permissionGrantPolicies/microsoft-user-default-recommended/includes
Host:    Graph Explorer, browser on the Mac Mini
UTC:     2026-09-12T16:35:05Z, from the response body's innerError.date
```

```json
{
    "error": {
        "code": "Authorization_RequestDenied",
        "message": "Insufficient privileges to complete the operation.",
        "innerError": {
            "date": "2026-09-12T16:35:05",
            "request-id": "7dce98bf-5412-40cb-a81c-f13954032321",
            "client-request-id": "4871974a-84e8-072e-b09b-2211f0e15a44"
        }
    }
}
```

## Capture 2

```
Command: GET https://graph.microsoft.com/v1.0/policies/permissionGrantPolicies/microsoft-user-default-allow-consent-apps/includes
Host:    Graph Explorer, browser on the Mac Mini
UTC:     2026-09-12T16:35:33Z, from the response body's innerError.date
```

```json
{
    "error": {
        "code": "Authorization_RequestDenied",
        "message": "Insufficient privileges to complete the operation.",
        "innerError": {
            "date": "2026-09-12T16:35:33",
            "request-id": "fa7dd945-8023-4744-a59f-18d53b1a0dec",
            "client-request-id": "1d8cc720-fbc9-a73c-edb6-2bfc2034c63e"
        }
    }
}
```

Step 4 of the sequence, the Microsoft Graph service principal read, was not run.

---

## What this capture proves, and what it does not

It proves both reads were refused at 403, about 28 seconds apart, with identical codes.

**It does not say which of two causes applies, and the difference matters.** Either the token lacks
the scope the endpoint requires, or the signed-in account is not in a role the endpoint admits.
`references/gotchas.md` records that a scope failure and a role failure are distinguishable:
`PermissionScopeNotGranted` against `Authentication_RequestFromUnsupportedUserRole`. Neither code
appeared here. **That rule does not generalise to this endpoint.** `Authorization_RequestDenied`
covers both causes and names neither.

The two reads that succeeded minutes earlier do not settle it either. `Policy.Read.All` admits
`policies/authorizationPolicy`. Whether it admits `policies/permissionGrantPolicies` is a separate
question, and it is unresolved at the time of this capture.

**The decode ran, and it deepened the question rather than closing it.** The token holds
`Policy.Read.All` and `Directory.Read.All`, and does not hold `Policy.Read.PermissionGrant`.
Microsoft Learn lists `Policy.Read.PermissionGrant` as least privileged for this path and
`Directory.Read.All` as the higher-privileged alternative. The token had the alternative. The call
was still refused. Consenting the least-privileged scope and re-running is the next test. A stale
Graph Explorer response body is a second candidate, and `references/gotchas.md` records that
behavior twice, both times fixed by a re-run.
