# Carryover

Open items, 2026-09-07.

Read `EXPOSURES.md` next.

## Closed this session

The plaintext credential is remediated. The account was already soft-deleted, not live. It is
now purged. The string is redacted in place. It remains in history at `62fd7bf`, by decision.
See `exercises/2026-09-07-plaintext-credential-remediation/report.md`.

## Lab state

Read 2026-09-07T15:45:34Z: pool `Data%` 82.39, metadata 4.01. Under the 85% gate by about
4 GiB, tighter than 09-06's 79.28. Host memory 2.5Gi available, down from 6.7Gi two days ago
with the same VMs running. Unexplained; track it.
Running: VM 100 (DC01), 104 (pfSense), 107 (CA01), containers 103 and 106. Stopped: VM 101, 102.
`pre-adcs-config` on VM 107 is a valid rollback point.

## C2 — CA issuing, enrollment still blocked

The CA is live. The client-auth template is correctly scoped and published to the CA.

`jsmith` still cannot enroll. **Raymond confirmed 2026-09-07: `jsmith` enrolled from VM 101.**
VM 101 is stopped, and it has no working QEMU guest agent. Run the next test at VM 101's own
console. Nothing scripted can capture from that machine.

The enrollment failure has no evidence file. It is Recalled. Capture it first, before testing
theories about its cause.

Next test, not yet run, on VM 101: `certutil -ca.cert`, then `certutil -verify -urlfetch`.
Hypothesis is CA chain or revocation validity. The root is hand-built OpenSSL, no CRL is
published, and `-installcert` already blocked once on a revocation dialog.

What is ruled out, and what is demoted, is listed in `EXPOSURES.md`. Do not rebuild a template
for the Server 2016 theory first.

`report.md` for C2 is still unwritten. Wait for enrollment to resolve.

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
`validate.py`: last run 2 ERROR, 25 WARN, 24 INFO. One ERROR is a checker bug:
`reference-missing` does not strip a `:81` line suffix. Re-run after this session's commits.
Credential scan: passes 1, 1b, 2, 3 clean at last commit. Pass 4 never run, needs the
Vaultwarden strings. Pass 5 needs the GA name.
