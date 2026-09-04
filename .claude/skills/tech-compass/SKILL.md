---
name: tech-compass
description: Capture lab evidence and write after-action reports for the district.local Active Directory lab. Use whenever Raymond runs, closes out, or writes up a lab exercise, asks what he verified versus assumed, or pastes raw lab output — even without naming the skill.
---

# Tech Compass

Reports for district.local are portfolio work. Readers use them to decide whether Raymond can do identity engineering. An unverified claim in a report is worse than no report. It invites an interview question with no answer.

Canonical copy: `.claude/skills/tech-compass/SKILL.md` in the repo. If a plugin copy differs, the repo copy wins.
Copy a changed `SKILL.md` or `references/` file to the plugin copy in the same session.

## Terms

Use these words for these meanings. Do not substitute synonyms.

- **Captured**: a file in `evidence/` holds the machine output that backs the claim.
- **Recalled**: no machine output backs the claim. A memory, a screenshot, and scrollback are each Recalled. A screenshot is a file, and it is still Recalled.
- **Inherited**: the claim comes from the October 2025 build or its imported baseline. No file backs it.
- **Confirmed**: a ledger row with a live evidence path.
- **Retired**: a Confirmed row moved out of Confirmed, with the reason recorded. Four reasons apply:
  - the evidence file is gone
  - the state changed, and a newer row supersedes this one
  - the claim was wrong when it was written
  - the row miscited its evidence file
- **Ledger**: `verified-claims.md` at the repo root.
- **Carryover**: `CARRYOVER.md` at the repo root.
- **Lab state**: the carryover block that holds VM inventory, VM state, and pool readings.
- **Exposures**: `EXPOSURES.md` at the repo root.
- **Host shell**: the Proxmox host shell, opened in the Proxmox web console.

## Why this skill exists

The October 2025 build was paired with another assistant. Its audit baseline was imported. Nobody can separate verified facts from assumed facts in that baseline. This skill stops that from recurring.

## Capture contract

Evidence is what the machine printed. A summary is not evidence. A recollection is not evidence. Put uncaptured claims in Open questions. Do not state them as fact.

**Access.** Claude has no live access to the lab. Raymond runs each command and pastes the output back. Give him one self-contained command block per turn.

**Where commands run.** Raymond works from a Mac Mini. The Proxmox host is a Dell laptop. He reaches the host through its web console in a browser. Say "in the Proxmox console" for host and guest commands. Say "in Terminal on the Mac Mini" for SSH tunnels and browser access. Do not say "on your laptop".

**DC01 path.** DC01 (VM 100) has no WinRM, RDP, or PowerShell remoting. This is by design, and it is a finding. Reach DC01 and VM 102 (entraconnect01) through the QEMU guest agent from the host shell:

```
qm guest exec 100 --timeout 30 -- powershell.exe -NonInteractive -Command "<command>"
```

Keep all four JSON fields: `out-data`, `err-data`, `exitcode`, `exited`. The exit code makes the record trustworthy.

**No TTY.** `qm guest exec` attaches no TTY. A command that waits for input hangs until timeout and orphans a process on the guest. Pass `-NonInteractive` on every PowerShell call. Run any command that needs a typed secret on the VM's own console. Read `references/gotchas.md` before the first command on DC01 or in the tenant.

**Tenant path.** Entra and Graph work does not use guest exec. Raymond runs Graph Explorer for API calls and the Entra admin center for portal-only flows. A portal screenshot is Recalled. Follow it with a Graph read to make the claim Captured.

**Tier rule.** Tier 0 credentials never land on a member server. Run Domain Admin tasks from DC01's console.

**Pre-flight.** Run these in the host shell before the first state change that touches DC01:

```
date -u
qm status 100
lvs -a -o+data_percent,metadata_percent
free -h
```

If thin pool Data% is 85 or higher, stop. Ask Raymond to name the snapshots to prune. Record the readings in The setup.

**Live state.** Read carryover's Lab state block for VM inventory, VM state, and pool readings. Do not take state from this file or from memory.

**Snapshots.** Keep the `clean-install` baseline for each VM. Keep the last few distinct states for each VM. Retire an exercise's before/after snapshot after Raymond confirms the after-state. Run `qm delsnapshot` only after Raymond names the snapshot and says go.

**Evidence files.** Write one file per diagnostic thread. Name the file for what it proves. Start each capture block with three lines: the command verbatim, the host, the UTC timestamp from `date -u`. Put only machine output below those lines. Put analysis in the report or the evidence-log. Screenshot or scrollback output is Recalled. Say so in the report. Recalled output cannot enter the ledger.

**Failure is evidence.** Keep error output. Keep failed attempts. A `Get-ADDomain` failure while ADWS initializes after boot is publishable behavior.

## Layout

```
exercises/YYYY-MM-DD-slug/
  evidence/           one file per thread, named for what it proves
  evidence-log.md     the running record; see Evidence-log structure
  report.md           the portfolio artifact; see Report structure
verified-claims.md    ledger
EXPOSURES.md          open risks, each cited to an evidence file; doubles as the exercise queue
CARRYOVER.md          Lab state, open items, next steps; overwritten at every close
CURRICULUM.md         exercise plan
README.md             repo entry point, written for a public reader
.gitignore            excludes local editor state
.claude/skills/tech-compass/
  SKILL.md            this file, the canonical copy
  references/
    gotchas.md          standing command behaviors
    credential-scan.md  the pre-commit scan
```

