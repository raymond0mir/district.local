# Evidence log — thin-pool headroom reclaim (Exercise A1)

Started 2026-09-02. In progress — this log is being written as the exercise runs, not after.

## Captured

1. `evidence/preflight-vg-headroom-and-media-20260902T1527Z.txt` — combined read-only sweep from
   the Proxmox host shell at 2026-09-02T15:27:45Z: `qm status 100`, `lvs -a` with data/metadata
   percentages, `vgs`, `pvs`, `free -h`, `lsblk`. Self-timestamped by the command, closing the
   timestamp gap that affected both 09-02 captures.

   This capture closes `CARRYOVER.md`'s open item "the `vgs`/`pvs` readings behind 'no room to
   extend the pool' were never filed as a proper evidence capture." They are now filed:
   VG `pve`, 1 PV, `VSize 237.47g`, `VFree 2.00g`; PV `/dev/nvme0n1p3`, `PSize 237.47g`,
   `PFree 2.00g`.

## Derived from the capture (arithmetic only, no new observation)

**Overcommit ratio, recomputed.** Sum of thin-provisioned `LSize` against the pool:

- snapshot volumes: 244.02 GiB
- live volumes (incl. two ~8.49 GiB RAM-state volumes): 261.00 GiB
- **total allocated: 505.02 GiB** against a **155.23 GiB** pool = **3.25x overcommitted**

**Correction to how this ratio was previously stated.** `EXPOSURES.md` carries a stale figure of
"roughly 3.6x overcommitted (864.93 GiB allocated against a 237.47 GiB volume group)." That
denominator is wrong for the quantity being described: thin volumes are provisioned against the
**pool** (155.23 GiB), not the volume group (237.47 GiB), so dividing by the VG understates
overcommit. Today's allocation measured the same (incorrect) way would read 2.13x — which would
have looked like an improvement from 3.6x while the pool got *fuller*, not emptier. The two
numbers were never comparable. Stated here rather than silently replaced.

## Mid-session finding: a ledger row cites evidence that does not contain its own number

`verified-claims.md` row 55 states `Data%` "was brought to 88.47% by pruning three already-
superseded snapshot pairs" and cites `preflight-thin-pool-and-memory-20260902.txt` and
`postprune-thin-pool-and-memory-20260902.txt`. Neither file contains 88.47%. The pre-flight file
shows 92.01%; the post-prune file shows 88.99%. The 88.47% figure came from a **third** prune
round (`pre-secure-admin-ws-scope-fix-20260901`) that was never captured to a file — it exists
only in `report.md` prose.

Under the capture contract, 88.47% is **Recalled**, not Captured, and was ineligible for the
ledger. It propagated from there into `EXPOSURES.md`, `CARRYOVER.md`, and `CURRICULUM.md` (twice,
including the gating table) as though it were captured. Today's reading supersedes the number
regardless, but the row's citation is wrong independent of that and is retracted on the record
here rather than edited away. `verified-claims.md` to be corrected at close.

Corroborating detail that the third prune did happen: the `pre-secure-admin-ws-scope-fix-20260901`
snapshot pair is present in the 88.99% capture and absent from today's `lvs`. So the prune is
real; only its resulting measurement is uncaptured.

## Not captured, and why

- **Actual space consumed by each snapshot.** `lvs` reports blank `Data%` for the snapshot and
  inactive volumes, so how much any individual snapshot would reclaim if deleted is **unknown**.
  `LSize` is virtual allocation and must not be read as reclaimable space. No prune here should be
  described in advance as freeing a specific amount.
- **What the pool does at 100%.** Still never observed. Unchanged from `EXPOSURES.md`.
- **Whether the orphaned `qm guest exec` process (pid 4624) on DC01 still exists.** Not checked
  this session. `qm status 100` reports `running`, but uptime was not read, so whether DC01
  rebooted since 09-02 is undetermined and the question stays open.

## Blocked

- **Exercise A1's premise cannot proceed as designed.** The plan is to use the USB stick as an
  external `vzdump` target. `lsblk` shows no USB mass-storage device attached. The only removable
  device present is `mmcblk0` at **30.6 MiB** — far too small to hold a backup of any VM here
  (the smallest, VM 104, is a 20 GiB volume). Until external media is actually attached and
  visible, there is no backup target, and the skill's rule that a snapshot is pruned only after
  its backup is verified cannot be satisfied for anything that is a sole rollback point.

