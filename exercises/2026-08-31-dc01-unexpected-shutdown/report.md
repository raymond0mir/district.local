# DC01 unexpected shutdown — crash investigation and thin-pool remediation

## What I set out to do

This wasn't planned. Mid-way through the `2026-08-31-dc01-constrained-admin-path` exercise, DC01 (VM 100) went down with no operator action behind it — Raymond hadn't stopped it, and restarting it wasn't enough to explain why it had gone down in the first place. Rather than restart and move on, the goal became: find the actual mechanism, using only what the host's own logs and tooling could confirm, and rule hypotheses out explicitly rather than settle on the first plausible-sounding one.

Retrospective note: this report is written after the investigation and remediation were already done, in the same session they happened in, not reconstructed from memory afterward — but per the capture contract, that distinction is worth stating plainly rather than letting the report read as if it were drafted live.

## The setup

Same lab as the constrained-admin-path exercise: single-DC forest `district.local`, DC01 = VM 100 (Windows Server 2022, `10.0.0.10`), on Proxmox host `proxmox`. DC01 has no remoting (WinRM/RDP/PS remoting all disabled by design); the only path in when it's up is `qm guest exec` over the QEMU guest agent. When it's down, that path doesn't exist at all — this exercise is entirely host-side: `qm`, `lvs`/`vgs`, and `journalctl` run directly on the Proxmox host by Raymond, with output pasted back for filing.

Storage backend: an LVM thin pool (`pve-data-tpool`) on a single physical volume, 237.47 GiB volume group. At the point this exercise starts, that pool had already been flagged as a risk (in the prior exercise's Open Questions) at 864.93 GiB of allocated snapshot volumes against the 237.47 GiB VG — that's virtual/allocated size, not actual data consumption, and this exercise is what put a real, current number on the latter for the first time.

Four VMs share the pool: 100 (DC01), 101 (a Windows 11 box), 104 (pfSense), 105 (Kali). VM 100 alone was carrying seven Proxmox snapshots at the start of this exercise.

## What I did

No `qm guest exec` in this exercise — DC01 was down for the first half of it, and the rest is host-level diagnosis that doesn't touch the guest at all. In order:

1. `lvs -a -o+lv_name,data_percent,metadata_percent,lv_size` — first read of pool health, prompted by DC01 being unexpectedly down.
2. Attempted the exercise's actual next planned command (`qm guest exec 100 ... Get-ADGroup ... objectSid ...`) — this is what surfaced the down state in the first place: it returned `VM 100 is not running` instead of JSON.
3. `vgs` — volume-group-level free space, to separate "pool is full" from "VG is full."
4. `journalctl --since "-3 hours" -p warning --no-pager` — first log sweep, warning priority and above.
5. `cat /proc/cmdline | grep -o 'split_lock_detect[^ ]*'` and `journalctl ... | grep -iE "1968|split_lock"` — chasing a specific lead surfaced by step 4, a split-lock trap logged at 08:57:13 against a KVM-tagged PID.
6. `journalctl --since "-3 hours" --no-pager | grep -iE "vm 100|:100:|qmeventd|terminat|signal 1968"` — full VM 100 lifecycle across the window, to build an actual timeline instead of reasoning from isolated lines.
7. `journalctl --since "09:37:30" --until "09:39:00" --no-pager` — once step 6 pinpointed the crash to 09:38:11, a full unfiltered dump of the two minutes around it.
8. `qm config 100 | grep -i mem` and `free -h` — checking VM 100's configured RAM against a fact step 7 surfaced (a 9.8G memory peak logged for the dying process's cgroup scope).
9. `coredumpctl list --since "-3 hours"` and `ls -la /var/crash/` — checking for a crash dump as a last direct check before concluding the mechanism couldn't be pinned down further from host logs alone.

Then, once Raymond decided to prune rather than just document the pool pressure:

10. Five `qm delsnapshot 100 <name>` calls — `audit-fixed-20260829`, `ipconfig`, `postinstall-config`, `win2022servLOCK`, `a826` — leaving `clean-install` and `pre-sysadmin-admin-removal-20260831` as VM 100's only remaining snapshots. Raymond chose which to keep and which to drop; I flagged `audit-fixed-20260829` specifically as uncertain (possible tie to the lab's known imported-audit-baseline defect) rather than assuming it was safe, and he included it in the prune list anyway — his call to make, not mine to infer from the name.
11. `qm listsnapshot 100` and `lvs -a -o+lv_name,data_percent,metadata_percent,lv_size` — post-prune verification.

