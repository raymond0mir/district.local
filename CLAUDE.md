# district.local operating contract

Read this file in every session.

Read `.claude/skills/tech-compass/SKILL.md` when you run an exercise, draft evidence, write a
report, update the ledger, or resolve an exception. That skill holds the templates, the command
paths, and the standing gotchas. This file holds the rules that never change.

## Purpose

This repository is public portfolio evidence for identity-engineering work. Readers use it to
decide whether Raymond can do identity engineering. A plausible unverified claim is worse than no
claim. It invites an interview question with no answer.

Prefer an honest unknown over an unsupported claim.

## Environment

Claude has no live access to the lab. Raymond runs every command and pastes the output back.

Give him one bounded sequence per turn: one diagnostic thread, or one state change. A sequence may
hold several commands when they run together and return together.

Raymond works from a Mac Mini. The Proxmox host is a Dell laptop. He reaches the host through its
web console. Say "in the Proxmox console" for host and guest commands. Say "in Terminal on the Mac
Mini" for SSH tunnels and browser access. Do not say "on your laptop".

## Sources of truth

- `CARRYOVER.md` is the sole source for current lab state, deadlines, pending decisions, blockers,
  and the next action.
- `exercises/<date-slug>/evidence/` is the source for Captured claims.
- `verified-claims.md` holds durable claims only. See Ledger scope.
- `EXPOSURES.md` holds standing risks, each cited to evidence. It doubles as the exercise queue.
- Reports explain one finding each. A report is not a status page.

Never restate changing state in `CURRICULUM.md`, in a report, or in `README.md`. Link to carryover
or to the evidence file instead.

Never state lab state from memory, from a previous session, or from a summary. Every claim about
what exists comes from a file read in this session. When a named file is missing, say so and list
what exists. Do not substitute a similar file in silence.

## Claim labels

Use these five words for these meanings. Do not substitute synonyms.

- **Captured**: a named evidence file holds the machine output that backs the claim.
- **Recalled**: no machine output backs the claim. A memory, a screenshot, and scrollback are each
  Recalled. A screenshot is a file, and it is still Recalled.
- **Inherited**: the claim comes from the October 2025 build or its imported baseline.
- **Confirmed**: a ledger row with a live evidence path.
- **Retired**: a Confirmed row moved out of Confirmed, with the reason recorded.

Never state a Recalled or Inherited claim as fact. Re-run it and capture it, or move it to Open
questions.

Never correct a wrong published claim by silent edit. Retire it on the record, in the ledger and in
the report. This applies to Claude's own errors. State them in the evidence log when caught, before
being asked.

## Ledger scope

A Captured claim does not earn a ledger row by itself.

Add a Confirmed row only when one of these is true:

- A document outside the originating exercise cites the claim.
- A later exercise depends on the claim as a precondition.
- The claim retires an existing Confirmed, Recalled, or Inherited claim.

Every other Captured claim stays in its evidence log and its report. The ledger is the durable
subset, not the archive.

## Session start

Read in this order:

1. `git status`, then `git log --oneline -15`.
2. `CARRYOVER.md`.
3. `EXPOSURES.md`.
4. The active exercise's `evidence-log.md`.

Then run `python3 validate.py` for a binary answer on repository integrity.

Then state these four things in five sentences or fewer:

- Current position, and where the last session stopped.
- The next safe action.
- Pending decisions and hard deadlines.
- Uncommitted and staged work.

## Pending decisions

Carryover records every decision handed to Raymond that he has not answered. Record the question
and a default action with it.

Do not re-ask an unanswered question as though it were new. State the recorded default, act on it,
and record that you acted.

Re-ask only when the default deletes data, publishes, changes standing privilege, or rewrites
history. Ask once. Do not offer option one and option two when the work is already decided and the
file is the obvious output. Write the artifact, then report what you wrote.

## Before a state change

- Run pre-flight in the host shell: `date -u`, `qm status <vmid>`,
  `lvs -a -o+data_percent,metadata_percent`, `free -h`. Record the readings.
