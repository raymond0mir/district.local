# Exclusive blocks per thin device

Command:

```
date -u; echo '--- containers ---'; pct list; echo '--- tool present ---'; which thin_ls; echo '--- thin ids ---'; lvs -a -o lv_name,lv_size,thin_id --units g; echo '--- clear stale reservation ---'; dmsetup message pve-data-tpool 0 release_metadata_snap 2>&1; echo '--- reserve ---'; dmsetup message pve-data-tpool 0 reserve_metadata_snap 2>&1; echo "reserve exit=$?"; echo '--- thin_ls ---'; thin_ls -m -o DEV,MAPPED_BYTES,EXCLUSIVE_BYTES,SHARED_BYTES /dev/mapper/pve-data_tmeta 2>&1; echo "thin_ls exit=$?"; echo '--- release ---'; dmsetup message pve-data-tpool 0 release_metadata_snap 2>&1; echo "release exit=$?"
```

Host: proxmox (host shell, Proxmox web console)
UTC: 2026-09-10T18:05:39Z

Exit codes: `reserve exit=0`, `thin_ls exit=0`, `release exit=0`. The first
`release_metadata_snap` returned "Invalid argument / Command failed", which is the expected
response when no reservation is held. It was included to clear a stale reservation, and none
existed.

```
Thu Sep 10 06:05:39 PM UTC 2026
--- containers ---
VMID       Status     Lock         Name                
103        running                 vaultwarden         
106        stopped                 rootca-offline      
--- tool present ---
/usr/sbin/thin_ls
--- thin ids ---
  LV                                                     LSize   ThId
  data                                                   155.23g     
  [data_tdata]                                           155.23g     
  [data_tdata]                                           155.23g     
  [data_tmeta]                                             1.44g     
  [lvol0_pmspare]                                          1.44g     
  root                                                    69.37g     
  snap_vm-100-disk-0_clean-install                         0.00g    5
  snap_vm-100-disk-0_pre-secure-admin-ws-relink-20260902   0.00g   47
  snap_vm-100-disk-1_clean-install                        60.00g    4
  snap_vm-100-disk-1_pre-secure-admin-ws-relink-20260902  60.00g   46
  snap_vm-101-disk-0_win11-ootb                            0.00g   14
  snap_vm-101-disk-1_win11-ootb                           64.00g   13
  snap_vm-101-disk-2_win11-ootb                            0.00g   15
  snap_vm-106-disk-0_pre-crl-setup-20260908                4.00g   56
  snap_vm-107-disk-0_pre-adcs-config                       0.00g   55
  snap_vm-107-disk-0_pre-ca-cert-reissue-20260908          0.00g   58
  snap_vm-107-disk-0_pre-cdp-setup-20260908                0.00g   60
  snap_vm-107-disk-1_pre-adcs-config                      60.00g   54
  snap_vm-107-disk-1_pre-ca-cert-reissue-20260908         60.00g   57
  snap_vm-107-disk-1_pre-cdp-setup-20260908               60.00g   59
  swap                                                     8.00g     
  vm-100-disk-0                                            0.00g    1
  vm-100-disk-1                                           60.00g    2
  vm-100-state-clean-install                               8.49g    3
  vm-101-disk-0                                            0.00g   49
  vm-101-disk-1                                           64.00g   48
  vm-101-disk-2                                            0.00g   50
  vm-101-state-win11-ootb                                  8.49g   12
  vm-102-disk-0                                            0.00g   44
  vm-102-disk-1                                           60.00g   45
  vm-104-disk-0                                           20.00g   19
  vm-106-disk-0                                            4.00g   51
  vm-107-disk-0                                            0.00g   52
  vm-107-disk-1                                           60.00g   53
--- clear stale reservation ---
device-mapper: message ioctl on pve-data-tpool  failed: Invalid argument
Command failed.
--- reserve ---
reserve exit=0
--- thin_ls ---
DEV MAPPED_BYTES EXCLUSIVE_BYTES SHARED_BYTES 
  1       589824          131072       458752 
  2  28656926720      5716639744  22940286976 
  3   1036451840      1036451840            0 
  4  11442323456      7937064960   3505258496 
  5       589824          589824            0 
 12   3976527872      3976527872            0 
 13  16375021568     15686696960    688324608 
 14       589824          589824            0 
 15        65536           65536            0 
 19   5848629248      5848629248            0 
 44       589824          589824            0 
 45  19989790720     19989790720            0 
 46  27851489280      4910546944  22940942336 
 47       589824          131072       458752 
 48  32498778112     31810453504    688324608 
 49       589824          589824            0 
 50        65536           65536            0 
 51    776404992         8323072    768081920 
 52       589824          131072       458752 
 53  14085455872      1201799168  12883656704 
 54  10622074880      2975203328   7646871552 
 55       589824          131072       458752 
 56    775553024         7471104    768081920 
 57  14079492096       761200640  13318291456 
 58       589824          131072       458752 
 59  14080278528       497614848  13582663680 
 60       589824          131072       458752 
thin_ls exit=0
--- release ---
release exit=0
```