Full commands and capture notes, including a gap in what step 10 captured, are in [`evidence/evidence-log.md`](evidence/evidence-log.md).

## Where Raymond was consulted

Two points in this exercise, both quoted verbatim from the session rather than paraphrased, since both happened in-session and the exact wording is available.

**1. Whether to write this up at all, and in what order.** Once the crash investigation had run out of confirmable leads (after the empty coredump check), I asked: *"Want me to write this up as its own incident record... Separately... do you want to look at pruning some of the older ones... or leave that for later?"* Raymond's answer set both the scope and the sequencing: *"i think it needs its own entry, but before we make an entry, lets attempt a clean up and best setup to future proof our exercises."* That's why this report exists after the remediation and the skill update rather than before them — his call, not a default ordering I picked.

**2. Which snapshots to prune.** I laid out the current snapshot inventory by VM, recommended `pre-sysadmin-admin-removal-20260831` and `clean-install` as keep-candidates, and flagged `audit-fixed-20260829` specifically as uncertain — a possible tie to the lab's known imported-audit-baseline defect, not something to infer as safe-to-delete from its name alone. I asked him to confirm the list rather than proceeding on my own read of the names. His answer: *"Prune audit-fixed-20260829, ipconfig, postinstall-config, win2022servLOCK, a826."* He included the one I'd flagged as uncertain — a deliberate call on his part, made with the caveat in front of him, not an oversight on mine. Worth being precise about that distinction: I raised the flag, he weighed it and decided anyway. See Open Questions for what that decision forecloses.

## What the box said

**Thin pool at the start of the investigation** (`evidence/thin-pool-utilization-pre-crash-96pct.txt`) — `pve-data-tpool` at **96.49% Data%**, 4.74% Meta%, on a 141.23 GiB pool. That's roughly 4.95 GiB of actual free space across every volume and snapshot sharing that pool. **Captured.**

**VG-level free space** (`evidence/vg-free-space.txt`) — `pve` VG: 237.47g total, **16.00g VFree**. **Captured.** This matters because it separates two different kinds of "full": the thin pool itself wasn't sized to use the whole VG, so there was headroom to extend the pool if needed — the 96.49% figure is the pool's own internal pressure, not a hard VG-level wall.

**Warning-level journal sweep** (`evidence/journal-warning-priority-3hr.txt`) surfaced two load-bearing facts:
- `dmeventd[425]: WARNING: Thin pool pve-data-tpool data is now 96.39% full.` at 08:34:40, and `96.45% full` at 09:11:34 — the host's own monitor confirming the pool was climbing, not just a single `lvs` snapshot catching it mid-spike.
- `x86/split lock detection: #AC: CPU 0/KVM/1968 took a split_lock trap at address: 0xfffff804726dfdff` at 08:57:13 — the lead that turned into a full side-investigation.

Both **captured**, at warning priority — meaning if the eventual crash had logged anything at `err` or above through this same query, it would have shown up here too. It didn't.

**Split-lock mode and trap** (`evidence/split-lock-detect-mode-and-trap.txt`):
```
x86/split lock detection: #AC: crashing the kernel on kernel split_locks and warning on user-space split_locks
x86/split lock detection: #AC: CPU 0/KVM/1968 took a split_lock trap at address: 0xfffff804726dfdff
```
**Captured**, and this rules the hypothesis out directly rather than by absence: the host's own boot-time message states its split-lock policy is warn-only for user-space (guest vCPU) traps, fatal only for kernel-space ones. CPU 0/KVM/1968's trap is the user-space case. Combined with the timeline below — DC01 kept running for another 41 minutes after this, through a full snapshot operation — this is closed. It's a real, logged event; it isn't the cause.

**Full VM 100 lifecycle across the window** (`evidence/vm100-lifecycle-3hr-grep.txt`) is what actually pinned down the crash moment:
```
08:37:43  VM 100 started with PID 1905.
08:55:22–08:56:57  vnc proxy session (Raymond viewing the console)
09:11:22–09:11:25  qm snapshot 100 pre-sysadmin-admin-removal-20260831  (the constrained-admin-path exercise's pre-change snapshot)
09:38:11  qmeventd[827]: read: Connection reset by peer
09:38:11  qmeventd[11866]: Starting cleanup for 100
09:38:11  qmeventd[11866]: Finished cleanup for 100
09:38:56  VM 100 started with PID 12012.  (the restart Raymond performed)
```
**Captured.** `qmeventd` watches each VM's QMP monitor socket; "Connection reset by peer" is what it sees when QEMU's own process dies out from under it without a clean shutdown handshake — this is the actual "went down on its own" event, not an inference. PID 1905 is the process that died; PID 12012 is the one that replaced it.

