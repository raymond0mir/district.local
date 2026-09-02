# Reclaiming thin-pool headroom without external media

**Exercise:** A1 from `CURRICULUM.md`, run 2026-09-02.
**Result:** thin pool `Data%` **91.06% -> 70.86%**. The lab is back under its own stop threshold
with 21.95 GiB of margin, having spent nothing and attached no new hardware.

---

## What I set out to do

`CURRICULUM.md` states A1's hypothesis as: *an external `vzdump` target on the USB stick lets a
snapshot be pruned safely — reclaiming real on-pool space — without ever making removable media
part of the live LVM stack.*

The lab had been above the skill's 85% pre-flight gate since 09-01, which blocks every subsequent
exercise that installs an OS or writes significantly. A1 exists to unblock the rest of the plan.

**The hypothesis was wrong in all three of its parts.** There was no USB stick. Snapshots were
not the reclaimable resource. And external media was never required in the first place. This
report is the record of establishing that, and the honest version of it is more useful than the
one where the plan worked.

---

## The setup

Proxmox host (Dell Latitude 5420, i5-1145G7 4C/8T, 16 GB RAM in one of two SODIMM slots), single
`PC SN530 NVMe WDC 256GB`. Lab VMs: 100 `winserver2022` (DC01), 101 `win11-client01`,
102 `entraconnect01`, 104 `pfsense-fw`, 105 `kali-red`.

Pre-flight readings, `evidence/preflight-vg-headroom-and-media-20260902T1527Z.txt`, 15:27:45Z:

- thin pool `Data%` **91.00%**, `Meta%` 4.38% — above the 85% gate
- VG `pve`: `VSize 237.47g`, **`VFree 2.00g`**, single PV `/dev/nvme0n1p3`
- host RAM: **113Mi available** of 15Gi, 189Mi buff/cache, 1.4Gi swap in use
- `lsblk`: no USB mass-storage device attached; sole removable device `mmcblk0` at **30.6 MiB**

The 113Mi reading is the worst this lab has captured. For contrast, the 09-02 pre-flight caught
169Mi and treated it as alarming.

This capture also closes a standing evidence gap: the `vgs`/`pvs` figures behind "there is no
`lvextend` path" had only ever been quoted from an interactive exchange, never filed. They are
now filed.

---

## What I did

1. **Read the state properly before touching anything**, including `lsblk`, which is what revealed
   the USB stick was not attached. The 30.6 MiB SD card is three orders of magnitude short of a
   backup target for any VM here.

2. **Recomputed the overcommit ratio.** Total thin allocation **505.02 GiB against a 155.23 GiB
   pool = 3.25x**. `EXPOSURES.md` carried a stale "~3.6x (864.93 GiB against a 237.47 GiB volume
   group)" — that denominator is the *volume group*, but thin volumes are provisioned against the
   *pool*. Measured the same wrong way, today would read 2.13x, which would have looked like an
   improvement while the pool actually got fuller.

3. **Shut down VM 102** to recover RAM before any other work. `qm shutdown 102 --timeout 120`,
   exit 0. **113Mi -> 2.8Gi available.**

4. **Confirmed snapshot names with `qm listsnapshot` before deleting anything.** The four LVs
   visible in `lvs` are the backing volumes of *two* Proxmox snapshots, both named
   `pre-staging-promotion-20260902`.

5. **Pruned both**, with before/after captured inside the same command block one minute apart:
   `Data%` **91.06% -> 88.95%**, `#LV` 23 -> 19, both `qm delsnapshot` exit 0.
   Reclaimed **3.28 GiB** — short of the **6.13 GiB** needed to reach the gate.

6. **Measured what was actually on the pool.** `lvs` reports no `Data%` for inactive volumes, so
   I activated three, read them, and deactivated them again. This is where the exercise turned:
   `vm-105-disk-0` (Kali) held **28.12 GiB** — a stopped VM, no snapshots, the second-largest
   real consumer on the box, and nobody had ever looked at it.

7. **Found the backup target that was there all along.** `df -h /`: `pve-root` is 68G with
   **43G free**, a separate logical volume from the thin pool, already declared in
   `/etc/pve/storage.cfg` as `dir: local` with `content iso,vztmpl,backup`.
   `/var/lib/vz/dump/` was **empty** — this lab had never taken a backup.

8. **Backed up VM 105 to `local` and verified the archive.**
   `vzdump 105 --storage local --mode stop --compress zstd`, exit 0, 1m57s at 353 MiB/s,
   archive ~10-11 GiB. `zstd -t` exit 0, decompressed size 27.13 GiB.

9. **Destroyed VM 105.** `qm destroy 105 --purge`, exit 0.
   `Data%` **88.98% -> 70.86%**, `Meta%` 4.12% -> 3.47%. Archive confirmed still present
   afterward, because "the backup survived the destroy" is a claim worth capturing rather than
   assuming.

