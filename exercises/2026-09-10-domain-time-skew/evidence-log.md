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

## Not captured, and why

- **DC01's monotonic clock rate.** `[Environment]::TickCount64` returned no output and no
  `err-data`. The 0.517 ratio in finding 20 is unexplained and untested.
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

- **`references/gotchas.md` states that `certutil -view` prints dates in UTC. Finding 33 disproves
  it.** That line also describes a seven-to-eight-hour discrepancy between `certutil` and
  `Get-ChildItem` in one evidence file on 2026-09-05. That discrepancy is the size of this lab's
  clock skew, which was not known when the line was written. The line is corrected in
  `references/gotchas.md` with the retraction stated there, not by silent edit.

## Open questions

- Does Entra CBA reject a certificate whose `NotBefore` is seven hours in the future? That is the
  lab's stated goal for this CA and the first consumer that does not share the wrong clock.
- Which repository claims carry a guest-derived timestamp, and are any of them wrong?
- Does DC01's monotonic clock run at about half of real time, and does `ostype: l26` cause it?
- What corrected DC01 by exactly −7h on 2026-09-05, and why has nothing done so since?
- What is the correct time design for a virtualised forest root with no internet route, and what
  does each alternative cost? The candidates are: fix `ostype` and `localtime` on VM 100, point the
  PDC emulator at the Proxmox host as an NTP server, or give the lab network a route to an external
  source. Each has a different failure mode and a different blast radius.
- How would a defender recognise this before a consumer rejects a certificate? CA01 logged `Id 50`
  three times on 9/10 and DC01 logged `Id 134` six times, and nothing acted on either.
- Does the domain's Kerberos remaining healthy make this harder to detect, not easier?

## Not started

- The `TickCount64` test on DC01.
- The repository timestamp audit.
- Any remediation. Every candidate fix is a state change on the domain controller and waits for
  Raymond.
- The alternatives half of the exercise: the correct time design and its cost.
