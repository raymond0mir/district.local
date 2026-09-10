# Host-side identity, authorization model, and what the host records

Command:

```
date -u; echo '--- pve version ---'; pveversion; echo '--- caller identity ---'; id; hostname; tty; echo '--- pve users ---'; pveum user list 2>&1; echo '--- pve groups ---'; pveum group list 2>&1; echo '--- pve acl ---'; pveum acl list 2>&1; echo '--- api tokens on root@pam ---'; pveum user token list root@pam 2>&1; echo '--- tfa file presence only ---'; ls -l /etc/pve/priv/tfa.cfg 2>&1; wc -l /etc/pve/priv/tfa.cfg 2>&1; echo '--- roles mentioning guest agent ---'; pveum role list 2>&1 | grep -iE 'guest|^Role' | head -20; echo '--- agent enabled on guests ---'; qm config 100 2>&1 | grep -iE '^agent|^name'; qm config 107 2>&1 | grep -iE '^agent|^name'; echo '--- recent pve tasks ---'; pvenode task list --limit 20 2>&1; echo '--- task types ever recorded ---'; awk -F: '{print $6}' /var/log/pve/tasks/index 2>/dev/null | sort | uniq -c | sort -rn | head -20; echo '--- pveproxy access log: agent calls ---'; grep -c 'agent' /var/log/pveproxy/access.log 2>&1; tail -3 /var/log/pveproxy/access.log 2>&1; echo '--- pvedaemon journal: agent mentions, 7d ---'; journalctl -u pvedaemon --since '7 days ago' --no-pager 2>&1 | grep -ci agent; echo '--- root history: counts only ---'; wc -l /root/.bash_history 2>&1; grep -c 'guest exec' /root/.bash_history 2>&1; echo '--- host login records ---'; last -n 15 2>&1; echo "exit=$?"
```

Host: proxmox (host shell, Proxmox web console)
UTC: 2026-09-10T18:13:42Z
Exit code: 0

The `pveum user list` table is quoted verbatim and carries Raymond's personal email address. That
exposure is already realized across this public repository and the decision to address it is
deferred, recorded in `CARRYOVER.md`. This capture adds an instance; it does not change the
decision. `/root/.bash_history` and `/etc/pve/user.cfg` were deliberately not dumped, because both
can hold typed secrets. Only counts and file presence were read.

