# Carryover

Open items, 2026-09-07.

Read `EXPOSURES.md` next.

## Uncommitted work in the tree

The 2026-09-07 write-up is finished and not committed. Four files are modified: `report.md` and
`evidence-log.md` under `exercises/2026-09-07-plaintext-credential-remediation/`, plus
`EXPOSURES.md` and `verified-claims.md`. They record the audit finding in evidence file 03: the
exposed credential was never used, the account lived 23.3 seconds, and Claude's claim that it held
Global Administrator is retracted. Credential-scan passes 1, 1b, 2, 3 are clean on these four
files. Passes 4 and 5 are still owed. `validate.py` reports 1 ERROR, the pre-existing missing
section in the 08-31 member-server-build report. Regenerate `validation.json` after the commit,
with `--json validation.json`, and commit it separately.

## Lab state

Read 2026-09-07T15:45:34Z: pool `Data%` 82.39, metadata 4.01. Under the 85% gate by about 4 GiB.
Host memory 2.5Gi available, down from 6.7Gi two days ago with the same VMs. Unexplained; track it.
Running: VM 100 (DC01), 104 (pfSense), 107 (CA01), containers 103, 106. Stopped: VM 101, 102.
`pre-adcs-config` on VM 107 is a rollback point. Re-read the pool before any state change.

## C2 — CA issuing, enrollment still blocked

The CA is live. The client-auth template is scoped correctly and published to the CA.

`jsmith` enrolled from **VM 101**, confirmed 2026-09-07. VM 101 is stopped and has no working
QEMU guest agent. Run the next test at its own console.

The enrollment failure has no evidence file. It is Recalled. Capture it first, before testing any
theory about its cause.

Next test, on VM 101: `certutil -ca.cert`, then `certutil -verify -urlfetch`. Hypothesis is CA
chain or revocation validity. `EXPOSURES.md` lists what is ruled out and what is demoted.

C2's `report.md` is unwritten. Wait for enrollment to resolve.

## Time-sensitive

- DC01 rearm due about 2026-09-12, then every 10 days. 5 left, to about 2026-11-01.
- CA01 licence grace ends about 2026-09-15.
- P2 trial ends 2026-10-04T00:00:00Z. Audit and sign-in log reads need it.
- `svc-entraconnect` password expires about 2026-10-13.

## Still open elsewhere

B1: `d9a6a116` report-only, `75882b6a`'s block unexercised. B4's PT4H re-run owed.
