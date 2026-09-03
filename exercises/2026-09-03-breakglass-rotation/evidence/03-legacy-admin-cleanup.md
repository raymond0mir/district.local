# De-privilege and disable every legacy Global Administrator, then verify a sole survivor

Scope grew mid-exercise: reading the full Global Administrator membership list (needed to confirm
the new account's role assignment) surfaced two accounts nobody had accounted for —
`labadmin@raytakosharkygmail.onmicrosoft.com` and the tenant's original `#EXT#` guest
(`raytakosharky_gmail.com#EXT#@raytakosharkygmail.onmicrosoft.com`, display name `R M`). Raymond
confirmed both predate any of these sessions — inherited from the October 2025 paired-build setup,
the same unverified baseline this whole skill exists to re-check. Handled all three legacy admins
(`breakglass`, `labadmin`, `R M`) with the same pattern: strip the role, disable sign-in, keep the
object.

All calls below run as the new (renamed) native break-glass account, signed in via Graph Explorer
— by this point it had already been verified (see `02-role-assignment-and-verification.md`) to
hold and exercise Global Administrator independently.

## breakglass@raytakosharkygmail.onmicrosoft.com — object id de938dc8-feb7-4140-9a01-8e32649b8fd6

Lookup: `GET /v1.0/users/breakglass@raytakosharkygmail.onmicrosoft.com?$select=id,accountEnabled,userPrincipalName,displayName`
```json
{
    "id": "de938dc8-feb7-4140-9a01-8e32649b8fd6",
    "accountEnabled": true,
    "userPrincipalName": "breakglass@raytakosharkygmail.onmicrosoft.com",
    "displayName": "breakglass"
}
```

Role removal: `DELETE /v1.0/directoryRoles/38d63b66-2238-4a84-bc42-2ad7d1d33418/members/de938dc8-feb7-4140-9a01-8e32649b8fd6/$ref`
Response: `204 No Content`

Disable: `PATCH /v1.0/users/de938dc8-feb7-4140-9a01-8e32649b8fd6` body `{"accountEnabled": false}`
Response: `204 No Content`

Re-read confirms: `{"id": "de938dc8-...", "accountEnabled": false, "userPrincipalName": "breakglass@raytakosharkygmail.onmicrosoft.com"}`

## labadmin@raytakosharkygmail.onmicrosoft.com — object id dde25d37-4119-4217-9252-6b69d2798519

Object id already known from the full-membership read that surfaced this account (see below) — no
separate lookup call needed.

Role removal: `DELETE /v1.0/directoryRoles/38d63b66-2238-4a84-bc42-2ad7d1d33418/members/dde25d37-4119-4217-9252-6b69d2798519/$ref`
Response: `204 No Content`

Disable: `PATCH /v1.0/users/dde25d37-4119-4217-9252-6b69d2798519` body `{"accountEnabled": false}`
Response: `204 No Content`

## R M (guest, raytakosharky_gmail.com#EXT#@raytakosharkygmail.onmicrosoft.com) — object id 888038b6-2970-46dc-9245-0dfa9a464939

Treated as a distinct finding, not just cleanup: this is a `#EXT#` guest account — Microsoft's own
emergency-access guidance says break-glass identities must be cloud-only and native to the tenant,
not guests dependent on an external IdP. This account holding Global Administrator was a real
design weakness independent of whether it was "accounted for." Consulted with Raymond before
touching it specifically, given it is plausibly the tenant's original creating identity — decided:
strip the role and disable sign-in (blocks sign-in via this tenant's guest object; does not touch
the underlying external Microsoft account), but do **not** delete the object, since some
consumer-signup tenants tie subscription/billing metadata loosely to the original creating
identity in the Microsoft 365 admin center, a concept separate from Entra directory roles — no
upside to testing whether deleting the guest object severs that.

Role removal: `DELETE /v1.0/directoryRoles/38d63b66-2238-4a84-bc42-2ad7d1d33418/members/888038b6-2970-46dc-9245-0dfa9a464939/$ref`
Response: `204 No Content`

Disable: `PATCH /v1.0/users/888038b6-2970-46dc-9245-0dfa9a464939` body `{"accountEnabled": false}`
Response: `204 No Content`

## Full membership discovery (the moment the scope grew)

Command: `GET /v1.0/directoryRoles/38d63b66-2238-4a84-bc42-2ad7d1d33418/members?$select=id,userPrincipalName,displayName`
Run while the new account still shared the role with all three legacy admins:

```json
{
    "value": [
        {
            "id": "888038b6-2970-46dc-9245-0dfa9a464939",
            "userPrincipalName": "raytakosharky_gmail.com#EXT#@raytakosharkygmail.onmicrosoft.com",
            "displayName": "R M"
        },
        {
            "id": "dde25d37-4119-4217-9252-6b69d2798519",
            "userPrincipalName": "labadmin@raytakosharkygmail.onmicrosoft.com",
            "displayName": "Lab Admin"
        },
        {
            "id": "6ca413e3-06ff-4704-ab36-1348bb7387c8",
            "userPrincipalName": "[REDACTED-NEW-BREAKGLASS-UPN]",
            "displayName": "[REDACTED-NEW-BREAKGLASS-DISPLAYNAME]"
        }
    ]
}
```

(Note: `breakglass@raytakosharkygmail.onmicrosoft.com` itself had already been removed from this
list by an earlier step in this same exercise, so it does not appear here — see its own section
above for that call.)

## Closing verification — sole survivor confirmed

Same query, re-run after all three legacy accounts were stripped:

```json
{
    "value": [
        {
            "id": "6ca413e3-06ff-4704-ab36-1348bb7387c8",
            "userPrincipalName": "[REDACTED-NEW-BREAKGLASS-UPN]",
            "displayName": "[REDACTED-NEW-BREAKGLASS-DISPLAYNAME]"
        }
    ]
}
```

One Global Administrator in the tenant: the new native break-glass account. All three legacy
identities (`breakglass`, `labadmin`, `R M`) are de-privileged and sign-in-disabled, objects
retained.

## Operator error along the way (kept, not scrubbed)

Two verification steps in this exercise were re-run because Graph Explorer's method/URL fields
were left pointing at the previous request before the next one was run (a stale `DELETE` on an
already-deleted test user; a stale `GET` on `labadmin`'s own object where the role-membership list
was expected). Both were caught immediately from the response not matching what was asked for, and
neither caused any actual state change beyond what was already intended. Recorded per the skill's
own instruction that a failure is evidence — these are UI-driven near-misses, not reasoning
errors, but the pattern (stale request state in Graph Explorer) is worth knowing about for anyone
reproducing this exercise.
