# Considerations

Design decisions for the repository's own tooling. Not lab work, and not an exercise.
Taken 2026-09-05, to be acted on in the next session.

Scope: how the repository checks itself. If an entry here is not about that, it belongs in
`CURRICULUM.md`, `EXPOSURES.md`, or a report.

## The division of labour

- `validate.py` determines repository facts. Binary answers only.
- Semantic review evaluates whether a conclusion follows from its cited evidence.
- The lab determines technical facts.
- Raymond resolves uncertainty by obtaining evidence, not by choosing an opinion.

A check moves to semantic review when no pattern decides it without false positives. That
already happened once: 27 of the first run's findings came from asking a regex whether a capture
contained a command. Graph captures lead with a bare HTTP verb, host captures use a fenced block,
others label the line. The check was removed rather than elaborated.

## Classify before correcting

The first run produced three kinds of finding. They get three different responses.

| Kind | Example | Response |
|---|---|---|
| Mechanical defect | a required report section is absent | Fix it |
| Historical exception | evidence-log schema before 2026-09-05 | Grandfather it, and record the date |
| Evidence deficiency | a capture with no UTC timestamp behind a timing claim | Escalate. Never fix |

The third row is the important one. A missing timestamp cannot be manufactured after the fact.
Writing one in would produce cosmetic compliance and destroy the property the repository sells.
An evidence deficiency goes to semantic review, or to a new capture, or to Open questions.

## Decided

- **The 08-31 member-server report gains its missing section.** It states the evidence boundary:
  the box produced limited Captured output, most build activity was observed through noVNC and
  stays Recalled, and the evidence-log records the limitation. This repairs a disclosure the
  report already owed. It does not change the exercise.
- **The six nested evidence-logs stay where they are.** Five reports of that era link to
  `evidence/evidence-log.md`. Moving them edits frozen records to satisfy today's layout.
  The validator holds the historical convention and its cutoff date. Uniformity by edit would be
  less honest than the record as it stands.

## Semantic review, when it is built

One operation, not an audit:

> Review this report's conclusions against the exact evidence those conclusions cite.

Fixed output per conclusion: the conclusion, the evidence cited, a verdict of Supported, Not
supported, or Indeterminate, the reason, and the evidence gap if one exists.

No edits. No repository cleanup. No vocabulary definitions. No reconstruction of lab state.
`Indeterminate` is a valid verdict and it ends the model's authority. The next action is a new
capture or a move to Open questions. A disagreement is not resolved by argument.

## Open, and worth deciding first

**`validation.json` is only trustworthy if it is fresh.** A tracked file asserting a clean tree
at a commit where nobody ran the validator is the same failure class as an unverified report. Two
consequences:

- The file needs a guarantee of freshness. That is the session-close step, or a pre-commit hook.
- Its `commit` field names HEAD at write time, which is the *parent* of the commit that carries
  it. The file describes the tree validated before commit N, and records commit N-1. Decide
  whether to keep that and document it, or to write the field at commit time instead.

## Order

1. Apply the two decided fixes. Reach a clean run.
2. Run one full session close through the validator.
3. Then add step 7a to `SKILL.md`, and sync the plugin copy.
4. `AGENTS.md` last. Codify the behaviour that survived contact with the repository, not the
   behaviour predicted for it.

## The contract split, 2026-09-09

`CLAUDE.md` now holds the operating rules. `SKILL.md` holds the playbook. This fills the slot the
Order section reserved for `AGENTS.md`, and it fills it first, not last. State the reason and the
cost.

**Reason.** The skill body is not always-on. A session start showed only the skill's `description`
in context, about 50 words. The 276-line body loaded only when the skill triggered. A session that
opens with "what's next" never loaded the rules at all. `CLAUDE.md` loads in every session in this
directory, so the rules bind whether or not the skill triggers.

**Cost.** Always-on context grows from about 50 words to about 1400. This buys enforcement. It
does not save tokens. Any claim that the split reduces context is wrong.

**What moved.** Claim labels, session start and close, state-change gates, public-repository
rules, the carryover template, output style, cross-surface, and working rules moved to `CLAUDE.md`.
Command paths, templates, layout, the loop, the nine questions, recommendation-label definitions,
portfolio framing, and token discipline stayed in `SKILL.md`. `SKILL.md` fell from 276 lines to
219 and gained a routing line at the top.

**Three defects fixed in the move.**

- `SKILL.md` said "Publish on completion" and "Commit only when Raymond asks". In a public
  repository those conflict. `CLAUDE.md` separates report-ready from published.
- Every Captured claim earned a ledger row. `verified-claims.md` reached 14,503 words and 218
  rows, and the skill mitigated its own rule with "do not read the ledger whole". `CLAUDE.md`
  adds a three-part Ledger scope test.
- "Start a new session for each exercise" was already abandoned in practice. Two exercises span
  sessions right now. `CLAUDE.md` replaces it with a handoff at close.

