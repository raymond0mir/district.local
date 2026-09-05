# A failed sign-in is never evaluated by Conditional Access

Command: GET https://graph.microsoft.com/v1.0/auditLogs/signIns?$filter=userId eq '03b0f0f4-1230-42c1-983c-9bb5ecb1a2c8'&$top=5
Host: Graph Explorer, signed in as the current break-glass Global Administrator
UTC timestamp: 2026-09-05T16:17:01Z host clock; response entries carry their own UTC times

HTTP status code not captured. A full response body with `@odata.nextLink` was returned.
Redactions applied: `ipAddress` and `location.geoCoordinates` identify a private residence.
jsmith's UPN and display name are retained; jsmith is a lab test identity, already named
throughout this repo.

## Context

The contrast test needed one sign-in by a user not excluded from the three report-only CA policies.
Two attempts were made. The first used a browser on the Mac Mini and failed on the password. The
second used a Windows Hello PIN on VM 101 and succeeded, confirmed by a screenshot of the My Apps
dashboard signed in as jsmith. The screenshot is Recalled. This query was run to Capture it.

## What the query returned

Four new entries, all failures, all from the Mac Mini. The successful VM 101 sign-in is absent.

| createdDateTime      | appDisplayName | errorCode | deviceDetail.operatingSystem | appliedConditionalAccessPolicies |
|----------------------|----------------|-----------|------------------------------|----------------------------------|
| 2026-09-05T16:15:37Z | My Apps        | 50126     | MacOs                        | [] |
| 2026-09-05T16:15:22Z | My Apps        | 50126     | MacOs                        | [] |
| 2026-09-05T16:15:17Z | My Apps        | 50126     | MacOs                        | [] |
| 2026-09-05T16:15:12Z | My Apps        | 50126     | MacOs                        | [] |

All four share `correlationId` efeffc2a-34b6-442e-8812-24fe4022282e, `clientAppUsed: "Browser"`,
`browser: "Firefox 155.0"`, `isInteractive: true`, and
`conditionalAccessStatus: "notApplied"`. Status on all four:

    "errorCode": 50126,
    "failureReason": "Error validating credentials due to invalid username or password.",
    "additionalDetails": "The user didn't enter the right credentials.  It's expected to see some
                          number of these errors in your logs due to users making mistakes."

The fifth entry is the pre-existing 2026-09-04T00:37:34Z Microsoft Authentication Broker sign-in
from DESKTOP-O860UU9, which predates the policies and also carries an empty policy array.

## Finding 1: credential failure precedes policy evaluation

Every failed attempt returned `appliedConditionalAccessPolicies: []`. No policy was evaluated, not
even in report-only mode. Credential validation runs first, and a sign-in that fails it never
reaches Conditional Access.

Consequence for break-glass work: a failed sign-in cannot verify or refute an exclusion. It
produces no report-only telemetry at all. Any exclusion test must use a sign-in that succeeds.

## Finding 2: the successful sign-in is not in the interactive stream

The VM 101 PIN sign-in succeeded at approximately 2026-09-05T16:20Z and does not appear in this
response. `GET /auditLogs/signIns` on v1.0 returns interactive user sign-ins by default. Desktop
single sign-on through the primary refresh token issues the token silently, which is recorded as a
non-interactive event.

This is the leading explanation for the 2026-09-04 case as well, where a break-glass sign-in was
recorded as producing no log entry. See evidence file 05.

## Incidental observation, not chased

VM 101's taskbar clock read 4:20 PM on 2026-09-05 while the Proxmox host reported 16:17 UTC three
minutes earlier. VM 101's clock therefore runs UTC, not America/Los_Angeles. EXPOSURES.md already
records a dated-artifact offset caused by clock differences. Not investigated in this exercise.
