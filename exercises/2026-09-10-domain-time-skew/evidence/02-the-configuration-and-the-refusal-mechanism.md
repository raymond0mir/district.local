# The clock configuration on both sides, and the mechanism that refuses the correction

Command:

```
date -u
qm config 100; echo "--- 107 ---"; qm config 107
qm guest exec 100 --timeout 60 -- powershell.exe -NonInteractive -Command 'w32tm /query /configuration; (Get-ADDomain).PDCEmulator; (Get-CimInstance Win32_OperatingSystem).LastBootUpTime; Get-WinEvent -FilterHashtable @{LogName="System"; ProviderName="Microsoft-Windows-Time-Service"} -MaxEvents 10 | Format-Table TimeCreated,Id,LevelDisplayName -AutoSize'
qm guest exec 107 --timeout 60 -- powershell.exe -NonInteractive -Command 'w32tm /query /configuration; (Get-CimInstance Win32_OperatingSystem).LastBootUpTime; w32tm /stripchart /computer:DC01.district.local /samples:2 /dataonly; Get-WinEvent -FilterHashtable @{LogName="System"; ProviderName="Microsoft-Windows-Time-Service"} -MaxEvents 8 | Format-List TimeCreated,Id,LevelDisplayName,Message'
date -u
```

Host: proxmox (host shell), executing on DC01 (VM 100) and CA01 (VM 107) through the QEMU guest
agent
UTC: 2026-09-10T21:45:53Z, returned 2026-09-10T21:45:59Z
Exit codes: both guest agent calls reported `"exitcode" : 0`, `"exited" : 1`.

`out-data` is reproduced below with `\r\n` and `\n` rendered as line breaks. No other alteration.
Guest timestamps in this file are the guests' own local time and are wrong; see
`evidence/01-three-clocks-disagree-and-dc01-answers-to-nothing.md`.

## Host, virtual machine clock configuration

```
Thu Sep 10 09:45:53 PM UTC 2026
agent: enabled=1
bios: ovmf
boot: order=ide2;scsi0;net0
cores: 2
cpu: host
efidisk0: local-lvm:vm-100-disk-0,efitype=4m,pre-enrolled-keys=1,size=4M
ide2: local:iso/lab.iso,media=cdrom,size=900K
localtime: 0
machine: q35
memory: 10000
meta: creation-qemu=10.0.2,ctime=1759192209
name: winserver2022
net0: virtio=BC:24:11:14:12:57,bridge=vmbr1,firewall=1
numa: 0
ostype: l26
parent: clean-install
scsi0: local-lvm:vm-100-disk-1,iothread=1,size=60G
scsihw: virtio-scsi-single
smbios1: uuid=dd1c71e2-2570-4361-9c2b-7f06077da8b1
sockets: 1
vmgenid: a860b331-ca66-4e08-9903-71be51a93e63
--- 107 ---
agent: enabled=1
bios: ovmf
boot: order=ide2;scsi0;net0
cores: 2
cpu: host
description: Enterprise issuing CA for Entra CBA. Subordinate to offline root in CT 106. Exercise 2026-09-05-adcs-issuing-ca-build.
efidisk0: local-lvm:vm-107-disk-0,efitype=4m,pre-enrolled-keys=1,size=4M
ide2: local:iso/SERVER_EVAL_x64FRE_en-us.iso,media=cdrom,size=4925874K
ide3: local:iso/virtio-win-0.1.285.iso,media=cdrom,size=771138K
machine: pc-q35-10.0
memory: 2048
meta: creation-qemu=10.0.2,ctime=1788643234
name: ca01
net0: virtio=BC:24:11:DE:44:84,bridge=vmbr1,firewall=1
ostype: win11
parent: pre-adcs-config
scsi0: local-lvm:vm-107-disk-1,iothread=1,size=60G
scsihw: virtio-scsi-single
smbios1: uuid=b68a7209-6230-4ae7-b262-4064ac12ab34
sockets: 1
vmgenid: 004a7289-773c-4558-822b-89824a014304
```

## DC01 (VM 100)

