# Break-glass account rotation

## What I set out to do

`breakglass@raytakosharkygmail.onmicrosoft.com` — this lab's working Global Administrator, used
across several published exercises since 2026-08-31 — has its full UPN sitting in a public
GitHub repo. `CARRYOVER.md` flagged this as a decision owed before `CURRICULUM.md`'s B1
(Conditional Access) made the account load-bearing: rotate the identity to something not
published, verify the replacement actually works, and only then retire the old one. Hypothesis
going in: this is a mechanical create-verify-retire operation on one account.

## The setup

Tenant-side work only — no VM state, no `qm guest exec`. Everything ran through Graph Explorer,
Raymond signed in as the relevant identity at each step, one request at a time, pasting responses
back. No pre-flight readings apply to this exercise (nothing here touches Proxmox host state).

## What I did

1. Created a new cloud-only user via `POST /users`, intending a non-obvious UPN from the start.
2. Assigned it Global Administrator via the tenant's `directoryRoles` collection.
3. Verified the new account from its own signed-in session — first via `/me/memberOf`, then by
   having it create and delete a real throwaway user object, proving exercised privilege rather
   than just a role claim in a token.
4. Read the full Global Administrator membership list to confirm the new account's assignment —
   this is the step that surfaced two additional, previously unaccounted-for Global Admins.
5. Consulted Raymond on both before touching them (see below), then applied the same
   strip-role-and-disable pattern to all three legacy admins: `breakglass`, `labadmin`, and the
   tenant's original `#EXT#` guest account (`R M`).
6. Re-read the membership list a final time: exactly one Global Administrator remains, the new
   account.

## Where Raymond was consulted

- **Naming discoverability, before creating anything:** asked whether the new account's name
  should appear in the published report the way the old one did. Decision: no — redact the exact
  UPN from every committed file, prose and evidence alike, since the whole point of this exercise
  is that this identity isn't publicly guessable.
- **Old account disposition, before creating anything:** asked whether `breakglass` should be
  deleted outright or de-privileged and disabled once retired. Decision: disable, keep the object
  — an inert historical anchor for the many prior reports that already reference it by name.
- **Mid-exercise, on hitting the account-creation validation error:** the first UPN attempt was
  rejected (`InvalidCharacter`); Raymond fell back to the planning conversation's example values
  (`emergencyaccess2@...`) to get unblocked, not as a considered choice. Flagged this directly —
  that name defeats the exercise's purpose — and asked whether it was deliberate. Raymond: *"ugh
  we can rename it or just go forward what think?"* Recommended renaming over delete-and-recreate
  (same object id, no soft-deleted litter, password stays valid) rather than picking for him
  outright; he agreed by proceeding with the rename.
- **On discovering `labadmin` and `R M` holding Global Administrator:** asked directly whether
  these were recognized. Raymond: *"labadmin old account from inital setup, same with the RM
  account, nothing i did outside these sessions, lets rip and pull."* Confirmed both predate any
  of these sessions — the October 2025 paired-build baseline this whole skill exists to re-audit.
- **On `R M` specifically, before touching it:** flagged that it's a guest/MSA account, not just
  an ordinary leftover admin, and that per Microsoft's own emergency-access guidance a guest
  account was never a sound break-glass design regardless of whether anyone remembered it existed
  — plus a genuine, if lower-probability, risk that it's tied to the tenant's original creation
  and could matter for account recovery on a free tenant with no support contract. Asked whether
  to proceed with strip-and-disable versus something more cautious. Raymond: *"yes go ahead."*

## What the box said

Full request/response pairs in `evidence/01-create-and-rename.md`,
`evidence/02-role-assignment-and-verification.md`, and `evidence/03-legacy-admin-cleanup.md`.
Headline results:

- New account created (`201`), renamed off the placeholder values (`204`), assigned Global
  Administrator (`204`).
