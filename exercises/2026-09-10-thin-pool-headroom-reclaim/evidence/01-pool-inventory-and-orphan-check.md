# Pool inventory and orphan check

Command:

```
date -u; echo '--- vm state ---'; qm list; echo '--- pool ---'; lvs -a -o+data_percent,metadata_percent; echo '--- lv detail by size ---'; lvs -a --units g -o lv_name,lv_size,data_percent,origin,lv_time --sort -lv_size; echo '--- snapshots ---'; qm listsnapshot 100; qm listsnapshot 107; echo '--- storage vs vms ---'; pvesm list local-lvm; echo '--- mem ---'; free -h
```

Host: proxmox (host shell, Proxmox web console)
UTC: 2026-09-10T18:00:17Z

Exit code: not captured. The command block did not echo `$?`. See the evidence log.

```
Thu Sep 10 06:00:17 PM UTC 2026
--- vm state ---
      VMID NAME                 STATUS     MEM(MB)    BOOTDISK(GB) PID       
       100 winserver2022        running    10000             60.00 123702    
       101 win11-client01       stopped    3072              64.00 0         
       102 entraconnect01       stopped    2048              60.00 0         
       104 pfsense-fw           stopped    2048              20.00 0         
       107 ca01                 running    2048              60.00 123791    
--- pool ---
  LV                                                     VG  Attr       LSize    Pool Origin                        Data%  Meta%  Move Log Cpy%Sync Convert Data%  Meta% 
  data                                                   pve twi-aotz-- <155.23g                                    84.23  4.21                             84.23  4.21  
  [data_tdata]                                           pve Twi-ao---- <155.23g                                                                                         
  [data_tmeta]                                           pve ewi-ao----   <1.44g                                                                                         
  [lvol0_pmspare]                                        pve ewi-------   <1.44g                                                                                         
  root                                                   pve -wi-ao----  <69.37g                                                                                         
  snap_vm-100-disk-0_clean-install                       pve Vri---tz-k    4.00m data vm-100-disk-0                                                                      
  snap_vm-100-disk-0_pre-secure-admin-ws-relink-20260902 pve Vri---tz-k    4.00m data vm-100-disk-0                                                                      
  snap_vm-100-disk-1_clean-install                       pve Vri---tz-k   60.00g data vm-100-disk-1                                                                      
  snap_vm-100-disk-1_pre-secure-admin-ws-relink-20260902 pve Vri---tz-k   60.00g data vm-100-disk-1                                                                      
  snap_vm-101-disk-0_win11-ootb                          pve Vri---tz-k    4.00m data                                                                                    
  snap_vm-101-disk-1_win11-ootb                          pve Vri---tz-k   64.00g data                                                                                    
  snap_vm-101-disk-2_win11-ootb                          pve Vri---tz-k    4.00m data                                                                                    
  snap_vm-106-disk-0_pre-crl-setup-20260908              pve Vri---tz-k    4.00g data vm-106-disk-0                                                                      
  snap_vm-107-disk-0_pre-adcs-config                     pve Vri---tz-k    4.00m data vm-107-disk-0                                                                      
  snap_vm-107-disk-0_pre-ca-cert-reissue-20260908        pve Vri---tz-k    4.00m data vm-107-disk-0                                                                      
  snap_vm-107-disk-0_pre-cdp-setup-20260908              pve Vri---tz-k    4.00m data vm-107-disk-0                                                                      
  snap_vm-107-disk-1_pre-adcs-config                     pve Vri---tz-k   60.00g data vm-107-disk-1                                                                      
  snap_vm-107-disk-1_pre-ca-cert-reissue-20260908        pve Vri---tz-k   60.00g data vm-107-disk-1                                                                      
  snap_vm-107-disk-1_pre-cdp-setup-20260908              pve Vri---tz-k   60.00g data vm-107-disk-1                                                                      
  swap                                                   pve -wi-ao----    8.00g                                                                                         
  vm-100-disk-0                                          pve Vwi-aotz--    4.00m data                               14.06                                   14.06        
  vm-100-disk-1                                          pve Vwi-aotz--   60.00g data                               44.48                                   44.48        
  vm-100-state-clean-install                             pve Vwi---tz--   <8.49g data                                                                                    
  vm-101-disk-0                                          pve Vwi---tz--    4.00m data snap_vm-101-disk-0_win11-ootb                                                      
  vm-101-disk-1                                          pve Vwi---tz--   64.00g data snap_vm-101-disk-1_win11-ootb                                                      
  vm-101-disk-2                                          pve Vwi---tz--    4.00m data snap_vm-101-disk-2_win11-ootb                                                      
  vm-101-state-win11-ootb                                pve Vwi---tz--   <8.49g data                                                                                    
  vm-102-disk-0                                          pve Vwi---tz--    4.00m data                                                                                    
  vm-102-disk-1                                          pve Vwi---tz--   60.00g data                                                                                    
  vm-104-disk-0                                          pve Vwi---tz--   20.00g data                                                                                    
  vm-106-disk-0                                          pve Vwi-a-tz--    4.00g data                               18.08                                   18.08        
  vm-107-disk-0                                          pve Vwi-aotz--    4.00m data                               14.06                                   14.06        
  vm-107-disk-1                                          pve Vwi-aotz--   60.00g data                               21.86                                   21.86        
--- lv detail by size ---
  LV                                                     LSize   Data%  Origin                        CTime                     
  data                                                   155.23g 84.23                                2025-09-29 08:21:00 -0700 
  [data_tdata]                                           155.23g                                      2025-09-29 08:21:06 -0700 
  root                                                    69.37g                                      2025-09-29 08:21:00 -0700 
  snap_vm-101-disk-1_win11-ootb                           64.00g                                      2025-09-30 15:54:58 -0700 
  vm-101-disk-1                                           64.00g        snap_vm-101-disk-1_win11-ootb 2026-09-03 17:07:14 -0700 
  vm-100-disk-1                                           60.00g 44.48                                2025-09-29 17:30:09 -0700 
  snap_vm-100-disk-1_clean-install                        60.00g        vm-100-disk-1                 2025-09-29 17:44:26 -0700 
  vm-102-disk-1                                           60.00g                                      2026-08-31 16:32:45 -0700 
  snap_vm-100-disk-1_pre-secure-admin-ws-relink-20260902  60.00g        vm-100-disk-1                 2026-09-02 10:07:44 -0700 
  vm-107-disk-1                                           60.00g 21.86                                2026-09-05 14:20:35 -0700 
  snap_vm-107-disk-1_pre-adcs-config                      60.00g        vm-107-disk-1                 2026-09-05 15:02:02 -0700 
  snap_vm-107-disk-1_pre-ca-cert-reissue-20260908         60.00g        vm-107-disk-1                 2026-09-08 07:00:07 -0700 
  snap_vm-107-disk-1_pre-cdp-setup-20260908               60.00g        vm-107-disk-1                 2026-09-08 15:53:17 -0700 
  vm-104-disk-0                                           20.00g                                      2026-06-12 11:27:20 -0700 
  vm-100-state-clean-install                               8.49g                                      2025-09-29 17:44:23 -0700 
  vm-101-state-win11-ootb                                  8.49g                                      2025-09-30 15:54:34 -0700 
  swap                                                     8.00g                                      2025-09-29 08:21:00 -0700 
  vm-106-disk-0                                            4.00g 18.08                                2026-09-05 14:13:54 -0700 
  snap_vm-106-disk-0_pre-crl-setup-20260908                4.00g        vm-106-disk-0                 2026-09-08 07:00:06 -0700 
  [data_tmeta]                                             1.44g                                      2025-09-29 08:21:00 -0700 
  [lvol0_pmspare]                                          1.44g                                      2025-09-29 08:21:03 -0700 
  vm-100-disk-0                                            0.00g 14.06                                2025-09-29 17:30:09 -0700 
  snap_vm-100-disk-0_clean-install                         0.00g        vm-100-disk-0                 2025-09-29 17:44:26 -0700 
  snap_vm-101-disk-0_win11-ootb                            0.00g                                      2025-09-30 15:54:58 -0700 
  snap_vm-101-disk-2_win11-ootb                            0.00g                                      2025-09-30 15:54:58 -0700 
  vm-102-disk-0                                            0.00g                                      2026-08-31 16:32:44 -0700 
  snap_vm-100-disk-0_pre-secure-admin-ws-relink-20260902   0.00g        vm-100-disk-0                 2026-09-02 10:07:44 -0700 
  vm-101-disk-0                                            0.00g        snap_vm-101-disk-0_win11-ootb 2026-09-03 17:07:14 -0700 
  vm-101-disk-2                                            0.00g        snap_vm-101-disk-2_win11-ootb 2026-09-03 17:07:14 -0700 
  vm-107-disk-0                                            0.00g 14.06                                2026-09-05 14:20:34 -0700 
  snap_vm-107-disk-0_pre-adcs-config                       0.00g        vm-107-disk-0                 2026-09-05 15:02:02 -0700 
  snap_vm-107-disk-0_pre-ca-cert-reissue-20260908          0.00g        vm-107-disk-0                 2026-09-08 07:00:07 -0700 
  snap_vm-107-disk-0_pre-cdp-setup-20260908                0.00g        vm-107-disk-0                 2026-09-08 15:53:17 -0700 
--- snapshots ---
`-> clean-install               2025-09-29 17:44:23     Fully patched + drivers, ready to clone
 `-> pre-secure-admin-ws-relink-20260902 2026-09-02 10:07:41     Before A2 step 3: relink Secure Admin WS off domain root, drop DC Deny-Apply exception, move VM102 into OU=Application Servers
  `-> current                                           You are here!
