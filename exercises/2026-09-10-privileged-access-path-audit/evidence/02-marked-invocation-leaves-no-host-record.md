# A marked invocation, and what the host recorded

Command:

```
date -u; T0=$(date -u +%s); echo "T0=$T0"; echo '--- guest exec on DC01 ---'; qm guest exec 100 --timeout 30 -- powershell.exe -NonInteractive -Command 'Write-Output "AUDITMARK-20260910-PAP"; whoami; hostname; $me=Get-CimInstance Win32_Process -Filter ("ProcessId=" + $PID); $par=Get-CimInstance Win32_Process -Filter ("ProcessId=" + $me.ParentProcessId); Write-Output ("child=" + $me.Name + " parent=" + $par.Name + " parentpid=" + $par.ProcessId)'; echo "guestexec exit=$?"; date -u; echo '--- pve tasks after ---'; pvenode task list --limit 4; echo '--- task index tail ---'; tail -3 /var/log/pve/tasks/index; echo '--- pvedaemon journal since T0 ---'; journalctl -u pvedaemon --since "@$T0" --no-pager; echo '--- the 2 agent mentions, 7d ---'; journalctl -u pvedaemon --since '7 days ago' --no-pager | grep -i agent; echo '--- pveproxy tail ---'; tail -3 /var/log/pveproxy/access.log; echo '--- auditd present? ---'; systemctl is-active auditd 2>&1; which auditctl 2>&1; echo '--- history cap ---'; echo "HISTSIZE=$HISTSIZE HISTFILESIZE=$HISTFILESIZE"; echo "exit=$?"
```

Host: proxmox (host shell, Proxmox web console)
UTC: 2026-09-10T18:18:48Z. T0 epoch 1789064328. The invocation returned at 2026-09-10T18:18:49Z.
Exit codes: `guestexec exit=0`, final `exit=0`. Guest agent reported `"exitcode" : 0`, `"exited" : 1`.

Marker string `AUDITMARK-20260910-PAP` was chosen so the guest-side search has an exact term.

```
Thu Sep 10 06:18:48 PM UTC 2026
T0=1789064328
--- guest exec on DC01 ---
{
   "exitcode" : 0,
   "exited" : 1,
   "out-data" : "AUDITMARK-20260910-PAP\r\nnt authority\\system\r\nDC01\r\nchild=powershell.exe parent= parentpid=\r\n"
}
guestexec exit=0
Thu Sep 10 06:18:49 PM UTC 2026
--- pve tasks after ---
│ UPID:proxmox:00042EA0:015E4C15:6AA2BB16:vncshell::root@pam:         │ vncshell      │     │ root@pam │ 1789049622 │ 1789063141 │ ERROR  │
│ UPID:proxmox:00047BB7:0173F2F4:6AA2F284:qmdelsnapshot:100:root@pam: │ qmdelsnapshot │ 100 │ root@pam │ 1789063812 │ 1789063812 │ OK     │
│ UPID:proxmox:00047BC0:0173F33F:6AA2F285:qmdelsnapshot:107:root@pam: │ qmdelsnapshot │ 107 │ root@pam │ 1789063813 │ 1789063813 │ OK     │
│ UPID:proxmox:00047BCA:0173F38D:6AA2F285:qmdelsnapshot:107:root@pam: │ qmdelsnapshot │ 107 │ root@pam │ 1789063813 │ 1789063814 │ OK     │
--- task index tail ---
UPID:proxmox:00047BB7:0173F2F4:6AA2F284:qmdelsnapshot:100:root@pam: 6AA2F284 OK
UPID:proxmox:00047BC0:0173F33F:6AA2F285:qmdelsnapshot:107:root@pam: 6AA2F285 OK
UPID:proxmox:00047BCA:0173F38D:6AA2F285:qmdelsnapshot:107:root@pam: 6AA2F286 OK
--- pvedaemon journal since T0 ---
-- No entries --
--- the 2 agent mentions, 7d ---
Sep 05 09:50:18 proxmox pvedaemon[94771]: QEMU Guest Agent is not running - VM 101 qmp command 'guest-ping' failed - got timeout
Sep 05 14:22:05 proxmox pvedaemon[127266]: QEMU Guest Agent is not running - VM 107 qmp command 'guest-ping' failed - got timeout
--- pveproxy tail ---
::ffff:192.168.1.164 - root@pam [10/09/2026:11:18:47 -0700] "GET /api2/json/cluster/tasks HTTP/1.1" 200 1087
::ffff:192.168.1.164 - root@pam [10/09/2026:11:18:48 -0700] "GET /api2/json/cluster/resources HTTP/1.1" 200 927
::ffff:192.168.1.164 - root@pam [10/09/2026:11:18:49 -0700] "GET /api2/json/nodes/proxmox/status HTTP/1.1" 200 1148
--- auditd present? ---
inactive
--- history cap ---
HISTSIZE=500 HISTFILESIZE=500
exit=0
```

The task table header row is elided for width. `which auditctl` produced no output, so `auditctl`
is not on the host's path.
