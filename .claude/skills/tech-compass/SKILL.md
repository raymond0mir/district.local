---
name: tech-compass
description: Capture lab evidence and write after-action reports for the district.local Active Directory lab. Use whenever Raymond runs, closes out, or writes up a lab exercise, asks what he verified versus assumed, or pastes raw lab output — even without naming the skill.
---

# Tech Compass

Reports for district.local are portfolio work. Readers use them to decide whether Raymond can do identity engineering. An unverified claim in a report is worse than no report. It invites an interview question with no answer.

Canonical copy: `.claude/skills/tech-compass/SKILL.md` in the repo. If a plugin copy differs, the repo copy wins.

## Terms

Use these words for these meanings. Do not substitute synonyms.

- **Captured**: a file in `evidence/` backs the claim.
- **Recalled**: a person remembers the claim. No file backs it.
- **Inherited**: the claim comes from the October 2025 build or its imported baseline. No file backs it.
- **Confirmed**: a ledger row with a live evidence path.
- **Retired**: a Confirmed row whose evidence file is gone or whose state changed.
- **Ledger**: `verified-claims.md` at the repo root.
- **Carryover**: `CARRYOVER.md` at the repo root.
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

If thin pool Data% is 85 or higher, prune snapshots before any state change. Record the readings in The setup.

**Live state.** Read carryover for VM inventory, VM state, and pool readings. Do not take state from this file or from memory.

**Snapshots.** Keep the `clean-install` baseline for each VM. Keep the last few distinct states for each VM. Retire an exercise's before/after snapshot after Raymond confirms the after-state. Run `qm delsnapshot` only after Raymond names the snapshot and says go.

**Evidence files.** Write one file per diagnostic thread. Name the file for what it proves. Start each capture block with three lines: the command verbatim, the host, the UTC timestamp from `date -u`. Put only machine output below those lines. Put analysis in the report or the evidence-log. Screenshot or scrollback output is Recalled. Say so in the report. Recalled output cannot enter the ledger.

**Failure is evidence.** Keep error output. Keep failed attempts. A `Get-ADDomain` failure while ADWS initializes after boot is publishable behavior.

## Layout

```
exercises/YYYY-MM-DD-slug/
  evidence/         one file per thread, named for what it proves
  evidence-log.md   what was captured, what was not, and why
  report.md
verified-claims.md  ledger
EXPOSURES.md        open risks, each cited to an evidence file; doubles as the exercise queue
CARRYOVER.md        open items only; overwritten at every close
CURRICULUM.md       exercise plan
```

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

## Claims

Label every factual claim while drafting: Captured, Recalled, or Inherited. Resolve every label before finishing. Check the ledger before you label a claim Inherited or Recalled.

- Recalled: re-run and capture, or move the claim to Open questions.
- Inherited: re-run first. These claims carry the highest value.

When a capture retires an Inherited claim, add a Confirmed row: claim, evidence file, exercise, date. When a Confirmed row's evidence file disappears or its state changes, move the row to Retired with the reason. Retract a wrong claim on the record, in the ledger and in the report. Never fix a wrong claim by silent edit. This includes Claude's own errors. State them in the evidence-log when caught.

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
- Keep carryover under 400 words. Carryover holds open items and next steps only. Resolved work lives in reports, evidence-logs, the ledger, and exposures.
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

- The repo is public. Run a credential scan before every commit. A literal password reached report prose on 2026-08-31.
- Keep Raymond's personal situation out of every repo artifact: legal, medical, leave, benefits, salary, and money pressure. Express a real constraint as the lab fact it produces: a deadline, a license limit, a sequencing dependency.
- Do not write the current tenant Global Administrator's name in any repo artifact. Raymond supplies it in session.
- The permission-sprawl thesis leads the series: access provisioned by copying a named user, and standing grants nobody removes. Connect an exercise to it when the link is real. Do not force it.
- A grant in use is not a grant that is appropriate.
- When removing a grant breaks something, the lesson is sequencing and break-glass. The lesson is not restoration.
- Watch for reports outpacing verified lab work. If the inherited baseline is still Inherited, say so.

## Session close

1. Write `evidence-log.md`.
2. Write `report.md`.
3. Update the ledger.
4. Update exposures.
5. Overwrite carryover.
6. Run the credential scan.
7. Commit only when Raymond asks.
