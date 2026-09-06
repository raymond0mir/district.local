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
