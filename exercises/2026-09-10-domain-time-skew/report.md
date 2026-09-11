# Domain time skew

## What I set out to do

A prior exercise noticed that DC01's wall clock did not match the Proxmox host's and did not
measure the difference. The hypothesis for this exercise: that difference is a real clock error
rather than a timezone or a rendering artefact, the domain controller is its own authority for it,
and the error reaches Kerberos and certificate validity. The first two hold. The third holds for
certificates and fails for Kerberos, and the reason it fails is the more useful result.

## The setup

`district.local` on Proxmox VE 9.0.3. VM 100 (DC01), the only domain controller and the PDC
emulator. VM 107 (CA01), the AD CS enterprise issuing CA. The Proxmox host is the reference clock:
`timedatectl` reports `America/Los_Angeles (PDT, -0700)`, `System clock synchronized: yes`,
`NTP service: active`.

The exercise changed no state. Every command is a read. Host uptime at 2026-09-10T22:02:31Z was
114180 s for VM 100 and 114179 s for VM 107, which puts both boots at 2026-09-09T14:19:31Z. That
single number turned every guest log timestamp into something that could be checked.

## What I did

Four read-only sequences, each bracketed by `date -u` on the host so that every guest reading sits
inside a bounded host window.

1. `Get-Date -Format o`, `[System.TimeZoneInfo]::Local.Id`, `w32tm /query /source` and
   `w32tm /query /status` on both guests.
2. `qm config 100` and `qm config 107`; `w32tm /query /configuration` on both;
   `w32tm /stripchart /computer:DC01.district.local /samples:2 /dataonly` from CA01; the
   Time-Service events from CA01's System log with message text.
3. `qm status --verbose` for host-side uptime; `w32tm /query /peers` and the Time-Service message
   text on DC01; `klist get host/DC01.district.local`, an ADSI read of `rootDSE`,
   `nltest /sc_verify:district.local` and `certutil -view` on CA01.
4. Event `4616` on both guests; CA01's full Time-Service event list;
   `certutil -view -restrict "RequestID>=8"` with disposition and submission dates.

## Where Raymond was consulted

- 2026-09-10. He opened the session and ran the clock and time-source sequence that the previous
  session's carryover named as the next safe action. He ran all four sequences and pasted every
  output back.
- No decision was handed to him inside this exercise. Every candidate fix is a state change on the
  domain controller, so remediation was not attempted and is recorded as owed.

## What the box said

Three clocks, three times, read inside one three-second host window:

| Machine | UTC | Offset from host |
| --- | --- | --- |
| proxmox | 2026-09-10T21:39:42Z | reference |
| DC01 | 2026-09-11T02:45:53.7Z | +5h 06m 10.7s |
| CA01 | 2026-09-11T04:39:45.5Z | +7h 00m 00.5s |

All three machines report the same timezone, so timezone explains none of it.

DC01 runs with `ostype: l26` and `localtime: 0`. The host is told a Windows Server 2022 domain
controller is Linux, and its emulated real time clock is set to UTC. Windows reads a real time
clock as local time. DC01's `Id 143` event, "The time service has started advertising as a good
time source", is stamped 2:19:52 PM local, twenty-one seconds after a real boot at 14:19:31Z. Its
base error at boot was 7h 00m 00s, the timezone offset exactly.

DC01 takes its time from `Local CMOS Clock` at `Stratum: 1` while configured to poll
`time.windows.com`. `Id 134` says why: "unable to set a manual peer ... because of DNS resolution
error", `0x80072AF9`, "No such host is known". The lab network has no route to it.

CA01 sees the difference and refuses to apply it. Its phase-correction limits are `4294967295`, so
nothing is capping the correction. `Id 50`, three times on 2026-09-10: "The time service detected a
time difference of greater than 5000 milliseconds for 900 seconds ... The time service is no longer
synchronized and cannot provide the time to other clients or update the system clock." The newest
of the three fired seventeen seconds before the capture that read it.

Kerberos works anyway:

```
A ticket to host/DC01.district.local has been retrieved successfully.
#0>     Client: ca01$ @ DISTRICT.LOCAL
        Server: krbtgt/DISTRICT.LOCAL @ DISTRICT.LOCAL
        Start Time: 9/10/2026 19:59:26 (local)
```

The client's own clock read 21:53:15.96 in the same command. DC01 read 19:59:24.99 in the same
block.

## What broke, and why

**Kerberos did not break, and that is the finding.** The ticket carries the KDC's clock. The
five-minute tolerance is measured against the KDC, not against real time, so a domain whose KDC is
internally consistent and externally wrong authenticates normally. `nltest /sc_verify` returns
`NERR_Success`, and the LDAP read behind an earlier ledger row still succeeds. Every ticket lifetime
in this domain is expressed in a clock that is five hours wrong, and nothing inside the domain can
tell.

**The certificates did break.** Request 9 is `Issued`, resolved at real 2026-09-09T22:20Z, with a
`NotBefore` written into the certificate of 2026-09-10T05:10Z. A relying party with a correct clock
would reject it as not yet valid for seven hours. Requests 5, 7 and 8 fall inside the same windows.
Nothing in the domain noticed, because every validator shares the wrong clock. Entra
certificate-based authentication, which is the stated goal for this CA, does not.

