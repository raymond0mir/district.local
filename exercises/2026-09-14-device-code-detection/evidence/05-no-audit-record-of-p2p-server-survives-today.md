# No audit record of P2P Server's creation is retrievable today, and retention is not ruled out

Command: GET https://graph.microsoft.com/v1.0/auditLogs/directoryAudits?$filter=activityDateTime ge 2026-09-04T00:25:00Z and activityDateTime le 2026-09-04T00:45:00Z&$top=50
Command: GET https://graph.microsoft.com/v1.0/auditLogs/directoryAudits?$filter=targetResources/any(t: t/id eq '505610fa-43e4-4e65-990e-364f5794827b')&$top=50
Command: GET https://graph.microsoft.com/v1.0/auditLogs/directoryAudits?$filter=activityDateTime ge 2026-09-04T00:00:00Z and activityDateTime le 2026-09-05T00:00:00Z&$top=100
Host: Graph Explorer on the Mac Mini, signed in as the native Global Administrator (`6ca413e3`)
UTC: 2026-09-14, after 15:05:51Z. Exact per-call times not captured.

All three returned the same body.

```json
{
    "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#auditLogs/directoryAudits",
    "value": []
}
```

## What this proves

**1. No `directoryAudits` record of either `P2P Server` object is retrievable from this tenant
today.** Three filters returned empty: a ten-minute bracket, an object-id filter on the service
principal, and the whole of 2026-09-04.

**2. The whole-day read being empty changes what the empty bracket means.** The bracket alone was
consistent with a creation that wrote no audit event. The whole day being empty as well is not:
2026-09-04 is a day on which this repository captured a device join, a WHfB registration, a password
change and a directory sync. Those actions write audit events. An empty day is therefore evidence
about **retention**, not about whether the creation was logged.

**3. The question C3 opened is not answered, and the reason is now specific.** C3 asked who created
`P2P Server`. The audit surface cannot answer it, because the audit surface no longer holds
2026-09-04. This is a different and more useful negative than "the creation wrote nothing".

**4. The retention boundary is not captured.** The tenant ran on Entra ID Free before the P2 trial
opened, and the trial's start date is Recalled rather than Captured
(`EXPOSURES.md`, Time-sensitive). Microsoft documents 7-day audit retention on Free and 30 days on
paid tiers; that is documentation, not a lab capture. Which of the two applied to 2026-09-04, and
when the boundary moved, is untested. One read of the oldest surviving `directoryAudits` event
settles it and was not run.

**5. The operational lesson stands independent of the cause.** A directory object whose provenance
is not written down at the time becomes unattributable once the audit window passes. `P2P Server`
was first noticed on 2026-09-12, eight days after it appeared. By 2026-09-14 the record that would
have named its creator was already gone. Nothing in this lab captured it in between.

## Not established by this capture

- Whether the creation wrote an audit event at all.
- Whether the Entra join of VM 101 created these objects. `evidence/04` records the three-second
  time relationship and deliberately stops short of the causal claim. This capture does not advance
  it.