**The anti-loop rule.** Carryover now records each unanswered decision with a default action.
`CLAUDE.md` forbids re-asking an unanswered question as new. Looping came from unanswered
decisions with no recorded state, not from instruction length.

**Not done, and still open.** The `AGENTS.md` question stands: whether a second file is needed for
agents that do not read `CLAUDE.md`. The two-copy plugin sync rule survived. Raymond proposed
removing it as deployment work. The counter-argument is that the plugin copy is what loads at
runtime, so dropping the rule makes drift silent. `validate.py` raises an ERROR on drift, which is
the current guarantee. Decide whether to remove the second copy instead of the rule.

**This reverses `a5270df`.** That commit dropped an earlier `CLAUDE.md` candidate and moved seven
of its rules into `SKILL.md`. It gave two reasons: the draft duplicated the skill's close-out,
consult list, and style rules, and it set the opposite commit default. Both reasons are answered
here. The duplication is gone, because `SKILL.md` lost the sections `CLAUDE.md` now owns. The
commit default matches: commit only when Raymond asks.

The fact that changes the decision is new. `a5270df` weighed two files holding the same rules. It
did not weigh whether the skill loads at all. It does not load by default. A session start shows
only its `description`. That makes the duplication argument the wrong test, and makes load
guarantee the right one.

## `evidence-modified` cannot see the difference between new and altered, 2026-09-09

`check_evidence_immutability` builds `changed` from `git diff --name-only` and
`git diff --cached --name-only`. An exercise counts as closed once `report.md` exists. Adding new
evidence to a closed exercise therefore raises one ERROR per file, and every one of them clears
the moment the commit lands.

Staging ADCS evidence 40 through 53 took the run from 1 ERROR to 18. Seventeen were this artifact.
The check intends immutability of published evidence. A file that does not exist in `HEAD` is not
published, so it cannot have been altered.

**Fixed 2026-09-09.** The check now reads `git diff HEAD --diff-filter=MDRT --name-only`. That
keeps modification, deletion, rename and typechange, and drops addition, which is the case that
produced the false errors. Five cases were tested: a clean tree, an altered file unstaged, the same
file staged, a new file staged, and a deletion. Only the alterations and the deletion raise the
error. Adding evidence to a closed exercise is ordinary work and is now silent.

**A correction on the record.** Commit `fdf8dcc` states "validate.py reports 1 ERROR, not 16",
against the prior carryover's claim of 16. The 1 was measured with the ADCS evidence untracked, so
those files were never examined. Staged, the same tree reports 18. The prior carryover's 16 was
closer to the truth than that commit message allows. The count is conditional on what is tracked,
and no bare number should be quoted without saying which.

**Consequence for `validation.json`.** Regenerating it while the exercise is staged records 18
ERRORs, a state that is false one second after the commit. The file was left at its committed
value for the ADCS commit and refreshed afterward, which is what commits 97a1a7c and b1b4b9c
already do.

## `evidence-modified` punishes legitimate repair at the moment a report lands, 2026-09-10

`validate.py` reported two `reference-missing` ERRORs at session start. `evidence/02` and
`evidence/03` of `2026-09-09-pim-for-groups` cited two B4 evidence files by bare number rather than
by filename, so the cited paths did not exist. Completing the citations cleared both errors. The
exercise was open at the time, with no `report.md`.

Writing `report.md` at the end of the same session closed the exercise. `check_evidence_immutability`
then reported the same two files as `evidence-modified`, "published evidence of a closed exercise is
altered".

**Both readings are correct, and they disagree because the check has no notion of when the edit
happened.** It compares the working tree against `HEAD` and asks only whether a file differs. An
edit made while an exercise was open is indistinguishable from an edit made after it closed, once
the report exists.

Both ERRORs clear when the work is committed, because `HEAD` then contains the edits and the diff is
empty. That is the same transience already recorded for the addition case in the entry above, and it
carries the same weakness: the check cannot see an alteration that has already been committed. It
detects uncommitted divergence from the last commit, which is a narrower thing than immutability.

**No change was made to `validate.py`.** Editing the check to clear an error it raised correctly
would be the wrong move, and the alternative — reverting the citations — would restore two genuine
`reference-missing` ERRORs. The edits are declared in the exercise's evidence log under Corrections
instead.

**The sequencing that avoids this entirely:** commit a repair to published evidence on its own,
before the report that closes the exercise. Raymond has not been asked to adopt that as a rule; it
is recorded here as the option that exists.

## The carryover's last block no longer carries a commit hash, 2026-09-10

`CLAUDE.md`'s carryover template asked block 8 for "what is in the index, and why it is not
committed." In practice that produced a commit hash, and a hash written into `CARRYOVER.md` is false
the moment the commit carrying that file lands. A commit cannot record its own hash.