---

## Captured (continued)

2. `evidence/vm102-shutdown-and-snapshot-names-20260902T1533Z.txt` — 2026-09-02T15:33:58Z.
   Confirmed both Proxmox snapshot names via `qm listsnapshot` before any destructive call
   (the four LVs seen in `lvs` are the backing volumes of **two** Proxmox snapshots, both named
   `pre-staging-promotion-20260902`). Shut VM 102 down gracefully, `exit 0`, `status: stopped`.
   RAM available moved **113Mi -> 2.8Gi**.

3. `evidence/prune-pre-staging-promotion-snapshots-20260902T1535Z.txt` — 2026-09-02T15:35:08Z.
   `qm delsnapshot 100 pre-staging-promotion-20260902` and `qm delsnapshot 102
   pre-staging-promotion-20260902`, both `exit 0`, four LVs reported removed by name.
   `vgs` `#LV` 23 -> 19, corroborating exactly four.

   Before/after captured inside the same command block, one minute apart:
   **`Data%` 91.06% -> 88.95%**, `Meta%` 4.39% -> 4.12%.
   RAM available **2.8Gi -> 4.0Gi**.

## Result against the hypothesis

Reclaimed: **3.28 GiB** (2.11 pp of a 155.23 GiB pool; 141.35 GiB -> 138.08 GiB consumed).
Still **6.13 GiB above** the skill's 85% gate. `VFree` unchanged at 2.00 GiB — pruning thin
snapshots returns blocks to the pool, not to the volume group, so the "no `lvextend` path"
constraint is untouched by this and always would have been.

**The exercise's hypothesis is not satisfied.** Pruning superseded snapshots was the only reclaim
available without external media, it was executed correctly, and it was not enough. The remaining
on-pool consumers are all blocked for reasons that are not about space:

- `clean-install` on VM 100 (plus `vm-100-state-clean-install`, ~8.49 GiB) — the named baseline
  the skill explicitly says to keep. Stamped **2025-09-29**, i.e. it is literally the Inherited
  October-2025 build baseline.
- `win11-ootb` on VM 101 (plus `vm-101-state-win11-ootb`, ~8.49 GiB) — VM 101's only rollback
  point, declined by Raymond on 2026-09-02 and not re-raised here.
- `vm-105-disk-0` (Kali, 40 GiB allocated) — inactive, so `lvs` reports no `Data%`; actual
  consumption **unmeasured**.

None of the three can be removed under the skill's own rule that a sole rollback point is pruned
only after a verified backup, because there is still no backup target. This converges on external
media being a hard prerequisite, not a preference.

## Finding: dated artifact names in this repo do not derive from the lab's clock

`timedatectl` on the Proxmox host: `America/Los_Angeles (PDT, -0700)`, NTP active, clock
synchronized, RTC in UTC. `qm listsnapshot` prints local time.

Both snapshots named `pre-staging-promotion-20260902` were created **2026-09-01 16:35 PDT =
2026-09-01 23:35 UTC** — 09-01 in *both* bases. The name asserts a date the snapshot was not
taken on. The same offset shows in the exercise directory `2026-09-02-entra-connect-upn-signin-test`,
whose evidence files carry `Sep 1` mtimes on Raymond's Mac.

Cause: these dates come from the assistant's session date, not from the host's clock, and the two
disagreed across a UTC midnight boundary. Consequence: anyone correlating this repo's exercise
and snapshot names against host-side logs will be off by a day. Not a security or integrity
problem, but it undercuts an evidence trail whose whole value is being checkable.

Convention worth adopting: derive snapshot names and exercise dates from the host's own
`date -u` output, which every capture block in this exercise already prints.

---

## Captured (continued)

4. `evidence/inactive-volume-consumption-20260902T1537Z.txt` — 2026-09-02T15:37:47Z. Activated
   three inactive thin volumes so `lvs` would report `Data%`, read them, deactivated all three.
   All six `lvchange` calls `exit 0`. No pool space consumed by activation.

**Real consumption, ranked (LSize x Data%):**

