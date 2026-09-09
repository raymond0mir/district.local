---
name: tech-compass
description: Capture lab evidence and write after-action reports for the district.local Active Directory lab. Use whenever Raymond runs, closes out, or writes up a lab exercise, asks what he verified versus assumed, or pastes raw lab output — even without naming the skill.
---

# Tech Compass

**Read `CLAUDE.md` at the repository root for the operating rules.** It holds the claim labels,
the session start and close sequences, the state-change gates, the public-repository rules, the
carryover template, and the output style. Those rules apply in every session.

Read this skill when you run an exercise, draft evidence, write a report, update the ledger, or
resolve an exception. It holds the templates, the command paths, and the reasoning.

Canonical copy: `.claude/skills/tech-compass/SKILL.md` in the repo. If a plugin copy differs, the
repo copy wins. Copy a changed `SKILL.md` or `references/` file to the plugin copy in the same
session. `validate.py` raises an ERROR when the copies differ.

## Why this skill exists

The October 2025 build was paired with another assistant. Its audit baseline was imported. Nobody
can separate verified facts from assumed facts in that baseline. This skill stops that from
recurring.

## Terms

`CLAUDE.md` defines Captured, Recalled, Inherited, Confirmed, and Retired. These terms extend that
list.

- **Ledger**: `verified-claims.md` at the repo root.
- **Carryover**: `CARRYOVER.md` at the repo root.
- **Lab state**: the carryover block that holds VM inventory, VM state, and pool readings.
- **Exposures**: `EXPOSURES.md` at the repo root.
- **Host shell**: the Proxmox host shell, opened in the Proxmox web console.

**The four reasons to Retire a Confirmed row.** Write the reason in the row.

- The evidence file is gone.
- The state changed, and a newer row supersedes this one.
- The claim was wrong when it was written.
- The row miscited its evidence file.

## The loop

The lab produces a loop, not a curriculum. Run it in this order:

1. Understand how the system works.
2. Break it deliberately.
3. Observe what happens.
4. Understand why it happened.
5. Detect it.
6. Defend it, or fix it.
7. Understand the alternatives.
8. Document the evidence.
9. Publish the useful result.

The goal is fluency in identity systems, and work that shows that fluency to an interviewer.

**Interrogate the technology.** Drive each exercise toward these nine questions:

- What does the system do internally?
- What does the system assume?
- What happens when an assumption fails?
- How does an attacker abuse that?
- What evidence does the abuse produce?
- How does a defender recognize it?
- What control prevents or contains it?
- What design alternatives exist?
- What tradeoffs do the alternatives introduce?

One exercise does not answer all nine. Write each unanswered question in Open questions. It becomes
the next exercise.

## Command paths

**DC01 path.** DC01 (VM 100) has no WinRM, RDP, or PowerShell remoting. This is by design, and it
is a finding. Reach DC01 and VM 102 (entraconnect01) through the QEMU guest agent from the host
shell:

```
qm guest exec 100 --timeout 30 -- powershell.exe -NonInteractive -Command "<command>"
```

Keep all four JSON fields: `out-data`, `err-data`, `exitcode`, `exited`. The exit code makes the
record trustworthy.

Run any command that needs a typed secret on the VM's own console. Read `references/gotchas.md`
before the first command on DC01 or in the tenant.

**Tenant path.** Entra and Graph work does not use guest exec. Raymond runs Graph Explorer for API
calls and the Entra admin center for portal-only flows. A portal screenshot is Recalled. Follow it
with a Graph read to make the claim Captured.

**Snapshots.** Keep the `clean-install` baseline for each VM. Keep the last few distinct states for
each VM. Retire an exercise's before/after snapshot after Raymond confirms the after-state. Run
`qm delsnapshot` only after Raymond names the snapshot and says go.

Derive the exercise date and snapshot names from `date -u`. The host clock runs
America/Los_Angeles.

## Evidence files

Write one file per diagnostic thread. Name the file for what it proves.

Start each capture block with three lines: the command verbatim, the host, and the UTC timestamp
from `date -u`. Put only machine output below those lines. Put analysis in the report or the
evidence log.

Screenshot or scrollback output is Recalled. Say so in the report. Recalled output cannot enter the
ledger.

## Layout

