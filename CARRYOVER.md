# Carryover

Open items, 2026-09-08.

Read `EXPOSURES.md` next.

## Uncommitted work in the tree

Tonight's C2 work is unstaged: ten evidence files, 30 to 39, under
`exercises/2026-09-05-adcs-issuing-ca-build/evidence/`, plus that exercise's `evidence-log.md`,
`verified-claims.md`, `EXPOSURES.md` and `references/gotchas.md`. Plugin copy synced. Run the
credential scan before committing; passes 4 and 5 are owed.

## C2 — root cause found, one defect fixed, one blocking

The enrolment question is answered. The template required the e-mail attribute in the subject and
the SAN, inherited from the built-in `User` template by duplication, and no user has `mail`. Fixed
2026-09-08: `msPKI-Certificate-Name-Flag` `-1509949440` to `-2113929216`, minor revision 4 to 5.
Rollback is a write back to `-1509949440`.

Request 5 then failed on `0x80092012 CRYPT_E_NO_REVOCATION_CHECK`, "Error Constructing or
Publishing Certificate". The CA cannot check revocation on its own chain.

**Next session, decided by Raymond: reissue the issuing CA certificate with a CDP.** Generate a
CRL on the offline root in container 106, publish it over HTTP, re-sign `ca01.req` with
`crlDistributionPoints`, reinstall with `certutil -installcert`. This also serves the tenant path:
Entra CBA needs one HTTP CDP; LDAP and OCSP are unsupported.

Template writes need a console. `qm guest exec` gets `Insufficient access rights`; `tmp-cainstall`
at CA01's console holds Full Control.

`report.md` is written and says in section one that the exercise is not closed. When a certificate
issues, update What the box said, What broke, and Open questions. Leave What I'd do differently
alone; it is complete.

## Lab state

Read 2026-09-07T22:28Z: pool `Data%` 82.91, metadata 4.03, about 3.2 GiB under the 85% gate.
Running at close: VM 100 (10000 MB), VM 107 (2048 MB), container 103 (1024 MB) on a 15 GiB host,
about 1.4 GiB free. Stopped: VM 101, 102, 104, container 106. Only container 103 has `onboot: 1`.
Re-read pool and memory before any state change.

## Time-sensitive

- P2 trial ends 2026-10-04T00:00:00Z. B4's PT4H re-run is owed. Whether tenant CBA is P2-gated is
  still not captured and needs a read inside the window.
- `svc-entraconnect` password expires about 2026-10-13.
- Neither Windows Server guest expires in September. DC01 runs to about 2027-03-02, CA01 to about
  2027-03-04. Both September dates were retracted 2026-09-08.

## Still open elsewhere

B1: `d9a6a116` report-only, `75882b6a`'s block unexercised. `Domain Users` still holds Enroll on
the client-auth template. A Vaultwarden password was shown in a screenshot 2026-09-08; rotation was
recommended and is unconfirmed.