This block lists every tracked path. Update it when a path is added or removed.

Derive the exercise date and snapshot names from `date -u`. The host clock runs America/Los_Angeles.

## Report structure

Use these eight sections in this order. Include every section.

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

Write one exercise per report. Two hypotheses make two reports. Keep repo chores out of exercise reports. A retrospective report says so in its first section.

## Evidence-log structure

Write `evidence-log.md` during the session, not at the close. It is the running record.

Use these six sections in this order. Include every section.

```
# [Exercise name] — evidence log
## Captured                      one entry per evidence file: what it proves, the file name
## Not captured, and why         each claim the session could not capture; name the blocker
## Where Raymond was consulted   the question, his decision, his reason; quote real exchanges
## Corrections                   wrong statements caught in session, including Claude's own
## Open questions                unresolved at close
## Not started                   planned work the session did not reach
```

The evidence-log and the report share two sections. The evidence-log is the source. The report quotes it. When the two disagree, correct the report.

## Claims

Label every factual claim while drafting: Captured, Recalled, or Inherited. Resolve every label before finishing. Check the ledger before you label a claim Inherited or Recalled.

- Recalled: re-run and capture, or move the claim to Open questions.
- Inherited: re-run first. These claims carry the highest value.

Add a Confirmed row for every Captured claim: claim, evidence file, exercise, date. This is the normal path. A capture that retires an Inherited or Recalled claim also adds a Confirmed row. Retire the old row in the same edit.

Move a Confirmed row to Retired when any of the four reasons in Terms applies. Write the reason in the row.

A retraction is a Retired row. Never fix a wrong claim by silent edit. Retract on the record, in the ledger and in the report. This includes Claude's own errors. State them in the evidence-log when caught.

## Output style

Apply these rules to every output: chat replies, command blocks, evidence-logs, carryover, exposures, and reports. Quoted exchanges and machine output are exempt.

- Use literal words. Use no idioms, metaphors, or adverbs.
- Keep descriptive sentences to 25 words or fewer.
- Keep instruction sentences to 20 words or fewer.
- Use active voice.
- Write one instruction per sentence.
- Use imperative verbs for steps.
- Limit noun clusters to three nouns.
- Write lists as single-action steps.
- Use a bullet list instead of a sentence joined by semicolons.
- Omit greetings, polite phrasing, and closing summaries.
- Use the defined terms above. Do not substitute synonyms.

## Token discipline

- Read carryover, then exposures, at session start. Read other files on demand.
- Search the ledger by claim when you label a claim. Do not read the ledger whole.
- Do not re-read a file that is already in context.
- Start a new session for each exercise. Close the session after the report.
- Keep carryover under 400 words. Carryover holds one Lab state block, open items, and next steps. Resolved work lives in reports, evidence-logs, the ledger, and exposures.
- Do not restate the capture contract in carryover, the README, or reports. Link to this file.
- Put standing command gotchas in `references/gotchas.md`, not in carryover.

## Working with Raymond

- Give structural pushback with receipts. Do not give encouragement.
- Rewrite a draft only when he asks.
- When a draft claim has no evidence file, name the claim. Ask: re-run, or move to Open questions.
- Ask before any action that touches standing privilege, changes security posture, or deletes data. Name the object. Examples: account removal, re-enabling a disabled account, UPN re-stamp, lowering LDAP signing, snapshot deletion.
- Proceed on routine technical defaults. Flag the choice afterward. Examples: RAM sizing, mirroring config from another VM, snapshot naming, next port in a diagnostic chain.
- State disproven hypotheses as plainly as confirmed ones.

## Portfolio rules

- The repo is public. Run the credential scan before every commit. Follow `references/credential-scan.md`. A literal password reached report prose on 2026-08-31.
- Keep Raymond's personal situation out of every repo artifact: legal, medical, leave, benefits, salary, and money pressure. Express a real constraint as the lab fact it produces: a deadline, a license limit, a sequencing dependency.
- Do not write the current tenant Global Administrator's name in any repo artifact. Raymond supplies it in session.
- The permission-sprawl thesis leads the series: access provisioned by copying a named user, and standing grants nobody removes. Connect an exercise to it when the link is real. Do not force it.
- A grant in use is not a grant that is appropriate.
- When removing a grant breaks something, the lesson is sequencing and break-glass. The lesson is not restoration.
- Watch for reports outpacing verified lab work. If the inherited baseline is still Inherited, say so.

## Session close

1. Finish `evidence-log.md`.
2. Write `report.md`.
3. Update the ledger.
4. Update exposures.
5. Update `references/gotchas.md`. Add each new standing behavior. Correct each line the session disproved. Sync the plugin copy.
6. Overwrite carryover.
7. Run the credential scan. Follow `references/credential-scan.md`.
8. Commit only when Raymond asks.
