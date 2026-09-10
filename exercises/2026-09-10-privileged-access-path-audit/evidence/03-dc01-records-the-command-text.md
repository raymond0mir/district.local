# DC01's logging posture, and the marker search

Command:

```
date -u; qm guest exec 100 --timeout 180 -- powershell.exe -NonInteractive -Command '$ErrorActionPreference="SilentlyContinue"; "== identity =="; whoami; "== process and parent =="; $me=Get-CimInstance Win32_Process -Filter ("ProcessId=" + $PID); Write-Output ("name=" + $me.Name + " pid=" + $me.ProcessId + " ppid=" + $me.ParentProcessId); $par=Get-CimInstance Win32_Process | Where-Object ProcessId -eq $me.ParentProcessId; Write-Output ("parentresolved=" + [bool]$par + " parentname=" + $par.Name + " parentpath=" + $par.ExecutablePath); "== qemu-ga service =="; Get-CimInstance Win32_Service | Where-Object Name -like "*qemu*" | Format-List Name,ProcessId,State,StartName,PathName; "== audit policy =="; auditpol /get /subcategory:"Process Creation"; auditpol /get /subcategory:"Logon"; "== 4688 count last 2h =="; (Get-WinEvent -FilterHashtable @{LogName="Security";Id=4688;StartTime=(Get-Date).AddHours(-2)} | Measure-Object).Count; "== security event ids last 30 min =="; Get-WinEvent -FilterHashtable @{LogName="Security";StartTime=(Get-Date).AddMinutes(-30)} | Group-Object Id | Sort-Object Count -Descending | Format-Table Count,Name -AutoSize; "== system providers last 30 min =="; Get-WinEvent -FilterHashtable @{LogName="System";StartTime=(Get-Date).AddMinutes(-30)} | Group-Object ProviderName | Format-Table Count,Name -AutoSize; "== application providers last 30 min =="; Get-WinEvent -FilterHashtable @{LogName="Application";StartTime=(Get-Date).AddMinutes(-30)} | Group-Object ProviderName | Format-Table Count,Name -AutoSize; "== powershell operational last 30 min =="; Get-WinEvent -FilterHashtable @{LogName="Microsoft-Windows-PowerShell/Operational";StartTime=(Get-Date).AddMinutes(-30)} | Group-Object Id | Format-Table Count,Name -AutoSize; "== marker search =="; Get-WinEvent -FilterHashtable @{LogName="Microsoft-Windows-PowerShell/Operational";StartTime=(Get-Date).AddMinutes(-30)} | Where-Object Message -like "*AUDITMARK*" | Measure-Object | Format-List Count; "== logging policy =="; Get-ItemProperty "HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging" | Format-List EnableScriptBlockLogging; Get-ItemProperty "HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ModuleLogging" | Format-List EnableModuleLogging; Get-ItemProperty "HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\Transcription" | Format-List EnableTranscripting; "== qemu-ga files =="; Get-ChildItem "C:\Program Files\Qemu-ga" | Format-Table Name,Length,LastWriteTime -AutoSize; "== done =="'; echo "guestexec exit=$?"; date -u
```

Host: proxmox (host shell), executing on DC01 (VM 100) through the QEMU guest agent
UTC: 2026-09-10T18:22:13Z, returned 2026-09-10T18:22:18Z
Exit codes: `guestexec exit=0`. Guest agent reported `"exitcode" : 0`, `"exited" : 1`.

`out-data` is reproduced below with `\r\n` rendered as line breaks. No other alteration.

```
== identity ==
nt authority\system
== process and parent ==
name=powershell.exe pid=620 ppid=4452
parentresolved=False parentname= parentpath=
== qemu-ga service ==

Name      : QEMU Guest Agent VSS Provider
ProcessId : 0
State     : Stopped
StartName : LocalSystem
PathName  : C:\Windows\system32\dllhost.exe /Processid:{FCF231F2-91E9-42F7-BF11-6DB9578C47E6}

Name      : QEMU-GA
ProcessId : 3060
State     : Running
StartName : LocalSystem
PathName  : "C:\Program Files\Qemu-ga\qemu-ga.exe" -d --retry-path

== audit policy ==
System audit policy
Category/Subcategory                      Setting
Detailed Tracking
  Process Creation                        Success
System audit policy
Category/Subcategory                      Setting
Logon/Logoff
  Logon                                   Success and Failure
== 4688 count last 2h ==
94
== security event ids last 30 min ==

Count Name
----- ----
   84 4627
   84 4672
   84 4624
   24 4674
   19 4688
   12 5140
    9 4673
    4 4799
    2 4768
    2 4702
    1 4662


== system providers last 30 min ==

Count Name                   
----- ----                   
   14 Service Control Manager


== application providers last 30 min ==

Count Name                          
----- ----                          
   16 qemu-ga                       
    2 Microsoft-Windows-Security-SPP


== powershell operational last 30 min ==

Count Name 
----- ---- 
   27 4104 
    2 40962
    2 53504
    2 40961


== marker search ==

Count : 2

== logging policy ==

EnableScriptBlockLogging : 1

== qemu-ga files ==

Name                              Length LastWriteTime         
----                              ------ -------------         
gspawn-win64-helper-console.exe    26496 11/24/2024 11:00:00 PM
gspawn-win64-helper.exe            26496 11/24/2024 11:00:00 PM
iconv.dll                          39092 10/29/2024 12:00:00 AM
libgcc_s_seh-1.dll                928166 1/13/2025 11:00:00 PM 
libglib-2.0-0.dll                1552239 11/24/2024 11:00:00 PM
libintl-8.dll                     213101 10/29/2024 12:00:00 AM
libpcre2-8-0.dll                  656968 10/29/2024 12:00:00 AM
libssp-0.dll                       87019 1/13/2025 11:00:00 PM 
libstdc++-6.dll                 25978360 1/13/2025 11:00:00 PM 
libwinpthread-1.dll                68679 1/13/2025 11:00:00 PM 
qemu-ga.exe                      4591857 8/4/2025 10:53:58 AM  
qga-vss.dll                       453889 8/4/2025 10:53:56 AM  
qga-vss.tlb                         2380 8/4/2025 10:53:34 AM  

== done ==
```

The `ModuleLogging` and `Transcription` reads produced no output lines, so neither registry key
exists and neither feature is configured.
