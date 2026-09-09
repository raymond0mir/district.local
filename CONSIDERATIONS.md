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
published, so it cannot have been altered. Compare against `HEAD` rather than the index, or
exclude paths absent from `HEAD`.

**A correction on the record.** Commit `fdf8dcc` states "validate.py reports 1 ERROR, not 16",
against the prior carryover's claim of 16. The 1 was measured with the ADCS evidence untracked, so
those files were never examined. Staged, the same tree reports 18. The prior carryover's 16 was
closer to the truth than that commit message allows. The count is conditional on what is tracked,
and no bare number should be quoted without saying which.

**Consequence for `validation.json`.** Regenerating it while the exercise is staged records 18
ERRORs, a state that is false one second after the commit. The file was left at its committed
value for the ADCS commit and refreshed afterward, which is what commits 97a1a7c and b1b4b9c
already do.
