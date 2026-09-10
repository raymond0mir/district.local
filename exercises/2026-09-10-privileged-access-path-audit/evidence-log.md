# Privileged access path audit — evidence log

Queued in `EXPOSURES.md` on 2026-09-10. Hardening DC01 did not remove a standing administrative
path. It moved that path to the Proxmox host shell. The hypothesis: `qm guest exec` is an
unbrokered, unlimited, credential-less administrative path into every VM in the lab, and it may
produce no durable record on either side. This exercise changes no state and consumes no pool.

Raymond has held PIM-governed eligibility for Exchange Administrator and Teams Administrator at a
prior employer, and that employer brokered VM access with StrongDM. He has operated as the
*recipient* of both patterns. The lab's own admin path is their anti-pattern. That comparison is
the portfolio value here, and the lab cannot manufacture the recipient-side experience.

## Captured

- **Host-side caller identity, the Proxmox authorization model, and every host logging surface, at
  2026-09-10T18:13:42Z.** `evidence/01-host-side-identity-and-authorization-model.md`. Exit code 0.
  Proxmox VE 9.0.3, kernel 6.14.8-2-pve.

**1. The host-side caller is root, and this is now Captured rather than Recalled.** `id` returns
`uid=0(root) gid=0(root) groups=0(root)` on host `proxmox`, tty `/dev/pts/0`. `EXPOSURES.md`
recorded on 2026-09-10 that this had "only been seen in session prompts, never written to an
evidence file". That gap is closed.

**2. There is no authorization model to bypass, because none was ever built.** `pveum user list`
returns exactly one user, `root@pam`. `pveum group list` returns nothing. `pveum acl list` returns
nothing. `pveum user token list root@pam` returns nothing. One identity holds the entire lab, and no
rule constrains it, because no rule exists.

**3. That single identity has no second factor.** `/etc/pve/priv/tfa.cfg` does not exist. The `keys`
and `tfa-locked-until` columns of `pveum user list` are both empty. `root@pam` authenticates through
Linux PAM, so the credential guarding every VM in the lab is the host root password alone.

**4. Proxmox models the exact privilege distinction the lab does not use.**
`VM.GuestAgent.Unrestricted` is a separate privilege from `VM.GuestAgent.FileRead`,
`VM.GuestAgent.FileWrite`, `VM.GuestAgent.FileSystemMgmt` and `VM.GuestAgent.Audit`. `PVEVMUser`
holds the file and audit privileges and **not** `Unrestricted`; `Administrator`, `PVEAdmin` and
`PVEVMAdmin` hold it. A least-privilege path for guest-agent work exists as a built-in role and is
assigned to nobody.

**5. The Proxmox task log records state changes and does not record guest-agent execution.** Twenty
task types appear across the whole task index: `vncproxy` 90, `qmstart` 31, `vncshell` 28,
`qmshutdown` 12, `qmstop` 11, `vzstart` 9, `qmdelsnapshot` 8, `aptupdate` 8, `qmsnapshot` 6,
`push_file` 5, and eleven more. **No task type corresponds to guest-agent command execution.** The
same capture shows the three `qmdelsnapshot` tasks from four minutes earlier, with UPID, VMID,
`root@pam` and both timestamps. The log demonstrably works. It simply does not cover this path.

**6. The API access log holds nothing either.** `grep -c 'agent' /var/log/pveproxy/access.log`
returns 0. The `qm` command-line tool does not traverse the HTTP API, so an invocation made from the
host shell leaves no `pveproxy` entry.

**7. The only surviving record of the path is root's shell history, and it is self-truncating.**
`/root/.bash_history` holds 500 lines, the default cap. 166 of those 500 contain `guest exec`. One
third of the entire retained history is this one administrative path, everything older is already
discarded, and the file is owned and writable by the principal being audited.

**8. Proxmox does log opening the host shell, and not what happens inside it.** Twenty-eight
`vncshell` tasks are recorded, one of them still open. The audit boundary sits at the shell prompt.

**9. Host login history reaches back three days.** `wtmpdb begins Mon Sep 7 15:55:26 2026`. Sessions
carrying `192.168.1.164` are SSH from the Mac Mini; sessions with a blank host are the web console
shell. Every one is `root`.

- **A marked `qm guest exec` invocation against DC01, and every host log surface read within one
  second of it, at 2026-09-10T18:18:48Z.** `evidence/02-marked-invocation-leaves-no-host-record.md`.
  Marker string `AUDITMARK-20260910-PAP`. Guest agent returned `exitcode 0`, `exited 1`.

**10. The path lands on the domain controller as `nt authority\system`.** `whoami` through the
agent returns SYSTEM on `DC01`. This is the highest local principal on the machine, and
`references/gotchas.md` already records that it authenticates outward as `DC01$`.