```
[Configuration]

EventLogFlags: 2 (Local)
AnnounceFlags: 5 (Local)
TimeJumpAuditOffset: 28800 (Local)
MinPollInterval: 6 (Local)
MaxPollInterval: 10 (Local)
MaxNegPhaseCorrection: 172800 (Local)
MaxPosPhaseCorrection: 172800 (Local)
MaxAllowedPhaseOffset: 300 (Local)

FrequencyCorrectRate: 4 (Local)
PollAdjustFactor: 5 (Local)
LargePhaseOffset: 50000000 (Local)
SpikeWatchPeriod: 900 (Local)
LocalClockDispersion: 10 (Local)
HoldPeriod: 5 (Local)
PhaseCorrectRate: 7 (Local)
UpdateInterval: 100 (Local)


[TimeProviders]

NtpClient (Local)
DllName: C:\Windows\system32\w32time.dll (Local)
Enabled: 1 (Local)
InputProvider: 1 (Local)
AllowNonstandardModeCombinations: 1 (Local)
ResolvePeerBackoffMinutes: 15 (Local)
ResolvePeerBackoffMaxTimes: 7 (Local)
CompatibilityFlags: 2147483648 (Local)
EventLogFlags: 1 (Local)
LargeSampleSkew: 3 (Local)
SpecialPollInterval: 1024 (Local)
Type: NTP (Local)
NtpServer: time.windows.com (Local)

NtpServer (Local)
DllName: C:\Windows\system32\w32time.dll (Local)
Enabled: 1 (Local)
InputProvider: 0 (Local)
AllowNonstandardModeCombinations: 1 (Local)

VMICTimeProvider (Local)
DllName: C:\Windows\System32\vmictimeprovider.dll (Local)
Enabled: 1 (Local)
InputProvider: 1 (Local)


DC01.district.local

Thursday, September 10, 2026 3:39:58 AM



TimeCreated           Id LevelDisplayName
-----------           -- ----------------
9/9/2026 2:21:01 PM  134 Warning
9/9/2026 2:20:18 PM  134 Warning
9/9/2026 2:20:04 PM  134 Warning
9/9/2026 2:19:52 PM  143 Information
9/9/2026 2:19:52 PM  139 Information
9/8/2026 10:54:46 PM 134 Warning
9/8/2026 10:54:03 PM 134 Warning
9/8/2026 10:53:50 PM 134 Warning
9/8/2026 10:53:38 PM 143 Information
9/8/2026 10:53:38 PM 139 Information
```

The second value is `(Get-ADDomain).PDCEmulator`. The third is `LastBootUpTime`.

## CA01 (VM 107)

