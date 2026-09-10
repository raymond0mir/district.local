# Three clocks disagree, and DC01 answers to nothing

Command:

```
date -u; timedatectl | head -6
qm guest exec 100 --timeout 30 -- powershell.exe -NonInteractive -Command 'Get-Date -Format o; [System.TimeZoneInfo]::Local.Id; w32tm /query /source; w32tm /query /status'
qm guest exec 107 --timeout 30 -- powershell.exe -NonInteractive -Command 'Get-Date -Format o; [System.TimeZoneInfo]::Local.Id; w32tm /query /source; w32tm /query /status'
date -u
```

Host: proxmox (host shell), executing on DC01 (VM 100) and CA01 (VM 107) through the QEMU guest
agent
UTC: 2026-09-10T21:39:42Z, returned 2026-09-10T21:39:45Z
Exit codes: both guest agent calls reported `"exitcode" : 0`, `"exited" : 1`.

The two `date -u` calls bracket the guest reads. Every guest reading below sits inside a
three-second host window, so each offset is bounded, not estimated.

`out-data` is reproduced below with `\r\n` and `\n` rendered as line breaks. No other alteration.

## Host, the reference clock

```
Thu Sep 10 09:39:42 PM UTC 2026
               Local time: Thu 2026-09-10 14:39:42 PDT
           Universal time: Thu 2026-09-10 21:39:42 UTC
                 RTC time: Thu 2026-09-10 21:39:42
                Time zone: America/Los_Angeles (PDT, -0700)
System clock synchronized: yes
              NTP service: active
```

## DC01 (VM 100)

```
{
   "exitcode" : 0,
   "exited" : 1,
   "out-data" : "..."
}
```

`out-data` rendered:

```
2026-09-10T19:45:53.7340571-07:00
Pacific Standard Time
Local CMOS Clock
Leap Indicator: 0(no warning)
Stratum: 1 (primary reference - syncd by radio clock)
Precision: -23 (119.209ns per tick)
Root Delay: 0.0000000s
Root Dispersion: 10.0000000s
ReferenceId: 0x4C4F434C (source name:  "LOCL")
Last Successful Sync Time: 9/9/2026 2:19:52 PM
Source: Local CMOS Clock
Poll Interval: 6 (64s)
```

## CA01 (VM 107)

```
{
   "exitcode" : 0,
   "exited" : 1,
   "out-data" : "..."
}
```

`out-data` rendered:

```
2026-09-10T21:39:45.5224237-07:00
Pacific Standard Time
DC01.district.local
Leap Indicator: 0(no warning)
Stratum: 2 (secondary reference - syncd by (S)NTP)
Precision: -23 (119.209ns per tick)
Root Delay: 0.0011612s
Root Dispersion: 10.6857364s
ReferenceId: 0x0A00000A (source IP:  10.0.0.10)
Last Successful Sync Time: 9/10/2026 9:38:42 PM
Source: DC01.district.local
Poll Interval: 9 (512s)
```

## Trailing host reading

```
Thu Sep 10 09:39:45 PM UTC 2026
```

## Derived values

All three machines report the same timezone. The host reports `America/Los_Angeles (PDT, -0700)`.
Both guests report `Pacific Standard Time` with a `-07:00` offset in the ISO-8601 stamp. Timezone
is therefore not the cause of any difference below.

Converting each local reading to UTC:

| Machine | Local reading | UTC | Offset from host |
| --- | --- | --- | --- |
| proxmox | 2026-09-10 14:39:42 PDT | 2026-09-10T21:39:42Z | reference |
| DC01 | 2026-09-10T19:45:53.734-07:00 | 2026-09-11T02:45:53.734Z | +5h 06m 10.7s |
| CA01 | 2026-09-10T21:39:45.522-07:00 | 2026-09-11T04:39:45.522Z | +7h 00m 00.5s |

CA01 minus DC01 = 1h 53m 51.8s. CA01 is ahead of DC01.

CA01's local wall time, 21:39:45.5, equals the host's UTC reading, 21:39:45, to within one second.
Its offset from the host is 7h 00m 00.5s, and the host's UTC offset is exactly -07:00.

## Comparison with the prior session's readings

`exercises/2026-09-10-privileged-access-path-audit/evidence-log.md` finding 26 records three host
UTC timestamps and the DC01 local timestamps they rendered as:

| Host UTC | DC01 local | DC01 UTC | Offset |
| --- | --- | --- | --- |
| 2026-09-10T18:18:48Z | 15:54:31 | 2026-09-10T22:54:31Z | +4h 35m 43s |
| 2026-09-10T18:25:15Z | 16:00:58 | 2026-09-10T23:00:58Z | +4h 35m 43s |
| 2026-09-10T21:39:43Z | 19:45:53.7 | 2026-09-11T02:45:53.7Z | +5h 06m 10.7s |

Host elapsed between the second and third rows: 3h 14m 28s. DC01 elapsed across the same
interval: 3h 44m 55s. DC01 gained 1827.7 seconds against 11668 seconds of host time.
