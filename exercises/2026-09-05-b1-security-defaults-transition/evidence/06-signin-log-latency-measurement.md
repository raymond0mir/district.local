Command (verbatim):
```
GET https://graph.microsoft.com/beta/auditLogs/signIns?$top=5&$orderby=createdDateTime desc
date -u
```
Host: Graph Explorer and the Proxmox host console, both run by Raymond.

First read: same five entries as the prior capture, all `createdDateTime` 2026-09-05T16:15:22Z
through 16:20:21Z. These are the earlier 2026-09-05 exercise's contrast sign-in, not the
sign-in just performed on VM 101.

Second read, taken immediately after: identical five entries, no new one.

`date -u` at the time of this exchange: 2026-09-05T18:49:20Z.

Finding: the sign-in performed on VM 101 (PIN entry reported shortly before 18:49:20Z) had
not appeared in the sign-in log as of 18:49:20Z. This is a real, multi-minute lower bound on
write latency, not yet an upper bound. Exceeds what either the 2026-09-04 or 2026-09-05
exercise assumed when each drew a conclusion from a single empty read. Retrying to establish
whether and when the entry appears.