**11. One controlled invocation produced zero host-side records.** With T0 fixed at epoch
1789064328 and the sweep run one second after the call returned: `pvenode task list` shows no new
task, the newest remaining `qmdelsnapshot` being eight minutes old; `/var/log/pve/tasks/index` is
unchanged; `journalctl -u pvedaemon --since @T0` returns `-- No entries --`; and the `pveproxy` tail
holds only the web interface's own polling GETs. **Four surfaces, one second, nothing.**

**12. `pvedaemon` logs guest-agent failures and never successes.** Both journal mentions of "agent"
in seven days are timeouts: VM 101 and VM 107 `guest-ping` failures on September 5. The only
guest-agent events that reach the journal are the ones where the agent did not answer.

**13. The host runs no command auditing.** `systemctl is-active auditd` returns `inactive`, and
`which auditctl` returns nothing, so the package is absent.

**14. The 500-line history cap is confirmed, not assumed.** `HISTSIZE=500 HISTFILESIZE=500`. Against
166 recorded `guest exec` lines, the sole record of this path holds roughly the last three sessions
of work and discards the rest.

**15. The invoked process reported no resolvable parent.** `child=powershell.exe parent= parentpid=`.
The `Win32_Process` lookup on `ParentProcessId` returned nothing. This is not yet explained, and it
matters for detection: process ancestry is the usual way an investigator ties a shell back to what
launched it. Re-tested in the guest-side sequence.

- **DC01's logging posture and a marker search, at 2026-09-10T18:22:13Z.**
  `evidence/03-dc01-records-the-command-text.md`. Exit code 0.

**16. DC01 records the invocation, and the hypothesis is half wrong.** `Process Creation` auditing is
`Success`, 94 event 4688 records exist in two hours, and PowerShell script block logging is enabled
(`EnableScriptBlockLogging : 1`) with 27 event 4104 records in thirty minutes. **A search for the
`AUDITMARK-20260910-PAP` string in the PowerShell Operational log returns 2 events.** The command
text sent from the host reached a durable log on the guest.

**17. The asymmetry is the finding, not the absence.** The host that authorises the action records
nothing. The guest that executes it records the full command text. An investigator working from
Proxmox alone sees nothing; an investigator working from DC01 sees the command and not who sent it.
Attribution and action are recorded on opposite sides of the boundary, and neither side holds both.

**18. `qemu-ga` writes to DC01's Application log: 16 events in thirty minutes.** The guest agent is
not silent on the guest. Content not yet read.

**19. The parentless process is explained by the agent's spawn mechanism.** `QEMU-GA` runs as
`LocalSystem` at PID 3060, from `"C:\Program Files\Qemu-ga\qemu-ga.exe" -d --retry-path`. The
invoked shell reported `pid=620 ppid=4452`, and 4452 is neither the service nor resolvable. The
install directory carries `gspawn-win64-helper-console.exe` and `gspawn-win64-helper.exe`, glib's
spawn helpers. **A live process-table walk cannot tie the shell to the guest agent, because the
intermediate has already exited.** Whether event 4688 preserves the real creator is the next test.

**20. Module logging and transcription are off.** Neither registry key exists. Script block logging
alone is what captured the marker.

**21. Logon volume on DC01 is high: 84 each of 4624, 4627 and 4672 in thirty minutes.** Not yet
attributed to any cause, and not assumed to relate to this path.

- **The content of the guest-side records, at 2026-09-10T18:25:15Z.**
  `evidence/04-what-the-guest-records-in-full.md`. Exit code 0.

**22. The guest agent writes the entire command line to DC01's Application log.** Provider
`qemu-ga`, event Id 1, Information level: `guest-exec called: "powershell.exe -NonInteractive
-Command ...`, followed by the complete command text. `guest-exec-status called, pid: 4704` and
`guest-ping called` appear alongside it. **This record does not depend on PowerShell script block
logging, and it is the most complete single record of the path that exists anywhere.**

**23. Event 4688 preserves the creator that the live process table lost.** `parentproc` is
`C:\Program Files\Qemu-ga\gspawn-win64-helper.exe` on both captured invocations, with
`subject: DC01$`. Finding 19's broken ancestry is a live-query artefact only. The Security log holds
the chain.

**24. No single guest log holds both the command and its parent.** 4688 names the parent and leaves
`cmdline` empty, because `ProcessCreationIncludeCmdLine_Enabled` does not exist under
`HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\Audit`. 4104 holds the
script text and no parent. The `qemu-ga` event holds the command and the agent verb. Reconstructing
one invocation needs at least two of the three.

**25. Script block logging attributes every invocation to `S-1-5-18`.** All three 4104 events carry
that UserId. SYSTEM is the only identity the guest ever sees, so no guest-side log can distinguish
one host operator from another. **This is the precise mechanical reason the boundary cannot be
bridged from the guest side.**

