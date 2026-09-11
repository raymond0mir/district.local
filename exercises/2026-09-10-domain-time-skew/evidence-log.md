# Domain time skew — evidence log

Opened 2026-09-10 from finding 26 of `exercises/2026-09-10-privileged-access-path-audit`, which
observed that DC01's wall clock does not match the Proxmox host's and did not measure the
difference. The hypothesis: the difference is a real clock error rather than a timezone or a
rendering artefact, DC01 is its own authority for it, and the error reaches Kerberos and
certificate validity.

This is a separate exercise, not a continuation of the audit, because it answers a different
hypothesis. The audit asked what the administrative path records. This asks whether the timestamps
in those records mean anything.

## Captured

- **The host, DC01 and CA01 clocks, timezones and time sources, read inside one three-second host
  window at 2026-09-10T21:39:42Z.**
  `evidence/01-three-clocks-disagree-and-dc01-answers-to-nothing.md`. Both guest calls exit code 0.

**1. The skew is not a timezone.** The host reports `America/Los_Angeles (PDT, -0700)`. DC01 and
CA01 both report `Pacific Standard Time` and both stamp `-07:00` in the ISO-8601 output. All three
machines agree on the offset they apply. Finding 26's statement that timezone does not explain the
difference is confirmed by direct reads rather than by inference from a non-hourly interval.

**2. Three clocks hold three different times, and the spread is over seven hours.** Converted to
UTC: host 2026-09-10T21:39:42Z, DC01 2026-09-11T02:45:53.7Z, CA01 2026-09-11T04:39:45.5Z. DC01 is
5h 06m 10.7s ahead of the host. CA01 is 7h 00m 00.5s ahead of the host, and 1h 53m 51.8s ahead of
DC01. The host is NTP-synchronised (`System clock synchronized: yes`, `NTP service: active`) and is
treated here as the reference.

**3. DC01's time source is its own virtual CMOS clock, and it announces itself as stratum 1.**
`Source: Local CMOS Clock`, `ReferenceId: 0x4C4F434C (source name: "LOCL")`,
`Stratum: 1 (primary reference - syncd by radio clock)`, `Root Dispersion: 10.0000000s`. The domain
controller answers to no external time authority. Its `Last Successful Sync Time` is
`9/9/2026 2:19:52 PM`, over a day before the read, which is consistent with a source that is never
polled over a network.

**4. CA01 does poll DC01, and reports a successful sync 63 seconds before the read, while sitting
1h 53m 51.8s away from it.** `Source: DC01.district.local`, `Stratum: 2`,
`ReferenceId: 0x0A00000A (source IP: 10.0.0.10)`, `Last Successful Sync Time: 9/10/2026 9:38:42 PM`
against a local read of 9:39:45 PM. A successful poll and an uncorrected two-hour difference cannot
both be true unless the correction is being refused. The reason is not captured. See Not captured.

**5. CA01's local wall time equals the host's UTC to within one second, and its error is the
timezone offset exactly.** CA01 reads 21:39:45.5 local while the host reads 21:39:45 UTC, and
CA01's error against the host is 7h 00m 00.5s where the host's UTC offset is exactly -07:00. A
clock whose error equals its own timezone offset is the signature of a base set once from a UTC
value and then treated as local time. This is a candidate cause, not a captured one. CA01's rate is
sound: it matched the host to the second across the read.

**6. DC01's offset is not constant, and finding 26's inference is disproven.** Against the audit's
two earlier readings, DC01 was +4h 35m 43s from the host at both 18:18:48Z and 18:25:15Z, and is
+5h 06m 10.7s at 21:39:43Z. DC01 gained 1827.7 seconds across 11668 seconds of host time between
the second and third readings. Inside the earlier seven-minute window the two clocks kept pace to
within one second, so the gain is not a uniform rate applied over the whole period. Either the
drift is intermittent or the clock was stepped. **Neither is captured, and two offset measurements
do not establish a rate.** Do not carry a drift figure forward as a rate.

- **The virtual machine clock configuration on the host, both guests' Time Service configuration,
  CA01's own measurement of its offset to DC01, and CA01's Time-Service event messages, at
  2026-09-10T21:45:53Z.** `evidence/02-the-configuration-and-the-refusal-mechanism.md`. Both guest
  calls exit code 0.

**7. DC01 is a Windows Server 2022 domain controller running with `ostype: l26`.** The host is told
this guest is Linux 2.6 or newer. The same config carries `name: winserver2022`, `bios: ovmf` and
`machine: q35`, and it sets `localtime: 0`. CA01, built later, carries `ostype: win11` and no
`localtime` line. The two virtual machines are given different clock treatment by the host, and the
domain controller has the wrong one.

**8. `localtime: 0` puts DC01's emulated real time clock in UTC, and Windows reads a real time
clock as local time.** That combination produces a base error equal to the timezone offset exactly,
which is 7h 00m 00s here. This is a candidate cause for DC01's base and it is not tested. Testing
it means restarting DC01 and reading the clock immediately, which is a state change.

**9. DC01 is configured to poll `time.windows.com` and is not doing so.** `Type: NTP`,
`NtpServer: time.windows.com`, `NtpClient Enabled: 1`, `InputProvider: 1`. `w32tm /query /source` in
`evidence/01` returns `Local CMOS Clock`. The configured external source is unreachable and w32time
has fallen back to the local clock. Six `Id 134` warnings appear on 9/8 and 9/9 and none on 9/10.
Their message text was not requested, so the reason for the failure is not captured.

**10. DC01 holds the PDC emulator role, and this is now Captured.** `(Get-ADDomain).PDCEmulator`
returns `DC01.district.local`. `AnnounceFlags: 5` is consistent with it: DC01 announces itself as a
reliable time source. CA01 carries `AnnounceFlags: 10`. The forest root role that is supposed to
anchor domain time is held by the machine whose clock answers to nothing.

**11. CA01's refusal to correct is not a phase-correction limit.** `MaxNegPhaseCorrection` and
`MaxPosPhaseCorrection` are both `4294967295`, which is the unlimited value. A 6829-second
correction is inside those limits. The hypothesis that a correction cap explains finding 4 is
disproven.

**12. The refusal is spike detection, and the event says so in full.** Two `Id 50` warnings on
9/10, at 4:31:49 PM and 6:15:01 PM local: "The time service detected a time difference of greater
than 5000 milliseconds for 900 seconds... The time service is no longer synchronized and cannot
provide the time to other clients or update the system clock." `LargePhaseOffset` is 50000000, which
is 5 seconds, and `SpikeWatchPeriod` is 900 seconds. CA01 receives valid time from DC01, classifies
it as an implausible spike, and stops applying it. **`Last Successful Sync Time` in finding 4 counts
a valid response received, not a clock corrected.** That is the whole of the contradiction, and it
is a designed behaviour rather than a fault.

**13. CA01 last corrected its clock on 9/9 at 2:35:10 PM local, and inherited DC01's time when it
did.** `Id 35`: "The time service is now synchronizing the system time with the time source
DC01.district.local ... with reference id 167772170", which is `0x0A00000A`, 10.0.0.10. CA01 booted
9/9 at 2:19:41 PM local. Its clock has free-run since the 2:35 PM sync.

**14. CA01 measures its own offset to DC01 and confirms the arithmetic in `evidence/01`.**
`w32tm /stripchart` returns `-6829.4511649s` and `-6829.4512051s` on two samples two seconds apart.
That is 1h 53m 49.45s, against 1h 53m 51.8s computed independently in `evidence/01` from two
`Get-Date` reads six minutes earlier. The two samples differ by 40 microseconds, so DC01 and CA01
are running at nearly the same rate at this moment.

