# Pre-flight, second session of this exercise

## Capture

```
command: date -u; qm status 100; qm status 107; lvs -a -o+data_percent,metadata_percent; free -h
host:    proxmox (host shell, Proxmox web console)
utc:     2026-09-10T14:13:49Z
```

```
Thu Sep 10 02:13:49 PM UTC 2026
status: running
status: running
  LV                                                     VG  Attr       LSize    Pool Origin                        Data%  Meta%
  data                                                   pve twi-aotz-- <155.23g                                    84.12  4.21
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
  vm-100-disk-0                                          pve Vwi-aotz--    4.00m data                               14.06
  vm-100-disk-1                                          pve Vwi-aotz--   60.00g data                               44.48
  vm-100-state-clean-install                             pve Vwi---tz--   <8.49g data
  vm-101-disk-0                                          pve Vwi---tz--    4.00m data snap_vm-101-disk-0_win11-ootb
  vm-101-disk-1                                          pve Vwi---tz--   64.00g data snap_vm-101-disk-1_win11-ootb
  vm-101-disk-2                                          pve Vwi---tz--    4.00m data snap_vm-101-disk-2_win11-ootb
  vm-101-state-win11-ootb                                pve Vwi---tz--   <8.49g data
  vm-102-disk-0                                          pve Vwi---tz--    4.00m data
  vm-102-disk-1                                          pve Vwi---tz--   60.00g data
  vm-104-disk-0                                          pve Vwi---tz--   20.00g data
  vm-106-disk-0                                          pve Vwi-a-tz--    4.00g data                               18.08
  vm-107-disk-0                                          pve Vwi-aotz--    4.00m data                               14.06
  vm-107-disk-1                                          pve Vwi-aotz--   60.00g data                               21.86
               total        used        free      shared  buff/cache   available
Mem:            15Gi        11Gi       2.2Gi        50Mi       1.4Gi       3.2Gi
Swap:          8.0Gi          0B       8.0Gi
```

No exit code was captured. The commands ran in the host shell directly, not through
`qm guest exec`, so no exit-code field exists to record.

## What this establishes

- VM 100 (DC01) and VM 107 (CA01) are running. `qm status` returned `running` for both.
- Thin pool `pve/data` is at Data% 84.12, Meta% 4.21. The stop condition is Data% 85 or higher.
  Headroom at this reading is 0.88 points.
- Host memory shows 11 GiB of 15 GiB used and 3.2 GiB available. Swap is untouched at 0 B.

## The pool rose while nothing was provisioned

The previous reading was Data% 83.97 at 2026-09-09T14:41:18Z. This reading is 84.12 at
2026-09-10T14:13:49Z. The pool rose 0.15 points across approximately 23.5 hours. No VM was
created, no snapshot was taken, and no disk was extended in that window. The session between the
two readings touched the Entra tenant only.

**Two readings are not a trend.** This file records a second data point, not a rate. The
mechanism is nonetheless ordinary: thin volumes grow when a running guest writes, and nothing
returns freed blocks to the pool without discard or TRIM from inside the guest. Idle running VMs
therefore consume pool.

The consequence is specific to this lab's stop condition. The 85% gate can be crossed with no
administrative action at all, by leaving DC01 and CA01 running. That is a different failure mode
from the one the gate was written for, which assumed consumption follows a deliberate change.

Related standing entries in `EXPOSURES.md`: unattributed pool consumption, and the untested
behavior of this pool at 100%.

## Not established

- Whether VM 106 is running. Its LV shows the `a` (active) attribute without the `o` (open)
  attribute that VM 100 and VM 107 carry. `qm status 106` was not run, so no claim is made.
- The rate of idle pool growth. Establishing it needs readings across more than two points.
- Whether discard is enabled on any guest disk in this lab.
