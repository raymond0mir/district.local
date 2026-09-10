# What the guest records, in full

Command:

```
date -u; qm guest exec 100 --timeout 180 -- powershell.exe -NonInteractive -Command '$ErrorActionPreference="SilentlyContinue"; "== 4104 marker events =="; Get-WinEvent -FilterHashtable @{LogName="Microsoft-Windows-PowerShell/Operational";Id=4104;StartTime=(Get-Date).AddMinutes(-60)} | Where-Object Message -like "*AUDITMARK*" | Select-Object TimeCreated,Id,UserId,@{n="head";e={$_.Message.Substring(0,[Math]::Min(420,$_.Message.Length))}} | Format-List; "== 4688 for powershell =="; Get-WinEvent -FilterHashtable @{LogName="Security";Id=4688;StartTime=(Get-Date).AddMinutes(-60)} | Where-Object {$_.Properties[5].Value -like "*powershell*"} | Select-Object -First 4 TimeCreated,@{n="subject";e={$_.Properties[1].Value}},@{n="newproc";e={$_.Properties[5].Value}},@{n="newpid";e={$_.Properties[4].Value}},@{n="creatorpid";e={$_.Properties[7].Value}},@{n="parentproc";e={$_.Properties[13].Value}},@{n="cmdline";e={$_.Properties[8].Value}} | Format-List; "== cmdline audit flag =="; Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\Audit" | Format-List ProcessCreationIncludeCmdLine_Enabled; "== qemu-ga app events =="; Get-WinEvent -FilterHashtable @{LogName="Application";ProviderName="qemu-ga";StartTime=(Get-Date).AddMinutes(-60)} | Select-Object -First 6 TimeCreated,Id,LevelDisplayName,Message | Format-List; "== scriptblock policy values =="; Get-Item "HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging" | Format-List Property; "== done =="'; echo "guestexec exit=$?"; date -u
```

Host: proxmox (host shell), executing on DC01 (VM 100) through the QEMU guest agent
UTC: 2026-09-10T18:25:15Z, returned 2026-09-10T18:25:17Z
Exit codes: `guestexec exit=0`. Guest agent reported `"exitcode" : 0`, `"exited" : 1`.

`out-data` is reproduced below with `\r\n` rendered as line breaks and `\"` rendered as `"`. The
long `guest-exec called` message is quoted in full, because it is the finding. No other alteration.

