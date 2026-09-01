# district.local

A hand-built Active Directory lab, run on a personal Proxmox box, documented as a series of
after-action reports. It exists to demonstrate identity engineering work to people deciding
whether I can do it — recruiters, hiring managers, anyone sizing up the difference between having
read about Active Directory and having run one, broken it, and fixed it back.

## The through-line

I worked help desk before this. The pattern I kept seeing there — an account provisioned by
copying a named user's access, a standing grant nobody removes because "it'll break something" —
is the thing most of these exercises are circling. `district.local` has its own version of it:
a service account with a direct grant on the domain controller, a throwaway lab account still
sitting in a privileged group months after it stopped being needed. Where an exercise runs into
that pattern, the report says so. Where it doesn't, it doesn't force it.

## The rule these reports follow

Evidence is what the machine printed, not what I remember it printing. Every claim in a report is
labeled Captured (a file backs it), Recalled (I remember it, nothing captured it), or Inherited
(it came from an earlier build and was never independently re-verified) — and Inherited claims
get re-run, not trusted. A report that reads as plausible but turns out to be wrong is worse than
no report at all, because the failure mode it invites is getting asked about it in an interview
and not having an answer. When a claim turns out to be wrong, the correction goes in the report
on the record, not as a quiet edit.

## Reading an exercise

```
exercises/
  YYYY-MM-DD-slug/
    evidence/       raw command output, one file per diagnostic thread
    evidence-log.md what was captured, what wasn't, and why
    report.md       the actual write-up
```

Each report follows the same structure: what I set out to do, the setup, what I did, where I was
asked for a decision rather than deciding unilaterally, what the box actually said, what broke
and why, what I'd do differently, and open questions. That last section is never empty by
default — if something wasn't proven, it's named as such rather than left implied.

Two files at the repo root track state across exercises:

- **`verified-claims.md`** — a running ledger of facts that have moved from inherited or recalled
  to captured, each with a live evidence path. A row moves to Retired, not deleted, once it's
  superseded, with the reason why.
- **`CARRYOVER.md`** — open items and next steps as of the last session.

## About the lab

Windows Server 2022 domain controller, plus supporting VMs for hybrid identity work (Entra
Connect, break-glass admin, that kind of thing), all on Proxmox. The domain controller has all
remoting disabled by design — no WinRM, no RDP, no PowerShell remoting — so every command runs
through the QEMU guest agent from the Proxmox host shell. That's a deliberate constraint, and one
of the reports is about what it's actually like to operate a box you can only reach that way.

This repo is worked with an AI assistant under a project-specific skill
(`.claude/skills/tech-compass/SKILL.md`) that encodes the capture contract above and enforces it
on every exercise. The repo itself is plain git — SSH-authenticated, nothing unusual — set up
alongside the second week of exercises once there was enough here worth pushing.
