# jsmith is a synced account, not cloud-only

Command: GET https://graph.microsoft.com/v1.0/users/03b0f0f4-1230-42c1-983c-9bb5ecb1a2c8?$select=id,userPrincipalName,displayName,accountEnabled,userType,onPremisesSyncEnabled,onPremisesSamAccountName,onPremisesDomainName,onPremisesImmutableId,onPremisesLastSyncDateTime,lastPasswordChangeDateTime
Host: Graph Explorer, signed in as the current break-glass Global Administrator
UTC timestamp: 2026-09-05T16:17:01Z (host `date -u`, Proxmox console, same turn)

HTTP status code not captured. A full response body was returned. No redaction applied; jsmith is
a lab test identity already named throughout this repo.

    "id": "03b0f0f4-1230-42c1-983c-9bb5ecb1a2c8",
    "userPrincipalName": "jsmith@raytakosharkygmail.onmicrosoft.com",
    "displayName": "John Smith",
    "accountEnabled": true,
    "userType": "Member",
    "onPremisesSyncEnabled": true,
    "onPremisesSamAccountName": "jsmith",
    "onPremisesDomainName": "district.local",
    "onPremisesImmutableId": "nSRJJKd2ZU6k0I5FUNxEAA==",
    "onPremisesLastSyncDateTime": "2026-09-04T00:33:32Z",
    "lastPasswordChangeDateTime": "2026-09-04T00:29:37Z"

## Why this was read

The contrast test for the break-glass exclusion needs one sign-in by a non-excluded user. jsmith is
the only other account with a registered MFA method. Establishing whether jsmith is cloud-only or
synced decides where a password reset would have to happen.

## What it establishes

jsmith is mastered in `district.local` and synced to Entra. Its password is therefore mastered on
DC01 and reaches Entra through Password Hash Sync. An Entra-side password reset is not the
operation for this account. A reset requires DC01 running, VM 102 running to carry the hash, and a
typed secret with no TTY available on either path.

`onPremisesLastSyncDateTime` 2026-09-04T00:33:32Z is four minutes after
`lastPasswordChangeDateTime` 2026-09-04T00:29:37Z. Both predate the three CA policies.

## Consequence for this exercise

The contrast sign-in does not need jsmith's password. VM 101 is Entra-joined as jsmith with a
Windows Hello for Business method registered during join, captured 2026-09-04. A PIN sign-in on
VM 101 produces the required non-excluded sign-in without touching DC01, VM 102, or any credential.