```
== 4104 marker events ==

TimeCreated : 9/10/2026 4:00:58 PM
Id          : 4104
UserId      : S-1-5-18
head        : Creating Scriptblock text (1 of 1):
              $ErrorActionPreference="SilentlyContinue"; "== 4104 marker events =="; Get-WinEvent -FilterHashtable 
              @{LogName="Microsoft-Windows-PowerShell/Operational";Id=4104;StartTime=(Get-Date).AddMinutes(-60)} | 
              Where-Object Message -like "*AUDITMARK*" | Select-Object 
              TimeCreated,Id,UserId,@{n="head";e={$_.Message.Substring(0,[Math]::Min(420,$_.Message.Length))}} | 
              Format-List; "== 4688 for

TimeCreated : 9/10/2026 3:57:57 PM
Id          : 4104
UserId      : S-1-5-18
head        : Creating Scriptblock text (1 of 1):
              $ErrorActionPreference="SilentlyContinue"; "== identity =="; whoami; "== process and parent =="; 
              $me=Get-CimInstance Win32_Process -Filter ("ProcessId=" + $PID); Write-Output ("name=" + $me.Name + " 
              pid=" + $me.ProcessId + " ppid=" + $me.ParentProcessId); $par=Get-CimInstance Win32_Process | 
              Where-Object ProcessId -eq $me.ParentProcessId; Write-Output ("parentresolved=" + [bool]$p

TimeCreated : 9/10/2026 3:54:31 PM
Id          : 4104
UserId      : S-1-5-18
head        : Creating Scriptblock text (1 of 1):
              Write-Output "AUDITMARK-20260910-PAP"; whoami; hostname; $me=Get-CimInstance Win32_Process -Filter 
              ("ProcessId=" + $PID); $par=Get-CimInstance Win32_Process -Filter ("ProcessId=" + $me.ParentProcessId); 
              Write-Output ("child=" + $me.Name + " parent=" + $par.Name + " parentpid=" + $par.ProcessId)
              
              ScriptBlock ID: 68a4ffdf-38ea-455e-a6a0-e92a9197bb4e
              Path: 

== 4688 for powershell ==

TimeCreated : 9/10/2026 3:57:57 PM
subject     : DC01$
newproc     : C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe
newpid      : 620
creatorpid  : 4452
parentproc  : C:\Program Files\Qemu-ga\gspawn-win64-helper.exe
cmdline     : 

TimeCreated : 9/10/2026 3:54:31 PM
subject     : DC01$
newproc     : C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe
newpid      : 1980
creatorpid  : 3720
parentproc  : C:\Program Files\Qemu-ga\gspawn-win64-helper.exe
cmdline     : 

== cmdline audit flag ==
== qemu-ga app events ==

TimeCreated      : 9/10/2026 4:00:59 PM
Id               : 1
LevelDisplayName : Information
Message          : guest-exec-status called, pid: 4704

TimeCreated      : 9/10/2026 4:00:59 PM
Id               : 1
LevelDisplayName : Information
Message          : guest-ping called

TimeCreated      : 9/10/2026 4:00:58 PM
Id               : 1
LevelDisplayName : Information
Message          : guest-exec-status called, pid: 4704

TimeCreated      : 9/10/2026 4:00:58 PM
Id               : 1
LevelDisplayName : Information
Message          : guest-ping called

TimeCreated      : 9/10/2026 4:00:58 PM
Id               : 1
LevelDisplayName : Information
Message          : guest-exec called: "powershell.exe -NonInteractive -Command 
                   $ErrorActionPreference="SilentlyContinue"; "== 4104 marker events =="; Get-WinEvent 
                   -FilterHashtable 
                   @{LogName="Microsoft-Windows-PowerShell/Operational";Id=4104;StartTime=(Get-Date).AddMinutes(-60)} 
                   | Where-Object Message -like "*AUDITMARK*" | Select-Object 
                   TimeCreated,Id,UserId,@{n="head";e={$_.Message.Substring(0,[Math]::Min(420,$_.Message.Length))}} | 
                   Format-List; "== 4688 for powershell =="; Get-WinEvent -FilterHashtable 
                   @{LogName="Security";Id=4688;StartTime=(Get-Date).AddMinutes(-60)} | Where-Object 
                   {$_.Properties[5].Value -like "*powershell*"} | Select-Object -First 4 TimeCreated,@{n="subject";e={
                   $_.Properties[1].Value}},@{n="newproc";e={$_.Properties[5].Value}},@{n="newpid";e={$_.Properties[4].
                   Value}},@{n="creatorpid";e={$_.Properties[7].Value}},@{n="parentproc";e={$_.Properties[13].Value}},@
                   {n="cmdline";e={$_.Properties[8].Value}} | Format-List; "== cmdline audit flag =="; 
                   Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\Audit" | 
                   Format-List ProcessCreationIncludeCmdLine_Enabled; "== qemu-ga app events =="; Get-WinEvent 
                   -FilterHashtable 
                   @{LogName="Application";ProviderName="qemu-ga";StartTime=(Get-Date).AddMinutes(-60)} | 
                   Select-Object -First 6 TimeCreated,Id,LevelDisplayName,Message | Format-List; "== scriptblock 
                   policy values =="; Get-Item 
                   "HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging" | Format-List Property; 
                   "== done =="

TimeCreated      : 9/10/2026 4:00:58 PM
Id               : 1
LevelDisplayName : Information
Message          : guest-ping called

== scriptblock policy values ==

Property : {EnableScriptBlockLogging}

== done ==
```

The `== cmdline audit flag ==` section produced no output line, so
`ProcessCreationIncludeCmdLine_Enabled` does not exist under
`HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\Audit`.

## Clock discrepancy, arithmetic only

The three `4104` events correspond to three invocations whose host-side UTC timestamps are known:
2026-09-10T18:18:48Z, 18:22:13Z and 18:25:15Z. DC01 renders them at 3:54:31 PM, 3:57:57 PM and
4:00:58 PM local.

The intervals agree. Host 3m25s and 3m02s; DC01 3m26s and 3m01s. **The offset is constant, and it is
not a whole number of hours.** The host runs America/Los_Angeles, where 18:18:48Z is 11:18:48. DC01
shows 3:54:31 PM for the same event. DC01's timezone and clock source were not read in this capture,
so the direction and size of the skew are not stated here. See the evidence log.
