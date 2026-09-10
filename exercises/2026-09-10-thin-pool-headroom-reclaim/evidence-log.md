# Thin-pool headroom reclaim, 2026-09-10 — evidence log

A repository chore, not a portfolio exercise. It exists because the 85% stop condition in
`CARRYOVER.md` blocks every state change in the lab, and the previous reclaim
(`exercises/2026-09-02-thin-pool-headroom-reclaim`) has been consumed.

## Captured

- **Pool inventory, orphan check, snapshot tree and host memory, one reading at
  2026-09-10T18:00:17Z.** `evidence/01-pool-inventory-and-orphan-check.md`. It proves the six
  findings below.

**1. No orphan volumes exist.** `pvesm list local-lvm` returns 13 volumes. Every one carries a VMID
that still exists: 100, 101, 102, 104, 106, 107. Nothing can be reclaimed by deleting a disk whose
VM is gone. The 2026-09-02 reclaim used exactly that route, by destroying VM 105. That route is now
closed.

**2. Pool Data% is 84.23, and headroom to the gate is 0.77 points.** 0.77% of 155.23 GiB is about
1.20 GiB. Allocated is about 130.75 GiB of 155.23 GiB.

**3. The growth rate is about 4.6x the rate carryover extrapolated from.** The prior reading was
84.12 at 2026-09-10T14:13:49Z
(`exercises/2026-09-09-pim-for-groups/evidence/07-session-2-preflight.md`). This reading is 84.23 at
2026-09-10T18:00:17Z. That is 0.11 points in 3.77 hours, or 0.029 points per hour. Carryover's
figure was 0.15 points in 23.5 hours, or 0.0064 points per hour. At the newer rate the gate is
reached in about 26 hours, near 2026-09-11T20:00Z, not 2026-09-16. **Still two readings, not a
rate.** Both intervals carry the same VM state, VM 100 and VM 107 running, so VM count does not
explain the difference. What does explain it is not Captured.

**4. Only 40.53 GiB of the 130.75 GiB allocated can be attributed from this reading.** `lvs`
reports Data% for active volumes only. Five are active: `vm-100-disk-1` at 44.48% of 60 GiB
(26.69 GiB), `vm-107-disk-1` at 21.86% of 60 GiB (13.12 GiB), `vm-106-disk-0` at 18.08% of 4 GiB
(0.72 GiB), and two 4 MiB EFI disks. **About 90.22 GiB sits in inactive volumes and in snapshots,
and this reading measures none of it.** No prune target can be named from this output.

**5. The pool is over-committed about 1.84x.** Thin volumes provision about 285 GiB against a
155.23 GiB pool. The largest single items are `vm-101-disk-1` at 64 GiB, then `vm-100-disk-1`,
`vm-102-disk-1` and `vm-107-disk-1` at 60 GiB each.

**6. Two RAM-state volumes are provisioned at 8.49 GiB each.** `vm-100-state-clean-install` and
`vm-101-state-win11-ootb`, 9114222592 bytes apiece per `pvesm`. Both are inactive, so this reading
does not measure their allocation. `evidence/02` does; see Corrections.

- **Exclusive versus shared blocks for all 27 thin devices, at 2026-09-10T18:05:39Z.**
  `evidence/02-exclusive-blocks-per-thin-device.md`. `thin_ls` against a reserved metadata
  snapshot, joined to `lvs -o thin_id`. It proves findings 7 to 10 below.

**7. The largest reclaim by far is VM 101's `win11-ootb` snapshot: 18.31 GiB, or 11.80 points.**
That is `snap_vm-101-disk-1_win11-ootb` at 14.61 GiB exclusive, plus the `vm-101-state-win11-ootb`
RAM state at 3.70 GiB, plus two empty EFI snapshots. It is more than four times every VM 107
snapshot combined.

**8. The three VM 107 snapshots return 3.94 GiB together, and they are ordered opposite to age.**
`pre-adcs-config` 2.77 GiB, `pre-ca-cert-reissue-20260908` 0.71 GiB, `pre-cdp-setup-20260908`
0.46 GiB. The two September 8 snapshots are hours apart and share about 12.5 GiB each with the live
disk, so deleting either returns little. This confirms the caution recorded before the measurement:
chained snapshots share nearly everything.

**9. Copy-on-write against snapshots is a measurable share of pool growth.** `vm-100-disk-1` maps
26.69 GiB but holds only 5.32 GiB exclusively; 21.36 GiB is shared with its two snapshots. Those
5.32 GiB are blocks DC01 allocated since 2026-09-02 because a snapshot pinned the originals.
`vm-107-disk-1` shows the same shape at 1.12 GiB exclusive since 2026-09-08.

**10. Every volume in the estate is thin-provisioned, and 35.41 GiB of the pool is shared by two or
more devices.** Exclusive blocks sum to 95.34 GiB against 130.75 GiB allocated. No single deletion
frees a shared block.

