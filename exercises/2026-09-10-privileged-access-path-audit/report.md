# Privileged access path audit

## What I set out to do

Hardening DC01 removed every interactive administrative path to it. `SeDenyInteractiveLogonRight`
denies Domain Admins console logon, `Administrator` is disabled, and `qm guest exec` from the
Proxmox host shell is the only working administrative path. The hypothesis was that this did not
remove a standing administrative path. It relocated one, to a place with no broker, no time limit,
no per-operator credential and possibly no record. This exercise audits that path. It changes no
state.

## The setup

Proxmox VE 9.0.3, kernel 6.14.8-2-pve, on the lab's single host. DC01 is VM 100, running, with
`agent: enabled=1`. CA01 is VM 107, running. The audit reads host-side authorization and logging,
then reads DC01's logs for a marked invocation.

Pre-flight readings are in `exercises/2026-09-10-thin-pool-headroom-reclaim/evidence/`. The thin
pool stood at 84.23% against an 85% stop condition at the session start, so a reclaim ran first.
This exercise consumes no pool and needed no gate.

## What I did

1. Read the host-side caller identity, the Proxmox user, group, ACL and token model, the TFA file,
   the built-in role definitions, and every host logging surface.
   `evidence/01-host-side-identity-and-authorization-model.md`.
2. Ran one `qm guest exec` against DC01 carrying the marker string `AUDITMARK-20260910-PAP`, with
   T0 fixed at epoch 1789064328, then read the Proxmox task list, the task index, the `pvedaemon`
   journal since T0 and the `pveproxy` access log, one second after the call returned.
   `evidence/02-marked-invocation-leaves-no-host-record.md`.
3. Read DC01's audit policy, its Security, System, Application and PowerShell Operational logs, the
   PowerShell logging policy keys, and searched for the marker.
   `evidence/03-dc01-records-the-command-text.md`.
4. Read the content of the matching records: the 4104 script blocks, the 4688 process-creation
   events, and the `qemu-ga` Application events.
   `evidence/04-what-the-guest-records-in-full.md`.

Commands ran as:

```
qm guest exec 100 --timeout 180 -- powershell.exe -NonInteractive -Command '<command>'
```

The `-Command` argument is single-quoted at the bash level throughout, per
`references/gotchas.md`.

## Where Raymond was consulted

- **Session order, 2026-09-10.** He named this exercise as the session's second item, verbatim:
  "now let's do the privileged-access-path audit". The reclaim ran first because the 85% stop
  condition blocked everything else.
- **Snapshot deletion, 2026-09-10.** Three snapshots were deleted to clear the stop condition, on
  his word, verbatim: "go ahead with those three". That work is recorded in its own exercise,
  `exercises/2026-09-10-thin-pool-headroom-reclaim`, and is not part of this audit.
- **Not consulted, and deliberately so.** Testing whether a non-root Proxmox user without
  `VM.GuestAgent.Unrestricted` is actually refused requires creating a Proxmox user. That is a state
  change touching standing privilege. It was left for him rather than assumed.

## What the box said

**The host-side caller is root.** `id` returns `uid=0(root) gid=0(root) groups=0(root)`. Until this
capture that fact had only appeared in session prompts.

**There is no authorization model to bypass, because none was ever built.** `pveum user list`
returns exactly one user, `root@pam`. `pveum group list`, `pveum acl list` and
`pveum user token list root@pam` all return nothing. `/etc/pve/priv/tfa.cfg` does not exist, and
`root@pam` authenticates through Linux PAM, so the host root password alone guards every VM.

**Proxmox already ships the control this lab does not use.** `VM.GuestAgent.Unrestricted` is a
distinct privilege from `VM.GuestAgent.FileRead`, `FileWrite`, `FileSystemMgmt` and `Audit`. The
built-in `PVEVMUser` role holds the file and audit privileges and not `Unrestricted`.

**The path lands on the domain controller as `nt authority\system`.**

**One controlled invocation produced zero host-side records.** No new Proxmox task; the task index
unchanged; `journalctl -u pvedaemon --since @T0` returning `-- No entries --`; and `pveproxy`
holding only the web interface polling itself. Twenty task types appear across the entire task
index, including `qmdelsnapshot` eight minutes earlier with UPID, VMID, user and both timestamps.
None corresponds to guest-agent command execution.

