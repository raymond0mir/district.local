# Evidence log — DC01 evaluation license status

Single-capture exercise, run and logged 2026-09-02.

## Captured

1. `evidence/os-and-licensing-status-20260902T1626Z.txt` — `Win32_OperatingSystem` and
   `SoftwareLicensingProduct` (`PartialProductKey IS NOT NULL`) via `qm guest exec` from the
   Proxmox host shell, 2026-09-02T16:26:33Z.

## Derived from the capture (arithmetic and cross-reference only, no new observation)

**The eval-media inference is confirmed, not contradicted.** `EXPOSURES.md` and
`exercises/2026-09-02-thin-pool-headroom-reclaim/report.md` both flagged "DC01 may be running on
expired evaluation media" as inference from two matching dates (`SERVER_EVAL_x64FRE_en-us.iso`
and the `clean-install` snapshot, both 2025-09-29) — explicitly not a capture. `InstallDate` reads
9/30/2025 12:36:49 AM, one calendar day later. That is not a disagreement: this project already
documented (`CARRYOVER.md`, "Convention change adopted today") that the host runs
America/Los_Angeles and guest/host clock comparisons have produced exactly this kind of one-day
offset before. `LicenseStatus: 5` (Notification/expired, per the status table already in
`CARRYOVER.md`) and `GracePeriodRemaining: 0` independently confirm DC01 is past its evaluation
window — Windows' own licensing state agrees with the inference regardless of the InstallDate
rounding. Windows Server 2022 evaluation runs 180 days; 2025-09-29 + 180 days lands around
2026-03-28, over five months before this capture, consistent with full grace exhaustion.

**`EvaluationEndDate: 12/31/1600 4:00:00 PM` is a null-sentinel, not data.** This is the classic
rendering of a zero `FILETIME` (the Windows epoch, 1601-01-01 UTC, shifted into whatever local
offset the conversion used) — `SoftwareLicensingProduct` does not carry a populated
`EvaluationEndDate` for a TIMEBASED_EVAL product once past Notification state. It does not tell us
when the eval technically expired and should not be read as though it does.

**pid 4624 is closed.** The hang that produced it happened during
`exercises/2026-09-02-entra-connect-upn-signin-test` (see that exercise's report.md), earlier the
same lab-day and before A1. `LastBootUpTime: 9/2/2026 8:27:36 AM` is a reboot that postdates that
hang, so whatever was orphaned did not survive it. `CARRYOVER.md`'s open item asking whether pid
4624 was ever terminated is answered: yes, by a reboot neither Raymond nor I triggered.

**New, not previously flagged: DC01 may be in the automatic hourly-restart mode.** DC01's
configured timezone was never captured, so the exact gap between `LastBootUpTime` and this
capture can't be pinned precisely — but under either candidate zone already in play for this host
(PDT -0700 or PST -0800), the reboot lands between roughly 1 minute and roughly 1 hour before the
16:26:33Z capture. Nobody restarted DC01 as part of A1 or this capture. A Windows Server
evaluation past its notification grace (`LicenseStatus: 5`, `GracePeriodRemaining: 0`) is
documented Microsoft behavior to begin forcing an automatic restart roughly every hour. One boot
timestamp is consistent with that but does not prove a recurring cycle by itself — a second
capture of just `LastBootUpTime`, taken later, would either show another reboot at the expected
interval (confirms the cycle) or show the same boot time unchanged (rules it out). Not run yet —
this is a Hypothesis, held to that label pending the follow-up capture.

## Addendum: DC01 crashed mid-exercise, root cause pursued and found

2. `evidence/system-eventlog-1074-6006-6008-41-1076-20260902T1644Z.txt` — `Get-WinEvent` against
   the System log for Event IDs 1074/6006/6008/41/1076, `-MaxEvents 20`, captured 2026-09-02
   after restarting DC01 (which had crashed with the same signature as
   `2026-08-31-dc01-unexpected-shutdown`) and waiting ~30s for the guest agent.

**Confirms the hourly-restart hypothesis was the wrong shape, but the right direction.** Not a
restart, not on a fixed timer — a full `wlms.exe`-initiated **shutdown**, "the license period for
this installation of Windows has expired," at irregular intervals (60 min to 16+ hours apart)
reaching back to at least 8/31 4:52 PM. Retracting the earlier framing on the record rather than
quietly correcting it: this evidence-log's own capture-1 analysis called it "the documented
Microsoft behavior to begin forcing an automatic restart roughly every hour" — that was wrong on
two counts, mechanism (shutdown, not restart) and cadence (irregular, not hourly). The underlying
direction — expired eval license as the driver — was right.

**Directly connects to an exercise closed two days ago.** 8/31 4:52:35 PM in this capture sits
seven seconds before the exact 16:52:42 timestamp that
`exercises/2026-08-31-dc01-unexpected-shutdown/report.md` logged as its unexplained "occurrence
2." That report is not being edited — it's closed, historical record, and its own candidates
(thin-pool pressure, memory ceiling) were honestly reported as unconfirmed rather than as fact.
This is new evidence that report never had access to, filed here and cross-referenced in
`verified-claims.md` and `EXPOSURES.md` instead.

**Does not explain everything.** A 9/1 1:46:15 PM shutdown was flagged by Windows itself as
*unexpected* (not `wlms.exe`-initiated) — a genuinely separate, still-open event. Whether the
*original* 8/31 09:38:11 crash was also `wlms.exe`-driven is unconfirmed; the 20-event query
doesn't reach back that far.

## Not captured

- DC01's configured timezone (`Get-TimeZone` / `tzutil /g`) — never run, in this exercise or any
  prior one. Moot for the root-cause question now that the event log gives exact guest-local
  timestamps directly; still open for the InstallDate-vs-ISO-date one-day gap.
- Whether DC01's eval was ever rearmed (`slmgr /dlv`'s `Remaining Windows rearm count` — not read;
  the `/dlv` command itself is the one explicitly avoided here since it hangs `qm guest exec` via
  its `wscript` GUI host). Largely moot now — `wlms.exe`'s own shutdown message is decisive
  regardless of rearm history.
- A bounded-time or larger `Get-WinEvent` query reaching back to 8/31 09:38:11, to check whether
  occurrence 1 of the 08-31 crash was also `wlms.exe`-driven.
- `pveproxy`'s access log, to identify the source of the unexplained `root@pam` auth at 09:27:13.