```
Thu Sep 10 06:13:42 PM UTC 2026
--- pve version ---
pve-manager/9.0.3/025864202ebb6109 (running kernel: 6.14.8-2-pve)
--- caller identity ---
uid=0(root) gid=0(root) groups=0(root)
proxmox
/dev/pts/0
--- pve users ---
┌──────────┬─────────┬───────────────────────┬────────┬────────┬───────────┬────────┬──────┬──────────┬────────────┬──────────────────┬────
│ userid   │ comment │ email                 │ enable │ expire │ firstname │ groups │ keys │ lastname │ realm-type │ tfa-locked-until │ tok
╞══════════╪═════════╪═══════════════════════╪════════╪════════╪═══════════╪════════╪══════╪══════════╪════════════╪══════════════════╪════
│ root@pam │         │ raymond0mir@gmail.com │ 1      │      0 │           │        │      │          │ pam        │                  │    
└──────────┴─────────┴───────────────────────┴────────┴────────┴───────────┴────────┴──────┴──────────┴────────────┴──────────────────┴────
--- pve groups ---
--- pve acl ---
--- api tokens on root@pam ---
--- tfa file presence only ---
ls: cannot access '/etc/pve/priv/tfa.cfg': No such file or directory
wc: /etc/pve/priv/tfa.cfg: No such file or directory
--- roles mentioning guest agent ---
│ Administrator     │ Datastore.Allocate,Datastore.AllocateSpace,Datastore.AllocateTemplate,Datastore.Audit,Group.Allocate,Mapping.Audit,Mapping.Modify,Mapping.Use,Permissions.Modify,Pool.Allocate,Pool.Audit,Realm.Allocate,Realm.AllocateUser,SDN.Allocate,SDN.Audit,SDN.Use,Sys.AccessNetwork,Sys.Audit,Sys.Console,Sys.Incoming,Sys.Modify,Sys.PowerMgmt,Sys.Syslog,User.Modify,VM.Allocate,VM.Audit,VM.Backup,VM.Clone,VM.Config.CDROM,VM.Config.CPU,VM.Config.Cloudinit,VM.Config.Disk,VM.Config.HWType,VM.Config.Memory,VM.Config.Network,VM.Config.Options,VM.Console,VM.GuestAgent.Audit,VM.GuestAgent.FileRead,VM.GuestAgent.FileSystemMgmt,VM.GuestAgent.FileWrite,VM.GuestAgent.Unrestricted,VM.Migrate,VM.PowerMgmt,VM.Replicate,VM.Snapshot,VM.Snapshot.Rollback │ 1       │
│ PVEAdmin          │ Datastore.Allocate,Datastore.AllocateSpace,Datastore.AllocateTemplate,Datastore.Audit,Group.Allocate,Mapping.Audit,Mapping.Use,Pool.Allocate,Pool.Audit,Realm.AllocateUser,SDN.Allocate,SDN.Audit,SDN.Use,Sys.Audit,Sys.Console,Sys.Syslog,User.Modify,VM.Allocate,VM.Audit,VM.Backup,VM.Clone,VM.Config.CDROM,VM.Config.CPU,VM.Config.Cloudinit,VM.Config.Disk,VM.Config.HWType,VM.Config.Memory,VM.Config.Network,VM.Config.Options,VM.Console,VM.GuestAgent.Audit,VM.GuestAgent.FileRead,VM.GuestAgent.FileSystemMgmt,VM.GuestAgent.FileWrite,VM.GuestAgent.Unrestricted,VM.Migrate,VM.PowerMgmt,VM.Replicate,VM.Snapshot,VM.Snapshot.Rollback                                                                                                          │ 1       │
│ PVEAuditor        │ Datastore.Audit,Mapping.Audit,Pool.Audit,SDN.Audit,Sys.Audit,VM.Audit,VM.GuestAgent.Audit                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  │ 1       │
│ PVEVMAdmin        │ VM.Allocate,VM.Audit,VM.Backup,VM.Clone,VM.Config.CDROM,VM.Config.CPU,VM.Config.Cloudinit,VM.Config.Disk,VM.Config.HWType,VM.Config.Memory,VM.Config.Network,VM.Config.Options,VM.Console,VM.GuestAgent.Audit,VM.GuestAgent.FileRead,VM.GuestAgent.FileSystemMgmt,VM.GuestAgent.FileWrite,VM.GuestAgent.Unrestricted,VM.Migrate,VM.PowerMgmt,VM.Replicate,VM.Snapshot,VM.Snapshot.Rollback                                                                                                                                                                                                                                                                                                                                                                 │ 1       │
│ PVEVMUser         │ VM.Audit,VM.Backup,VM.Config.CDROM,VM.Config.Cloudinit,VM.Console,VM.GuestAgent.Audit,VM.GuestAgent.FileRead,VM.GuestAgent.FileSystemMgmt,VM.GuestAgent.FileWrite,VM.PowerMgmt                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             │ 1       │
--- agent enabled on guests ---
agent: enabled=1
name: winserver2022
agent: enabled=1
name: ca01
--- recent pve tasks ---
(20 rows; the three qmdelsnapshot tasks at the tail are this session's deletions)
│ UPID:proxmox:0002C109:00F97003:6AA1B8E3:vncshell::root@pam:         │ vncshell      │     │ root@pam │ 1788983523 │ 1789004298 │ OK     │
│ UPID:proxmox:0002C94B:00FA5616:6AA1BB30:vncshell::root@pam:         │ vncshell      │     │ root@pam │ 1788984112 │ 1789004312 │ OK     │
│ UPID:proxmox:0003453F:01083D79:6AA1DEC8:vncproxy:107:root@pam:      │ vncproxy      │ 107 │ root@pam │ 1788993224 │ 1788994125 │ OK     │
│ UPID:proxmox:0003516F:01099D74:6AA1E24D:vncproxy:107:root@pam:      │ vncproxy      │ 107 │ root@pam │ 1788994125 │ 1788995026 │ OK     │
│ UPID:proxmox:00035DB1:010AFD7D:6AA1E5D2:vncproxy:107:root@pam:      │ vncproxy      │ 107 │ root@pam │ 1788995026 │ 1788995927 │ OK     │
│ UPID:proxmox:000369EC:010C5D86:6AA1E957:vncproxy:107:root@pam:      │ vncproxy      │ 107 │ root@pam │ 1788995927 │ 1788996828 │ OK     │
│ UPID:proxmox:00037623:010DBD6D:6AA1ECDC:vncproxy:107:root@pam:      │ vncproxy      │ 107 │ root@pam │ 1788996828 │ 1788997729 │ OK     │
│ UPID:proxmox:00038257:010F1DA8:6AA1F062:vncproxy:107:root@pam:      │ vncproxy      │ 107 │ root@pam │ 1788997730 │ 1788998631 │ OK     │
│ UPID:proxmox:00038EA2:01107DE4:6AA1F3E8:vncproxy:107:root@pam:      │ vncproxy      │ 107 │ root@pam │ 1788998632 │ 1788999533 │ OK     │
│ UPID:proxmox:00039B02:0111DE27:6AA1F76D:vncproxy:107:root@pam:      │ vncproxy      │ 107 │ root@pam │ 1788999533 │ 1789000434 │ OK     │
│ UPID:proxmox:0003A73F:01133E38:6AA1FAF3:vncproxy:107:root@pam:      │ vncproxy      │ 107 │ root@pam │ 1789000435 │ 1789001336 │ OK     │
│ UPID:proxmox:0003B36E:01149E48:6AA1FE78:vncproxy:107:root@pam:      │ vncproxy      │ 107 │ root@pam │ 1789001336 │ 1789002237 │ OK     │
│ UPID:proxmox:0003BFB0:0115FE39:6AA201FD:vncproxy:107:root@pam:      │ vncproxy      │ 107 │ root@pam │ 1789002237 │ 1789003138 │ OK     │
│ UPID:proxmox:0003CBEE:01175E4C:6AA20582:vncproxy:107:root@pam:      │ vncproxy      │ 107 │ root@pam │ 1789003138 │ 1789004039 │ OK     │
│ UPID:proxmox:0003D839:0118BE43:6AA20907:vncproxy:107:root@pam:      │ vncproxy      │ 107 │ root@pam │ 1789004039 │ 1789004298 │ OK     │
│ UPID:proxmox:00042AC3:015DE209:6AA2BA07:aptupdate::root@pam:        │ aptupdate     │     │ root@pam │ 1789049351 │ 1789049360 │ ERROR  │
│ UPID:proxmox:00042EA0:015E4C15:6AA2BB16:vncshell::root@pam:         │ vncshell      │     │ root@pam │ 1789049622 │ 1789063141 │ ERROR  │
│ UPID:proxmox:00047BB7:0173F2F4:6AA2F284:qmdelsnapshot:100:root@pam: │ qmdelsnapshot │ 100 │ root@pam │ 1789063812 │ 1789063812 │ OK     │
│ UPID:proxmox:00047BC0:0173F33F:6AA2F285:qmdelsnapshot:107:root@pam: │ qmdelsnapshot │ 107 │ root@pam │ 1789063813 │ 1789063813 │ OK     │
│ UPID:proxmox:00047BCA:0173F38D:6AA2F285:qmdelsnapshot:107:root@pam: │ qmdelsnapshot │ 107 │ root@pam │ 1789063813 │ 1789063814 │ OK     │
--- task types ever recorded ---
     90 vncproxy
     31 qmstart
     28 vncshell
     12 qmshutdown
     11 qmstop
      9 vzstart
      8 qmdelsnapshot
      8 aptupdate
      6 qmsnapshot
      5 push_file
      4 vzstop
      3 qmreboot
      2 vzshutdown
      2 vzcreate
      2 stopall
      2 startall
      1 vzsnapshot
      1 vzdump
      1 qmrollback
      1 qmdestroy
--- pveproxy access log: agent calls ---
0
::ffff:192.168.1.164 - root@pam [10/09/2026:11:13:43 -0700] "GET /api2/json/cluster/resources HTTP/1.1" 200 939
::ffff:192.168.1.164 - root@pam [10/09/2026:11:13:43 -0700] "GET /api2/json/nodes/proxmox/status HTTP/1.1" 200 1144
::ffff:192.168.1.164 - root@pam [10/09/2026:11:13:44 -0700] "GET /api2/json/cluster/resources HTTP/1.1" 200 934
--- pvedaemon journal: agent mentions, 7d ---
2
--- root history: counts only ---
500 /root/.bash_history
166
--- host login records ---
root     pts/0                         Thu Sep 10 11:00 - still logged in
root     pts/1        192.168.1.164    Thu Sep 10 07:14 - 10:59  (03:44)
root     pts/0                         Thu Sep 10 07:13 - 10:59  (03:45)
root     pts/0        192.168.1.164    Wed Sep  9 19:29 - 20:12  (00:43)
root     pts/2                         Wed Sep  9 13:01 - 18:38  (05:36)
root     pts/1        192.168.1.164    Wed Sep  9 12:52 - 18:43  (05:50)
root     pts/0                         Wed Sep  9 12:52 - 18:38  (05:46)
root     pts/1                         Wed Sep  9 07:17 - 08:12  (00:55)
root     pts/0        192.168.1.164    Wed Sep  9 06:55 - 08:12  (01:16)
root     pts/0                         Tue Sep  8 16:45 - 06:42  (13:56)
root     pts/2        192.168.1.164    Tue Sep  8 16:14 - 06:42  (14:28)
root     pts/0                         Tue Sep  8 15:48 - 16:44  (00:56)
root     pts/1        192.168.1.164    Tue Sep  8 07:28 - 17:42  (10:13)
root     pts/0                         Tue Sep  8 06:56 - 08:07  (01:11)
root     pts/1        192.168.1.164    Mon Sep  7 15:55 - 17:51  (01:56)

wtmpdb begins Mon Sep  7 15:55:26 2026
exit=0
```

The 20-row task table above is reproduced with its header row elided for width. The UPID, Type, ID,
User, Starttime, Endtime and Status columns are verbatim.
