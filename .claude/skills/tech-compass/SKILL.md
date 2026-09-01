---
name: tech-compass
description: Capture lab evidence and write after-action reports for the district.local Active Directory lab. Use this whenever Raymond is running a lab exercise, closing one out, drafting or revising a tech-compass write-up, or asking what he actually verified versus what he assumed — including when he doesn't name the skill and just says things like "let's document this one", "write up the AD CS exercise", "did I ever prove that", or pastes raw console output from the lab and wants something done with it.
---

# Tech Compass

After-action reports for the district.local lab. Each one answers four questions: what he set out to do, how he built it, what the machine actually said, and what he'd do differently. They are written for publication as portfolio work, and they are read by people deciding whether he can do identity engineering. That audience is the whole design constraint — a report that reads as plausible but unverified is worse than no report, because the failure mode it invites is being asked about it in an interview.

## The capture contract

The lab's history has a known defect: the October 2025 build was done paired with another assistant, the audit baseline was imported rather than written, and the consequence is that parts of district.local cannot be distinguished between "verified" and "assumed". This skill exists primarily to stop that from recurring. Everything below serves that.

**Evidence is what the machine printed.** Not a summary of it, not a recollection of it, not a plausible reconstruction of what it would have printed. If the output was not captured, the claim it supports does not go in the report as fact — it goes in as an open question.

**Capture path.** DC01 (VM 100) has all remoting disabled by design; there is no WinRM, RDP, or PowerShell remoting path, and that constraint is itself a finding worth keeping. Reach it instead through the QEMU guest agent over the virtio serial channel, from the Proxmox host shell:

```
qm guest exec 100 --timeout 30 -- powershell.exe -Command "<command>"
```

This returns JSON with `out-data`, `err-data`, `exitcode`, and `exited`. Keep all four. The exit code is the part people drop and the part that makes the record trustworthy. Boot order for the lab is 104 (pfSense) → 100 (DC01) → 105 (Kali).

**Infrastructure pre-flight.** Before starting any exercise that runs commands against or changes DC01, check the host's own headroom from the Proxmox shell — the Aug 31 2026 exercise stalled when VM 100 went down unprompted mid-session, and the trail led to `pve-data-tpool` sitting at 96%+ full with no direct kernel confirmation available after the fact to prove it as the cause. A thirty-second check up front rules this class of problem in or out before it costs an exercise:

```
qm status 100
lvs -a -o+lv_name,data_percent,metadata_percent,lv_size
free -h
```

If the thin pool's `Data%` is at or above 85%, stop and prune snapshots (see Snapshot retention, below) before doing anything else — don't start an exercise on top of a pool that's already tight. Note the pool and memory readings in the exercise's **The setup** section so a stalled or crashed exercise has this ruled in or out from the start, not reconstructed after the fact.

**Snapshot retention.** Unmanaged Proxmox snapshots are the main driver of thin-pool pressure — one VM alone reached seven before the Aug 31 2026 crash. After closing an exercise, retire any snapshot whose only purpose was that exercise's own before/after state once the after-state is confirmed good; keep a named baseline (e.g. `clean-install`) and the most recent handful of meaningfully-different states per VM, not every intermediate checkpoint. Deleting a snapshot is irreversible — always get Raymond's explicit go-ahead on which ones, by name, before running `qm delsnapshot`, and never infer "safe to delete" from a name alone.

**Where captures land.** Exercises live under `exercises/`, one directory per exercise, named `YYYY-MM-DD-slug` (e.g. `2026-08-31-adcs-esc1`), containing `evidence/` and `report.md` as siblings:

```
exercises/
  2026-08-31-adcs-esc1/
    evidence/
    report.md
```

Write raw output to `evidence/` inside the exercise directory, one file per command, named for what it proves rather than when it ran — `adws-ntds-service-state.json`, not `output3.json`. Alongside each, record the command verbatim and the timestamp. The prose gets written against these files, never against memory of them.

Getting output from the Proxmox host to the vault is `scp` from the Mac. If a capture only exists as a screenshot or a terminal scrollback, say so in the report rather than transcribing it and presenting it as captured.

**A failure is evidence.** Do not clean up error output or omit the attempt that didn't work. A `Get-ADDomain` that fails with a full CategoryInfo and FullyQualifiedErrorId because ADWS is still initializing after boot is a real operational behavior worth publishing — that exact pattern reads as a broken DC to a tier-1 tech at 7am, and knowing it isn't broken is the kind of thing that separates someone who ran the lab from someone who read about it.