This bit twice in one day. The session opened on a carryover naming `7aaad13` with the PIM exercise
uncommitted, when the tree was clean at `fd60ab7` — the previous session had committed after writing
the file. That one mattered, because it asserted uncommitted work that did not exist. Later the same
day, `413d396` committed a carryover naming `19b908d` with two files uncommitted, and landing the
commit falsified both claims. The correction in `dfb3de3` then named `413d396` while `HEAD` moved to
`dfb3de3`. Each correction invalidates the hash it writes.

**Raymond's decision, 2026-09-10: drop the hash.** Block 8 now asks whether the tree is clean and
whether it matches `origin/main`. Both statements survive the commit that carries them, because
neither names a moving value.

**Half of that last sentence is wrong, and is corrected in the entry below, same date.** The
`origin/main` clause does name a moving value. It survives a commit and does not survive a push.

Nothing is lost. Session start already reads `git status` and `git log --oneline -15` as its first
step, before it reads carryover, so the exact pointer is in hand before the file is opened. The hash
in carryover was a second, staler copy of something the session had already read correctly.

`validate.py` is unchanged. `check_carryover` enforces the word cap only and has never checked block
contents, so the template change needs no validator change. The template lives only in `CLAUDE.md`;
`SKILL.md` refers to it rather than restating it, so the two-copy rule does not apply here.

## Passes 4 and 5 scan the working tree, not the history they were written for, 2026-09-10

`references/credential-scan.md` says of passes 4 and 5: "It searches the whole tracked tree, not the
staged diff, because a string may already sit in an earlier commit."

The implementation does not do that. `.githooks/pre-commit` runs:

```
git -C "$REPO" grep -InFf "$PATTERNS" -- .
```

`git grep` with no revision argument reads the working tree. A string that sat in an earlier commit
and was later removed is exactly what it cannot see. The stated reason for the pass is the case it
misses.

Demonstrated with a non-secret string on 2026-09-10. The line "Reclaim thin-pool headroom. Nothing
that touches a VM can proceed past the 85 gate" was removed from `CARRYOVER.md` this session. It
returns nothing from the hook's command and returns three commits from
`git grep -lF <string> $(git rev-list --all)`.

This matters more than it would in a private repository. The four commits pushed on 2026-09-10 are
public. Rotating a leaked lab credential is cheap; unpublishing it is not, and
`credential-scan.md` already says so. Passes 4 and 5 have never run in this repository, because the
patterns file has never existed, so nothing has ever been checked against either the tree or the
history.

**The history-wide form, which prints commit, file and line and never the matched text:**

```
git grep -InFf "$PATTERNS" $(git rev-list --all) | cut -d: -f1,2,3 | sort -u
```

**Not decided.** Making that the hook's default would put a full-history walk in front of every
commit, and the tree grows. The candidates are: run it in `--all` only, run it on a `--history`
flag, or leave the hook alone and add the command to `credential-scan.md` as a periodic sweep.
Raymond has not been asked. Default until he is: leave the hook unchanged and treat the command
above as a manual sweep.

Two things were tested rather than assumed. With a patterns file holding a string that is in the
tree, the hook blocked and withheld the matched text, printing 62 file-and-line locations, so the
wiring works. Blank lines in the patterns file are harmless: `git grep -F` ignores an empty pattern
rather than matching every line, tested with an empty line between two patterns.

**The patterns file is still absent, on purpose.** A file holding placeholder values would turn the
honest `SKIPPED, no patterns file` into a `clean` that means nothing. The directory
`~/.config/district-local` exists at mode 700, with `add-scan-pattern.sh` beside it: it reads one
value with echo off, refuses anything under six characters, and never prints, echoes or
argument-passes the value, so no secret reaches shell history or terminal scrollback. Raymond adds
the real strings.


## Block 8 loses the `origin/main` clause too, 2026-09-10

The entry above dropped the commit hash from carryover's last block on the ground that the two
remaining statements "survive the commit that carries them, because neither names a moving value".
That holds for "the tree is clean". It does not hold for "matches `origin/main`", and the reason is
one step further along than the hash problem.

A commit invalidates a hash. A push invalidates the `origin/main` clause. Writing a true line
therefore means predicting the push, committing that prediction, and pushing it — which puts the
tree one commit ahead again, so the line is only true for the state the push produces. Both pushes
on 2026-09-10 cost an extra commit for nothing else: `d7491d5` and `8c06007` exist to make block 8
true. The treadmill is structural, not an oversight in how the file was written.

**Raymond's decision, 2026-09-10: cut the clause.** Block 8 now states what is uncommitted and why,
and whether the tree is clean. Neither statement changes when the file is committed or pushed.

Nothing is lost, for the same reason the hash was not missed. Session start reads `git status` and
`git log --oneline -15` before it opens carryover, and `git status` states the branch's position
against its upstream in that first read. Carryover was carrying a staler second copy of it.

`validate.py` is unchanged. `check_carryover` enforces the word cap and has never read block
contents. The template lives only in `CLAUDE.md`; `SKILL.md` refers to it rather than restating it,
so the two-copy rule does not apply.
