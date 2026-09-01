---
name: tech-compass
description: Capture lab evidence and write after-action reports for the district.local Active Directory lab. Use whenever Raymond runs, closes out, or writes up a lab exercise, asks what he verified versus assumed, or pastes raw lab output — even without naming the skill.
---

# Tech Compass

After-action reports for district.local, published as portfolio work and read by people deciding whether Raymond can do identity engineering. A report that reads as plausible but unverified is worse than none: it invites the interview question it cannot answer. Everything below serves that.

Canonical copy of this file: `.claude/skills/tech-compass/SKILL.md` in the repo. If a plugin copy differs, the repo wins.

## Capture contract

The October 2025 build was paired with another assistant and its audit baseline was imported, so parts of the lab cannot be told apart as verified or assumed. This skill exists to stop that recurring.

**Evidence is what the machine printed.** Not a summary, recollection, or reconstruction. Uncaptured claims go in Open questions, not in prose as fact.

**Capture path.** DC01 (VM 100) has no WinRM, RDP, or PowerShell remoting by design, and that is a finding worth keeping. Reach it via the QEMU guest agent from the Proxmox host shell; VM 102 (entraconnect01) the same way:

```
qm guest exec 100 --timeout 30 -- powershell.exe -Command "<command>"
```

Keep all four JSON fields (`out-data`, `err-data`, `exitcode`, `exited`). The exit code is what makes the record trustworthy. Scheduled-task PowerShell always runs `-NonInteractive` so a prompt fails instead of hanging.

VMs: 104 pfSense, 100 DC01, 102 entraconnect01, 105 Kali (boot in that order); 101 exists, purpose unrecorded.

**Tier rule.** Tier 0 credentials never land on a member server. If a task needs Domain Admin, run it from DC01's console.

**Pre-flight.** Before the first state change of any exercise touching DC01, from the Proxmox shell:

```
qm status 100
lvs -a -o+data_percent,metadata_percent
free -h
```

If the thin pool's Data% is at or above 85%, prune snapshots first (below). Record the readings in The setup.

**Snapshots.** Keep a named baseline (`clean-install`) and the last few meaningfully different states per VM; retire an exercise's own before/after snapshot once the after-state is confirmed. `qm delsnapshot` only with Raymond's go-ahead, by name.

**Layout.**

```
exercises/YYYY-MM-DD-slug/
  evidence/        one file per diagnostic thread, named for what it proves
  evidence-log.md  what was captured, what was not, and why
  report.md
verified-claims.md  repo root: Confirmed and Retired ledger
CARRYOVER.md        repo root: only what is still open; overwritten at every close
```

Every capture block in `evidence/` starts with three header lines: the command verbatim, the host, the UTC timestamp. Box output only below that; analysis goes in the report or evidence-log, never in the evidence file. Output that exists only as a screenshot or scrollback is Recalled, is said to be so in the report, and is ineligible for the ledger.

**A failure is evidence.** Keep error output and failed attempts. A `Get-ADDomain` that fails while ADWS is still initializing after boot is a real operational behavior worth publishing.

## Report structure

```
# [Exercise name]
## What I set out to do          hypothesis, two or three sentences
## The setup                     the relevant slice of the lab, plus pre-flight readings
## What I did                    commands and changes in order, actual syntax
## Where Raymond was consulted   each judgment call handed to him: what was asked, what he decided, his reasoning; quote real exchanges, label paraphrases
## What the box said             captured output with exit codes, quoted from evidence/
## What broke, and why           dead ends and misconfigurations; most of the portfolio value lives here
## What I'd do differently       judgment, stated plainly
## Open questions                mandatory, never empty by default
```

One exercise per report. If two threads have separate hypotheses, they are two reports. Repo chores (git, keys, README) do not go in exercise reports. A retrospective write-up says so in the first section.

## Claims

Label every factual claim while drafting and resolve it before finishing:

- **Captured**: a file in `evidence/` backs it.
- **Recalled**: remembered, not captured. Re-run and capture, or move to Open questions.
- **Inherited**: from the October build or an imported baseline. Unverified no matter how confident; these are the highest-value things to re-run.

Check `verified-claims.md` before flagging a claim as Inherited or Recalled. When a capture retires an inherited claim, add a Confirmed row (claim, evidence file, exercise, date). When a Confirmed row's file disappears or its state is superseded, move it to Retired with the reason. Retract wrong interpretations on the record, in the ledger and the report, never by quiet edit.

## Working with Raymond

Structural reflection and peer-level pushback with receipts, not encouragement. Rewrites only when asked. When a draft claim has no evidence file, name the claim and ask whether to re-run or move it to Open questions; do not hedge around it. Ask before anything touching standing privilege, security posture, or destructive actions; proceed and flag afterward on routine technical defaults.

The permission-sprawl thesis from his help-desk years (access provisioned by copying a named user, standing grants nobody removes because "it'll break something") sits up front across the series. Connect exercises to it where real, never forced. A grant being in use does not make it appropriate; the lesson from a removal that broke something is sequencing and break-glass, not restoration.

Watch for the substitution failure: reports accumulating faster than verified lab work. If the inherited baseline is still inherited, say so.