**26. DC01's clock does not agree with the host's, and the offset is not a timezone.** Three
invocations at host UTC 18:18:48, 18:22:13 and 18:25:15 render on DC01 as 3:54:31 PM, 3:57:57 PM and
4:00:58 PM. The intervals match to within one second, so the offset is constant. It is not a whole
number of hours, so `references/gotchas.md`'s standing timezone warning does not explain it. Size and
direction are not stated, because DC01's timezone and time source were not read.
**Retracted in part, 2026-09-10.** "The offset is constant" is wrong. The inference held inside the
seven-minute window and not beyond it. `exercises/2026-09-10-domain-time-skew` measures the offset
at +4h 35m 43s here and +5h 06m 10.7s three hours later. Size and direction are now Captured there:
DC01 is ahead of the host.

## Not captured, and why

- **Whether `push_file` is the guest-agent file-write task.** If it is, Proxmox logs pushing a file
  into a guest but not running a command in it, which sharpens finding 5. This is not asserted.
- **DC01's timezone, clock and time source.** Finding 26 establishes that a constant, non-hourly
  offset exists. `Get-Date`, `[TimeZoneInfo]::Local` and `w32tm /query /source` were not run, so
  nothing is claimed about the direction or the cause.
- **Which policy enabled script block logging, and when.** The value sits in the Policies hive, so a
  GPO or local policy set it. No exercise in this repository records doing so.
- **Whether the `qemu-ga` Application log rotates, and how large it is.** The most complete record of
  the path may also be the most easily lost.
- **Whether a non-root PVE user without `VM.GuestAgent.Unrestricted` is actually refused.** Finding 4
  makes this the cheapest available control. Testing it creates a PVE user, which is a state change
  touching standing privilege, so it waits for Raymond.

## Where Raymond was consulted

- 2026-09-10. He named this exercise as the session's second item, verbatim: "now let's do the
  privileged-access-path audit".

## Corrections

- **Claude's stated hypothesis was that the path "may produce no durable record on either side". The
  guest half is disproven.** Before running the guest-side sequence Claude wrote, in session: "If
  `Process Creation` auditing is off and script block logging is disabled, then neither side of this
  path records anything, and that is the finding the exercise exists to establish." Both are
  enabled, and the marker string is present twice in DC01's PowerShell Operational log. The exercise
  gets a better finding than the one predicted, and the prediction is recorded here as wrong.
  Stated before being asked, per `CLAUDE.md`.

- **Two lines of this log were stale at 2026-09-10 session close, and are corrected here.** "Not
  captured, and why" still carried "Whether the guest records anything. No DC01 capture has run."
  after findings 16 to 25 answered it, and "Not started" still listed `report.md`, the marker
  events, the 4688 records and the `qemu-ga` events after all four were done. Both lines are
  removed. No captured claim changed. Caught at the following session start, same date, before
  being asked.

- **Finding 26's claim that the offset is constant is retracted.** A later read on 2026-09-10 put
  DC01 at +5h 06m 10.7s from the host where the two readings in this exercise put it at
  +4h 35m 43s. The three timestamps used here sit inside seven minutes, and constancy over that
  window does not extend to three hours. The finding is annotated in place rather than deleted, and
  the measurement now lives in `exercises/2026-09-10-domain-time-skew`.

## Open questions

The nine questions in `SKILL.md` reduce to these for this exercise. None is answered yet.

- ~~Which identity executes the call on the host?~~ Answered: `root`, finding 1. The guest half is
  still open.
- ~~Who else could make that call?~~ Answered: nobody, because `root@pam` is the only user that
  exists, finding 2.
- ~~Does the Proxmox task log or `pveproxy` access log record the invocation?~~ Answered: no,
  findings 5 and 6. The `pvedaemon` journal is not yet settled.
- ~~Does the guest record anything at all?~~ Answered: yes, findings 16 to 20 and 22 to 25.
- ~~Does event 4688 preserve the parent the live process table cannot resolve?~~ Answered: yes,
  finding 23.
- What causes 84 logon events in thirty minutes on DC01?
- Why is DC01's clock offset from the host's by a non-hourly constant, and what else does that
  affect? Kerberos tolerates five minutes. Certificate validity windows and Entra Connect both
  depend on the answer.
- Is there any time limit, approval, or session recording on the path?
- What would a broker impose that is absent here, and what does the broker cost?
- Would assigning `PVEVMUser` to a non-root PVE user actually block `qm guest exec`, given
  finding 4? That is the cheapest available control and it has not been tested.

## Not started

- Testing whether `PVEVMUser` without `VM.GuestAgent.Unrestricted` actually blocks `qm guest exec`.
- The alternatives half of the exercise: what a broker imposes, and what it costs.
- Reading DC01's clock and time source, which finding 26 requires.
