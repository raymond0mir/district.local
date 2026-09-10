# Event 4616 dates every clock step, and certutil prints local time

Command:

```
date -u; qm status 100 --verbose | grep uptime; qm status 107 --verbose | grep uptime
qm guest exec 100 --timeout 60 -- powershell.exe -NonInteractive -Command 'Get-Date -Format o; [Environment]::TickCount64; Get-WinEvent -FilterHashtable @{LogName="Security"; Id=4616} -MaxEvents 6 | Format-List TimeCreated,Message'
qm guest exec 107 --timeout 90 -- powershell.exe -NonInteractive -Command 'Get-Date -Format o; Get-WinEvent -FilterHashtable @{LogName="System"; ProviderName="Microsoft-Windows-Time-Service"} -MaxEvents 30 | Format-Table TimeCreated,Id -AutoSize; Get-WinEvent -FilterHashtable @{LogName="Security"; Id=4616} -MaxEvents 6 | Format-List TimeCreated,Message; certutil -view -restrict "RequestID>=8" -out "RequestID,Disposition,DispositionMessage,SubmittedWhen,ResolvedWhen,NotBefore,NotAfter,CommonName"'
date -u
```

Host: proxmox (host shell), executing on DC01 (VM 100) and CA01 (VM 107) through the QEMU guest
agent
UTC: 2026-09-10T22:02:31Z, returned 2026-09-10T22:02:35Z
Exit codes: both guest agent calls reported `"exitcode" : 0`, `"exited" : 1`.

Every `4616` record below is reproduced with its `TimeCreated`, `Previous Time` and `New Time`
verbatim. The `Subject`, `Process Information` and explanatory paragraph are identical in all
twelve records and are stated once instead of repeated. No value is altered. `TimeCreated` is the
guest's own local time. `Previous Time` and `New Time` are in the guest's own UTC frame.

Every record carries: `Security ID: S-1-5-19`, `Account Name: LOCAL SERVICE`,
`Account Domain: NT AUTHORITY`, `Logon ID: 0x3E5`, `Name: C:\Windows\System32\svchost.exe`.
`Process ID` is `0x448` on DC01 and `0x16c` on CA01.

## Host

```
Thu Sep 10 10:02:31 PM UTC 2026
uptime: 114180
uptime: 114179
```

## DC01 (VM 100)

`Get-Date -Format o`:

```
2026-09-10T20:08:43.9371729-07:00
```

`[Environment]::TickCount64` returned no output. No `err-data` field was present.

`4616` records, newest first:

```
TimeCreated : 9/7/2026 6:49:19 AM
Previous Time: ?2026?-?09?-?07T13:49:19.463180200Z
New Time:      ?2026?-?09?-?07T13:49:19.464330400Z

TimeCreated : 9/7/2026 6:49:19 AM
Previous Time: ?2026?-?09?-?06T18:54:54.421420800Z
New Time:      ?2026?-?09?-?07T13:49:19.463180200Z

TimeCreated : 9/6/2026 10:29:17 AM
Previous Time: ?2026?-?09?-?06T17:29:17.985661400Z
New Time:      ?2026?-?09?-?06T17:29:17.999181100Z

TimeCreated : 9/6/2026 10:29:17 AM
Previous Time: ?2026?-?09?-?06T01:35:58.994528400Z
New Time:      ?2026?-?09?-?06T17:29:17.985661400Z

TimeCreated : 9/5/2026 2:45:00 PM
Previous Time: ?2026?-?09?-?05T21:45:00.985228600Z
New Time:      ?2026?-?09?-?05T21:45:00.985945200Z

TimeCreated : 9/5/2026 2:45:00 PM
Previous Time: ?2026?-?09?-?06T04:45:00.144106100Z
New Time:      ?2026?-?09?-?05T21:45:00.969179800Z
```

## CA01 (VM 107)

`Get-Date -Format o`:

```
2026-09-10T22:02:35.0220782-07:00
```

Time-Service events, newest first:

```
TimeCreated            Id
-----------            --
9/10/2026 10:02:18 PM  50
9/10/2026 4:31:49 PM   50
9/10/2026 6:15:01 PM   50
9/9/2026 2:35:10 PM    35
9/9/2026 7:35:01 AM    37
9/9/2026 7:35:01 AM   138
9/9/2026 7:20:00 AM   129
9/9/2026 7:19:59 AM   129
9/8/2026 11:08:56 PM   35
9/8/2026 4:08:46 PM    37
9/8/2026 4:08:46 PM   138
9/8/2026 3:53:46 PM   129
9/8/2026 3:53:45 PM   129
9/8/2026 2:16:30 PM    35
9/8/2026 7:16:20 AM    37
9/8/2026 7:16:20 AM   138
9/8/2026 7:01:20 AM   129
9/8/2026 7:01:19 AM   129
9/7/2026 10:45:10 PM   35
9/7/2026 3:44:56 PM    37
9/7/2026 3:44:55 PM    37
9/7/2026 7:11:46 AM    35
9/7/2026 7:11:32 AM    37
9/7/2026 7:11:30 AM    37
9/7/2026 6:55:55 AM    35
9/7/2026 6:55:41 AM    37
9/7/2026 6:55:40 AM    37
9/7/2026 6:50:05 AM    50
9/7/2026 6:47:51 AM    24
9/7/2026 6:33:17 AM    34
```

