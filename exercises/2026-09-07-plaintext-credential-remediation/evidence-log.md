# Plaintext credential remediation — evidence log

## Captured

- `evidence/01-account-is-soft-deleted-not-live.md` — five Graph reads. Proves the exposed account
  was soft-deleted 2026-09-03T15:02:45Z, not live. Proves Graph prefixes the object id onto the UPN
  at soft delete. Proves the only live account matching `breakglass` is the disabled `breakglass@`
  account. Records two failed lookups as dead ends.
- `evidence/02-purge-and-redaction.md` — the permanent delete, its verification read, and the
  repository redaction. The verification read returns an empty `value` array. The scope check
  before the edit names one file and one commit.
- `evidence/03-audit-proves-no-use-and-names-the-actor.md` — three Graph reads, taken after the
  purge. Proves the exposed credential was never used: interactive and non-interactive sign-in
  collections are both empty, and `directoryAudits` holds four events only. Proves the account
  lived 23.3 seconds, created 2026-09-03T15:02:22.5383841Z and soft-deleted
  2026-09-03T15:02:45.8516049Z. Proves the account never held Global Administrator. Names the
  acting identity on all four events as the break-glass account, object id
  `6ca413e3-06ff-4704-ab36-1348bb7387c8`. Gives the purge its UTC timestamp,
  2026-09-07T17:55:34.1473136Z.

## Not captured, and why

- The `DELETE` response status code. Graph Explorer returns `204 No Content` with an empty body.
  No output was pasted back. The verification read stands as the proof instead. The status code is
  Recalled and is not used to support any claim.
- The exact UTC timestamp of reads 4 and 5. Successful Graph responses carry no
  `innerError.date`. The failed reads bracket them at 2026-09-07T17:51:31Z to 17:52:54Z. **The
  `DELETE` timestamp is no longer missing.** File 03's audit read returns the purge as a
  `Hard Delete user` event at 2026-09-07T17:55:34.1473136Z.
- The time of day of Raymond's 2026-09-07 decision that `adm-jsmith` is the go-forward
  administrative account. It was stated in session, not captured. File 03's purge event runs the
  same day, so the two cannot be ordered.
- The original `PATCH` request that failed on 2026-09-03. It was never written to a file. Its
  failure mode cannot now be reproduced or explained. See Open questions.

## Where Raymond was consulted

- **Purge now, or wait for the automatic 30-day purge?** Raymond: "purge it." The object was
  permanently deleted the same session. Reason not stated. The effect is that the restore window
  closed 26 days early.
- **Is the password string reused anywhere else?** Raymond: "no." This is Recalled. It cannot be
  captured from the lab. It was the basis for calling the residual risk closed in effect. **It is
  no longer the basis.** File 03 proves the credential was never used against the account it
  belonged to. The Recalled answer now covers only reuse outside this tenant, which no lab command
  can reach.
- **Redact in place, or rewrite git history?** Raymond: "redact and note." The value is replaced at
  `exercises/2026-09-03-breakglass-rotation/evidence/02-role-assignment-and-verification.md:81`.
  A note below the code block states that commit `62fd7bf` still carries the value.

## Corrections

- **`EXPOSURES.md` stated the account was "confirmed still live by Raymond 2026-09-07."** That claim
  was Recalled. It is false. The account had been soft-deleted four days earlier, on 2026-09-03.
  Retracted here and in `EXPOSURES.md`.
- **`CARRYOVER.md` named the next step as: read granted scopes, then disable the account.** Both
  steps were impossible. A soft-deleted object cannot be disabled, and the earlier failure was not a
  scope failure. Claude proposed this order at session start and then argued against it, on the
  grounds that an insufficient-scope failure returns `403 Authorization_RequestDenied`, not `400`.
  The read-first order found the real state in three requests.
- **Claude's first command included `signInActivity` in `$select`.** That property forces Graph to
  resolve the key as a GUID, so the UPN lookup failed at the key parser with a misleading `400`.
  The error described the query, not the account. Claude wrote the fallback into the same turn, so
  the cost was one round trip.
- **Claude asserted that the exposed account held Global Administrator, and classified the
  exposure on that basis.** That was wrong. The role assignment in
  `exercises/2026-09-03-breakglass-rotation/evidence/02-role-assignment-and-verification.md:35`
  targets `directoryObjects/6ca413e3-06ff-4704-ab36-1348bb7387c8`, the break-glass account. It
  does not target `84360e8b`. The exposed account was the object used to prove the role worked,
  not a holder of it. The error came from reading that file's title line and its role lookup, and
  not the assignment body four sections below. It shaped how the exposure was described for part
  of the session. Retracted in `EXPOSURES.md` and in `report.md`.
- **File 03's analysis states that the purge ran "four days after the 2026-09-07 decision".** Both
  dates are 2026-09-07. The interval is zero days. The four-day figure belongs to the account's
  soft delete on 2026-09-03. The same paragraph calls the purge "the first test after the
  decision"; the decision has no captured time of day, so the purge cannot be placed after it
  within that date. **File 03 is committed evidence and was not edited to fix this.** An edit was
  made and reverted after `validate.py` raised `evidence-modified`. The correction lives here, in
  `report.md`, and in `EXPOSURES.md` instead. Machine output in file 03 is unaffected; only its
  closing analysis paragraph carries the error.

## Open questions

- Why did the 2026-09-03 `PATCH` return `400 Request_BadRequest`, "Property accountEnabled is
  invalid," rather than `404 Request_ResourceNotFound`? A `PATCH` to the purged object id would now
  return `404`, as read 3 did. The most likely explanation is that the request used the other id in
  the same evidence file, `38d63b66-2238-4a84-bc42-2ad7d1d33418`, which is a role object with no
  `accountEnabled` property. The request was never captured, so this cannot be settled.
- ~~Who deleted the account on 2026-09-03, and was the deletion deliberate?~~ **Answered by file
  03.** `directoryAudits` names the break-glass account as `initiatedBy` on the create, the
  password set and the soft delete, all three inside 23.3 seconds from one Graph Explorer session
  and one browser. It was cleanup by the same operator, in the same session. The prior answer
  named the same actor as "most likely"; it is now Captured.
- Does any other evidence file in this repository hold a credential that the current scan passes
  miss? The scan gained a JSON-quoted pass on 2026-09-06. This value predates it. Nothing has
  re-scanned the pre-09-06 evidence files as a set.

## Not started

- Credential-scan pass 4 and pass 5. Pass 4 needs the Vaultwarden strings. Pass 5 needs the Global
  Administrator name.
- The deferred question of Raymond's personal email in pushed git history. This exercise touched the
  same history and did not change that decision.
