# Pre-flight, and the standing on-premises grant B4 tests

## Pre-flight

Command: `date -u; qm status 100; lvs -a -o+data_percent,metadata_percent; free -h`
Host: Proxmox host shell
Timestamp: 2026-09-06T16:55:54Z

```
Sun Sep  6 04:55:54 PM UTC 2026
status: running
  LV                                                     VG  Attr       LSize    Pool Origin                        Data%  Meta%  Move Log Cpy%Sync Convert Data%  Meta% 
  data                                                   pve twi-aotz-- <155.23g                                    79.28  3.87                             79.28  3.87  
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
  snap_vm-107-disk-0_pre-adcs-config                     pve Vri---tz-k    4.00m data vm-107-disk-0                                                                      
  snap_vm-107-disk-1_pre-adcs-config                     pve Vri---tz-k   60.00g data vm-107-disk-1                                                                      
  swap                                                   pve -wi-ao----    8.00g                                                                                         
  vm-100-disk-0                                          pve Vwi-aotz--    4.00m data                               14.06                                   14.06        
  vm-100-disk-1                                          pve Vwi-aotz--   60.00g data                               43.98                                   43.98        
  vm-100-state-clean-install                             pve Vwi---tz--   <8.49g data                                                                                    
  vm-101-disk-0                                          pve Vwi-a-tz--    4.00m data snap_vm-101-disk-0_win11-ootb 14.06                                   14.06        
  vm-101-disk-1                                          pve Vwi-a-tz--   64.00g data snap_vm-101-disk-1_win11-ootb 47.29                                   47.29        
  vm-101-disk-2                                          pve Vwi-a-tz--    4.00m data snap_vm-101-disk-2_win11-ootb 1.56                                    1.56         
  vm-101-state-win11-ootb                                pve Vwi-a-tz--   <8.49g data                               43.63                                   43.63        
  vm-102-disk-0                                          pve Vwi-a-tz--    4.00m data                               14.06                                   14.06        
  vm-102-disk-1                                          pve Vwi-a-tz--   60.00g data                               31.03                                   31.03        
  vm-104-disk-0                                          pve Vwi-aotz--   20.00g data                               20.54                                   20.54        
  vm-106-disk-0                                          pve Vwi-aotz--    4.00g data                               16.35                                   16.35        
  vm-107-disk-0                                          pve Vwi-aotz--    4.00m data                               14.06                                   14.06        
  vm-107-disk-1                                          pve Vwi-aotz--   60.00g data                               18.91                                   18.91        
               total        used        free      shared  buff/cache   available
Mem:            15Gi       8.3Gi       5.8Gi        54Mi       1.2Gi       6.7Gi
Swap:          8.0Gi       549Mi       7.5Gi
```

Thin pool Data% 79.28 is under the 85 gate. The reading rose from 78.42 on 2026-09-05.

## Domain Admins membership

Command: `qm guest exec 100 --timeout 30 -- powershell.exe -NonInteractive -Command "Get-ADGroupMember -Identity 'Domain Admins' | Select-Object name,objectClass,distinguishedName | ConvertTo-Json -Compress"`
Host: DC01 (VM 100), through the QEMU guest agent
Timestamp: 2026-09-06T16:55:54Z or later, same console session

```
{
   "exitcode" : 0,
   "exited" : 1,
   "out-data" : "[{\"name\":\"Administrator\",\"objectClass\":\"user\",\"distinguishedName\":\"CN=Administrator,OU=Admins,DC=district,DC=local\"},{\"name\":\"System Admin\",\"objectClass\":\"user\",\"distinguishedName\":\"CN=System Admin,OU=Site 1,OU=Test Users,DC=district,DC=local\"}]\r\n"
}
```

## sysadmin standing state

Command: `qm guest exec 100 --timeout 30 -- powershell.exe -NonInteractive -Command "Get-ADUser -Identity sysadmin -Properties adminCount,whenChanged,memberOf | Select-Object SamAccountName,Enabled,adminCount,whenChanged,@{n='memberOf';e={\$_.memberOf -join ';'}} | ConvertTo-Json -Compress"`
Host: DC01 (VM 100), through the QEMU guest agent
Timestamp: 2026-09-06T16:55:54Z or later, same console session

```
{
   "exitcode" : 0,
   "exited" : 1,
   "out-data" : "{\"SamAccountName\":\"sysadmin\",\"Enabled\":true,\"adminCount\":1,\"whenChanged\":\"\\/Date(1788222424000)\\/\",\"memberOf\":\"CN=SG_Share_Site1_RW,OU=Resources,OU=Security,OU=Groups,DC=district,DC=local;CN=SG_admin_tier0_domain,OU=Admins,DC=district,DC=local;CN=Domain Admins,CN=Users,DC=district,DC=local\"}\r\n"
}
```

`whenChanged` 1788222424000 decodes to 2026-09-01T00:27:04Z.
