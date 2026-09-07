# Carryover

Open items, 2026-09-07.

Read `EXPOSURES.md` next. The skill holds the contract; gotchas live in its `references/`.

## Priority — live credential in the public repo

`exercises/2026-09-03-breakglass-rotation/evidence/02-role-assignment-and-verification.md:81`
holds a literal plaintext password (line 81, `passwordProfile.password`, not reproduced here) for
account `breakglassrotationverify@raytakosharkygmail.onmicrosoft.com` (id
`84360e8b-3321-4e37-b9ec-10fccd0263b8`). Raymond confirmed the credential is still live 2026-09-07.
Caught by credential-scan pass 1b (added 2026-09-06), which the file predates.

Disable attempted 2026-09-07, failed both by UPN and by object id: `PATCH /v1.0/users/{id}` with
`{"accountEnabled": false}` returns `400 Request_BadRequest`, "Property accountEnabled is
invalid." JSON body confirmed correct; not a malformed-request problem. Cause not yet found —
check Graph Explorer's actual granted scopes first. Disable, not rotate: this account had no
purpose beyond the 2026-09-03 verification step.

Separately, once disabled: decide whether to redact the file in place (quick, leaves the string
in git history) or rewrite history (`git filter-repo`/BFG plus a force-push — destructive, needs
Raymond's explicit go-ahead, do not do this unprompted).

## Lab state

Read 2026-09-07T15:45:34Z: pool `Data%` 82.39, metadata 4.01, under the 85% gate with about
4 GiB margin — tighter than 2026-09-06's 79.28, watch it. Host memory 1.7Gi free, 2.5Gi
available, down from 6.7Gi two days ago with the same VMs running; unexplained, worth tracking.
Running: VM 100 (DC01), VM 104, VM 107 (CA01), container 103 (vaultwarden), container 106
(rootca-offline). Stopped: VM 101, VM 102. `pre-adcs-config` on VM 107 is a valid rollback point.

## C2 — CA built and issuing, enrollment blocked

The issuing CA is live, published in AD, and confirmed working three ways (`certutil -ping`,
AD object search, `SetupStatus`). A client-auth certificate template exists, correctly scoped:
Client Authentication only, `PKI-CBA-Pilot` group holds Enroll, `jsmith` is its only member —
all confirmed by direct LDAP read, not the console screen.

`jsmith` cannot enroll from it. Every permission layer checked out correct (template ACL, CA
ACL, live token, RPC reachability). Ruled out: CertSvc instability, stale local enrollment-policy
cache. Untested: the template's Compatibility setting (Windows Server 2016, schema version 4) —
its dropdown won't downgrade in place; testing needs a fresh duplicate built with a lower
compatibility level chosen at creation. Full diagnostic trail in this exercise's `evidence-log.md`.
Do not repeat the three already-tried branches (restart timing, policy cache, schema
compatibility half-tested) without new information.

Also found: revoking Enterprise Admins from a live console session does not revoke what that
session's Kerberos ticket already carries. Real exposure, written up in `EXPOSURES.md`.

`report.md` for this exercise is still unwritten — three sessions of work. Wait for the
enrollment question to resolve rather than report a known-incomplete mechanism as done.

## Decisions closed 2026-09-07

`districtsafetyphoto.com`: dropped. DC01 rearm-vs-rebuild: deferred, no risk — the math already
lines up (5 rearms at 10-day intervals from ~09-12 lands at ~11-01, the lab's own end date).
`evidence/04`'s PII: still a non-issue, stays deferred.

## Time-sensitive

- DC01 rearm due about 2026-09-12, then every 10 days. 5 rearms left, covers to about 2026-11-01.
- CA01 licence grace ends about 2026-09-15. Rearm count not captured.
- P2 trial ends 2026-10-04T00:00:00Z.
- `svc-entraconnect` password expires about 2026-10-13.

## Still open elsewhere

B1: `d9a6a116` report-only, `75882b6a`'s block unexercised, telemetry on one user. B4's PT4H
over-limit re-run (as `adm-jsmith`, private window) still owed; not blocking.

## Repository and git

`origin/main` reached `dc3b62a` on 2026-09-07. Run `git status` for anything after it.
`validate.py` baseline: 1 ERROR, 11 WARN, 24 INFO. Re-run it.
Pass 4 of the credential scan has never run; it needs the Vaultwarden strings.