- **Three snapshots deleted and the pool reclaimed, at 2026-09-10T18:10:11Z.**
  `evidence/03-three-snapshots-deleted-pool-reclaimed.md`. Data% 84.23 to 80.11, Meta% 4.21 to 3.84.
  All four exit codes 0.

**11. The reclaim beat the prediction by 0.66 GiB, and the reason is method, not luck.** 6.40 GiB
returned against 5.74 GiB predicted. `thin_ls` reports exclusivity per device. A block shared only
between two devices that are both deleted is exclusive to neither, and is freed anyway. **Summing
exclusive bytes across a deletion set gives a lower bound, not an estimate.**

**12. Headroom is 4.89 points, and the objective is met.** The 85 stop is no longer imminent. At the
0.029 points per hour observed today the gate returns near 2026-09-17.

## Not captured, and why

- **Exit code of the inventory command.** The block did not echo `$?`. `CLAUDE.md` requires the exit
  code on every capture. The output is complete and self-evidently succeeded, but the field is
  absent, and the file says so. Claude wrote that block and omitted the echo. Fixed in the next
  sequence.
- **The cause of the faster growth rate, in full.** Copy-on-write against snapshots is now
  measured and is part of it, per finding 9. Whether guest writes with no discard are the rest is
  untested. No `fstrim` or discard setting was read on any guest.
- **Where CT 103 (`vaultwarden`) stores its rootfs.** `pct list` proves it is running.
  `pvesm list local-lvm` returns no volume for VMID 103, so it lives on other storage. That storage
  was not enumerated.
- **Whether `qm listsnapshot 101` describes `win11-ootb` as VM 101's baseline.** It is VM 101's only
  snapshot, taken 2025-09-30, one day after the pool was created. Its description was not read; the
  command was run for VM 100 and VM 107 only.

## Where Raymond was consulted

- The snapshot-prune question stood open from 2026-09-10, recorded in `CARRYOVER.md` with the
  default "none without Raymond naming them". It was not re-asked before the measurement. Measuring
  exclusive blocks first is what made an answer to it meaningful.
- **2026-09-10, snapshot deletion.** Claude presented the per-operation reclaim figures from
  `evidence/02` and recommended deleting three snapshots whose after-states are confirmed:
  `100 pre-secure-admin-ws-relink-20260902`, `107 pre-ca-cert-reissue-20260908`, and
  `107 pre-cdp-setup-20260908`. Claude recommended keeping both `clean-install` baselines,
  `101 win11-ootb`, and `107 pre-adcs-config`. Raymond's decision, verbatim: "go ahead with those
  three". He named no additional object and did not take the larger 18.31 GiB reclaim on
  `101 win11-ootb`. The `CARRYOVER.md` pending decision is answered by this exchange.

## Corrections

- **Claude expected the two RAM-state volumes to be fully allocated, and they are not.**
  `evidence-log.md` recorded that expectation before the measurement, reasoning that a `vmstate`
  write dumps guest RAM in full. `thin_ls` disproves it: `vm-100-state-clean-install` holds 0.97 GiB
  against 8.49 GiB provisioned, and `vm-101-state-win11-ootb` holds 3.70 GiB. The volume is sized
  for guest RAM and allocated only for what was written. Stated here before being asked, per
  `CLAUDE.md`.
- **Carryover's gate estimate of about 2026-09-16 is superseded.** It was labelled indicative and
  derived from two readings. A third reading moves it to about 2026-09-11. Carryover is corrected at
  close.
- **`exercises/2026-09-09-pim-for-groups/evidence-log.md` lists "`report.md` for this exercise"
  under Not started, and that report exists.** Commit `4585f69` added `report.md` in the same commit
  that wrote the line. The line is stale. Corrected at close.

## Open questions

- Why has `vm-101-disk-1` diverged 29.63 GiB from the snapshot it was rolled back to on
  2026-09-03? The volume shares only 0.64 GiB with `snap_vm-101-disk-1_win11-ootb`. A stopped Win11
  client allocating 29 GiB of new blocks in seven days is not explained by this reading.
- Would enabling discard on the guests return any of the 95.34 GiB of exclusive blocks, or is the
  allocation genuinely in use? Untested, and it is the only reclaim route that costs no snapshot.
- Is `pve-root` at 69.37 GiB, holding about 23 GiB, a better reclaim target than any snapshot?
  `EXPOSURES.md` records it as a known inefficiency with real risk of an unbootable host.
- Does the 2 GiB `VFree` on the volume group still make the pool unextendable? `EXPOSURES.md`
  states it does, citing 2026-09-02 evidence. Not re-run.

## Not started

- The larger reclaim. `101 win11-ootb` still holds 18.31 GiB and was deliberately kept.
- `report.md`. This is a chore, and it earns a report only if the reclaim produces a finding worth
  publishing.