**15. A third offset reading shows DC01 tracking the host's rate, so the earlier gain was not a
steady drift.** Derived from the stripchart, DC01 read 19:52:07.5 local at host 21:45:56.5Z, an
offset of +5h 06m 11.0s against +5h 06m 10.7s six minutes earlier. DC01 elapsed 6m 13.8s across
6m 13.5s of host time. **Finding 6 recorded a gain of 1827.7 s across 11668 s of host time. A rate
that large would have shown here as roughly 28 seconds and it did not.** DC01's clock is unstable
in rate. No single rate describes it, and none is written down.

**16. Both guests enable `VMICTimeProvider` as an input provider.** That provider is the Hyper-V
integration time source. The host is KVM. Neither guest has a working host time reference through
it, and DC01's `ostype: l26` removes the hypervisor enlightenments that would otherwise be offered.
Whether either machine has any working host clock reference is not captured.

- **Host uptime for both guests, DC01's peer state and Time-Service message text, and CA01's
  Kerberos, secure channel, LDAP and certificate-database state, at 2026-09-10T21:53:12Z.**
  `evidence/03-kerberos-survives-and-the-boot-offset-is-exact.md`. Both guest calls exit code 0.

**17. Both guests booted at the same instant, 2026-09-09T14:19:31Z.** Host uptime 113621 s and
113620 s at 21:53:12Z. This gives every guest event a real anchor for the first time.

**18. DC01's base error at boot was 7h 00m 00s, exactly the timezone offset, and finding 8's
prediction is confirmed without restarting anything.** Its `Id 143` event, "The time service has
started advertising as a good time source", is stamped 2:19:52 PM local, 21 seconds after the real
boot. DC01's local clock read 14:19:52 when real UTC was 14:19:52. `localtime: 0` puts the emulated
real time clock in UTC, Windows reads it as local, and the machine starts exactly one timezone
offset ahead. **The state change that finding 8 said this test needed is not needed.**

**19. DC01 has lost 1h 53m 49s since boot.** From +7h 00m 00s at 2026-09-09T14:19:31Z to
+5h 06m 11.0s at 2026-09-10T21:45:56.5Z, across 113,545 s. The loss is not steady: finding 6
measured a gain of 1827.7 s inside that period and finding 15 measured near-perfect tracking. The
net is a loss and the instantaneous rate is whatever it happens to be.

**20. DC01's uptime does not reconcile with the host's, and CA01's does.** CA01's `LastBootUpTime`
minus its own clock matches the host's uptime to 6 seconds. DC01's implies an uptime of 58,767 s
against the host's 113,621 s, a ratio of 0.517, and it is also 13h 20m 27s later than the machine's
own boot in its own frame. Elapsed-time accounting on DC01 is wrong as well as the wall clock. The
mechanism is not captured. `ostype: l26` remains a candidate for both and is not established.

**21. DC01 cannot resolve its configured time source, and the message says so.** `Id 134`:
"NtpClient was unable to set a manual peer to use as a time source because of DNS resolution error
on 'time.windows.com'", errors `0x80072AF9` "No such host is known" and `0x80072AFA`.
`w32tm /query /peers` shows one peer, `time.windows.com`, `State: Pending`, `Stratum: 0`. The lab
network has no DNS path to the internet. Finding 9's open question is closed.

**22. Kerberos survives a 6829-second skew.** `klist get host/DC01.district.local` returns "A ticket
to host/DC01.district.local has been retrieved successfully." Six tickets are cached, all
AES-256-CTS-HMAC-SHA1-96, all with `Kdc Called: DC01.district.local`. **The prediction that a
6829-second difference would break authentication is disproven.**

**23. The tickets carry the KDC's clock, and that is why it works.** The TGT's `Start Time` is
9/10/2026 19:59:26 local, on a client whose own clock read 21:53:15.96 in the same command. DC01
read 19:59:24.99 in the same block. Both machines report the same timezone, so this is not a
rendering difference. The client adopted the KDC's time for the exchange. **The five-minute
tolerance is checked against the KDC's clock, not against real time, so a domain whose KDC is
wrong stays internally consistent and authenticates normally.** Every ticket lifetime in the domain
is therefore expressed in DC01's wrong time.

**24. The secure channel is healthy.** `nltest /sc_verify:district.local` returns
`Trusted DC Connection Status Status = 0 0x0 NERR_Success` and
`Trust Verification Status = 0 0x0 NERR_Success`, with `Flags: b0 HAS_IP HAS_TIMESERV`.

**25. The LDAP read still succeeds, so the 2026-09-06 row is not retired.**
`([ADSI]"LDAP://DC01.district.local/rootDSE").ldapServiceName` returns
`district.local:dc01$@DISTRICT.LOCAL`. Claude predicted this call might now fail and it did not.

**26. Four cached tickets are expired in both frames.** Tickets 1, 3, 4 and 5 carry
`End Time: 9/10/2026 13:12:40 (local)` against a client clock of 21:53 and a KDC clock of 19:59.
Not investigated.

**27. Eight of the nine certificate rows were stamped before CA01's clock moved, and the ninth
cannot be placed.** Row 5's `NotBefore` of 9/8 2:24 PM matches the independently Confirmed issuance
of request 5 at 2026-09-08T14:34Z, less the ten-minute backdating a Windows CA applies, which
establishes that `certutil -view` prints UTC here and that CA01's clock was correct on 9/8. Row 8's
`NotAfter` of 9/9 8:08 PM matches the host `date -u` reading of 2026-09-09T20:08:49Z in
`exercises/2026-09-05-adcs-issuing-ca-build/evidence/54-pki-cba-pilot-gates-enrollment-non-member-denied.txt`
for the request that produced it, which puts CA01's clock
correct as late as 20:08Z on 9/9. Row 9, stamped 9/9 10:10 PM, is the only row that could fall
after the move. **No certificate is shown to be post-dated, and none is shown not to be.**

- **Event 4616 on both guests, CA01's full Time-Service event list, and the disposition and dates
  of requests 8 and 9, at 2026-09-10T22:02:31Z.**
  `evidence/04-event-4616-dates-every-step-and-certutil-prints-local.md`. Both guest calls exit
  code 0.

**28. CA01's move is dated to the second, and finding 27's open question is closed.** Event `4616`
steps CA01 from 2026-09-09T14:35:10.509Z to 2026-09-09T21:35:10.902Z, a jump of +7h 00m 00.393s, by
`svchost.exe` running as `LOCAL SERVICE`. The host puts CA01's boot at 2026-09-09T14:19:31Z, so
14:35:10.5Z is real time and the step landed at boot plus 15m 39s. **CA01 boots correct and is moved
to DC01's base inside sixteen minutes, every boot.**

**29. DC01 has not been stepped since 2026-09-07, so its loss is drift.** Its newest `4616` is
9/7 6:49:19 AM local. Between the 2026-09-09T14:19:31Z boot at +7h 00m 00s and +5h 06m 11.9s now,
no process wrote to that clock. Finding 19's loss and finding 6's gain are both free-running
behaviour of the virtual clock.

**30. DC01's `4616` history shows the same pattern twice more.** A step of −7h 00m 00s on 9/5, from
2026-09-06T04:45:00.144Z to 2026-09-05T21:45:00.969Z, and two large forward steps on 9/6 and 9/7.
The −7h step is the size of the base error. Something corrected DC01 once and nothing has since.

**31. Fourth offset reading. Both clocks are stable across nine minutes.** DC01 +5h 06m 11.9s at
host 22:02:32Z; CA01 +7h 00m 00.0s at 22:02:35Z.