| Volume | LSize | Data% | Actual |
|---|---|---|---|
| `vm-101-disk-1` (Win11) | 64.00 GiB | 62.26% | 39.85 GiB |
| `vm-105-disk-0` (Kali) | 40.00 GiB | 70.30% | **28.12 GiB** |
| `vm-100-disk-1` (DC01) | 60.00 GiB | 42.73% | 25.64 GiB |
| `vm-102-disk-1` (entraconnect01) | 60.00 GiB | 24.90% | 14.94 GiB |
| `vm-101-state-win11-ootb` | 8.49 GiB | 43.63% | 3.70 GiB |
| `vm-104-disk-0` (pfSense) | 20.00 GiB | 14.68% | 2.94 GiB |
| `vm-100-state-clean-install` | 8.49 GiB | 11.37% | 0.97 GiB |

## Correction to an earlier figure in this same log

Above, under "Result against the hypothesis," the two RAM-state volumes were described as
"~8.49 GiB" each on the basis of their `LSize`. That was the exact mistake this exercise flagged
one section earlier — reading `LSize` as consumption — and I made it while flagging it.
Measured, they hold **3.70 GiB and 0.97 GiB, 4.67 GiB combined**, not ~17 GiB. Stated here rather
than corrected in place. Consequence: retaining both named baselines is cheap and there is no
space argument for touching either.

## What the measurement changes

`vm-105-disk-0` (Kali, VM 105) holds **28.12 GiB** — stopped, zero snapshots, and 4.6x the
**6.13 GiB** needed to clear the 85% gate. It is the only large consumer that is neither a
running production VM nor a retained rollback point.

**Not attributed:** the named volumes sum to 116.15 GiB against a pool reporting 138.08 GiB
consumed — a 21.93 GiB gap. The two retained snapshot sets (`clean-install`, `win11-ootb`) are
the likely holders, but their `Data%` was not read: both carry the `k` (skip-activation)
attribute and would need `lvchange -K` to activate, which was not done. The gap is therefore
**unmeasured**, not explained. Per-volume `Data%` counts referenced blocks, which can be shared
between an origin and its snapshot, so these figures bound the picture rather than partitioning it.

**Media spec, now answerable:** a `vzdump` of VM 105 must hold 28.12 GiB of used blocks
(compressed, so less in practice, but the target should be sized against the uncompressed figure,
not a hoped-for ratio). The only removable device present is `mmcblk0` at 30.6 MiB — short by
three orders of magnitude.

---

## Captured (continued)

5. `evidence/host-hardware-and-root-usage-20260902T1548Z.txt` — 2026-09-02T15:48:05Z. Host
   hardware inventory and root filesystem usage, prompted by Raymond asking whether the lab is
   hardware-limited.

   - `pve-root`: 68G, **23G used, 43G available (35%)**. Of that 23G, **19G is `/var/lib/vz`**
     — Proxmox's `local` storage directory (ISOs, templates, dumps). The host OS itself is using
     roughly 4G.
   - Host: **Dell Latitude 5420**. CPU **i5-1145G7**, 4 cores / 8 threads.
   - RAM: **2 SODIMM slots, one populated.** `DIMM A` = 16 GB DDR4-3200. **`DIMM B` = "No Module
     Installed."** The host is running single-channel on one stick.
   - Storage: single `PC SN530 NVMe WDC 256GB`. No second NVMe present.

## RETRACTION: "external media is a hard prerequisite" was wrong

Earlier in this log, under "Result against the hypothesis," I wrote that the remaining reclaim
candidates were blocked because "there is still no backup target," and concluded: "This converges
on external media being a hard prerequisite, not a preference." I repeated it to Raymond in
session. **That conclusion is withdrawn.**

It was wrong because I equated "backup target" with "external device" and never checked the host's
own filesystem. `pve-root` is a **separate logical volume from the thin pool** with **43 GiB
free**, already exposed by Proxmox as the `local` storage. A `vzdump` of VM 105 — 28.12 GiB of
used blocks, less once compressed — fits there with room to spare. The target existed for the
entire exercise and I did not look for it.

This is the same class of error as the `LSize`-vs-`Data%` slip corrected above: reasoning from
what a name suggests rather than from a reading. In this instance it produced a recommendation to
spend money on hardware that was not required.

**Scope of the correction.** Backing up to `pve-root` is a *rollback* point, not disaster
recovery: it lives on the same physical NVMe as the pool, so a drive failure takes both. That is
adequate for the stated purpose here (a restore point before destroying a rebuildable VM) and is
**not** adequate as this lab's general backup posture. The case for real external media stands on
its own merits; it just is not what blocks this exercise.