**An earlier exercise saw the symptom and wrote down the wrong cause.** `references/gotchas.md`
carried the rule "`certutil -view` prints dates in UTC", written to explain a seven-to-eight-hour
discrepancy between two readings in one evidence file on 2026-09-05. That discrepancy is this
skew. `certutil -view` prints local time. Request 8's `Request Submission Date` of `9/9/2026
8:08 PM` is CA01's local reading of a real 2026-09-09T20:08:49Z, anchored to that same exercise's
own host `date -u`. A plausible explanation closed the question and the real defect stayed open for
five days.

**The mechanism is a two-machine loop, and both halves are misconfigured independently.** DC01 boots
seven hours ahead because of `localtime: 0`. CA01 boots correct, finds the PDC emulator, and is
stepped to DC01's base inside sixteen minutes; event `4616` dates that step at boot plus 15m 39s and
sizes it at +7h 00m 00.393s. DC01 then drifts, with no clock-change event since 2026-09-07, losing
1h 53m 49s in one period and gaining 1827.7 s inside another. CA01 chases it, twice by 2h 24m on
2026-09-10, then declares the source implausible and holds. The two machines end up more than an
hour and a half apart while both remain inside a domain that reports itself healthy.

**Detection existed and nobody was listening.** CA01 logged `Id 50` three times. DC01 logged
`Id 134` six times. Both are the correct warnings, in the correct log, with accurate text. Kerberos
staying healthy is what made them easy to ignore.

## What I'd do differently

Take the clock reading first, not on the fourth day. This lab has produced certificate work, PKI
chain work and a privileged-access audit, all of which used guest timestamps, and the skew predates
all of them.

Anchor a claim to `date -u` before writing a rule that explains a discrepancy away. The retracted
`certutil` gotcha was written from two guest readings with no host reading between them. The same
anchor that disproved it five days later was already sitting in that exercise's own evidence file.

Read `qm config` when building a Windows guest. `ostype` is not cosmetic. It decides what clock the
hypervisor offers. **Corrected, 2026-09-10: VM 100 has carried the wrong `ostype` and `localtime`
value since at least 2026-08-31, but not the wrong clock.** DC01's own event log, read for a
different exercise, shows its clock accurate across nine reboots between 8/31 and 9/2. The
misconfiguration was dormant for months and started producing a real error only between 9/2 and
9/5, most likely when DC01 lost DNS resolution to `time.windows.com` and could no longer correct
the boot-time defect on its own. See `evidence-log.md`, findings 41-43.

State a prediction before running the test, and keep it when it is wrong. Three predictions failed
here — Kerberos breaking, the LDAP read failing, and, in the middle of the exercise, a retraction of
a correct prediction about the certificates. That middle error reached the ledger and
`EXPOSURES.md` before evidence reversed it. All three are recorded in the evidence log.

## Open questions

- Does Entra CBA reject a certificate whose `NotBefore` is seven hours in the future? That is the
  first consumer that does not share this domain's clock.
- **Answered, 2026-09-10.** The repository timestamp audit is complete for the GPO, licence-status,
  and B1/B4/PIM exercises named in carryover, plus the ADCS build audited earlier. None carries a
  claim this skew touches. See `evidence-log.md`, findings 41, 44.
- What changed DC01's route to `time.windows.com` between 2026-09-02 and 2026-09-05? DC01's clock
  was accurate through 9/2 despite already carrying the `ostype`/`localtime` misconfiguration; a
  lost DNS route, not the misconfiguration alone, is the leading candidate for why the error started
  when it did. See `evidence-log.md`, findings 41-43.
- **Answered in part, 2026-09-11.** Yes: `[Environment]::TickCount`, a hardware-timer counter
  `w32tm` never touches, reads 0.5675 of real elapsed time since boot, against 0.517 from
  `LastBootUpTime` on the same boot. The two disagree with each other, ruling out a constant rate,
  and agree DC01 loses ticks, not only sync. `TickCount64` itself returns null without error on
  this PowerShell build; `TickCount` is the working substitute. Still open: whether `ostype: l26`
  or host scheduling pressure causes the loss. See `evidence-log.md`, findings 45-47.
- **Tested against induced load, 2026-09-11, inconclusive.** Three paired readings of host pressure
  and DC01's `TickCount`: two idle segments at parity, one segment mostly under a deliberately
  induced eight-core CPU load, sub-parity for the first time (ratio 0.98721). The load is confirmed
  to reach DC01's own vCPUs (`pressurecpusome` 0→0.7), but the load segment is short enough (83 s)
  that integer-second rounding on `uptime` bounds the noise at 1.2%-2.4%, as large as the observed
  1.28% deviation. Neither hypothesis is confirmed or disproven. A longer, more intense induced load
  (more workers than cores, minutes rather than under 90 s) is the next test, not yet run. See
  `evidence-log.md`, findings 48-50.
- What corrected DC01 by exactly −7h on 2026-09-05, and why has nothing done so since?
- What is the correct time design here? The candidates are fixing `ostype` and `localtime` on
  VM 100, pointing the PDC emulator at the Proxmox host as an NTP source, or giving the lab network
  a route to an external source. Each has a different blast radius, and all three are state changes
  on the domain controller. The dormant-for-months pattern favours the network-route or
  host-as-NTP candidates over the `ostype`/`localtime` fix alone.
- Does a domain whose Kerberos stays healthy make this class of fault harder to detect, not easier?