**32. CA01 chased DC01 twice on 9/10 and gave up.** `4616` records a step of −2h 24m 16.15s at
3:51:01 PM local and a step of +2h 24m 16.97s at 6:57:10 PM local, net zero. `Id 50` fired three
times on 9/10, the newest at 10:02:18 PM local, seventeen seconds before this capture. **The refusal
is live, not historical.**

**33. `certutil -view` prints local time, not UTC, and the standing gotcha is wrong.** Request 8 was
submitted inside the command block recorded in
`exercises/2026-09-05-adcs-issuing-ca-build/evidence/54-pki-cba-pilot-gates-enrollment-non-member-denied.txt`,
which carries its own host reading `Timestamp: 2026-09-09T20:08:49Z`. CA01 was at +7h from
14:35:10Z that day, so its UTC read 2026-09-10T03:08:49Z and its local read 9/9 8:08 PM. `certutil`
printed `Request Submission Date: 9/9/2026 8:08 PM`. The local value matches; the UTC value does
not.

**34. Request 9 is Issued, and its certificate is post-dated by seven hours.** `Request Disposition:
0x14 (20) -- Issued`, resolved at CA01 local 9/9 10:20 PM, which is real 2026-09-09T22:20Z. The
`NotBefore` written into the certificate is CA01's own UTC value for local 10:10 PM, which is
2026-09-10T05:10Z. **A relying party with a correct clock would have rejected that certificate as
not yet valid for the next seven hours.**

**35. The same applies to every certificate CA01 issued while it was at +7h, and that includes the
CBA pilot certificates.** Findings 28 and 33 place CA01 at +7h across 9/8 and from 14:35:10Z on 9/9.
Rows 5, 7, 8 and 9 fall inside those windows. The absolute validity windows in those certificates
are seven hours ahead of the real times at which they were issued.

**36. Entra certificate-based authentication is validated against Microsoft's clock, not this
domain's.** That is the lab's stated goal for this CA, and it is the first consumer that does not
share the wrong clock. No test has been run; the exposure is stated, not measured.

**37. Request 8 is `Denied by Policy Module` and still carries `NotBefore` and `NotAfter`.** The
policy module computes a validity window before the denial. This is why finding 27 could use a
denied request as a timeline anchor.

**38. DC01's clock was accurate 69 seconds before an independent host anchor, closing part of the
"what corrected DC01 on 9/5" gap.** `CA01 joined the domain` on 9/5 wrote `Created`
`/Date(1788645440000)/` onto the new `CN=CA01,CN=Computers,DC=district,DC=local` object, an AD
FILETIME-backed attribute that DC01 itself timestamps, not a `certutil` local-time display. Decoded
as an epoch, that value is 2026-09-05T21:57:20Z. The same capture's host `date -u` line reads
2026-09-05T21:58:29Z, 69 seconds later. This is DC01's directory clock, not a guest console
display, and it agrees with the host to the minute, consistent with finding 30's correction of
DC01 twelve minutes earlier the same evening (2026-09-05T21:45:00.969Z). It narrows, without
closing, finding 30's open question: DC01 was correct by 21:57Z on 9/5, not only immediately after
the step. `exercises/2026-09-05-adcs-issuing-ca-build/evidence/10-ca01-joined-and-adcs-role-installed.txt`.

**39. Request 5's own disposition record shows CA01 already displaying the +7h signature on 9/8, a
full calendar day before finding 28's dated onset.** The same capture block that resolved request 5
carries both a host `date -u` line, `2026-09-08T14:34:27Z`, and CA01's own
`certutil -view` output, `Request Resolution Date: 9/8/2026 2:34 PM`. `2:34 PM` is `14:34`, the same
hour and minute as the real UTC anchor taken in the same command batch — the identical
local-digits-equal-real-UTC pattern findings 33 and 34 established for requests 8 and 9. Applying
that pattern here means CA01's local clock was already missing its `-07:00` offset on 9/8, not only
from the 2026-09-09T14:35:10Z step event finding 28 dates. `exercises/2026-09-05-adcs-issuing-ca-build/evidence/47-console-installcert-succeeds-and-request-5-issues.txt`.

**40. This exercise's own durable artifacts already carry the corrected, full scope.**
`report.md` ("Requests 5, 7 and 8 fall inside the same windows"), the ledger row dated 2026-09-10
("Rows 5, 7, 8 and 9 all fall inside windows where CA01 was at +7h"), and `EXPOSURES.md`'s
domain-time-skew paragraph ("requests 5, 7 and 8 fall inside the same windows") all match finding 35.
Direct read of all three, 2026-09-10. No correction is owed to any of them. The stale framing is
confined to finding 27 below, inside this file.

**41. The GPO exercise's guest timestamps predate the skew, and new evidence proves it rather than
assumes it.** The same-day `2026-09-02-dc01-eval-license-status` exercise recorded nine
`wlms.exe`-driven reboots of DC01 between 8/31 4:52 PM and 9/2 9:27 AM, all full power-offs. DC01's
local clock advances smoothly across every one, with no seven-hour jump anywhere in the sequence.
Its 8/31 4:52:35 PM event sits seven seconds from an independent host-side reading of the same
crash, 16:52:42, in
`exercises/2026-08-31-dc01-unexpected-shutdown/evidence/second-occurrence-crash-signature.txt`. Its
`gpresult /r` read on 9/2, "Last time Group Policy was applied: 9/2/2026 at 9:58:07 AM," is
consistent with the same session's host capture at 17:00:27Z. **DC01's clock was accurate through
at least 2026-09-02, across repeated reboots.**
`exercises/2026-09-02-a2-gpo-surface-and-domain-root-link/evidence/gpo-origin-timestamps-and-full-reports-20260902T1656Z.txt`,
`exercises/2026-09-02-a2-gpo-surface-and-domain-root-link/evidence/gpresult-and-secedit-verified-20260902T1700Z.txt`,
`exercises/2026-09-02-dc01-eval-license-status/evidence/system-eventlog-1074-6006-6008-41-1076-20260902T1644Z.txt`.

**42. `report.md`'s claim that VM 100 "has carried the wrong value since it was created" is wrong,
and VM 100's own config narrows the real question instead of closing it.**
`exercises/2026-08-31-member-server-build/evidence/dc01-hardware-config-baseline.txt` shows
`ostype: l26` and `localtime: 0` already present on 8/31, with Proxmox's own
`meta: ctime=1759192209` dating VM 100's creation to 2025-09-30T00:30:09Z, a host-written value.
The misconfiguration was present for at least the eleven months before this reading. Finding 41
shows DC01's clock was accurate through 2026-09-02 despite it. **The configuration causes the
error. The configuration's presence does not explain when the error started.**

**43. The likely trigger is a lost DNS route to `time.windows.com`, not the boot-time defect alone,
and this is a candidate, not a capture.** DC01 polls `time.windows.com` and cannot resolve it
(findings 9, 21). A working resolution would let `w32tm` correct the `localtime: 0` boot error
within moments of every boot, which fits finding 41's smooth, reboot-heavy record showing no defect
through 9/2. The −7h correction at 2026-09-05T21:45:00.969Z (finding 30) is the last recorded
correction anywhere in DC01's `4616` history. The `Id 134` DNS-failure entries captured in this
exercise (`evidence/02`) come from a `-MaxEvents 10` query and reach back only to
2026-09-08T22:53Z. **They do not establish when DC01 lost the route, only that it was already lost
by then.** Whether DC01 could resolve `time.windows.com` before 2026-09-05, and what changed, is
not captured.

