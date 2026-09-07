# Plaintext credential remediation — evidence log

## Captured

- `evidence/01-account-is-soft-deleted-not-live.md` — five Graph reads. Proves the exposed account
  was soft-deleted 2026-09-03T15:02:45Z, not live. Proves Graph prefixes the object id onto the UPN
  at soft delete. Proves the only live account matching `breakglass` is the disabled `breakglass@`
  account. Records two failed lookups as dead ends.
- `evidence/02-purge-and-redaction.md` — the permanent delete, its verification read, and the
  repository redaction. The verification read returns an empty `value` array. The scope check
  before the edit names one file and one commit.

## Not captured, and why

- The `DELETE` response status code. Graph Explorer returns `204 No Content` with an empty body.
  No output was pasted back. The verification read stands as the proof instead. The status code is
  Recalled and is not used to support any claim.
- The exact UTC timestamp of reads 4 and 5, and of the `DELETE`. Successful Graph responses carry
  no `innerError.date`. The failed reads bracket them at 2026-09-07T17:51:31Z to 17:52:54Z.
- The original `PATCH` request that failed on 2026-09-03. It was never written to a file. Its
  failure mode cannot now be reproduced or explained. See Open questions.

## Where Raymond was consulted

- **Purge now, or wait for the automatic 30-day purge?** Raymond: "purge it." The object was
  permanently deleted the same session. Reason not stated. The effect is that the restore window
  closed 26 days early.
- **Is the password string reused anywhere else?** Raymond: "no." This is Recalled. It cannot be
  captured from the lab. It is the basis for calling the residual risk closed in effect.
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

## Open questions

- Why did the 2026-09-03 `PATCH` return `400 Request_BadRequest`, "Property accountEnabled is
  invalid," rather than `404 Request_ResourceNotFound`? A `PATCH` to the purged object id would now
  return `404`, as read 3 did. The most likely explanation is that the request used the other id in
  the same evidence file, `38d63b66-2238-4a84-bc42-2ad7d1d33418`, which is a role object with no
  `accountEnabled` property. The request was never captured, so this cannot be settled.
- Who deleted the account on 2026-09-03, and was the deletion deliberate? No capture records the
  act. `deletedDateTime` is the only trace. The most likely actor is the break-glass account, which
  `EXPOSURES.md` records as the identity used for routine tenant work.
- Does any other evidence file in this repository hold a credential that the current scan passes
  miss? The scan gained a JSON-quoted pass on 2026-09-06. This value predates it. Nothing has
  re-scanned the pre-09-06 evidence files as a set.

## Not started

- Credential-scan pass 4 and pass 5. Pass 4 needs the Vaultwarden strings. Pass 5 needs the Global
  Administrator name.
- The deferred question of Raymond's personal email in pushed git history. This exercise touched the
  same history and did not change that decision.
