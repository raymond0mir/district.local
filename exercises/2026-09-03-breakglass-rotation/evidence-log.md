# Evidence log — break-glass rotation

## What was captured

- Account creation, role assignment, and role verification for the new native break-glass
  account: `evidence/01-create-and-rename.md`, `evidence/02-role-assignment-and-verification.md`.
- De-privilege and disable of all three legacy Global Administrators found in this tenant
  (`breakglass`, `labadmin`, `R M`): `evidence/03-legacy-admin-cleanup.md`.
- Every step is a real Graph Explorer request/response pair, captured as Raymond ran it and
  pasted the result back — Captured, not Recalled, throughout.

## What was not captured, and why

- The new account's password was never captured anywhere, deliberately — Raymond generated and
  stored it himself; it never appeared in this chat or in any file.
- The new account's UPN and display name are redacted in every committed file
  (`[REDACTED-NEW-BREAKGLASS-UPN]` / `[REDACTED-NEW-BREAKGLASS-DISPLAYNAME]`), per Raymond's
  decision this session — the point of the rotation is that this identity's name isn't publicly
  discoverable the way `breakglass` was. The real values did transiently appear in this chat
  session twice (once via a screenshot, once via a membership-listing response that has no way to
  omit a member's own UPN) — noted on the record rather than silently ignored, since the capture
  contract requires flagging exactly this kind of thing. Neither instance reached a committed
  file.
- `R M`'s status as the tenant's original creating identity is Recalled from `CARRYOVER.md`
  (itself sourced from an earlier exercise's MSA-rejection finding), not re-verified this session
  — the object id and guest-account type are Captured; the specific claim "this is the original
  tenant creator" is inference from that prior finding, not independently re-confirmed here.

## Deviations from the plan going in

The exercise scope grew mid-session: it started as "rotate the one published break-glass
account" and became "de-privilege every Global Administrator this tenant has that predates these
sessions." That expansion happened because reading the full role-membership list (a step needed
regardless, to confirm the new account's assignment) surfaced two accounts nobody currently
working on this lab had accounted for. Both were confirmed with Raymond before being touched,
consistent with the standing rule to ask before anything touching standing privilege — this
wasn't scope creep executed without a checkpoint.
