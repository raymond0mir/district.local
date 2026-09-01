# Carryover

Open items only, as of 2026-09-02 (session continuing from 2026-09-01). This file is overwritten
at each session close per `.claude/skills/tech-compass/SKILL.md` — resolved work lives in
`report.md` files, `evidence-log.md` files, and `verified-claims.md`, not here.

## From the 2026-09-01 review's follow-up list

Sections A (six captures), B1–4/6 (report fixes), C (ledger corrections), and D (README) are all
done — see `verified-claims.md` and the git log for what changed. Still open:

- **B5 — split `exercises/2026-09-01-entra-connect-connector-account/report.md` in two.**
  Explicitly held, Raymond's call: needs real narrative rework (separate "What I set out to do"
  framing for the GPO-lockout/tattoo half vs. the connector-account/wizard half, and deciding how
  today's addendum content divides between them), not mechanical cut-and-paste. Drop step 14 and
  consultation point 10 (GitHub setup) when this happens — that content now lives in `README.md`.
- **F — prose pass on the six committed 08-31 reports.** Structure and evidence citations were
  checked 2026-09-01; prose wasn't. For each: does it lead with the finding, is it a reasonable
  length, does "What the box said" quote rather than summarize. Fold in the addendum below.
- **`constrained-admin-path`'s report needs a short addendum.** Its central remediation (removing
  `sysadmin`'s direct `BUILTIN\Administrators` grant) was correct, but the 09-01 exercise found
  the *sequencing* around it — disabling every other admin path first — created a full lockout.
  No addendum exists on that report yet; add one pointing to
  `exercises/2026-09-01-entra-connect-connector-account/report.md`'s corrected "What broke"
  section rather than re-litigating it there.
- **G — reconcile the stale plugin copy of the skill.** The app's plugin copy (under
  `~/Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin/.../skills/tech-compass/SKILL.md`)
  still predates the 2026-09-01 streamline. Invoking `/tech-compass` outside this repo loads the
  old version. Either re-import from the repo or remove it; the repo copy
  (`.claude/skills/tech-compass/SKILL.md`) is canonical per its own header.
- **H — a known-exposures page**, built only from captured facts, doubling as the next exercise
  queue. Candidates as of today: `svc-entraconnect`'s password expiry (below), AD Recycle Bin not
  enabled, the five GPOs applying to DC01 (not all fully read), `districtsafetyphoto.com`
  verification (below).

## Entra Connect: still unresolved

- **Promote out of staging mode** and watch what actually happens on a real export. The original
  reason to watch this closely — `bhound` failing on its fallback UPN — is now moot, since
  `bhound` was disabled 2026-09-01 and won't sync at all. Still worth doing to confirm the rest
  of the sync scope behaves as staging predicted.
- **The authoritative test for the whole "Not Added" UPN question**: a real synced account
  (`sysadmin` or another restamped user) actually signing in to Microsoft Entra ID with their
  on-premises credential. Per Microsoft Learn's UPN-population rules, the staging preview's
  positive signal can't distinguish a verified suffix from an unverified one computing the same
  value by coincidence — this sign-in test is the only thing that can.
- **`svc-entraconnect`'s password expires approximately 2026-10-13** (42-day default max age,
  `PasswordLastSet` 2026-09-01 07:54:57 AM). Rotate before then or set up a fine-grained password
  policy exemption — not yet decided which.

## Other open questions

- **Origin of `Secure Admin WS`'s domain-root GPO link** — deliberate design choice or setup-time
  scope creep — was never established, only its current effective scope.
- **Whether the tattooed `SeDenyInteractiveLogonRight` could re-tattoo DC01** on a future GPO
  refresh cycle was never observed over time, only immediately after the one fix applied.
- **AD Recycle Bin is not enabled on `district.local`** — flagged by the Entra Connect wizard's
  own completion screen, not addressed.
- **The wizard's "Filtering" step was never actually reviewed** — screenshot skipped, contents
  unknown.
- **`districtsafetyphoto.com` verification never happened.** The roughly one-month registration
  window flagged 2026-08-31 has nearly elapsed as of this writing.