`-> pre-adcs-config             2026-09-05 15:02:01     Before Install-AdcsCertificationAuthority. Role binaries installed, domain joined, no CA configured.
 `-> pre-ca-cert-reissue-20260908 2026-09-08 07:00:07     issuing CA before certificate reissue with HTTP CDP
  `-> pre-cdp-setup-20260908    2026-09-08 15:53:17     no-description
   `-> current                                          You are here!
--- storage vs vms ---
Volid                                Format  Type             Size VMID
local-lvm:vm-100-disk-0              raw     images        4194304 100
local-lvm:vm-100-disk-1              raw     images    64424509440 100
local-lvm:vm-100-state-clean-install raw     images     9114222592 100
local-lvm:vm-101-disk-0              raw     images        4194304 101
local-lvm:vm-101-disk-1              raw     images    68719476736 101
local-lvm:vm-101-disk-2              raw     images        4194304 101
local-lvm:vm-101-state-win11-ootb    raw     images     9114222592 101
local-lvm:vm-102-disk-0              raw     images        4194304 102
local-lvm:vm-102-disk-1              raw     images    64424509440 102
local-lvm:vm-104-disk-0              raw     images    21474836480 104
local-lvm:vm-106-disk-0              raw     rootdir    4294967296 106
local-lvm:vm-107-disk-0              raw     images        4194304 107
local-lvm:vm-107-disk-1              raw     images    64424509440 107
--- mem ---
               total        used        free      shared  buff/cache   available
Mem:            15Gi        11Gi       2.0Gi        50Mi       1.4Gi       3.1Gi
Swap:          8.0Gi          0B       8.0Gi
```