```
exercises/YYYY-MM-DD-slug/
  evidence/           one file per thread, named for what it proves
  evidence-log.md     the running record; see Evidence-log structure
  report.md           the portfolio artifact; see Report structure
CLAUDE.md             the operating contract, read in every session
verified-claims.md    ledger
EXPOSURES.md          open risks, each cited to an evidence file; doubles as the exercise queue
CARRYOVER.md          current state and open items; overwritten at every close
CURRICULUM.md         exercise plan
CONSIDERATIONS.md     design decisions for the repository's own tooling
validate.py           deterministic repository checks; binary answers only
validation.json       the last validate.py run, overwritten each run
README.md             repo entry point, written for a public reader
.gitignore            excludes local editor state
.githooks/pre-commit  the credential scan; enable with core.hooksPath
.claude/skills/tech-compass/
  SKILL.md            this file, the canonical copy
  references/
    gotchas.md          standing command behaviors
    credential-scan.md  the pre-commit scan
```

This block lists every tracked path. Update it when a path is added or removed.

## Report structure

Use these eight sections in this order. Include every section. `validate.py` checks them.

```
# [Exercise name]
## What I set out to do          the hypothesis, two or three sentences
## The setup                     the lab slice used, plus pre-flight readings
## What I did                    commands and changes in order, actual syntax
## Where Raymond was consulted   each decision handed to him: the question, his decision, his reason; quote real exchanges; label paraphrases
## What the box said             captured output with exit codes, quoted from evidence/
## What broke, and why           dead ends and misconfigurations; most portfolio value lives here
## What I'd do differently       judgment, stated plainly
## Open questions                mandatory; never empty by default
```

Write one exercise per report. Two hypotheses make two reports. Keep repo chores out of exercise
reports. A retrospective report says so in its first section.

## Evidence-log structure

Write `evidence-log.md` during the session, not at the close. It is the running record.

Use these six sections in this order. Include every section. `validate.py` checks them.

```
# [Exercise name] — evidence log
## Captured                      one entry per evidence file: what it proves, the file name
## Not captured, and why         each claim the session could not capture; name the blocker
## Where Raymond was consulted   the question, his decision, his reason; quote real exchanges
## Corrections                   wrong statements caught in session, including Claude's own
## Open questions                unresolved at close
## Not started                   planned work the session did not reach
```

The evidence log and the report share two sections. The evidence log is the source. The report
quotes it. When the two disagree, correct the report.

## Resolving claims

Label every factual claim while drafting. Resolve every label before finishing. Check the ledger
before you label a claim Inherited or Recalled.

- **Recalled**: re-run and capture, or move the claim to Open questions.
- **Inherited**: re-run first. These claims carry the highest value.

Apply `CLAUDE.md`'s Ledger scope before adding a row. A capture that retires an Inherited or
Recalled claim always earns a row. Retire the old row in the same edit.

## Recommendation labels

`CLAUDE.md` requires a label on every recommendation. These are the definitions.

- **Necessary**: required to unlock the next experiment.
- **Useful**: improves understanding or evidence.
- **Optional**: does not change capability.
- **Polishing**: process or tooling work that can wait. Name the label. Redirect him.
- **High-value**: strong technical content, or portfolio material. Do it first.

Answer a gap with the next thing to learn, build, or break, and the reason it matters. Do not
answer a gap with a retrospective on the previous session.

## Portfolio framing

- The permission-sprawl thesis leads the series: access provisioned by copying a named user, and
  standing grants nobody removes. Connect an exercise to it when the link is real. Do not force it.
- A grant in use is not a grant that is appropriate.
- When removing a grant breaks something, the lesson is sequencing and break-glass. The lesson is
  not restoration.
- Watch for reports outpacing verified lab work. If the inherited baseline is still Inherited, say
  so.
- Raymond built every condition in this lab. The lab cannot show that such conditions arise on
  their own. His operational history is the observation. The lab is the demonstration. Frame the
  series that way.

## Token discipline

- Read other files on demand.
- Search the ledger by claim when you label a claim. Do not read the ledger whole.
- Do not re-read a file that is already in context.
- Do not restate `CLAUDE.md` in carryover, the README, or a report. Link to it.
- Put standing command gotchas in `references/gotchas.md`, not in carryover.
