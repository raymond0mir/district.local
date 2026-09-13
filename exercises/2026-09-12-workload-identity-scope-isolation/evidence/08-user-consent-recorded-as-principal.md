# The consent is user consent, granted by adm-jsmith, for one scope

```
Command: GET https://graph.microsoft.com/v1.0/oauth2PermissionGrants?$filter=clientId eq '4c43a528-ba33-40b0-8821-c8643587f351'
Host:    Graph Explorer, browser on the Mac Mini
UTC:     after the 2026-09-13T01:07:50Z sign-in, before 2026-09-13T01:15Z
Signing identity: the native Global Administrator, 6ca413e3-06ff-4704-ab36-1348bb7387c8
```

```json
{
    "value": [
        {
            "clientId": "4c43a528-ba33-40b0-8821-c8643587f351",
            "consentType": "Principal",
            "id": "KKVDTDO6sECIIchkNYfzUb47HpG_M1xKif_yoJNjuqpGZe4DE_HFTrqd5XOBsMko",
            "principalId": "03ee6546-f113-4ec5-ba9d-e57381b0c928",
            "resourceId": "911e3bbe-33bf-4a5c-89ff-f2a09363baaa",
            "scope": " User.Read"
        }
    ]
}
```

**This read ran after the sign-in, not before it.** It was requested as a pre-consent baseline and
was run late, so it captures the grant's existence and not its absence beforehand. The ordering is
recoverable from `directoryAudits` if it is ever needed. Recorded as a gap rather than presented as
a baseline.

---

## What it establishes

**The tenant permits a member to consent to this scope with no administrator.** `consentType` is
`Principal`, which is consent for one user rather than for the tenant. `adm-jsmith` granted it during
the device code sign-in. No `AADSTS65001` appeared and no administrator acted.

**This closes the question that three refused reads could not.** Captures 02 and 04 tried to read the
tenant's permission grant policies and were refused at 403 each time, and Graph Explorer's permissions
panel would not load, so `Policy.Read.PermissionGrant` could not be consented. The empirical answer
arrived from the flow itself. The consent posture question is answered for this scope; it is not
answered in general, because a scope requiring admin consent was never attempted.

**One grant, one scope.** `scope` reads `" User.Read"`, with the leading space Entra keeps because it
stores the value as a space-delimited list. `resourceId` `911e3bbe-33bf-4a5c-89ff-f2a09363baaa` is the
Microsoft Graph service principal in this tenant, which is a different object from the Microsoft Graph
application id `00000003-0000-0000-c000-000000000000` used everywhere else in this exercise.

**The grant is a standing object, and it outlives the token.** The access token expired about 72
minutes after issue. This grant did not expire with it. It is the durable artifact of the sign-in, it
is what a refresh or a new sign-in reuses without prompting anyone, and removing the application is
what removes it. That is the permission-sprawl shape at the workload layer: a consent nobody revisits,
attached to a client nobody remembers registering.
