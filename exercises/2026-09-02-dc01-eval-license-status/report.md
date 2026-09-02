# DC01's evaluation license: from correlation to Windows saying it plainly

**Exercise:** the single queued action left at the close of A1, run 2026-09-02.
**Result:** confirmed, then confirmed again more sharply. DC01 is running Windows Server 2022
Standard Evaluation, past its evaluation window, in Notification state (`LicenseStatus: 5`,
`GracePeriodRemaining: 0`). One prior open question (pid 4624) closes as a side effect. **DC01
crashed mid-session** while this report was being written — and its own System event log names
the exact mechanism: `wlms.exe` (Windows License Manager) has been repeatedly, deliberately
shutting DC01 down because its evaluation license expired, at irregular intervals reaching back at
least to 8/31. This is very likely the same mechanism behind **occurrence 2** of the crash
documented in `exercises/2026-08-31-dc01-unexpected-shutdown/report.md`, whose root cause that
report explicitly could not pin down at the time — nobody yet knew DC01's license was expired.
**Mitigated same day**: rearmed via `slmgr /rearm` (through `cscript`, not the bare command),
buying roughly 10 days before Notification state resumes, with 5 of 6 rearms left. Not a permanent
fix. See both addenda below.

---

## What I set out to do

`EXPOSURES.md` and A1's report both carried the same flagged correlation: `SERVER_EVAL_x64FRE_
en-us.iso` and DC01's `clean-install` snapshot share the date 2025-09-29, and Windows Server
evaluation runs 180 days — landing around 2026-03-28, over five months before today. Both write-
ups were explicit that this was **inference from two matching dates, not a capture**, and both
named the same next step: read the licensing state directly off DC01 via CIM instead of `slmgr
/dlv` (which hangs `qm guest exec` — it's VBScript hosted by `wscript`, and that's the failure
mode that produced the still-open pid 4624 question). The hypothesis: DC01's own licensing state
agrees with the two-date correlation.

## The setup

DC01 (VM 100) running, per A1's close. No pre-flight pool/RAM check — this is a read-only query,
not a state change, so the skill's pre-flight gate doesn't apply. Reached the usual way, `qm guest
exec` from the Proxmox host shell; Raymond ran the command and pasted the output back.

## What I did

One command, combining `Win32_OperatingSystem` (for `InstallDate` and `LastBootUpTime`) and
`SoftwareLicensingProduct` filtered to the row with a partial product key (for `LicenseStatus`,
`GracePeriodRemaining`, `EvaluationEndDate`):

```
qm guest exec 100 --timeout 90 -- powershell.exe -NonInteractive -Command 'Get-CimInstance Win32_OperatingSystem | Select-Object Caption,Version,InstallDate,LastBootUpTime | Format-List; Get-CimInstance SoftwareLicensingProduct -Filter "PartialProductKey IS NOT NULL" | Select-Object Name,Description,LicenseStatus,GracePeriodRemaining,EvaluationEndDate | Format-List'
```

## Where Raymond was consulted

Not run yet at the point this report was drafted: whether to treat the hourly-restart signal
(below) as worth a same-session follow-up capture, or to leave it for later. Asked, not yet
answered — see Open questions.

## What the box said

Full output in `evidence/os-and-licensing-status-20260902T1626Z.txt`. Exit code 0.

```
Caption        : Microsoft Windows Server 2022 Standard Evaluation
Version        : 10.0.20348
InstallDate    : 9/30/2025 12:36:49 AM
LastBootUpTime : 9/2/2026 8:27:36 AM

