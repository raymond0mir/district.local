# Evidence log

Capture path: raw host-shell output from the Proxmox host (root@proxmox), pasted in by Raymond after running interactively. No `qm guest exec` / QEMU guest agent involved anywhere in this exercise — DC01 was down for part of it, and the rest is host-side (LVM, systemd, journal) diagnostics that don't go through the guest agent at all. No JSON envelope, no exit-code field — these are raw terminal transcripts, filed verbatim including the shell prompt lines.

| Evidence file | Command (verbatim) | Approx. time captured |
|---|---|---|
| `thin-pool-utilization-pre-crash-96pct.txt` | `lvs -a -o+lv_name,data_percent,metadata_percent,lv_size` | 2026-08-31, ~16:34 UTC (first diagnostic round, VM already down) |
| `vg-free-space.txt` | `vgs` | ~16:35 UTC |
| `journal-warning-priority-3hr.txt` | `journalctl --since "-3 hours" -p warning --no-pager \| tail -100` | ~16:35 UTC |
| `split-lock-detect-mode-and-trap.txt` | `cat /proc/cmdline \| grep -o 'split_lock_detect[^ ]*'; journalctl --since "-3 hours" --no-pager \| grep -iE "1968\|split_lock"` | ~16:41 UTC |
| `vm100-lifecycle-3hr-grep.txt` | `journalctl --since "-3 hours" --no-pager \| grep -iE "vm 100\|:100:\|qmeventd\|terminat\|signal 1968"` | ~16:41 UTC |
| `crash-window-narrow-unfiltered.txt` | `journalctl --since "09:37:30" --until "09:39:00" --no-pager` | ~16:46 UTC |
| `vm100-memory-config-and-host-free.txt` | `qm config 100 \| grep -i mem; free -h` | ~16:51 UTC |
| `coredump-check-empty.txt` | `coredumpctl list --since "-3 hours" 2>/dev/null; ls -la /var/crash/ 2>/dev/null` | ~16:51 UTC |
| `snapshot-prune-verification.txt` | `qm listsnapshot 100` and `lvs -a -o+lv_name,data_percent,metadata_percent,lv_size`, run after 5 `qm delsnapshot 100 <name>` calls | 2026-08-31, ~16:53 UTC |

Note on the deletion commands themselves: `qm delsnapshot 100 audit-fixed-20260829`, `ipconfig`, `postinstall-config`, `win2022servLOCK`, and `a826` were run sequentially per Raymond's confirmation, but their individual command output was not pasted back — only the pre-state (`thin-pool-utilization-pre-crash-96pct.txt`, captured earlier for an unrelated reason) and the post-state (`snapshot-prune-verification.txt`) were captured. This is a real gap: there is no per-command confirmation that each of the five deletions succeeded cleanly versus one silently no-op'ing. The before/after diff is strong secondary evidence — `qm listsnapshot 100` afterward shows exactly the two snapshots Raymond asked to keep (`clean-install`, `pre-sysadmin-admin-removal-20260831`) and no others, and pool usage dropped from 96.49% to 77.48% — but it's inference from state, not five individual captured confirmations. Flagged as **Recalled** rather than fully **Captured** for the per-snapshot deletion success, though the aggregate before/after state is captured directly.

Note on timestamps: none of this exercise's commands went through `qm guest exec`, so there's no server-side JSON timestamp to cite. Times above are approximate, based on when each block was pasted into the session.
