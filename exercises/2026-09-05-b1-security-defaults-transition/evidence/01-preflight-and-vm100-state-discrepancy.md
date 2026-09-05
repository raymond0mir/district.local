Command (verbatim):
```
date -u
qm status 100
lvs -a -o+data_percent,metadata_percent
free -h
```
Host: Proxmox host console.
UTC timestamp: 2026-09-05T18:25:14Z.

```
Sat Sep  5 06:25:14 PM UTC 2026
status: running
  LV                                                     VG  Attr       LSize    Pool Origin                        Data%  Meta%  Move Log Cpy%Sync Convert Data%  Meta% 
  data                                                   pve twi-aotz-- <155.23g                                    64.74  3.36                             64.74  3.36  
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
  swap                                                   pve -wi-ao----    8.00g                                                                                         
  vm-100-disk-0                                          pve Vwi-aotz--    4.00m data                               14.06                                   14.06        
  vm-100-disk-1                                          pve Vwi-aotz--   60.00g data                               43.36                                   43.36        
  vm-100-state-clean-install                             pve Vwi---tz--   <8.49g data                                                                                    
  vm-101-disk-0                                          pve Vwi-a-tz--    4.00m data snap_vm-101-disk-0_win11-ootb 14.06                                   14.06        
  vm-101-disk-1                                          pve Vwi-a-tz--   64.00g data snap_vm-101-disk-1_win11-ootb 38.16                                   38.16        
  vm-101-disk-2                                          pve Vwi-a-tz--    4.00m data snap_vm-101-disk-2_win11-ootb 1.56                                    1.56         
  vm-101-state-win11-ootb                                pve Vwi-a-tz--   <8.49g data                               43.63                                   43.63        
  vm-102-disk-0                                          pve Vwi-a-tz--    4.00m data                               14.06                                   14.06        
  vm-102-disk-1                                          pve Vwi-a-tz--   60.00g data                               31.03                                   31.03        
  vm-104-disk-0                                          pve Vwi-aotz--   20.00g data                               18.51                                   18.51        
               total        used        free      shared  buff/cache   available
Mem:            15Gi        13Gi       1.2Gi        54Mi       419Mi       1.3Gi
Swap:          8.0Gi       988Ki       8.0Gi
```

Finding: VM 100 status is `running`. Carryover recorded VM 100 stopped as of
2026-09-05T16:51:16Z, at the prior exercise's close. This read contradicts that record.
Cause not yet determined. Pool Data% is 64.74, under the 85% gate. Available memory is 1.3Gi
with VM 100 and VM 104 both running.