`4616` records, newest first:

```
TimeCreated : 9/10/2026 6:57:10 PM
Previous Time: ?2026?-?09?-?11T01:57:10.700474300Z
New Time:      ?2026?-?09?-?11T01:57:10.703130200Z

TimeCreated : 9/10/2026 6:57:10 PM
Previous Time: ?2026?-?09?-?10T23:32:53.728582900Z
New Time:      ?2026?-?09?-?11T01:57:10.700474300Z

TimeCreated : 9/10/2026 3:51:01 PM
Previous Time: ?2026?-?09?-?10T22:51:01.687774000Z
New Time:      ?2026?-?09?-?10T22:51:01.688365400Z

TimeCreated : 9/10/2026 3:51:01 PM
Previous Time: ?2026?-?09?-?11T01:15:17.836144900Z
New Time:      ?2026?-?09?-?10T22:51:01.687774000Z

TimeCreated : 9/9/2026 2:35:10 PM
Previous Time: ?2026?-?09?-?09T21:35:10.902215700Z
New Time:      ?2026?-?09?-?09T21:35:10.903388600Z

TimeCreated : 9/9/2026 2:35:10 PM
Previous Time: ?2026?-?09?-?09T14:35:10.509283500Z
New Time:      ?2026?-?09?-?09T21:35:10.902215700Z
```

`certutil -view -restrict "RequestID>=8"`:

```
Schema:
  Column Name                   Localized Name                Type    MaxLength
  ----------------------------  ----------------------------  ------  ---------
  RequestID                     Issued Request ID             Long    4 -- Indexed
  Request.Disposition           Request Disposition           Long    4 -- Indexed
  Request.DispositionMessage    Request Disposition Message   String  8192
  Request.SubmittedWhen         Request Submission Date       Date    8 -- Indexed
  Request.ResolvedWhen          Request Resolution Date       Date    8 -- Indexed
  NotBefore                     Certificate Effective Date    Date    8
  NotAfter                      Certificate Expiration Date   Date    8 -- Indexed
  CommonName                    Issued Common Name            String  8192 -- Indexed

Row 1:
  Issued Request ID: 0x8
  Request Disposition: 0x1f (31) -- Denied
  Request Disposition Message: "Denied by Policy Module"
  Request Submission Date: 9/9/2026 8:08 PM
  Request Resolution Date: 9/9/2026 8:08 PM
  Certificate Effective Date: 9/9/2026 7:58 PM
  Certificate Expiration Date: 9/9/2028 8:08 PM
  Issued Common Name: "jsmith"

Row 2:
  Issued Request ID: 0x9
  Request Disposition: 0x14 (20) -- Issued
  Request Disposition Message: "Issued"
  Request Submission Date: 9/9/2026 10:20 PM
  Request Resolution Date: 9/9/2026 10:20 PM
  Certificate Effective Date: 9/9/2026 10:10 PM
  Certificate Expiration Date: 9/9/2027 10:10 PM
  Issued Common Name: "DC01.district.local"

Maximum Row Index: 2

2 Rows
CertUtil: -view command completed successfully.
```

## Trailing host reading

```
Thu Sep 10 10:02:35 PM UTC 2026
```

## Derived values

**Fourth offset reading, and both clocks are stable across nine minutes.** DC01 read 20:08:43.94
local at host 22:02:32Z, an offset of +5h 06m 11.9s against +5h 06m 11.0s nine minutes earlier.
CA01 read 22:02:35.02 local at host 22:02:35Z, an offset of +7h 00m 00.0s.

**CA01's move is dated exactly.** The oldest `4616` above steps CA01 from 2026-09-09T14:35:10.509Z
to 2026-09-09T21:35:10.902Z, a jump of +7h 00m 00.393s. The host puts CA01's boot at
2026-09-09T14:19:31Z, so the "Previous Time" of 14:35:10.5Z is real time and the step happened at
boot plus 15m 39s. CA01 boots correct and is moved to DC01's base within sixteen minutes.

**DC01 has not been stepped since 2026-09-07.** Its newest `4616` is 9/7 6:49:19 AM local. Its
change from +7h 00m 00s at the 2026-09-09T14:19:31Z boot to +5h 06m 11.9s now is therefore drift,
not correction. No process wrote to that clock.

**`certutil -view` prints local time, not UTC.** Request 8 was submitted during the command block
recorded in `exercises/2026-09-05-adcs-issuing-ca-build/evidence/54-pki-cba-pilot-gates-enrollment-non-member-denied.txt`,
whose own host reading is `Timestamp: 2026-09-09T20:08:49Z`. CA01 was at +7h from 14:35:10Z that
day, so its own UTC then read 2026-09-10T03:08:49Z and its local read 2026-09-09 8:08 PM.
`certutil` printed `Request Submission Date: 9/9/2026 8:08 PM`. The local value matches and the UTC
value does not.

**Request 9's certificate is post-dated by seven hours in absolute terms.** It resolved at CA01
local 9/9 10:20 PM, which is real 2026-09-09T22:20Z. The `NotBefore` written into the certificate is
CA01's own UTC value for its local 10:10 PM, which is 2026-09-10T05:10Z.