**44. The GPO, licence-status, and B1/B4/PIM exercises named in carryover as owed carry no claim
this skew touches.** Each is checked against the same test: does a claim depend on a DC01- or
CA01-printed timestamp read at a moment this exercise has not shown the guest clock to be accurate.
`2026-09-04-b1-conditional-access-report-only`'s one DC01 read returns a null
`AccountExpirationDate`; its device-registration dates are Microsoft Graph timestamps, stamped by
Entra, not by either guest. `2026-09-04-b1-security-defaults-and-ca-report-only` and
`2026-09-05-b1-security-defaults-transition` make no DC01 or CA01 read.
`2026-09-05-b1-breakglass-exclusion-verification` reads DC01 three times for state, not for a date;
its two date fields, `onPremisesLastSyncDateTime` and `lastPasswordChangeDateTime`, are Graph
timestamps. `2026-09-06-b4-pim-eligible-role`'s one guest-timestamp value, `sysadmin`'s
`whenChanged`, decodes to 2026-09-01T00:27:04Z, inside the accurate window finding 41 establishes;
every PIM `startDateTime`/`endDateTime` in this exercise is a Graph timestamp.
`2026-09-09-pim-for-groups` touches DC01 only for `qm status`, not a guest clock read.
`2026-09-10-pim-policy-authoring` makes no DC01 or CA01 read at all. **No correction is owed to any
of these seven exercises.** The GPO and licence-status exercises are covered by finding 41.

**45. `[Environment]::TickCount64` produces zero output on DC01 with exit code 0, isolated and
error-handled, and the cause is not identified.** Command: `date -u; qm status 100 --verbose |
grep uptime; qm guest exec 100 --timeout 30 -- powershell.exe -NonInteractive -Command 'try {
Write-Output ([Environment]::TickCount64) } catch { Write-Output ("ERROR: " +
$_.Exception.Message) }'; date -u`. Host: proxmox. UTC: 2026-09-11T01:28:57Z, returned
2026-09-11T01:28:59Z. Host uptime for VM 100: 126566 s. The guest agent call returned
`{"exitcode": 0, "exited": 1}` with no `out-data` key and no `err-data` key at all — not an empty
string, an absent field. Exit 0 rules out a PowerShell parse or runtime error reaching the process
exit code; the `try`/`catch` printing nothing rules out a caught .NET exception with a message.
**The command produced no output on either stream while still exiting cleanly, and this is now
reproduced once bundled (finding from evidence/04) and once isolated.** Not identified: whether
`qm guest exec`'s own capture drops a bare numeric pipeline result, whether the PowerShell version
on DC01 lacks `TickCount64` in a way that fails before entering the `try` block, or some other
mechanism.

**Isolated further, same session.** Command: `qm guest exec 100 --timeout 30 -- powershell.exe
-NonInteractive -Command 'Write-Output "hello"; $PSVersionTable.PSVersion.ToString();
[Environment]::TickCount64'`. UTC 2026-09-11T01:30:48Z. `out-data`: `"hello\r\n5.1.20348.4163\r\n"`.
`Write-Output "hello"` and the bare expression `$PSVersionTable.PSVersion.ToString()` both printed.
`[Environment]::TickCount64`, third and last, printed nothing, and the exec still exited 0. DC01
runs Windows PowerShell 5.1.20348.4163. **The exec path and bare-expression output both work. The
failure is specific to `[Environment]::TickCount64` itself, not to how it is called or where it
sits in the script.**

**46. `[Environment]::TickCount64` returns null without throwing on DC01, and `TickCount` is the
working substitute.** Command: `qm guest exec 100 --timeout 30 -- powershell.exe -NonInteractive
-Command 'try { $a = [Environment]::TickCount; $b = [Environment]::TickCount64; "TickCount=" + $a
+ " TickCount64=" + $b } catch { "CAUGHT: " + $_.Exception.GetType().FullName + " -- " +
$_.Exception.Message }'`. UTC 2026-09-11T01:33:28Z. `out-data`:
`"TickCount=71981500 TickCount64=\r\n"`. The assignment to `$b` did not throw — no `CAUGHT:` prefix
appears — and `$b` stringifies to nothing, which in PowerShell string concatenation means `$b` is
`$null`. `TickCount`, the older Int32 member, returned a real value. **`TickCount64` is present and
does not error; it returns nothing usable, on Windows PowerShell 5.1.20348.4163.** The cause is not
identified and is not pursued further. `TickCount` wraps at 24.9 days; DC01's uptime is far short
of that, so the substitute is safe here.

**47. DC01's own hardware timer is running slow, not only its wall clock, and this confirms finding
20 by an independent method.** `TickCount` reads 71981500 ms (71981.5 s) at 2026-09-11T01:33:28Z.
The host's own uptime reading for VM 100, 126566 s at 2026-09-11T01:28:57Z (finding 45), carries
forward to 126837 s at this reading, 4m31s later, with no reboot in between. The ratio is 0.5675.
Finding 20's `LastBootUpTime`-derived ratio, from the same boot, was 0.5171. **The two independent
measurements agree on the shape — DC01 believes roughly half the real time has passed since it
booted — and disagree on the exact number, which rules out a single constant rate and confirms this
is the guest's own sense of elapsed time, not an artefact of wall-clock corrections.** `TickCount`
is a hardware-timer-backed counter that `w32tm` never touches. A domain controller can lose ticks,
not only lose sync.

**48. A first paired reading of host scheduling pressure and DC01's tick rate shows a near-real-time
marginal rate during a near-zero-pressure interval.** Command: `date -u; cat /proc/loadavg; free -h;
qm status 100 --verbose | grep -E 'uptime|cpu'; qm guest exec 100 --timeout 30 -- powershell.exe
-NonInteractive -Command "[Environment]::TickCount"; date -u`. Host: proxmox. UTC:
2026-09-11T01:43:37Z to 01:43:39Z. `loadavg`: `0.21 0.14 0.10`. `free -h`: 2.1Gi free, 3.2Gi
available of 15Gi, swap unused. `qm status 100 --verbose`: `pressurecpufull: 0`, `pressurecpusome:
0`, `uptime: 127446`. Guest exec exit code 0: `TickCount` = 72591078 ms = 72591.078 s.

Cumulative ratio since boot: 72591.078 / 127446 = 0.5696, in line with findings 20 and 47 (0.517,
0.5675). **The marginal rate against finding 47's reading is the new result.** Finding 47 read
71981.5 s of `TickCount` at a real elapsed time of 126837 s. Between that reading and this one, real
elapsed time advanced 609 s and `TickCount` advanced 609.578 s — a marginal ratio of 1.00095,
indistinguishable from parity given integer-second precision on `uptime`. **DC01 ticked at
essentially the real-time rate over this specific ten-minute interval, and the interval's host
pressure readings are at or near zero** (`loadavg` 0.21, `pressurecpufull` and `pressurecpusome`
both 0). This is one data point, not a correlation: it is consistent with the host-scheduling-
pressure hypothesis (no pressure, no loss) and does not rule out an unidentified intermittent cause
unrelated to pressure. It does not by itself distinguish the two, because no reading yet pairs a
tick measurement with a period of measured host pressure above zero.

**The semantics of `pressurecpufull` and `pressurecpusome` are not confirmed.** Whether they are an
instantaneous PSI reading, a short-window average, or something else is not established from this
capture alone. Reading `/proc/pressure/cpu` and `/proc/pressure/memory` directly on the host would
give `avg10`/`avg60`/`avg300` and a cumulative `total=` stall figure, which bounds pressure over a
longer window than a single instant and does not require waiting for a future high-load period to
be informative.