- Stop when thin pool Data% is 85 or higher. Ask Raymond to name the snapshots to prune.
- Ask Raymond first when the change touches standing privilege, security posture, credentials,
  account state, or deletion. Name the object.
- Define a rollback and a proof of healthy sync before any live Entra Connect change.
- Keep Tier 0 credentials off member servers. Run Domain Admin tasks from DC01's console.
- Pass `-NonInteractive` on every PowerShell call through `qm guest exec`. No TTY is attached, and
  a waiting command orphans a process on the guest.
- Capture the command verbatim, the host, the UTC timestamp, the output, and the exit code.

Keep failed attempts and error output. Failure is evidence.

## Public repository rules

- Run the credential scan before every commit. `.githooks/pre-commit` enforces it once
  `git config core.hooksPath .githooks` is set. Follow `references/credential-scan.md`. A literal
  password reached report prose on 2026-08-31.
- Keep Raymond's personal situation out of every artifact: legal, medical, leave, benefits, salary,
  and money pressure. Express a real constraint as the lab fact it produces: a deadline, a license
  limit, or a sequencing dependency.
- Never write the current tenant Global Administrator's name in an artifact. Raymond supplies it in
  session.

## Ready is not published

A report is ready when its hypothesis is answered and its evidence is cited.

Publishing means committing and pushing this public repository. Commit only when Raymond asks.

Do not gate a ready report on a future exercise. A short honest report has more value than a
delayed complete one.

## Session close

Close every exercise with a handoff. Work may span sessions.

1. Update the active exercise's `evidence-log.md`.
2. Update its `report.md` when the hypothesis is complete.
3. Add or retire ledger claims that meet Ledger scope. Add no others.
4. Update `EXPOSURES.md` and `references/gotchas.md` when the session changed either.
5. Overwrite `CARRYOVER.md` using the template below.
6. Run `.githooks/pre-commit --all` for a whole-tree credential sweep.
7. Run `python3 validate.py --json validation.json`.
8. Do not commit unless Raymond asks.

## Carryover template

Overwrite `CARRYOVER.md` with these blocks, in this order. Keep the file under 400 words.
`validate.py` enforces the cap.

1. **Last verified** — the UTC timestamp of the newest reading in this file.
2. **Next safe action** — one action, stated as an imperative.
3. **Lab state** — VM inventory, VM state, pool readings, each with an evidence path.
4. **Stop conditions** — the gates that halt work.
5. **Hard deadlines** — each with a date, and whether it is verified or unverified.
6. **Pending decisions** — each with the question, the date it was asked, and the default action.
7. **Blockers** — each with the owner.
8. **Uncommitted and staged work** — what is uncommitted, and why. State whether the tree is
   clean. **Write no commit hash, and do not state whether the tree matches `origin/main`.**
   Both are moving values that the commit or the push carrying this file invalidates, and
   Session start reads `git status` and `git log` before it opens this file.

Resolved detail belongs in the exercise record. Do not restate this contract in carryover.

## Working with Raymond

- Give structural pushback with receipts. Do not give encouragement.
- Label every recommendation: Necessary, Useful, Optional, Polishing, or High-value.
- Rewrite a draft only when he asks.
- Proceed on routine technical defaults. Flag the choice afterward.
- State disproven hypotheses as plainly as confirmed ones.
- Teach a missing foundation. Do not work around it.
- Say a point once. Do not reopen a decision he has closed.

## Output style

Apply these rules to chat replies and to repository artifacts. Quoted exchanges and machine output
are exempt.

- Use literal words. Use no idioms, metaphors, or adverbs.
- Keep descriptive sentences to 25 words or fewer.
- Keep instruction sentences to 20 words or fewer.
- Use active voice. Write one instruction per sentence. Use imperative verbs for steps.
- Limit noun clusters to three nouns.
- Write lists as single-action steps.
- Omit greetings, polite phrasing, and closing summaries.
- Use the defined terms. Do not substitute synonyms.

## Cross-surface

Claude on claude.ai cannot read Claude Code sessions. A lab-state answer given there from chat
history is stale and wrong.

Carryover is the only bridge. Write anything that must reach a chat conversation into carryover,
for a reader with no access to this repository.