Name                 : Windows(R), ServerStandardEval edition
Description          : Windows(R) Operating System, TIMEBASED_EVAL channel
LicenseStatus        : 5
GracePeriodRemaining : 0
EvaluationEndDate    : 12/31/1600 4:00:00 PM
```

`LicenseStatus: 5` is Notification — per the status table already carried in `CARRYOVER.md` (1
Licensed, 2 OOB grace, 3 out-of-tolerance grace, 5 Notification/expired — nags, eventually
restarts hourly, 6 extended grace), this is the fully-expired state, not a grace period. Windows
agrees with the two-date correlation independent of any date arithmetic.

## What broke, and why

Nothing broke in the sense of a failed command — exit 0, clean output. What "broke" is a prior
open question's framing:

**The InstallDate didn't match the ISO date exactly, and that's fine.** 2025-09-29 (ISO, snapshot)
vs. 9/30/2025 (`InstallDate`) is a one-day gap. `CARRYOVER.md` already flagged, from unrelated
snapshot-naming work the same day, that this host runs America/Los_Angeles and that guest/host
clock comparisons had produced exactly this kind of one-day offset before. Read alone, a one-day
gap could look like the inference failing its own test. It isn't — `LicenseStatus` and
`GracePeriodRemaining` confirm the same conclusion independent of any date math, so the gap is
almost certainly the known timezone artifact, not a wrong inference. I'm flagging this explicitly
rather than quietly treating "close enough" as "confirmed," because the difference matters: DC01's
actual configured timezone was never captured, so this is a strong read of two data points, not a
closed one.

**`EvaluationEndDate: 12/31/1600 4:00:00 PM` looks like data and isn't.** It's a zero `FILETIME`
(the Windows epoch, shifted by whatever local offset the conversion used) — a null sentinel, not
an actual date. I nearly used it to answer "when did the eval end" before recognizing the pattern;
worth naming so it doesn't get cited as a real date later.

## What I'd do differently

Should have captured DC01's configured timezone (`Get-TimeZone`) in the same round-trip as this
query — it's a single added line, it would have closed the InstallDate question exactly instead of
within a band, and it would let the hourly-restart hypothesis below be timed precisely instead of
bracketed between two candidate offsets.

## Addendum, same day: root cause confirmed by DC01's own event log

While this report was open, DC01 crashed — `qm guest exec` returned `VM 100 is not running`.
Host-side, the signature matched `2026-08-31-dc01-unexpected-shutdown` exactly: `qmeventd: read:
Connection reset by peer` at 09:27:58 local, `100.scope` reporting a 9.7G memory peak and 120.3M
swap peak on the way down, no OOM-kill message, no split-lock trap in the window. A `pvedaemon`
`root@pam` auth line at 09:27:13 (45 seconds before) is **not explained by Raymond** — confirmed
with him directly that he had not touched the Proxmox web dashboard, only the terminal, this
session. Left open rather than assumed benign.

Rather than stack another correlation onto the three unresolved candidates from 08-31 (thin-pool
pressure, memory ceiling, split-lock), DC01 was restarted and its own System event log pulled for
the shutdown-tracker event IDs (`1074`, `6006`, `6008`, `41`, `1076`) — evidence 08-31's
investigation never had access to, since that exercise reasoned entirely from host-side logs.

**It answers the question directly.** Event 1074, 9/2/2026 9:27:52 AM: *"The process
C:\Windows\system32\wlms\wlms.exe (DC01) has initiated the shutdown of computer DC01 on behalf of
user NT AUTHORITY\SYSTEM for the following reason: Other (Planned) ... Comment: The license period
for this installation of Windows has expired. The operating system is shutting down."* Six seconds
before the host logged the crash signature. `wlms.exe` is Windows' evaluation-license enforcement
component; `Shutdown Type: shutdown` means a full power-off, not a reboot — which is also why
DC01 stayed stopped this time instead of coming back under a new PID the way it apparently did on
08-31.

The same message appears repeatedly further back in the log, at irregular intervals — 8/31
4:52:35 PM, 6:13:11 PM, 10:50:23 PM; 9/1 8:03:20 AM, 9:03:49 AM, 11:05:44 AM, 5:29:54 PM — not a
clean fixed timer (gaps range from ~60 minutes to over 16 hours), but always the same process,
same reason, same comment. **8/31 4:52:35 PM sits seven seconds before the exact timestamp
(16:52:42) that `2026-08-31-dc01-unexpected-shutdown/report.md` logged as its "occurrence 2"** —
the report that explicitly stated its root cause "could not be pinned down." That report's own
candidates (thin-pool pressure, DC01's memory ceiling) were real correlations, honestly reported
as unconfirmed; this evidence, unavailable to that investigation at the time, is the more direct
explanation for at least that occurrence. **Not editing that report** — closed reports in this
repo are historical record — but the connection belongs on the record here, in `verified-claims.md`,
and in `EXPOSURES.md`.

**What this doesn't explain, and stays open:** a shutdown at **1:46:15 PM on 9/1** was flagged by
Windows itself as *unexpected* on the next boot (Event 41 + 6008 at 11:29 PM that night) — no
`wlms.exe` entry appears near it in this capture. That is a genuinely different event, still
unaccounted for, and a candidate for the same qemu-level mechanism 08-31 went looking for and
didn't find. And whether the **original** occurrence 1 (8/31, 09:38:11) was also `wlms.exe`-driven
could not be checked — the query only returned 20 events and doesn't reach back that far; a wider
or time-bounded query would settle it but wasn't run this round.

## Open questions

- **Whether the 8/31 09:38:11 crash (occurrence 1) was also `wlms.exe`-driven.** Not reachable
  with a 20-event query; needs a `-FilterHashtable` bounded by `StartTime`/`EndTime`, or a much
  larger `MaxEvents`, to check.
- **The 9/1 1:46:15 PM unexpected shutdown.** No `wlms.exe` entry near it — does not fit the
  pattern established above and is the strongest remaining candidate for a genuine host/qemu-level
  crash independent of the license issue.
- **The unexplained `pvedaemon` `root@pam` auth at 09:27:13, 45 seconds before today's crash.**
  Confirmed not Raymond via the dashboard. Not yet checked against `pveproxy`'s access log for a
  source IP/origin.
- **DC01's configured timezone.** Still never captured — moot for the root-cause question now that
  the event log gives exact guest-local timestamps directly, but still open for the earlier
  InstallDate-vs-ISO-date one-day gap.
- **The decision this forced: decided and applied, same day.** See addendum below.

## Second addendum, same day: rearmed

Checked `RemainingWindowsReArmCount` via CIM first (6 available — a plain read, no `slmgr`
needed). Ran `slmgr /rearm` through an explicit `cscript //NoLogo //B` invocation rather than the
bare command: `slmgr.vbs` is the same VBScript that makes `/dlv` hang `qm guest exec` when it
falls through to the default `wscript` (GUI) host, so the console host was forced explicitly
instead of testing whether `/rearm` happens to dodge that on its own. Clean exit, no hang.

Rearm requires a restart to take effect — deliberate here, not the crash pattern, worth keeping
distinct in the record. Post-restart: `LicenseStatus` moved from `5` (Notification/expired) to `2`
(OOB Grace); `GracePeriodRemaining` **14400 minutes — exactly 10 days**, not a reset of the full
180-day evaluation window; `RemainingWindowsReArmCount` now `5`. `EvaluationEndDate` still reads
the same null-`FILETIME` sentinel as before rearm — now confirmed across two different license
states, so this looks like a field that never populates for this SKU/channel at all, not just a
Notification-state artifact.

**What this actually bought:** roughly 10 days before DC01 is back in Notification state and the
`wlms.exe` shutdown cycle resumes, and 5 rearms left — call it ~50 more days of runway if stretched
to the limit, not a permanent fix. Worth a calendar reminder around **2026-09-12** to rearm again
or make the longer-term call (real activation key, or rebuild) before it lapses back.