**49. A second paired reading, three minutes later, confirms near-parity marginal tick rate and
gives the host's own PSI totals for the first time.** Command as finding 48, with `cat
/proc/pressure/cpu` and `cat /proc/pressure/memory` added before `free -h`. Host: proxmox. UTC:
2026-09-11T01:46:51Z to 01:46:53Z. `loadavg`: `0.16 0.13 0.09`. `/proc/pressure/cpu`: `some avg10=0.00
avg60=0.00 avg300=0.00 total=89661560`; `full avg10=0.00 avg60=0.00 avg300=0.00 total=0`.
`/proc/pressure/memory`: `some ... total=147630`; `full ... total=147195`. `qm status 100 --verbose`:
`uptime: 127639`. Guest exec exit code 0: `TickCount` = 72784781 ms = 72784.781 s.

Marginal rate against finding 48: real elapsed 193 s (127639 − 127446), `TickCount` elapsed 193.703 s
— ratio 1.00364, again indistinguishable from parity at this precision. **Two consecutive marginal
readings, three minutes apart, both near 1.0, both during measured `avg10`/`avg60`/`avg300` CPU and
memory pressure of exactly zero.** The host's cumulative CPU `full` stall total is 0 microseconds
since the host's own boot — every non-idle task has never simultaneously stalled on this host, at
any point this counter has been running. The cumulative `some` CPU stall total is 89,661,560
microseconds, about 89.7 s; small on its face, but with no host-boot-time anchor captured, its
proportion of host lifetime is not established here.

**Where this leaves the two hypotheses.** Every reading so far — this one, finding 48, and finding
15's six-minute wall-clock window in the earlier part of this exercise — shows DC01 tracking real
time closely whenever host pressure reads at or near zero. No reading has yet caught DC01 mid-loss
next to a nonzero pressure reading. The cumulative deficit (findings 20, 47: ratios of 0.517 and
0.5675 since boot) is real and unexplained by anything captured in this window; it must have
accumulated in a period this test has not sampled, most plausibly close to boot, when host activity
from bringing up DC01 and CA01 together would have been highest. That period cannot be re-sampled
after the fact. Confirming or disproving the pressure hypothesis now needs either a reading during a
naturally occurring high-pressure window, which this idle host is not producing, or a deliberately
induced one — a state change, and Raymond's decision.

**50. A deliberately induced host CPU load reached DC01's own vCPUs, and the resulting tick-rate
change is suggestive but not distinguishable from measurement noise at this duration.** Raymond chose
to induce load rather than wait or stop. Command: pre-flight (`date -u`, `nproc`, `qm status`, `lvs`,
`free -h`, `/proc/loadavg`, `/proc/pressure/cpu`, `/proc/pressure/memory`), then `for i in $(seq 1
$(nproc)); do timeout 90 yes > /dev/null & done`, then reads at T+20s and T+100s. Host: proxmox.
`nproc` = 8; eight workers, one per core, self-terminated at 90s (all exited `124`, the `timeout`
exit code for a reached limit).

Pre-load (UTC 2026-09-11T01:49:15Z): `loadavg` 0.23/0.17/0.11. `pressurecpusome` (VM100, from `qm
status`) 0. Host `/proc/pressure/cpu` `some` `total=89741692` (89.74 s), `full` `total=0`.

T+20s (UTC 01:49:35-39Z): `loadavg` 2.44/0.68/0.28. **`pressurecpusome` (VM100) reads 0.7, the first
nonzero reading this test has produced for a VM100-specific pressure metric.** Host `/proc/pressure/
cpu` `some avg10=0.40`, `total=90007236` (a rise of 265,544 µs, 0.266 s, in about 20-24 s). This is
the manipulation check, and it passes: the induced load reached DC01's own vCPUs, not only the host
in general.

T+100s (UTC 01:50:59-01:51:01Z, about 10 s after the workers exited): `loadavg` 5.09/2.18/0.85, still
rising, an expected lag in the load-average's own trailing window. `pressurecpusome` (VM100) 0.21,
decaying. Host `/proc/pressure/cpu` `total=91448019`, a further rise of 1,440,783 µs (1.44 s) across
the 84 s since the T+20s reading. Total cpu-`some` stall across the whole ~105 s window (pre-load to
T+100s): 1,706,327 µs, about 1.7 s, roughly 1.6% of wall time. `full` stayed at `total=0` throughout:
no moment of complete starvation was produced. Memory pressure totals did not move at all across the
test (`147630`/`147195` unchanged) — `yes` costs no memory, and none was expected.

**The tick-rate segments.** `TickCount` was read at the T+20s and T+100s points only; the nearest
prior reading is finding 49 (UTC 01:46:53Z, `TickCount` 72784.781 s, `uptime` 127639 s). Finding
49-to-T+20s spans 166 s of real elapsed time, of which about 144 s were idle (before this test's
pre-load reading) and about 22 s were under load: ratio 166.281/166 = 1.00169, parity, as expected
for an idle-dominated segment. **T+20s-to-T+100s spans 83 s, of which roughly 70 s were under load
and 13 s were post-load cooldown: ratio 81.938/83 = 0.98721, the first sub-parity marginal reading
this test has produced.**

**This is suggestive, not confirmed.** `uptime` is reported in whole seconds; two readings bracketing
an 83 s segment carry a combined rounding uncertainty of roughly ±1-2 s, which is 1.2%-2.4% of the
segment — as large as or larger than the observed 1.28% deviation. The two earlier, longer segments
(finding 48's 609 s and finding 49's 193 s) carry proportionally much smaller rounding uncertainty
(0.16% and 0.5%), which is why their near-parity readings are reliable in a way this one is not. **A
sub-parity reading appearing for the first time in the one segment that was mostly under induced
load is consistent with the host-scheduling-pressure hypothesis. It cannot yet be told apart from
integer-rounding noise at this segment length.** The induced pressure itself was also modest — eight
workers on eight cores produced measurable but not severe contention (`some` avg10 peaking at 0.40%,
`pressurecpusome` at 0.7), not the sustained starvation a worker count exceeding the core count would
produce.

**51. A harder, longer induced load reached full starvation on DC01's own vCPUs for the first time,
but a bracket design flaw leaves the tick-rate ratio unresolved.** Raymond ran the requested
follow-up: 16 workers (2x `nproc`) against 8 host cores, `timeout 290 yes > /dev/null` each, against
finding 50's 8-on-8. Command: pre-flight (`date -u`, `nproc`, `qm status`, `lvs`, `free -h`,
`/proc/loadavg`, `/proc/pressure/cpu`, `/proc/pressure/memory`), `TickCount` at T0, the load launch,
a T+30s manipulation check, a T+280s end-of-load reading, and a T+340s cooldown reading. Host:
proxmox.

Pre-load (UTC 2026-09-11T14:07:26-28Z): `pressurecpusome` (VM100) 0, `pressurecpufull` 0, `uptime`
172075. Host `/proc/pressure/cpu` `some total=120329397` (120.33 s), `full total=0`. `TickCount` =
117220312 ms = 117220.312 s, read between 14:07:27Z and 14:07:28Z, exit code 0.

T+30s (UTC 14:07:58Z): **`pressurecpusome` (VM100) reads 0.88, and host-wide `some avg10` reads
80.15%** — against finding 50's 0.7 and 0.40% for the same check at half the worker count. The
manipulation check passes far more decisively than finding 50's.

T+280s (UTC 14:12:11-17Z): **`pressurecpufull` (VM100) reads 0.14, the first nonzero full-stall
reading this exercise has produced for VM100.** DC01's vCPUs were completely starved for part of
this window, not only contended. `pressurecpusome` reads 2.11. `uptime` 172362. `TickCount` =
117509250 ms = 117509.250 s, exit code 0. Host `/proc/pressure/cpu some total=351570445` — a rise
of 231,241,048 microsec (231.24 s) since pre-load, over roughly 285-291 s of wall time: **79-81% of
the load window carried measurable host CPU contention**, against finding 50's 1.6%.

Cooldown (UTC 14:13:17Z, all 16 workers confirmed self-terminated at exit code 124): `some
total=352446069`, a rise of only 875,624 microsec across about 60-66 s — contention ended with the
workers. Memory pressure totals are unchanged from findings 48-49 (`147633`/`147198`) throughout:
`yes` costs no memory, confirmed again at this scale.

**The tick-rate bracket itself is flawed, and the flaw is mine.** T0's `TickCount` call sat alone
between two `date -u` calls, a 1 s window, the method findings 48-50 used. T+280's did not: the
command placed `qm status`, the `TickCount` call, and two more `cat` reads between its opening and
closing `date -u`, so the 6 s span between 14:12:11Z and 14:12:17Z brackets three operations, not
one, and nothing isolates when inside that span the guest-exec call landed.

`TickCount` elapsed exactly 288.938 s. Real elapsed, from the `date -u` brackets alone, ranges from
283 s (latest possible T0, earliest possible T+280) to 290 s (earliest T0, latest T+280). **Ratio
range: 0.996 to 1.021 — straddling parity in both directions.** This is a wider span than finding
50's already-inconclusive 1.2%-2.4% rounding bound, despite 3.5 times the duration and roughly 50
times the measured host contention (`some avg10` 80% against 0.40%). A load this hard should have
produced a clear reading either way. The non-resolution is a measurement failure, not a null result.

**52. The corrected bracket narrowed the ratio range but did not resolve it, because the
measurement tool's own latency grows under the load it is measuring.** Raymond re-ran the same
16-worker, 290 s load with `TickCount` isolated alone between its own `date -u` calls at both ends,
every other read moved outside both brackets. Host: proxmox.

Pre-load (UTC 2026-09-11T14:28:55-58Z, idle): `pressurecpusome`/`pressurecpufull` (VM100) both 0,
`uptime` 173366. Host `/proc/pressure/cpu some total=353028462`. `TickCount` = 118509875 ms =
118509.875 s, exit code 0. **The bracket around this call — nothing else inside it, same as
findings 48-50 — still spanned 2 s** (14:28:56Z to 14:28:58Z), under zero measured host pressure.

T+30s (UTC 14:29:28Z, exactly 30 s after load start): `pressurecpusome` 1.02, `pressurecpufull` 0,
`uptime` 173399. Host `some avg10=76.38`, `total=379335306` — a rise of 26,306,844 microsec
(26.31 s) in 30 s, about 88% of wall time under contention, a faster ramp than finding 51's.

End-of-load (UTC 14:33:40-44Z, isolated bracket): `TickCount` = 118796250 ms = 118796.250 s, exit
code 0, the only command between the two `date -u` calls. **The bracket still spanned 4 s** — half
of finding 51's 6 s, but not the 1-2 s findings 48-50 and this same test's own idle T0 bracket
achieved. The context reads taken immediately after, outside the bracket: `pressurecpufull` 0,
`pressurecpusome` 1.88, `uptime` 173655, host `some avg10=78.92`, `total=584492871` — a rise of
205,157,565 microsec (205.16 s) since T+30, sustaining roughly 80% contention through the window.
All 16 workers self-terminated at exit code 124 about 4 s after this reading, confirming the read
landed inside the load period, not after it.

Cooldown (UTC 14:34:47Z): `some total=585474172`, a rise of only 981,301 microsec across about
63 s — contention ended with the load. Whole-window accounting, preflight to end-of-load context
read: 231,467,560 microsec of `some` stall across 289 s of wall time, 80.1%, matching finding 51's
81% and confirming the load was reproduced at the same intensity.

**The comparison that matters: the identical single-call bracket took 2 s under 0% host pressure
and 4 s under 78-79% host pressure.** `qm guest exec`'s own round trip slows under the load its
result is meant to characterize. This is a confound in the instrument, not in the command
sequence — finding 51's fix (isolate the call) was necessary and reduced the bracket from 6 s to
4 s, but it could not reach the 1-2 s the same tool achieves at idle, because part of that latency
is the tool contending for the same CPU as the workers.

`TickCount` elapsed exactly 286.375 s. Real elapsed ranges from 282 s (latest T0, earliest T+280)
to 288 s (earliest T0, latest T+280). **Ratio range: 0.994 to 1.016** — narrower than finding 51's
0.996-1.021 by about 0.4 percentage points, still straddling parity, still inconclusive.

**Finding 51 predicted that an isolated bracket would let this resolve. It has not, twice now,
with two different bracket designs.** The remaining lever is proportion, not bracket precision: a
bracket of a given size matters less the longer the segment it brackets. A 900 s (15-minute)
segment at this load's intensity would put even a generous 10 s combined bracket uncertainty at
about 1.1%, likely enough to separate a real tick-loss effect from noise if one exists at this
severity. Worker count and load intensity are not the lever left to pull; duration is.

**53. Stretching the segment to 900 s resolved the question, and the answer disfavours the
host-pressure hypothesis.** Same 16-worker load, same isolated bracket. Host: proxmox.

Pre-load (UTC 2026-09-11T14:42:49-51Z, idle): `pressurecpusome`/`pressurecpufull` (VM100) both 0,
`uptime` 174200. `TickCount` = 119343484 ms = 119343.484 s, bracketed by `date -u` at 14:42:50Z
and 14:42:51Z — **1 s window**, the tightest this exercise has produced, idle.

T+30s (UTC 14:43:22Z, exactly 30 s after load start): `pressurecpusome` 2.17, `uptime` 174232.
Host `some avg10=79.48`, a rise of 26,521,185 microsec (26.52 s) in 30 s — about 88% of wall time
under contention, matching findings 51-52's ramp.

End-of-load (UTC 14:57:04-08Z, isolated bracket, 850 s after load start, workers still 44-48 s
from their 900 s cutoff): `TickCount` = 120200515 ms = 120200.515 s, the only command between the
two `date -u` calls. **The bracket spanned 4 s**, the same width finding 52's identical call held
under the same load — confirms the 4 s figure is a property of the load level, not a one-off.
Context reads immediately after: `pressurecpufull` 0.01, `pressurecpusome` 1.99, `uptime` 175060,
host `some avg10=78.39 avg60=79.00 avg300=76.05`, `total=1274642409` (1274.642 s) — a rise of
662,344,195 microsec (662.34 s) since T+30 across about 826 s, roughly 80.2% of wall time under
contention, sustained at the same intensity as findings 51-52 for three times as long. All 16
workers self-terminated at exit code 124 shortly after, confirmed at the cooldown read.

Cooldown (UTC 14:58:41Z): `some total=1307422356`, `avg10` already down to 0.67 — contention ended
with the load, `avg60`/`avg300` still elevated as expected from their own trailing windows.
Memory pressure totals unchanged throughout (`147633`/`147198`).

**The computation.** `TickCount` elapsed exactly 857.031 s. Real elapsed, from the `date -u`
brackets alone, ranges from 853 s (latest T0, earliest T+850) to 858 s (earliest T0, latest
T+850). **Ratio range: 0.9989 to 1.0047 — a 0.6-percentage-point span, against finding 52's 2.2
points and finding 51's 2.5, for the same absolute bracket slack spread over three times the
duration, exactly as predicted.** The range brackets parity tightly and does not reach finding
50's original 0.987 reading by a wide margin.

**Sustained, heavy host CPU contention — about 80% for 900 s, far past anything a one-time VM
boot would produce — does not reproduce a detectable tick-rate loss on DC01.** Every marginal-rate
reading taken after boot in this exercise — findings 15, 48, 49, and now 51-53 — is
indistinguishable from parity once its own bracket noise is accounted for. Finding 50's 83 s
sub-parity reading, the only one that ever pointed the other way, sat entirely inside a rounding
bound wide enough to produce it by chance. **The cumulative deficit (findings 20, 47: DC01 has run
at 0.517-0.5696 of real time since boot) is real, confirmed by two independent methods, and this
exercise has never been able to reproduce any of it as an ongoing rate, under conditions ranging
from idle to heavier contention than boot itself would plausibly generate.** The loss is
concentrated at or near boot, not continuous — consistent with findings 41-43's separate
conclusion that DC01's clock was accurate for months before the skew began, and with a one-time
clocksource miscalibration under `ostype: l26` during DC01's and CA01's simultaneous bring-up,
rather than an ongoing hypervisor-scheduling effect.

## Not captured, and why

- **Whether DC01 could resolve `time.windows.com` before 2026-09-05, and what changed.** See
  finding 43. Answering it needs the lab network's own history, not a repository read.

- **Why `[Environment]::TickCount64` returns null instead of a value or an exception on DC01.**
  Findings 45-46. Not pursued: `TickCount` is a working substitute and answers the rate question
  (finding 47). The rate itself, and whether `ostype: l26` or host scheduling pressure causes it,
  is tracked in Open questions, not here.
- **What corrected DC01 by −7h 00m 00s on 2026-09-05.** The `4616` record states the step and not
  the source.
- **Why CA01 stepped forward by 2h 24m on 9/10 to a value seven hours ahead of real time, rather
  than to DC01's time.** The record holds the numbers. The source is not identified.
- **Whether Entra CBA rejects a certificate from this CA.** Finding 36 is stated from the design of
  certificate validation, not from a test in this lab.
- **Which repository claims carry a guest-derived timestamp.** Findings 33 and 35 make this an
  audit that is now owed. Not started.
- **Whether `certutil -view` ever prints UTC.** Finding 33 disproves the standing rule for this
  capture. It does not establish what the rule should be for other verbs.

## Where Raymond was consulted

- 2026-09-10. He ran the clock and time-source sequence named as the session's next safe action and
  pasted all four outputs back. No decision was handed to him in this thread.
- 2026-09-11. Asked how to test the host-scheduling-pressure hypothesis once two idle readings
  (findings 48-49) produced no contrast case: take a third idle reading, induce synthetic load, or
  stop and write up as inconclusive. He chose to induce load. Reason not stated beyond the choice
  itself.
- 2026-09-11. After finding 50's induced-load test came back noise-bound rather than conclusive, and
  a stronger follow-up test (more workers than cores, minutes rather than under 90 s) was proposed,
  he said "lets stop wait till next session." Default for the next session: run the stronger test
  named above, using the same paired-reading method as findings 48-50.
- 2026-09-11, next session. He ran the stronger induced-load sequence named above and pasted the
  full output back. No decision was handed to him in this thread; finding 51 is the result.
- 2026-09-11, same session. He ran the corrected, isolated-bracket sequence immediately after
  finding 51, with no separate ask. No decision was handed to him in this thread; finding 52 is
  the result.
- 2026-09-11, same session. After finding 52, offered a choice: run the 900 s version now, or
  stop for the session. He said "run it now and lets wrap this task." Finding 53 is the result,
  and closes this exercise's tick-rate sub-question.

## Corrections

- **Finding 26 of the privileged-access-path audit stated that DC01's offset from the host is
  constant. That is wrong, and finding 6 above disproves it.** The audit inferred constancy from
  three invocations inside a seven-minute window, where the two clocks did in fact keep pace. The
  inference did not hold over three hours. The audit's evidence log and report are corrected on the
  record rather than edited silently, per `CLAUDE.md`.

- **Claude proposed in session that CA01's error was a base set from a UTC value and treated as
  local time, because that error equals CA01's timezone offset almost exactly. Finding 13 does not
  support it.** CA01 corrected its clock from DC01 on 9/9 at 2:35:10 PM and has free-run since, so
  its base is inherited from DC01 and not read from a real time clock. The near-exact seven hours is
  the sum of DC01's own offset and the 6829 s that has opened up since, not a timezone artefact.
  The mechanism is still worth testing, on DC01 rather than CA01, where `localtime: 0` makes it a
  live candidate. Stated before being asked.

- **Finding 13 said CA01 "inherited DC01's time" at its 2026-09-09 2:35:10 PM sync and has
  "free-run since". Finding 27 does not support either half.** Real anchors put CA01's clock
  correct at 2026-09-09T20:08Z, hours after that event, so the event did not move it and it has not
  free-run since. The `Id 35` event records a source selection, not a correction. When CA01 moved
  is now an open question rather than a finding.

- **Claude predicted that the certificates CA01 has already issued carry validity windows hours in
  the future. Finding 27 does not support it.** Eight of nine rows are anchored to a correct clock.
  One row is unresolved. The forward risk is unchanged: anything CA01 issues now is stamped seven
  hours ahead of real UTC.

- **Claude predicted that a 6829-second skew would break Kerberos between CA01 and DC01, and that
  the LDAP read behind the 2026-09-06 ledger row would now fail. Findings 22, 24 and 25 disprove
  both.** Authentication is healthy. The reason is finding 23, and it is a better result than the
  prediction: the tolerance is measured against the KDC's own clock.

- **Claude's correction in the previous turn was itself wrong, and is withdrawn.** That entry said
  the prediction of post-dated certificates was "not supported", on the reasoning that row 8's dates
  put CA01's clock correct at 20:08Z on 9/9. Findings 28 and 33 show the opposite: CA01 was at +7h
  from 14:35:10Z that day, and `certutil -view` prints local time, so row 8's "8:08 PM" is CA01's
  local reading of a real 20:08:49Z. **The original prediction holds.** The sequence was: predicted
  correctly, retracted wrongly, reinstated on evidence. All three steps are on the record here
  because the middle one reached the ledger and `EXPOSURES.md` before it was caught.

- **Finding 27's "CA01's clock was correct on 9/8" and "correct as late as 20:08Z on 9/9" are
  superseded, and its "no certificate is shown to be post-dated" is wrong.** Finding 27 read the
  local-digits-equal-real-UTC pattern in rows 5 and 8 as proof of an accurate clock. Findings 33 and
  34, reading the same pattern in row 8, reach the opposite conclusion: the match is the signature of
  the +7h error, not evidence against it. Finding 35 already corrects the scope to "rows 5, 7, 8 and
  9 all fall inside windows where CA01 was at +7h," and finding 39 above independently confirms the
  error was present as early as request 5's resolution. Finding 27 was never marked superseded at
  the point finding 35 passed it, and the Corrections-section entry above ("Eight of nine rows are
  anchored to a correct clock") restates finding 27's framing without flagging it. `report.md`,
  `EXPOSURES.md` and `verified-claims.md` were checked 2026-09-10 and already carry finding 35's
  scope; this correction is confined to finding 27 and the Corrections entry in this file.

- **`references/gotchas.md` states that `certutil -view` prints dates in UTC. Finding 33 disproves
  it.** That line also describes a seven-to-eight-hour discrepancy between `certutil` and
  `Get-ChildItem` in one evidence file on 2026-09-05. That discrepancy is the size of this lab's
  clock skew, which was not known when the line was written. The line is corrected in
  `references/gotchas.md` with the retraction stated there, not by silent edit.

- **`report.md`'s "What I'd do differently" said VM 100 "has carried the wrong value since it was
  created in October 2025." Finding 41 disproves it.** DC01's clock matched an independent host
  reading to seven seconds on 8/31 and behaved consistently through 9/2, across nine reboots that
  each should have shown the boot-time defect if it were live. The configuration was present by
  then (finding 42); the error was not. `report.md` is corrected below to state the narrower,
  supported claim.

- **Findings 45-50 sat under "Not captured, and why" instead of "Captured", every command and
  reading in them notwithstanding.** Moved into "Captured" this session, in place, no content
  changed. The section that held them kept only its two genuinely uncaptured items throughout.

- **Claude's own bracket design in finding 51 is a defect, stated here as well as in the finding
  itself.** The T+280 `TickCount` read sat behind two extra `cat` reads before its closing `date
  -u`, widening that endpoint's real-elapsed uncertainty from `date -u`'s usual 1 s to 6 s and
  producing a ratio range, 0.996-1.021, that resolves nothing despite the hardest load and longest
  duration this exercise has run. Findings 48-50 bracketed the guest-exec call alone; finding 51
  did not. Stated before being asked. The fix: bracket `TickCount` alone at both ends of a segment,
  and move every other read outside the bracket.

- **The fix named above was necessary and insufficient, and the claim that it would resolve the
  ratio is corrected by finding 52.** Isolating the T+280 `TickCount` call cut its bracket from 6 s
  to 4 s, not to the 1-2 s findings 48-50 and finding 52's own idle T0 bracket achieved. Finding 52
  shows why: the same single-call bracket took 2 s under 0% host pressure and 4 s under 78-79%
  pressure. Part of `qm guest exec`'s round-trip latency is itself load-dependent, so no bracket
  design removes all of the slack from a reading taken during the load it measures. Duration, not
  bracket precision, is the remaining lever.

## Open questions

- Does Entra CBA reject a certificate whose `NotBefore` is seven hours in the future? That is the
  lab's stated goal for this CA and the first consumer that does not share the wrong clock.
- **Answered, 2026-09-10.** The repository timestamp audit is complete for every exercise named in
  carryover. `2026-09-05-adcs-issuing-ca-build` was audited first: its report, ledger rows and
  `EXPOSURES.md` entry already carried the corrected scope (findings 38-40); only this file's own
  finding 27 was stale, corrected above. `2026-09-02-a2-gpo-surface-and-domain-root-link` and
  `2026-09-02-dc01-eval-license-status` are audited and clean, on new evidence rather than
  inference (finding 41). `2026-09-04-b1-conditional-access-report-only`,
  `2026-09-04-b1-security-defaults-and-ca-report-only`, `2026-09-05-b1-security-defaults-transition`,
  `2026-09-05-b1-breakglass-exclusion-verification`, `2026-09-06-b4-pim-eligible-role`,
  `2026-09-09-pim-for-groups` and `2026-09-10-pim-policy-authoring` are audited and clean (finding
  44). No exercise outside `2026-09-05-adcs-issuing-ca-build` needs a correction.
- What changed DC01's route to `time.windows.com` between 2026-09-02 and 2026-09-05, and does
  restoring DNS resolution make `w32tm` self-correct the boot error on every future boot? Findings
  41-43 make this the live mechanism question, ahead of the drift-rate and PDC-emulator-source
  questions below.
- **Answered in part, 2026-09-11.** DC01's monotonic clock does run at about half of real time —
  findings 20 and 47 measure 0.517 and 0.5675 independently, by different methods, on the same
  boot. Whether `ostype: l26` causes it is still open: it is a plausible mechanism (a Linux-typed
  guest may not receive the paravirtualized clocksource a Windows guest expects), but it is not
  tested against the alternative that host CPU or memory pressure is stealing ticks — finding 15
  already showed DC01 tracking the host almost exactly over a six-minute window, which a constant
  hypervisor-clocksource defect would not produce. **Three paired readings exist, 2026-09-11
  (findings 48-50): two idle-dominated segments at parity (1.00095, 1.00169), and one segment mostly
  under a deliberately induced eight-core CPU load, sub-parity for the first time (0.98721).** The
  induced load is confirmed to reach DC01's own vCPUs (`pressurecpusome` 0→0.7). The sub-parity
  reading is consistent with the host-pressure hypothesis and cannot yet be told apart from
  integer-second rounding noise, because the load segment (83 s) is short enough that the rounding
  bound (1.2%-2.4%) covers the observed deviation (1.28%). Neither hypothesis is confirmed or
  disproven.
- **Retested with a harder load, 2026-09-11 (finding 51), still not confirmed or disproven, for a
  different reason.** 16 workers against 8 cores drove host `some` CPU pressure to 79-81% of the
  289 s load window and produced the first nonzero `pressurecpufull` reading this exercise has
  seen for VM100 — real starvation, not only contention, far past finding 50's 1.6%. The tick-rate
  bracket itself was flawed: an extra pair of reads between the `TickCount` call and its closing
  `date -u` widened that endpoint's timing uncertainty to 6 s, and the resulting ratio range,
  0.996-1.021, straddles parity. A load this hard should have produced a clear reading. The next
  attempt needs a tight bracket, `date -u` immediately before and after `TickCount` alone at both
  segment ends, nothing else between them.
- **Retested with the tight bracket, same session (finding 52), still not confirmed or disproven,
  for a third reason.** Isolating `TickCount` between its own `date -u` calls, with the same
  16-worker load, cut the end-of-load bracket from 6 s to 4 s — but not to the 1-2 s the identical
  call took under zero pressure in this same test's T0 read. `qm guest exec`'s own round trip is
  slower under the load it is measuring, which is a confound in the tool, not the command sequence.
  Ratio range: 0.994-1.016, narrower than finding 51's but still straddling parity. Bracket design
  is now exhausted as a lever; segment duration is not. A 900 s (15-minute) segment at the same
  load intensity would cut a 10 s combined bracket uncertainty to about 1.1% of the window, against
  this attempt's roughly 2.2%.
- **Answered, 2026-09-11 (finding 53), against the host-pressure hypothesis.** The 900 s version
  of the same test narrowed the ratio range to 0.9989-1.0047, a 0.6-percentage-point span, cleanly
  bracketing parity and nowhere near finding 50's original 0.987. About 80% sustained host CPU
  contention for 900 s — far past anything a one-time VM boot would produce — did not reproduce a
  detectable tick loss. Every after-boot reading in this exercise (findings 15, 48, 49, 51-53) is
  parity within its own noise; finding 50's sub-parity reading was inside its own rounding bound
  and did not replicate. The cumulative deficit (findings 20, 47) is real but concentrated at or
  near boot, not an ongoing rate — consistent with `ostype: l26` causing a one-time clocksource
  miscalibration during bring-up rather than a continuous hypervisor-scheduling effect. Not tested:
  whether the boot-time event itself is reproducible; that needs a fresh VM boot, a state change.
- What corrected DC01 by exactly −7h on 2026-09-05, and why has nothing done so since? Finding 43
  narrows this to a DNS or routing change; the change itself is not identified.
- What is the correct time design for a virtualised forest root with no internet route, and what
  does each alternative cost? The candidates are: fix `ostype` and `localtime` on VM 100, point the
  PDC emulator at the Proxmox host as an NTP server, or give the lab network a route to an external
  source. Each has a different failure mode and a different blast radius. Finding 43 favours the
  external-route or host-as-NTP candidates over an `ostype`/`localtime` fix alone, since the
  defect stayed dormant for months while the config was already wrong.
- How would a defender recognise this before a consumer rejects a certificate? CA01 logged `Id 50`
  three times on 9/10 and DC01 logged `Id 134` six times, and nothing acted on either.
- Does the domain's Kerberos remaining healthy make this harder to detect, not easier?

## Not started

- Finding when DC01 lost its DNS route to `time.windows.com` (finding 43). Needs lab network
  history, not a repository read.
- Whether DC01's boot-time clocksource event (findings 41-43, 53) is reproducible. Needs a fresh
  VM boot, a state change, to test directly rather than infer from steady-state behavior.
- Any remediation. Every candidate fix is a state change on the domain controller and waits for
  Raymond.
- The alternatives half of the exercise: the correct time design and its cost.