**`pvedaemon` logs guest-agent failures and never successes.** Both mentions of "agent" in seven
days are `guest-ping` timeouts.

**The host runs no command auditing.** `auditd` is `inactive` and `auditctl` is absent.
`HISTSIZE=500 HISTFILESIZE=500`, and 166 of those 500 lines contain `guest exec`.

**DC01 records the invocation three separate ways.** The `qemu-ga` provider writes
`guest-exec called: "powershell.exe -NonInteractive -Command ...` with the complete command text to
the Application log. Event 4688 records the process with
`parentproc: C:\Program Files\Qemu-ga\gspawn-win64-helper.exe` and `subject: DC01$`. Event 4104
records the script block text. The marker string returns matches in the PowerShell Operational log.

**Every guest-side record attributes to `S-1-5-18`.**

## What broke, and why

**The hypothesis was half wrong, and the correction is the finding.** The exercise predicted that
the path might produce no durable record on either side. The guest half is disproven. DC01 holds
the full command text in a durable log, twice over.

The real shape is an asymmetry. **The side that authorises the action records nothing. The side
that executes it records everything except who asked.** An investigator working from Proxmox sees
no invocation at all. An investigator working from DC01 sees the exact command and one identity,
`S-1-5-18`, which every invocation shares. Neither side holds both halves, and no correlation key
links them.

Three smaller things broke on the way.

**Live process ancestry inside the guest is useless here.** The invoked shell reported
`ppid=4452`, and that process did not exist by the time the shell queried it. The guest agent
spawns through glib's `gspawn-win64-helper.exe`, which exits immediately. Only event 4688, which
records the creator at creation time, preserves the chain.

**No single guest log holds both the command and its parent.** 4688 names the parent and leaves
`cmdline` empty, because `ProcessCreationIncludeCmdLine_Enabled` does not exist. 4104 holds the
script text and no parent. Reconstructing one invocation needs at least two logs.

**DC01's clock does not agree with the host's.** Three invocations at host UTC 18:18:48, 18:22:13
and 18:25:15 render on DC01 as 3:54:31 PM, 3:57:57 PM and 4:00:58 PM. The intervals match to within
one second, so the offset is constant, and it is not a whole number of hours. The host's clock is
already Confirmed as NTP-synchronized. DC01's timezone and time source were not read, so no
direction or size is claimed here. This was found while correlating logs across the boundary, which
is exactly the operation the skew would obstruct.

## What I'd do differently

The first inventory command omitted `echo $?`, so its exit code is absent from
`evidence/01`. `CLAUDE.md` requires the exit code on every capture. The file records the omission
rather than hiding it.

I predicted the outcome before measuring it, in session, and said so in a way that framed the
absence of logging as the expected result. The measurement contradicted it. Predicting a result
before the capture adds nothing and risks steering the reading.

The clock discrepancy was visible in the third capture and I did not notice it until the fourth.
Timestamps from two hosts appeared side by side and I read them as agreeing.

## Open questions

- Why is DC01's clock offset from the host's? **This report first called that offset constant. That
  wording is retracted.** The three timestamps behind it sit inside seven minutes. A read three
  hours later put DC01 at +5h 06m 10.7s from the host, against +4h 35m 43s here.
  `exercises/2026-09-10-domain-time-skew` carries the measurement and the retraction. A Confirmed
  row from 2026-09-06 puts CA01 and DC01 within 1.69 seconds of each other; that no longer holds
  either, because CA01 now reads 1h 53m 51.8s ahead of DC01. Kerberos tolerates five minutes.
  Certificate validity windows and Entra Connect sync both depend on the answer.
- Does assigning `PVEVMUser`, which lacks `VM.GuestAgent.Unrestricted`, actually refuse
  `qm guest exec`? That is the cheapest available control and it is untested.
- Does the `qemu-ga` Application log rotate? The most complete record of this path may also be the
  most easily lost.
- Which policy enabled PowerShell script block logging on DC01, and when? No exercise in this
  repository records doing it.
- What causes 84 logon events in thirty minutes on DC01?
- What would a broker impose that is absent here, and what does it cost? Raymond has been the
  recipient of brokered VM access at a prior employer. The lab cannot manufacture that experience,
  and the comparison is the point of the exercise. Not started.