## Derived table

`DEV` joined to `ThId` from the same capture, sorted by exclusive bytes, converted to GiB at
1 GiB = 1073741824 bytes. This block is arithmetic on the output above, not a second reading.

```
DEV  LV                                                         MAPPED      EXCL    SHARED
48   vm-101-disk-1                                               30.27     29.63      0.64
45   vm-102-disk-1                                               18.62     18.62      0.00
13   snap_vm-101-disk-1_win11-ootb                               15.25     14.61      0.64
4    snap_vm-100-disk-1_clean-install                            10.66      7.39      3.26
19   vm-104-disk-0                                                5.45      5.45      0.00
2    vm-100-disk-1                                               26.69      5.32     21.36
46   snap_vm-100-disk-1_pre-secure-admin-ws-relink-20260902      25.94      4.57     21.37
12   vm-101-state-win11-ootb                                      3.70      3.70      0.00
54   snap_vm-107-disk-1_pre-adcs-config                           9.89      2.77      7.12
53   vm-107-disk-1                                               13.12      1.12     12.00
3    vm-100-state-clean-install                                   0.97      0.97      0.00
57   snap_vm-107-disk-1_pre-ca-cert-reissue-20260908             13.11      0.71     12.40
59   snap_vm-107-disk-1_pre-cdp-setup-20260908                   13.11      0.46     12.65
51   vm-106-disk-0                                                0.72      0.01      0.72
56   snap_vm-106-disk-0_pre-crl-setup-20260908                    0.72      0.01      0.72
5    snap_vm-100-disk-0_clean-install                             0.00      0.00      0.00
14   snap_vm-101-disk-0_win11-ootb                                0.00      0.00      0.00
44   vm-102-disk-0                                                0.00      0.00      0.00
49   vm-101-disk-0                                                0.00      0.00      0.00
1    vm-100-disk-0                                                0.00      0.00      0.00
47   snap_vm-100-disk-0_pre-secure-admin-ws-relink-20260902       0.00      0.00      0.00
52   vm-107-disk-0                                                0.00      0.00      0.00
55   snap_vm-107-disk-0_pre-adcs-config                           0.00      0.00      0.00
58   snap_vm-107-disk-0_pre-ca-cert-reissue-20260908              0.00      0.00      0.00
60   snap_vm-107-disk-0_pre-cdp-setup-20260908                    0.00      0.00      0.00
15   snap_vm-101-disk-2_win11-ootb                                0.00      0.00      0.00
50   vm-101-disk-2                                                0.00      0.00      0.00

sum EXCLUSIVE = 95.34 GiB
pool allocated at 84.23% of 155.23 GiB = 130.75 GiB
blocks shared by 2+ devices = 35.41 GiB
```

## Reclaim per candidate operation

Each figure is the sum of the exclusive bytes of every device the operation removes. Deleting a
device frees its exclusive blocks only. Points are of the 155.23 GiB pool.

```
qm delsnapshot 101 win11-ootb                             18.31 GiB  11.80 points
qm delsnapshot 100 clean-install                           8.36 GiB   5.38 points
destroy VM 104 pfsense                                     5.45 GiB   3.51 points
qm delsnapshot 100 pre-secure-admin-ws-relink-20260902     4.57 GiB   2.95 points
qm delsnapshot 107 pre-adcs-config                         2.77 GiB   1.79 points
qm delsnapshot 107 pre-ca-cert-reissue-20260908            0.71 GiB   0.46 points
qm delsnapshot 107 pre-cdp-setup-20260908                  0.46 GiB   0.30 points
qm delsnapshot 106 pre-crl-setup-20260908                  0.01 GiB   0.00 points
```