**Narrow window around 09:38:11** (`evidence/crash-window-narrow-unfiltered.txt`), unfiltered, everything the host logged in that two minutes:
```
09:38:11  100.scope: Deactivated successfully.
09:38:11  100.scope: Consumed 3min 39.271s CPU time, 9.8G memory peak.
```
plus network-interface teardown lines (`tap100i0`, `fwbr100i0`, `fwpr100p0` disabling) — the downstream effect of the process disappearing, not a cause. **Captured**, and the load-bearing fact here is negative: no dm-thin space-exhaustion message, no OOM-killer line, nothing at `err` or above at all in this window. Whatever killed PID 1905, it didn't leave the signature either of those failure modes usually leaves.

**Memory configuration vs. host headroom** (`evidence/vm100-memory-config-and-host-free.txt`):
```
memory: 10000
Mem:  15Gi total, 11Gi used, 3.7Gi free, 3.8Gi available
Swap: 8.0Gi total, 0B used
```
**Captured.** VM 100 is configured for 10000 MiB (~9.77 GiB) RAM — almost exactly the 9.8G peak the dying scope reported. That's a real correlation. It is not proof: a VM legitimately using close to its full assigned memory is normal, unremarkable behavior on its own, and nothing in any log confirms a memory-triggered kill (cgroup-scoped OOM kills log a specific `Memory cgroup out of memory: Killed process...` line — the same kind of unmissable message system-wide OOM kills produce — and it isn't present anywhere in this exercise's captures). The `free -h` reading is also *post-crash, post-restart* state, not the state at 09:38:11 — worth being explicit that it doesn't directly describe the moment in question.

**Core dump check** (`evidence/coredump-check-empty.txt`) — both `coredumpctl list` and `ls /var/crash/` returned nothing. **Captured** as a negative result. Either core dump collection isn't configured on this host, or the process didn't die from a signal in a way that produces one — this check can't distinguish between those two explanations, which is itself worth naming rather than picking one.

### Remediation: pruning VM 100's snapshots

**Post-prune state** (`evidence/snapshot-prune-verification.txt`) — after five `qm delsnapshot 100 <name>` calls (`audit-fixed-20260829`, `ipconfig`, `postinstall-config`, `win2022servLOCK`, `a826`):
```
qm listsnapshot 100:
  clean-install (2025-09-29)
  pre-sysadmin-admin-removal-20260831 (2026-08-31)
  current

lvs: pve-data-tpool Data% = 77.48%, Meta% = 3.63%
```
**Captured** for the end state. Pool usage dropped from 96.49% to 77.48% — roughly 19 percentage points of a 141.23 GiB pool, on the order of 26.8 GiB freed. VM 100 now carries exactly the two snapshots Raymond chose to keep and no others.

What's **not** captured, and is logged as a gap rather than smoothed over: the five `qm delsnapshot` calls themselves were run without their individual output being pasted back. There's no per-command confirmation that each succeeded cleanly rather than, say, one silently no-op'ing on a name that didn't match. The before/after diff is strong evidence — exactly two snapshots remain, exactly the two requested, and pool usage moved by an amount consistent with removing five ~60 GiB-class disk-1 snapshots — but it's evidence by inference from state, not five individually confirmed successes. See Open Questions.

## What broke, and why

