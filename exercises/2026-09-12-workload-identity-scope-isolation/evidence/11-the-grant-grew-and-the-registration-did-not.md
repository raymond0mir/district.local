# The consent grant grew. The registration an administrator reads did not.

Two reads taken after both device code runs. They were predicted in
`evidence/10-one-variable-changed-and-the-refusal-became-a-success.md` under "Not proven here", and
run afterward.

```
Host:    Graph Explorer, browser on the Mac Mini
UTC:     after 2026-09-13T01:22:29Z
Signing identity: the native Global Administrator, 6ca413e3-06ff-4704-ab36-1348bb7387c8,
                  Captured in evidence/09-control-attempt-failed-session-never-switched.md
```

## Capture 1 — the consent grant

```
Command: GET https://graph.microsoft.com/v1.0/oauth2PermissionGrants?$filter=clientId eq '4c43a528-ba33-40b0-8821-c8643587f351'
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
            "scope": " User.Read User.ReadBasic.All"
        }
    ]
}
```

## Capture 2 — the application registration

```
Command: GET https://graph.microsoft.com/v1.0/applications(appId='388b9dd8-d98f-46f3-8eed-4418346e5673')?$select=displayName,requiredResourceAccess
```

```json
{
    "displayName": "Lab-AI-Agent-CLI",
    "requiredResourceAccess": [
        {
            "resourceAppId": "00000003-0000-0000-c000-000000000000",
            "resourceAccess": [
                {
                    "id": "e1fe6dd8-ba31-4d61-89e7-88639da4683d",
                    "type": "Scope"
                }
            ]
        }
    ]
}
```

---

## Findings

**1. The two objects disagree, and only one of them is enforced.** The grant carries
`" User.Read User.ReadBasic.All"`. The registration declares one permission, unchanged from
`evidence/06-...`. Graph enforces the grant. The portal's API permissions blade renders the
registration. An administrator reading the blade sees one permission and is reading the wrong
object.

**2. Entra amended the existing grant. It did not create a second one.** The grant id is
`KKVDTDO6sECIIchkNYfzUb47HpG_M1xKif_yoJNjuqpGZe4DE_HFTrqd5XOBsMko` in
`evidence/08-user-consent-recorded-as-principal.md` and the identical string here. One grant exists
per client, principal and resource, and the scopes accumulate inside its `scope` string.

**This is a detection finding.** A control that counts consent grants sees one grant before the
second run and one grant after. Nothing increments. The growth is inside a space-delimited string on
an object that did not change in number, and the object carries no per-scope timestamp. Monitor the
`scope` value, not the row count. `directoryAudits` records each consent event, and that is the
stream where the second grant is visible as an event.

**3. No administrator acted, at any point.** `consentType` stayed `Principal`. `adm-jsmith` holds no
directory role, and its `wids` claim in both runs holds only the non-guest marker. It widened a
workload identity's access twice, on its own, in fifteen minutes.

**4. The permission-sprawl thesis, stated at the workload layer.** An application registration's
declared permission list is a statement of intent, not a limit. It is what an administrator reviews,
and it is not what the directory enforces. The gap between them opens without any administrative
action, and it does not announce itself in the interface where an administrator would look.