- From the new account's own session: `/me/memberOf` lists Global Administrator directly; a real
  `POST /users` (`201`) followed by `DELETE` (`204`) proves the role actually functions, not just
  that a claim exists.
- All three legacy admins: role removal `204`, `accountEnabled: false` set via `PATCH` `204`,
  each re-read afterward to confirm the disabled state directly rather than trusting the `PATCH`
  response alone.
- Closing read of the full membership list: one entry, the new account.

## What broke, and why

**The account-creation UX pushed toward exactly the failure this exercise was trying to prevent.**
A UPN validation error mid-setup created pressure to fall back to convenient example values
(`emergencyaccess2@...`, `displayName: "Emergency Access 2"`) — a name that announces itself as
the break-glass account to anyone who can list users in the tenant, which is a broader and
arguably worse exposure than the original "it's in a public repo" problem, since directory
browsing doesn't require finding this specific repo at all. Caught before the account held any
role, cost one rename operation to fix, but it's worth keeping as a caution: convenience fallbacks
under a validation error are exactly how "temporary" values become permanent state.

**The rotation surfaced sprawl it wasn't looking for.** The exercise went in scoped to one named
account. Reading the full role-membership list — a step required anyway, to confirm the new
account's own assignment — turned up two more Global Administrators, `labadmin` and a guest
account (`R M`), both inherited from the October 2025 baseline and unknown to anyone currently
working on this lab. This is close to the exact pattern this whole portfolio is built around:
standing access nobody currently working on the system can explain, discovered as a side effect
of doing something else, not by deliberately auditing for it. Worth stating plainly: this
exercise did not set out to find this, and would not have found it without the membership-list
read that the original plan already required for an unrelated reason.

**Graph Explorer's stale request state produced two harmless near-misses.** Twice during
verification, running "the next step" actually re-ran the previous request because the
method/URL fields hadn't been changed first — a `DELETE` on an already-deleted test user
(harmless 404, confirmed cleanup rather than causing damage), and a `GET` on `labadmin`'s own
object where the full role-membership list was expected (caught immediately because the response
shape didn't match what was asked for). Neither changed any state beyond what was already
intended, but both are a reminder that Graph Explorer keeps its previous request loaded rather
than resetting between steps.

## What I'd do differently

Give explicit character constraints for the UPN *before* the first creation attempt, not after
the first one failed — the validation error is what created the pressure to fall back to
convenience values in the first place. And when handing off a multi-field request in Graph
Explorer, call out explicitly that both the method dropdown and the URL bar need to change
together — the two stale-request near-misses both came from updating one but not the other.

## Open questions

- **Whether `R M`'s guest object is genuinely tied to tenant subscription/billing ownership in
  the Microsoft 365 admin center was never checked** — the decision to disable rather than delete
  was made to avoid finding out the hard way, not because the tie was confirmed to exist. Worth an
  independent read of the Microsoft 365 admin center's organization/billing profile if this
  matters later.
- **Whether any other identity in this tenant holds an administrative role short of Global
  Administrator** (e.g. Privileged Role Administrator, User Administrator) was not checked — this
  exercise only enumerated the one role it set out to rotate.
- **The new account's authentication method is deliberately unregistered** (no MFA, per standard
  break-glass guidance — the long random password is the control). Whether Entra Free's Security
  Defaults, confirmed tenant-wide in the A3 exercise, would force an MFA registration prompt on
  this account's next real sign-in was not tested — if it does, that changes the account's
  practical usability as a true break-glass path and would need a Conditional Access or Security
  Defaults exclusion once B1 stands up Conditional Access properly.
- **This is the first exercise where the capture contract's own evidence artifacts had to be
  deliberately redacted** rather than published verbatim. Worth revisiting whether this pattern
  (redact the new account's identity, publish the process around it) holds up as more of the lab
  moves toward Conditional Access, where policy objects may reference this account by id even
  where its name stays hidden.