The proximate finding is uncomfortable but real: **the crash's root cause could not be pinned down from this host's logs**, despite methodically checking every mechanism that normally leaves a trace. Split-lock — ruled out directly (logged as non-fatal by the host's own stated policy, and the VM operated normally for 41 minutes afterward). System-wide or cgroup OOM-kill — ruled out by absence of the specific, hard-to-miss kernel message that mechanism always produces, checked at both a broad warning-level sweep and a narrow unfiltered dump of the exact crash window. Thin-pool exhaustion — real correlation (96.45% and climbing, snapshot operation 27 minutes before the crash), no confirming error at the crash instant. A configured-memory ceiling — real correlation (10000 MiB configured vs. 9.8G peak reported), no confirming kill message. A signal-driven crash — no core dump to confirm or examine.

That's not a failure of the investigation; it's what an honest investigation looks like when the evidence runs out. The instinct to pick the most plausible-sounding of the two remaining correlated candidates and write it up as "the cause" was there, and resisting it is the actual point of this report — a portfolio piece that quietly overclaims a root cause it didn't have is a worse artifact than one that names the limit of what host logs could prove.

Separately: the local-log path guesses I made mid-investigation (`/var/log/pve/qemu-server/100.log`, a `qemu-server@100` systemd unit) were both wrong for this Proxmox install — dead ends that cost a round trip each, not filed as evidence because they produced no output to file, but worth naming here as exactly the kind of guess that should have been checked against how this specific host is actually configured (no per-VM systemd unit, no persistent qemu-server log path) before being handed over as a command to run.

## What I'd do differently

Check thin-pool and host-memory headroom *before* starting any exercise that runs commands against or changes DC01, not after something goes wrong. That's now written into the scoped skill (`.claude/skills/tech-compass/SKILL.md`) as a standing pre-flight step, specifically because this exercise is the reason it needed to exist — better to have it as a boring thirty-second check every time than to reconstruct a timeline after a crash to find out it would have caught this in advance.

I'd also have checked the actual log-capture setup for this Proxmox host (does QEMU stderr go anywhere? is `coredumpctl` even configured to collect for this cgroup delegate?) before assuming the standard paths would work. Two of my early diagnostic commands were built on guessed conventions rather than confirmed ones, and both failed cleanly — which is fine, a clean failure is still evidence — but a five-second check first would have saved the round trip.

On the remediation side: capture each `qm delsnapshot` call's own output next time, even when a before/after `lvs` diff is going to prove the aggregate result anyway. Five individual confirmations is a stronger record than one aggregate diff, and it's barely more work to ask for.

## Open questions

- **Update — this exercise recurred.** A second occurrence of the identical crash signature (`qmeventd`: "Connection reset by peer", ungraceful, not a clean shutdown) happened later the same day, during the entra-connect-install exercise, while VM 102's Windows Server install was writing real data to the pool concurrently. Full diagnosis in `evidence/second-occurrence-crash-signature.txt`. **The root cause is still not confirmed** — the pool was measured at 86.48% only after the crash and after continued install activity, not at the exact crash instant, so this strengthens the thin-pool-pressure candidate's plausibility without actually proving it caused either occurrence. Stated as narrowing, not closing.
- **Resolved: the pool extension alternative was tested.** `lvextend -L +14G pve/data`, using confirmed-still-available VG free space (16.00 GiB, re-verified via `vgs` before acting, unchanged since this exercise's original reading). Combined with pruning VM 101's and VM 104's previously-untouched snapshots, Data% dropped from 86.48% to **73.00%** — better than either action alone would have achieved. Full detail in `evidence/pool-extended-and-pruned.txt`.
- **Resolved: VM 101 and VM 104's snapshots were pruned**, per Raymond's direct instruction once pool pressure recurred — exactly the scenario this exercise's own open question anticipated ("in scope for space if pool pressure becomes a problem again"). `a829` (VM 101) and all three of VM 104's snapshots (`postdiodeisolated`, `stable`, `stableconfiged`) removed. **New consequence worth carrying forward: VM 104 (pfSense) now has zero snapshots** — flagged explicitly before the deletion, not discovered after. If a future firewall config change goes wrong, there is currently no rollback point for the router.
- **New, from this round: the process gap that let the pool exceed threshold undetected.** The preflight before VM 102 was created passed cleanly (78.63%). No recheck happened once the VM's OS install began writing significant data, and a preflight is a point-in-time gate, not a standing guarantee — a concurrent large install is exactly the condition that can push a passing pool over the line before the next planned checkpoint. Worth a standing practice: recheck pool state after any exercise involving a large install or disk-heavy operation, not just before starting.
- **Whether the five original `qm delsnapshot` calls (VM 100's prune) each succeeded cleanly is inferred, not individually confirmed** — the *second* round of pruning (VM 101/104, this update) captured each call's own output individually, applying the lesson from this exact gap; the original round did not, and that gap in the original evidence is unchanged.
- **Whether `audit-fixed-20260829` had any connection to the lab's known imported-audit-baseline defect is now unanswerable — it's deleted.** Unchanged from the original finding.
- **What actually happens on this host when the thin pool hits 100% is still unknown.** Unchanged — it has come close twice now (96.49%, then 86.48%) but the boundary itself has never been crossed and observed directly.