## Report structure

Use these sections in this order, so the reports read as a series rather than unrelated posts:

```
# [Exercise name]
## What I set out to do
## The setup
## What I did
## Where Raymond was consulted
## What the box said
## What broke, and why
## What I'd do differently
## Open questions
```

**What I set out to do** — the hypothesis or capability being tested, in two or three sentences. Not a tutorial framing.

**The setup** — the relevant slice of district.local only. Which VMs, which services, what state they were in. Enough that someone could rebuild the conditions; not a full lab tour repeated in every post.

**What I did** — commands and configuration changes, in order, with the actual syntax used.

**Where Raymond was consulted** — every point in the exercise where a judgment call, a destructive or hard-to-reverse action, or a fork in approach was handed to him instead of decided unilaterally. For each one, record: what was asked, where in the sequence it happened, what he decided, and his stated reasoning if he gave one. This is a different thing from Open Questions — those are gaps in the evidence; this is a record of where human judgment, not machine output, actually drove the exercise, and it's exactly as load-bearing for a hiring audience as the technical evidence is: knowing when to act unilaterally versus when to hand a call back is part of what's being demonstrated. Reconstruct it faithfully — quote the actual question and answer when they happened in the current session; if a decision point predates the session and only survives as prose in an earlier draft, say that plainly rather than presenting a paraphrase as a verbatim exchange.

**What the box said** — captured output, quoted from `evidence/`. This section is the reason the report is credible. Include exit codes.

**What broke, and why** — the dead ends, the misconfigurations, the things that took an afternoon. This section carries most of the portfolio value, because working through failure is the skill being demonstrated. The OS Type field on VM 100 reading Linux 6.x on a Windows Server 2022 guest is an example of the class: a config mismatch that produces symptoms far from its cause.

**What I'd do differently** — judgment, stated plainly.

**Open questions** — anything not proven. This section is mandatory and must not be empty by default. If an attack chain's detection half was validated but the chain past the write was never run, that belongs here, named as such.

## Evidence versus reconstruction

When drafting, mark every factual claim as one of three things and resolve it before the report is finished:

- **Captured** — there is a file in `evidence/` behind it.
- **Recalled** — he remembers it but nothing captured it. Either re-run the command and capture it, or move the claim to Open questions. Do not let it stand as fact.
- **Inherited** — it came from the October build or an imported baseline. Treat as unverified regardless of how confident it feels. These are the highest-value things to re-run, because they are exactly where the lab's credibility is thinnest.

Before flagging a claim as inherited or recalled, check `verified-claims.md` at the project root — if the claim is already listed under Confirmed with a live evidence path, cite that instead of re-flagging it as unverified. When a report re-runs and captures something that was previously inherited or recalled, add a row to `verified-claims.md` (claim, evidence file, exercise, date) so later reports don't re-litigate it. If an evidence file backing a Confirmed row no longer exists, move that row to Retired rather than silently trusting the claim.

If a draft is being written after the fact about work already done, say so in the report. A retrospective write-up is honest; a retrospective write-up dressed as a live capture is the thing this skill exists to prevent.

## Working with Raymond on these

He wants structural reflection and peer-level pushback with receipts, not encouragement. Rewrites only when he asks for them.

The specific pushback that matters here: when a claim in a draft has no evidence file behind it, say which claim and ask whether to re-run the command or move it to Open questions. Do not smooth over the gap, and do not write around it with hedged language — hedging is how an unverified claim survives into a published post.

The permission-sprawl thesis from his help-desk years (accounts provisioned by copying a named user's access, sprawl nobody would remove because "it'll break something") is the through-line intended to sit up front across the series. Where an exercise touches it, connect them; where it doesn't, don't force it.

Watch for the substitution failure: polished write-ups accumulating faster than verified lab work. If the reports are getting written and the inherited baseline is still inherited, name that.

Consultation points are part of the record now, not just the technical findings — see **Where Raymond was consulted** in Report structure. When a report is being drafted or revised and it includes a moment where he was asked for a decision (a destructive action, a fork in approach, a "your call" flagged mid-conversation), that exchange goes in the report, not just its outcome.
