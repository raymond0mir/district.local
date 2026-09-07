# Carryover

Open items, 2026-09-07.

Read `EXPOSURES.md` next.

## Priority — live credential in the public repo

A live plaintext password sits in `exercises/2026-09-03-breakglass-rotation/evidence/02-role-assignment-and-verification.md:81`.
Full detail, including the failed disable attempts, is in `EXPOSURES.md`. Next step: read Graph
Explorer's granted scopes, then disable the account. Do not rotate it.

Once disabled, choose redact-in-place or history rewrite. The rewrite needs Raymond's go-ahead.

## Lab state

Read 2026-09-07T15:45:34Z: pool `Data%` 82.39, metadata 4.01. Under the 85% gate by about
4 GiB, tighter than 09-06's 79.28. Host memory 2.5Gi available, down from 6.7Gi two days ago
with the same VMs running. Unexplained; track it.
Running: VM 100 (DC01), 104 (pfSense), 107 (CA01), containers 103 and 106. Stopped: VM 101, 102.
`pre-adcs-config` on VM 107 is a valid rollback point.

## C2 — CA issuing, enrollment still blocked

The CA is live. The client-auth template is correctly scoped **and already published to the
CA**: `certutil -CATemplates` lists it first (`evidence/29`).

`jsmith` still cannot enroll. Confirmed correct: template ACL and EKU, CA ACL, `jsmith`'s live
token, RPC reachability. Ruled out: CertSvc instability, stale policy cache, non-publication.
Demoted: the Server 2016 compatibility theory is untested and unsupported. Do not rebuild a
template for it first. Both retractions sit in the evidence-log's Corrections.

Next test, not yet run: `certutil -ca.cert`, then `certutil -verify -urlfetch` on CA01.
Hypothesis is CA chain or revocation validity: the root is hand-built OpenSSL, no CRL is
published, and `-installcert` already blocked once on a revocation dialog.

That test needs one fact the log never recorded: which machine `jsmith` enrolled from.

`report.md` is still unwritten. Wait for enrollment to resolve.

## Time-sensitive

- DC01 rearm due about 2026-09-12, then every 10 days. 5 left, covers to about 2026-11-01.
- CA01 licence grace ends about 2026-09-15. Rearm count not captured.
- P2 trial ends 2026-10-04T00:00:00Z.
- `svc-entraconnect` password expires about 2026-10-13.

## Still open elsewhere

B1: `d9a6a116` report-only, `75882b6a`'s block unexercised, telemetry on one user. B4's PT4H
over-limit re-run still owed; not blocking.

## Repository and git

Run `git status` and `git log -1`.
`validate.py`: 2 ERROR, 25 WARN, 24 INFO. The 1/11/24 baseline was stale, not a regression. One
ERROR is a checker bug: `reference-missing` does not strip a `:81` line suffix.
Credential scan: passes 1, 1b, 2, 3 clean at last commit. Pass 4 never run, needs the
Vaultwarden strings. Pass 5 needs the GA name.
