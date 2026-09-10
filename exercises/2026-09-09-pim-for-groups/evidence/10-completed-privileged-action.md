# A completed privileged action through the group path

## Capture header

```
Action:  Entra admin center, Users -> dumbuser2 -> Revoke sessions, run as adm-jsmith
Read:    GET https://graph.microsoft.com/v1.0/users/11033cf6-328f-4a1a-b66d-82807b0f2acb
             ?$select=id,userPrincipalName,signInSessionsValidFromDateTime
Host:    Mac Mini, browser. Portal action in a private window as adm-jsmith.
         Graph read through Graph Explorer; signing identity not established, and not
         required -- see evidence/09's correction.
UTC:     2026-09-10T14:32:27Z (action), read at approximately 14:33Z
```

## The read

```json
{
    "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users(id,userPrincipalName,signInSessionsValidFromDateTime)/$entity",
    "id": "11033cf6-328f-4a1a-b66d-82807b0f2acb",
    "userPrincipalName": "dumbuser2@raytakosharkygmail.onmicrosoft.com",
    "signInSessionsValidFromDateTime": "2026-09-10T14:32:27Z"
}
```

`@odata.context` matches the resource requested. **Captured.**

## What this establishes

`revokeSignInSessions` stamps `signInSessionsValidFromDateTime` on the target user. Tokens issued
before that instant stop being accepted. The property is the platform's own record that the
operation took effect, and it is machine-readable rather than a portal message.

The stamp reads 2026-09-10T14:32:27Z. The activation window runs 14:20:40Z to 16:20:40Z, from
`evidence/08`. The action landed 1 minute 47 seconds after the window opened and 1 hour 48 minutes
before it closed.

**`adm-jsmith` completed a `User Administrator` action that took effect, while holding the role
only through activated membership of `PIM-UserAdmin-Pilot`.** `evidence/08` established that the
before-state control held: `Active assignments` under Microsoft Entra roles returned `No results`
immediately before activation, so B4's direct eligible path was not active and cannot account for
this.

This closes the gap `evidence/08` named. That file proved the authorization gate stopped firing,
by the change in refusal text, and could not show a privileged action completing. This one
completes.

## Why this target and this action

`evidence/09` established that twelve of the tenant's sixteen users are mastered on-premises, and
that the tenant does not have password writeback enabled. An administrative password reset was
therefore impossible against any synced user at any privilege level. Of the four cloud-only
accounts, two are break-glass accounts, one is `adm-jsmith` itself, and one is `labadmin` whose
role assignments have never been read. No confirmed valid target for a password reset exists in
this tenant today.

`revokeSignInSessions` avoids that entirely. It is a cloud-side token operation. It does not touch
on-premises Active Directory, so writeback is irrelevant, and it works against a synced user.
`dumbuser2` had no active sessions, so the operational effect was nil while the audit effect was
real.

**The choice of action was forced by the tenant's configuration, not chosen for convenience.** An
exercise that had checked writeback state before choosing its test would have reached this target
in one step rather than three.

## Owed: attribution is not yet Captured

`signInSessionsValidFromDateTime` records that the revocation happened and when. **It does not
record who performed it.** The property carries no actor.

The attribution rests on two things that are not machine output: Raymond ran the action in a
private window signed in as `adm-jsmith`, and reported doing so in session. That is Recalled.

`directoryAudits` carries the actor. The read that would move attribution to Captured is:

```
GET https://graph.microsoft.com/v1.0/auditLogs/directoryAudits
    ?$filter=activityDateTime ge 2026-09-10T02:00:00Z
     and targetResources/any(t:t/id eq '11033cf6-328f-4a1a-b66d-82807b0f2acb')
```

It must run as an account holding a reporting role. Two attempts, at 14:28:22Z and 14:34:11Z,
returned `Authentication_RequestFromUnsupportedUserRole` because Graph Explorer was signed in as
`adm-jsmith`, and `User Administrator` is not a reporting role. That refusal is itself a finding,
recorded in `evidence/09` section D.

**Until that read runs, this file proves the action occurred inside the activation window and does
not prove which identity performed it.** The distinction is stated rather than glossed, because
the whole exercise turns on attribution.

The same read answers a second question: whether the refused attempt at 02:30Z produced any audit
event at all.