## Hardware constraint, answered

The question was whether the Latitude is the limit, or whether a second MFF Dell / an iMac is
needed. Captured answer:

- **Disk is the binding constraint.** 237.47 GiB VG on a 256 GB drive, of which 69.37 GiB
  (29%) went to `pve-root` at install time and only 23 GiB of that is used. The Latitude 5420
  has a single M.2 slot, so the upgrade path is *replacing* the 256 GB NVMe, not adding one.
- **RAM is not a hardware limit at all — there is an empty slot.** `DIMM B` is unpopulated. A
  second 16 GB DDR4-3200 SODIMM takes the host to 32 GB and restores dual-channel operation.
  This is the cheapest fix available to the lab and it requires no reinstall, no migration, and
  no second machine.
- **CPU has never been a measured constraint** and at 4C/8T is not the thing binding a five-VM
  lab.

A second physical host is therefore not required to unblock any current exercise. It remains
independently worth doing for *architecture* reasons a single node cannot demonstrate — a second
domain controller and real replication, or an attacker box on separate hardware from the domain's
own hypervisor — but that is a different exercise with a different justification, and it should
not be bought as a storage fix.

---

## Captured (continued)

6. `evidence/storage-config-iso-inventory-vm105-config-20260902T1551Z.txt` — 2026-09-02T15:51:25Z.
   `/etc/pve/storage.cfg` confirms `dir: local`, path `/var/lib/vz`, `content iso,vztmpl,backup`.
   `/var/lib/vz/dump/` **empty** — this lab had never taken a backup. ISO store is 19G across
   8 files including `kali-linux-2026.1-installer-amd64.iso` (4.5G) and two virtio images at
   754M each. Full `qm config 105` captured, nine lines.

7. `evidence/vzdump-vm105-to-local-verified-20260902T1555Z.txt` — 2026-09-02T15:55:48Z.
   `vzdump 105 --storage local --mode stop --compress zstd`, **exit 0**, 1m57s, 353 MiB/s,
   archive ~10-11 GiB. `zstd -t` **exit 0**, decompressed 27.13 GiB. Root 23G -> 33G used.
   *Excerpted:* the ~40 per-percent progress lines are omitted with a note in the file itself;
   all summary and result lines are verbatim.

8. `evidence/destroy-vm105-pool-reclaimed-20260902T1607Z.txt` — 2026-09-02T16:07:36Z.
   `qm destroy 105 --purge`, **exit 0**. `Data%` **88.98% -> 70.86%**, `Meta%` 4.12% -> 3.47%,
   `#LV` 18. Archive confirmed still present after the destroy. `VFree` unchanged at 2.00 GiB.

## Final result

**Reclaimed 28.13 GiB. Pool 91.06% -> 70.86%, under the 85% gate with 21.95 GiB of margin.**
No hardware purchased, no external media used, no snapshot deleted beyond the two confirmed-
superseded ones.

Prediction check: 70.84% predicted before the destroy from the measured 28.12 GiB, 70.86% actual —
0.02 pp. The earlier 3.7% overshoot in the *size* estimate (28.12 derived vs 27.12 GiB of live
data) did not propagate to the pool figure, because pool `Data%` tracks allocated blocks, which is
exactly what the derivation was based on.

## Two findings from `qm list` that outlive this exercise

- **VM 101 is `win11-client01`** — a stopped Windows 11 client, 64.00 GB boot disk, 4096 MB.
  This closes a standing **Recalled** claim (VM 101's purpose was only ever Raymond's
  description) with a host-side capture, and it means `CURRICULUM.md` exercise B1 needs no new
  Windows 11 build.
- **Host RAM is over-committed by 3.77 GiB.** 10000 MB to VM 100, 4096 to 101, 3072 to 102,
  2048 to 104 = 18.77 GiB on a 15 GiB host. The 113Mi pre-flight reading was an allocation
  problem, not a hardware ceiling.

## Not captured, carried forward

- Restore from the archive (only integrity was verified, not restorability).
- `Data%` of the two retained snapshot sets — 21.93 GiB unattributed.
- DC01 uptime, so pid 4624's fate stays undetermined.
- DC01's Windows licensing state (`slmgr /dlv`) — the evaluation-media question is inference only.