---

## Where Raymond was consulted

**1. Prune scope for the 09-02 snapshots.** Presented as a choice between all four backing
volumes, VM 102's pair only, or holding entirely, with the note that reclaim was unknown until
executed. He chose all four. *(Selection from options I drafted, not his own phrasing.)*

**2. The 113Mi RAM reading.** Offered: shut down VM 102, leave all three VMs running, or stop
lab work for the day. He chose shutting down 102. That single action recovered more RAM than
the entire 09-02 prune round had.

**3. Whether Kali held anything irreplaceable.** This was the decision the exercise turned on, and
it is not one I could answer from the host. He answered that nothing on it was irreplaceable.
*(Selection from options I drafted.)* Corroborating fact captured afterward:
`kali-linux-2026.1-installer-amd64.iso` is on the box, so the rebuild path is present, not
hypothetical, and `qm config 105` is nine lines, all captured.

**4. Hardware direction.** He asked directly whether the lab is hardware-limited and whether a
second MFF Dell, an iMac, or the Latitude itself is the constraint. After the captured answer, his
decision, verbatim: *"lets put aside the purchases, it can be something, lets just run lean on
what we got gonna run the code rn"*. That was the right call and the numbers bore it out —
the exercise completed with no purchase.

---

## What the box said

Pool, across the whole exercise:

| Point | `Data%` | Source |
|---|---|---|
| Pre-flight | 91.00% | `preflight-vg-headroom-and-media-20260902T1527Z.txt` |
| Immediately before prune | 91.06% | `prune-pre-staging-promotion-snapshots-20260902T1535Z.txt` |
| After prune | 88.95% | same file |
| Immediately before destroy | 88.98% | `destroy-vm105-pool-reclaimed-20260902T1607Z.txt` |
| **After destroy** | **70.86%** | same file |

Real consumption by volume, `inactive-volume-consumption-20260902T1537Z.txt`:

| Volume | LSize | Data% | Actual |
|---|---|---|---|
| `vm-101-disk-1` (Win11) | 64.00 GiB | 62.26% | 39.85 GiB |
| `vm-105-disk-0` (Kali) | 40.00 GiB | 70.30% | **28.12 GiB** |
| `vm-100-disk-1` (DC01) | 60.00 GiB | 42.73% | 25.64 GiB |
| `vm-102-disk-1` (entraconnect01) | 60.00 GiB | 24.90% | 14.94 GiB |
| `vm-101-state-win11-ootb` | 8.49 GiB | 43.63% | 3.70 GiB |
| `vm-104-disk-0` (pfSense) | 20.00 GiB | 14.68% | 2.94 GiB |
| `vm-100-state-clean-install` | 8.49 GiB | 11.37% | 0.97 GiB |

RAM, three readings: **113Mi -> 2.8Gi** (VM 102 shutdown) **-> 4.0Gi** (after prune and destroy).

---

## What broke, and why

**My conclusion that external media was a hard prerequisite. Retracted.**
Mid-exercise I wrote, in the evidence log and to Raymond directly, that the remaining reclaim
candidates were blocked because "there is still no backup target," and concluded that external
media was a hard prerequisite rather than a preference. That was wrong. `pve-root` is a separate
logical volume with 43 GiB free, already exposed by Proxmox as `local` storage with `backup` in
its content list. I equated "backup target" with "external device" and never ran `df`. The target
had been there the entire time, and the error was on track to recommend a hardware purchase that
was not required.

The limit of the correction, stated so it isn't overread: a backup on `pve-root` sits on the same
physical NVMe as the pool, so a drive failure takes both. It is a rollback point, not disaster
recovery. Adequate for "restore point before destroying a rebuildable VM," not adequate as this
lab's backup posture.

**Reading `LSize` as consumption — while flagging that exact error.**
I wrote a warning into the evidence log that `LSize` is virtual allocation and must not be read
as reclaimable space, and then two sections later described the RAM-state volumes as "~8.49 GiB
each" on the basis of their `LSize`. Measured, they hold 3.70 GiB and 0.97 GiB. Knowing the trap
by name was not sufficient to avoid it.

**A ledger row citing evidence that does not contain its own number.**
`verified-claims.md` recorded `Data%` "brought to 88.47%" and cited two evidence files. Neither
contains 88.47% — they show 92.01% and 88.99%. The 88.47% figure came from a third prune round
that was never captured to a file and existed only in report prose. Under the capture contract it
was **Recalled**, ineligible for the ledger, and it had already propagated into `EXPOSURES.md`,
`CARRYOVER.md`, and `CURRICULUM.md` — including the table gating Phase A. Corrected at this
exercise's close.

