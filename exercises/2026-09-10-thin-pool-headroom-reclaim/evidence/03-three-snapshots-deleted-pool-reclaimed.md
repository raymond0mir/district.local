# Three snapshots deleted, pool reclaimed

Command:

```
date -u; echo '--- before ---'; lvs -a -o+data_percent,metadata_percent | grep -E '^  data |LV '; echo '--- delete ---'; qm delsnapshot 100 pre-secure-admin-ws-relink-20260902; echo "del100 exit=$?"; qm delsnapshot 107 pre-ca-cert-reissue-20260908; echo "del107a exit=$?"; qm delsnapshot 107 pre-cdp-setup-20260908; echo "del107b exit=$?"; echo '--- settle ---'; sleep 20; echo '--- after ---'; lvs -a -o+data_percent,metadata_percent | grep -E '^  data |LV '; qm listsnapshot 100; qm listsnapshot 107; echo "final exit=$?"
```

Host: proxmox (host shell, Proxmox web console)
UTC: 2026-09-10T18:10:11Z

Exit codes: `del100 exit=0`, `del107a exit=0`, `del107b exit=0`, `final exit=0`.

Authorised by Raymond in session, verbatim: "go ahead with those three". See the evidence log.

```
Thu Sep 10 06:10:11 PM UTC 2026
--- before ---
  LV                                                     VG  Attr       LSize    Pool Origin                        Data%  Meta%  Move Log Cpy%Sync Convert Data%  Meta% 
  data                                                   pve twi-aotz-- <155.23g                                    84.23  4.21                             84.23  4.21  
--- delete ---
  Logical volume "snap_vm-100-disk-1_pre-secure-admin-ws-relink-20260902" successfully removed.
  Logical volume "snap_vm-100-disk-0_pre-secure-admin-ws-relink-20260902" successfully removed.
del100 exit=0
  Logical volume "snap_vm-107-disk-1_pre-ca-cert-reissue-20260908" successfully removed.
  Logical volume "snap_vm-107-disk-0_pre-ca-cert-reissue-20260908" successfully removed.
del107a exit=0
  Logical volume "snap_vm-107-disk-1_pre-cdp-setup-20260908" successfully removed.
  Logical volume "snap_vm-107-disk-0_pre-cdp-setup-20260908" successfully removed.
del107b exit=0
--- settle ---
--- after ---
  LV                                        VG  Attr       LSize    Pool Origin                        Data%  Meta%  Move Log Cpy%Sync Convert Data%  Meta% 
  data                                      pve twi-aotz-- <155.23g                                    80.11  3.84                             80.11  3.84  
`-> clean-install               2025-09-29 17:44:23     Fully patched + drivers, ready to clone
 `-> current                                            You are here!
`-> pre-adcs-config             2026-09-05 15:02:01     Before Install-AdcsCertificationAuthority. Role binaries installed, domain joined, no CA configured.
 `-> current                                            You are here!
final exit=0
```

## Result against prediction

Data% 84.23 to 80.11. That is 4.12 points, or 6.40 GiB of the 155.23 GiB pool. Meta% 4.21 to 3.84.

`evidence/02` predicted 5.74 GiB from summing exclusive bytes. The actual reclaim exceeded the
prediction by 0.66 GiB.

**The exclusive-byte sum is a lower bound when several devices are deleted together.** A block
shared only by `snap_vm-107-disk-1_pre-ca-cert-reissue-20260908` and
`snap_vm-107-disk-1_pre-cdp-setup-20260908` counts as SHARED for both devices and as exclusive to
neither. Deleting both frees it. `thin_ls` reports exclusivity per device, not per deletion set.

Headroom to the 85 stop is now 4.89 points. At the 0.029 points per hour observed on 2026-09-10 that
is about 168 hours, near 2026-09-17.
