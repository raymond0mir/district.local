# Evidence log

Two capture paths in this exercise, and they don't carry equal weight:

1. **Proxmox host shell** (`qm create`, `qm config`, `qm agent`, `qm guest exec`) — genuine terminal output, pasted by Raymond, filed as text/JSON exactly like every other exercise in this project.
2. **Proxmox noVNC console, screen-shared as screenshots** — everything from Windows Setup through the domain join. This is **not** filed as evidence under this project's capture contract; a screenshot is informational, same treatment as the October Entra tenant screenshot in the hybrid-identity exercise. The reason is structural, not a shortcut: no QEMU Guest Agent exists inside the VM until near the very end of the build, so there is no `qm guest exec` channel to capture real command output through for most of this exercise. The narrative in `report.md` covering OS install, driver loads, and domain join is reconstructed from what was visible on screen, not from filed command output — stated plainly there rather than presented as uniformly captured.

| Evidence file | Command / source | Type |
|---|---|---|
| `proxmox-preflight-before-build.txt` | `qm status 100; lvs -a -o+lv_name,data_percent,metadata_percent,lv_size; free -h` | Captured, host shell |
| `iso-inventory-and-vm-list.txt` | `ls -la /var/lib/vz/template/iso/` ; `qm list` | Captured, host shell |
| `dc01-hardware-config-baseline.txt` | `qm config 100` | Captured, host shell |
| `vm102-created.txt` | `qm create 102 ...` (full command in file) | Captured, host shell |
| `guest-agent-verified.json` | `qm agent 102 ping` ; `qm guest exec 102 -- cmd.exe /c hostname` | Captured, host shell |

**Not filed, informational only (console screenshots, described in report.md's What I did / What the box said):**
- Windows Setup language/edition screens
- Disk selection requiring a VirtIO storage driver load (`vioscsi\2k22\amd64`)
- Install progress and completion
- Server Manager post-install state (computer name, OS version, RAM/disk figures, benign SPP/DCOM boilerplate log entries)
- Network Connections showing zero adapters (missing NetKVM driver), and the adapter appearing with a full DHCP lease after the driver was loaded
- Static IP configuration screen (`10.0.0.11` / `255.255.255.0` / gateway `10.0.0.1` / DNS `10.0.0.10`)
- `nslookup district.local` / `ping dc01.district.local` pre-join sanity check (clean, 0% loss)
- Post-join Server Manager state (`DISTRICT.LOCAL`, activated Product ID, Time-Service/DNS-Client warning noise)
- Device Manager showing an unrecognized "PCI Simple Communications Controller" (missing `vioserial` driver, blocking the guest agent's communication channel) before that driver was loaded

## Corrections made during this exercise, on the record

**"No driver load needed" was asserted and was wrong.** After the disk-selection screen, Raymond reported "disk showed up, installing now" without confirming whether a driver load had occurred. That was read as "it auto-detected," stated as a finding, and was incorrect — Raymond clarified moments later that he had in fact loaded the VirtIO storage driver. Corrected immediately rather than left standing. Lesson applied for the rest of the exercise: don't infer a mechanism from an ambiguous status update when the actual mechanism can just be asked about directly.

**A repeating pattern, not three unrelated glitches.** Three separate points in this build hit the same underlying shape of problem: Windows Setup or a fresh install only prompts for (or ships inbox support for) the VirtIO driver that's immediately blocking — storage, to see the disk. The network adapter (NetKVM) and the serial channel the guest agent depends on (vioserial) both required a manual driver load discovered only once each one's absence blocked the next step (no network adapter at all; guest agent installed but "not running"). Sweeping Device Manager once for every "Other devices" entry immediately after first boot, rather than reactively chasing each blocker as it appeared, would have caught all three in one pass — see report's What I'd do differently.
