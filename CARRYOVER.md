# Carryover

Open items, 2026-09-07.

Read `EXPOSURES.md` next.

## First: finish the 2026-09-07 write-up

Committed and pushed at `50e4f38`. Three later Graph reads produced a finding, captured in
`exercises/2026-09-07-plaintext-credential-remediation/evidence/03-audit-proves-no-use-and-names-the-actor.md`.
Read it; it is self-contained. These updates are owed and nothing else reflects them:

- `report.md`: the exposure closes on evidence, not on the Recalled "not reused" answer. The
  account lived 23.3 seconds, never signed in, never held a role. Two Open questions are answered.
- `evidence-log.md` Corrections: Claude wrongly claimed the exposed account held Global
  Administrator. File 03 records the correction.
- `verified-claims.md`: add Confirmed rows for the no-use proof and the 23.3-second lifetime.

- `EXPOSURES.md`: upgrade the closed entry to closed-on-evidence. Add the 2026-09-07 break-glass
  data point; that entry's own test ran and showed break-glass as `initiatedBy`.

Keep the Global Administrator's UPN and the operator IP out of every artifact. File 03 explains.

## Lab state

Read 2026-09-07T15:45:34Z: pool `Data%` 82.39, metadata 4.01. Under the 85% gate by about 4 GiB.
Host memory 2.5Gi available, down from 6.7Gi two days ago with the same VMs. Unexplained; track it.
Running: VM 100 (DC01), 104 (pfSense), 107 (CA01), containers 103, 106. Stopped: VM 101, 102.
`pre-adcs-config` on VM 107 is a rollback point.

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

## Repository

Credential scan passes 1, 1b, 2, 3 clean at `50e4f38`. Pass 4 needs the Vaultwarden strings.
Pass 5 needs the GA name. `validate.py`: one pre-existing ERROR on the 08-31 member-server-build
report.