```
[Configuration]

EventLogFlags: 2 (Local)
AnnounceFlags: 10 (Local)
TimeJumpAuditOffset: 28800 (Local)
MinPollInterval: 6 (Local)
MaxPollInterval: 10 (Local)
MaxNegPhaseCorrection: 4294967295 (Local)
MaxPosPhaseCorrection: 4294967295 (Local)
MaxAllowedPhaseOffset: 300 (Local)

FrequencyCorrectRate: 4 (Local)
PollAdjustFactor: 5 (Local)
LargePhaseOffset: 50000000 (Local)
SpikeWatchPeriod: 900 (Local)
LocalClockDispersion: 10 (Local)
HoldPeriod: 5 (Local)
PhaseCorrectRate: 1 (Local)
UpdateInterval: 100 (Local)


[TimeProviders]

NtpClient (Local)
DllName: C:\Windows\system32\w32time.dll (Local)
Enabled: 1 (Local)
InputProvider: 1 (Local)
CrossSiteSyncFlags: 2 (Local)
AllowNonstandardModeCombinations: 1 (Local)
ResolvePeerBackoffMinutes: 15 (Local)
ResolvePeerBackoffMaxTimes: 7 (Local)
CompatibilityFlags: 2147483648 (Local)
EventLogFlags: 1 (Local)
LargeSampleSkew: 3 (Local)
SpecialPollInterval: 1024 (Local)
Type: NT5DS (Local)

VMICTimeProvider (Local)
DllName: C:\Windows\System32\vmictimeprovider.dll (Local)
Enabled: 1 (Local)
InputProvider: 1 (Local)

NtpServer (Local)
DllName: C:\Windows\system32\w32time.dll (Local)
Enabled: 0 (Local)
InputProvider: 0 (Local)


Wednesday, September 9, 2026 2:19:41 PM
Tracking DC01.district.local [10.0.0.10:123].
Collecting 2 samples.
The current time is 9/10/2026 9:45:57 PM.
21:45:57, -6829.4511649s
21:45:59, -6829.4512051s




TimeCreated      : 9/10/2026 4:31:49 PM
Id               : 50
LevelDisplayName : Warning
Message          : The time service detected a time difference of greater than 5000 milliseconds for 900 seconds. The
                   time difference might be caused by synchronization with low-accuracy time sources or by suboptimal
                   network conditions. The time service is no longer synchronized and cannot provide the time to other
                   clients or update the system clock. When a valid time stamp is received from a time service
                   provider, the time service will correct itself.

TimeCreated      : 9/10/2026 6:15:01 PM
Id               : 50
LevelDisplayName : Warning
Message          : The time service detected a time difference of greater than 5000 milliseconds for 900 seconds. The
                   time difference might be caused by synchronization with low-accuracy time sources or by suboptimal
                   network conditions. The time service is no longer synchronized and cannot provide the time to other
                   clients or update the system clock. When a valid time stamp is received from a time service
                   provider, the time service will correct itself.

TimeCreated      : 9/9/2026 2:35:10 PM
Id               : 35
LevelDisplayName : Information
Message          : The time service is now synchronizing the system time with the time source DC01.district.local
                   (ntp.d|0.0.0.0:123->10.0.0.10:123) with reference id 167772170. Current local stratum number is 2.

TimeCreated      : 9/9/2026 7:35:01 AM
Id               : 37
LevelDisplayName : Information
Message          : The time provider NtpClient is currently receiving valid time data from DC01.district.local
                   (ntp.d|0.0.0.0:123->10.0.0.10:123).

TimeCreated      : 9/9/2026 7:35:01 AM
Id               : 138
LevelDisplayName : Information
Message          : NtpClient succeeds in resolving domain peer DC01.district.local after a previous failure.

TimeCreated      : 9/9/2026 7:20:00 AM
Id               : 129
LevelDisplayName : Warning
Message          : NtpClient was unable to set a domain peer to use as a time source because of discovery error.
                   NtpClient will try again in 15 minutes and double the reattempt interval thereafter. The error was:
                   The entry is not found. (0x800706E1)

TimeCreated      : 9/9/2026 7:19:59 AM
Id               : 129
LevelDisplayName : Warning
Message          : NtpClient was unable to set a domain peer to use as a time source because of discovery error.
                   NtpClient will try again in 15 minutes and double the reattempt interval thereafter. The error was:
                   The entry is not found. (0x800706E1)

TimeCreated      : 9/8/2026 11:08:56 PM
Id               : 35
LevelDisplayName : Information
Message          : The time service is now synchronizing the system time with the time source DC01.district.local
                   (ntp.d|0.0.0.0:123->10.0.0.10:123) with reference id 167772170. Current local stratum number is 2.
```

The first value is `LastBootUpTime`.

## Trailing host reading

```
Thu Sep 10 09:45:59 PM UTC 2026
```

## Derived values

**DC01's offset, third reading.** CA01's stripchart states its own time as 9/10/2026 21:45:57
local and DC01 as 6829.4512 s behind it. CA01's local clock tracked the host's UTC to within one
second across both captures, so DC01's local time at host 2026-09-10T21:45:56.5Z was
21:45:57 - 6829.45 s = 19:52:07.5. Its offset from the host is therefore +5h 06m 11.0s, unchanged
from the reading six minutes earlier within the precision available here.

**DC01's rate against the host across this interval.**

| Host UTC | DC01 local | Source |
| --- | --- | --- |
| 2026-09-10T21:39:43Z | 19:45:53.73 | `evidence/01`, direct `Get-Date` |
| 2026-09-10T21:45:56.5Z | 19:52:07.5 | this file, derived from the stripchart |

DC01 elapsed 6m 13.8s across 6m 13.5s of host time. The difference is about 0.3 s in 374 s.

**CA01's rate against the host across the same interval.** CA01 read 21:39:45.52 local at host
21:39:45Z and 21:45:57 local at host 21:45:56.5Z. Elapsed 6m 11.5s against 6m 11.5s.