**Dated artifact names in this repo do not come from the lab's clock.**
`timedatectl`: host is `America/Los_Angeles (PDT, -0700)`, NTP synchronized, RTC in UTC. Both
snapshots named `pre-staging-promotion-20260902` were created **2026-09-01 23:35 UTC** — 09-01 in
both bases. The name asserts a date they were not taken on, and the exercise directory
`2026-09-02-entra-connect-upn-signin-test` carries the same offset. Cause: these dates came from
the assistant's session date rather than the host's clock, across a UTC midnight boundary.
Nobody is misled about lab state, but anyone correlating this repo against host-side logs lands a
day off, and checkability is the entire value of the evidence trail.

**What did not break, worth noting:** the prune ran correctly and did exactly what it was supposed
to. It simply was not enough, because superseded snapshots were never where the space was. A
correct action against the wrong target.

---

## What I'd do differently

**Measure before theorising about scarcity.** The exercise spent its first half reasoning about
which snapshot to prune and what media to buy, and its second half discovering that a stopped VM
nobody had looked at held 28.12 GiB — more than four times what was needed. `lvs` will not show
`Data%` for inactive volumes, so the largest reclaimable object on the box was invisible to every
previous capture. One `lvchange -ay` would have reordered the whole exercise.

**Read the host's own filesystem before reaching for hardware.** Same error in a different
costume. `df -h /` is one command and it invalidated a purchase recommendation.

**Derive dates from the machine, not from the session.** Every capture block in this exercise
self-timestamps with `date -u`. Snapshot names and exercise directories should do the same.

**On the estimate that was close:** the derived 28.12 GiB versus the actual 27.12 GiB of live
data is a 3.7% overshoot, and the gap is meaningful rather than noise. `vzdump` reported 12.88 GiB
(32%) of the disk as zeros — blocks allocated in the pool but freed inside the guest and never
discarded. Thin `Data%` measures allocation, not live data. Fine for sizing, wrong if quoted as
"how much is in there."

---

## Not the permission-sprawl thesis, but the same shape

`CURRICULUM.md` says A1 carries no SC-300 coverage and the report should say so plainly rather
than reach for a mapping that isn't there. It doesn't, and this isn't one.

What is worth naming is a structural rhyme, offered as analogy and not as a security finding.
Every resource this exercise recovered was allocated once and never revisited: 69.37 GiB of disk
to a host OS using 23 GiB, 10 GB of RAM to a domain controller, a 40 GiB Kali VM that had been
powered off and unmeasured, snapshots retained past the confirmation of the state they protected.
Nothing was misconfigured. Each allocation was defensible when made, nobody was wrong, and the
aggregate still walked the lab into its own stop threshold. That is the same failure mode as
standing access nobody removes because it might break something — the mechanism is *"granted
once, reviewed never,"* and it does not require anyone to make a mistake. The lesson transfers;
the finding does not.

---

## Open questions

- **The restore path is unverified.** `zstd -t` proves the archive is not corrupt. It does not
  prove a restore produces a bootable Kali. A real test needs pool space to restore into — which
  now exists (21.95 GiB of margin), so this is testable and was not tested.
- **21.93 GiB of pool consumption remains unattributed.** Named volumes summed to 116.15 GiB
  against a pool reporting 138.08 GiB before the destroy. The retained `clean-install` and
  `win11-ootb` snapshot sets are the likely holders, but both carry the `k` skip-activation
  attribute and were never activated with `lvchange -K` to read their `Data%`.
- **DC01 may be running on expired evaluation media.** `SERVER_EVAL_x64FRE_en-us.iso` is dated
  2025-09-29 and DC01's `clean-install` snapshot carries the same date — that correlation is
  **inference from two matching dates, not a capture**. Windows Server evaluation runs 180 days,
  which from that date elapsed around 2026-03-28. Either it was rearmed, activated, or the domain
  controller is past its window. Settled by `slmgr /dlv` on DC01.
- **RAM is over-allocated, and it is not primarily a hardware limit.** `qm list` shows
  10000 MB assigned to DC01, 4096 to VM 101, 3072 to VM 102, 2048 to pfSense — **18.77 GiB
  committed on a 15 GiB host, 3.77 GiB beyond physical.** That, not the hardware, is why three
  VMs drove available memory to 113Mi. Whether DC01 needs 10 GB for a lab domain of this size is
  untested and looks unlikely. Separately, `DIMM B` is empty and the board takes a second module.
- **`pve-root` holds 19 GiB of ISOs**, including two virtio images 754M each at different
  versions. Not binding now; free reclaim if wanted.
- **VM 102 is stopped and Entra Connect is not syncing.** Must be restarted before any
  sync-dependent exercise.
- **Whether the orphaned `qm guest exec` process (pid 4624) on DC01 still exists** was not
  checked this session. DC01's uptime was never read, so whether it rebooted since 09-02 is
  undetermined.
