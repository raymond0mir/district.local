# Building the Entra Connect member server

## What I set out to do

The hybrid-identity exercise left one prerequisite unbuilt: a domain-joined Windows Server member server to eventually host Entra Connect. Installing Connect directly on DC01 is supported by Microsoft but not best practice, and "why not on the DC" is exactly the kind of thing worth having actually built the correct way rather than just knowing the rule. This exercise is that build: a fresh VM, Server 2022 with Desktop Experience (Connect doesn't run on Server Core — a hard requirement, not a preference), domain-joined, and reachable via the same `qm guest exec` automation this entire project depends on.

## The setup

Proxmox host, same as every exercise. Preflight before touching anything: thin pool at 78.63% (still under the 85% stop-threshold, slightly up from the last two checks), but **memory was tight** — only 3.7Gi free / 3.8Gi available, since VM 100 (DC01, 10GB configured) and VM 104 (pfSense, 2GB) were both already running. Full readout in `evidence/proxmox-preflight-before-build.txt`.

Both required ISOs already existed on the host — `SERVER_EVAL_x64FRE_en-us.iso` (Windows Server 2022 evaluation) and `virtio-win.iso` (VirtIO drivers), both dated from the same window as DC01's original build. No download needed. VMIDs 100, 101, 104, 105 were in use; 102 was free and confirmed by Raymond. Full inventory in `evidence/iso-inventory-and-vm-list.txt`.

## What I did

**VM provisioning** (`qm create`, full command and output in `evidence/vm102-created.txt`) — mirrored DC01's known-working hardware profile (`qm config 100`, captured in `evidence/dc01-hardware-config-baseline.txt`: OVMF/UEFI, q35 machine type, `virtio-scsi-single` controller) with three deliberate departures:

- **Memory: 3072 MiB, not Microsoft's documented 4GB minimum for Entra Connect.** A direct consequence of the tight preflight headroom. The alternative — right-sizing DC01's generously-oversized 10GB allocation to free real headroom — was considered and declined for this exercise specifically to avoid a second planned DC01 restart today; noted as revisitable if 3GB proves insufficient in practice.
- **`ostype: win11`, not `l26`.** `qm config 100` surfaced that DC01 itself has `ostype: l26` — Proxmox's code for a Linux guest — despite being Windows Server 2022. This is the exact config-mismatch-produces-symptoms-far-from-its-cause pattern the tech-compass skill's own documentation names as a known finding on this DC. Not fixed on DC01 here (out of scope for this build), but not propagated to the new VM either.
- A real install ISO and a VirtIO driver ISO attached (`ide2`/`ide3`) in place of DC01's leftover, irrelevant `lab.iso` mount.

**Everything from here through the domain join was driven through the Proxmox noVNC console, screen-shared as screenshots** — not through `qm guest exec`, because no guest agent exists inside a VM until Windows is installed and the agent is running within it. Per this exercise's evidence-log, screenshots are informational under this project's capture contract, not filed evidence; what follows is a faithful narrative of what was on screen, not a claim that it was independently captured.

Windows Setup: English (United States) defaults, evaluation license (no product key), **Windows Server 2022 Standard (Desktop Experience)** — the GUI-required edition, not Server Core, selected deliberately per the hard constraint above. Custom install. At disk selection, the VirtIO SCSI disk required a manual driver load (`vioscsi\2k22\amd64` from the attached VirtIO ISO) — see "What broke, and why" for a mistake made and corrected about this exact step. Install completed cleanly; Server Manager on first boot confirmed Windows Server 2022 Standard Evaluation, 2.98GB RAM, 59.37GB disk — both matching what was provisioned.

Post-install configuration, in order: renamed the computer to `ENTRACONNECT01` (from the auto-generated `WIN-NIMK703BAE1`); discovered the network adapter wasn't present in Windows at all (Network Connections showed zero items) because the VirtIO network driver (NetKVM) hadn't been loaded — a separate package from the storage driver, and Windows Setup doesn't prompt for it since networking isn't required to complete an install. Loaded `NetKVM\2k22\amd64`; the adapter appeared immediately and picked up a full, correct DHCP lease from DC01 (`10.0.0.102`, gateway `10.0.0.1`, DNS `10.0.0.10`, suffix `district.local`) — incidental confirmation that the gateway and DNS forwarder fixes from the hybrid-identity exercise are actually serving a second machine on the subnet, not just DC01 itself.

Converted to static per Raymond's choice: `10.0.0.11` / `255.255.255.0` / gateway `10.0.0.1` / DNS `10.0.0.10`. Pre-join sanity check (`nslookup district.local`, `ping dc01.district.local`) came back clean — resolved to `10.0.0.10`, 0% packet loss. Joined the domain via Server Manager's Local Server page; Raymond authenticated with his usual domain credential. Domain join requires no elevated rights by default (any authenticated domain user can join up to the domain's `ms-DS-MachineAccountQuota`, 10 by default) — worth stating plainly since `sysadmin` had its `BUILTIN\Administrators` grant on DC01 removed in an earlier exercise, and that removal has no bearing on its ability to join a machine to the domain.

Post-join, Server Manager confirmed `Workgroup: DISTRICT.LOCAL` (domain membership), static IP retained through the restart, and two batches of expected, benign warning-level log noise (`Microsoft-Windows-Time-Service`, `Microsoft-Windows-DNS-Client-Events`) consistent with a machine switching to domain-hierarchy time sync and registering DNS for the first time.

**Guest agent installation** — the first step in this exercise with real captured evidence again. The MSI (`guest-agent\qemu-ga-x86_64.msi` on the VirtIO ISO) installed without a visible wizard, which is expected — it silently installs a Windows service. `qm agent 102 ping` and `qm guest exec 102 -- cmd.exe /c hostname` both failed with "QEMU guest agent is not running" on the first attempt. Same root cause as the network adapter: a third, separate VirtIO driver (`vioserial`, the serial-channel device the agent's service actually communicates over) hadn't been loaded, and Device Manager showed the same "unrecognized device" shape as the NetKVM gap had. Loaded `vioserial\2k22\amd64`; both commands then succeeded (`evidence/guest-agent-verified.json`) — `ping` returned clean, and `hostname` returned `ENTRACONNECT01` through the actual automation channel.

## Where Raymond was consulted

**Static IP versus leaving it on DHCP.** Once the NetKVM driver was loaded, DHCP had already handed out a fully correct configuration (right gateway, right DNS, right suffix) — meaning static wasn't strictly required to proceed. I recommended static anyway (a server intended to run Entra Connect shouldn't have an address that can shift on lease renewal) but framed it as Raymond's call given DHCP was already working. His answer: *"set static now."* Documented because the technically-correct default (static) and the already-working state (DHCP) genuinely diverged here, not a case where there was only one reasonable answer.

## What the box said

A provenance note first, in this project's later terms. Four of the five evidence files record
raw terminal scrollback pasted by Raymond, which the capture contract labels **Recalled**, not
Captured. Only `evidence/guest-agent-verified.json` carries a command run through the automation
channel with an exit code. This section quotes all five and says which is which. The distinction
is stated here rather than corrected in the dated files.

**Pre-flight, before anything was created.** Scrollback, `evidence/proxmox-preflight-before-build.txt`.

```
--- qm status 100 ---
status: running

--- lvs (load-bearing rows) ---
  data      pve twi-aotz-- <141.23g      78.63  3.68

--- free -h ---
               total        used        free      shared  buff/cache   available
Mem:            15Gi        11Gi       3.7Gi        52Mi       382Mi       3.8Gi
```

The pool passed at 78.63%, under the 85% gate. Memory did not have the same margin: 3.8Gi
available, because VM 100 and VM 104 together held 12GB of the host's 15GB. That reading is the
direct cause of the 3072 MiB allocation, below Microsoft's documented 4GB minimum.

**Host inventory.** Scrollback, `evidence/iso-inventory-and-vm-list.txt`.

```
      VMID NAME                 STATUS     MEM(MB)    BOOTDISK(GB) PID
       100 winserver2022        running    10000             60.00 27910
       101 win11-client01       stopped    4096              64.00 0
       104 pfsense-fw           running    2048              20.00 17647
       105 kali-red             stopped    4096              40.00 0
```

Both ISOs were already on the host, dated 2025-09-11 and 2025-09-29, from the window of DC01's own
build. VMIDs 102 and 103 were free. Raymond confirmed 102.

**DC01's hardware profile, captured to mirror.** Scrollback, `evidence/dc01-hardware-config-baseline.txt`.

```
bios: ovmf
machine: q35
scsihw: virtio-scsi-single
ostype: l26
memory: 10000
```

`ostype: l26` is Proxmox's code for a Linux guest, set on a Windows Server 2022 VM. The command
was run to copy a working profile and returned a defect instead. It was not fixed on VM 100, and
it was not propagated: VM 102 uses `ostype: win11`.

**VM creation.** Scrollback, `evidence/vm102-created.txt`.

```
efidisk0: successfully created disk 'local-lvm:vm-102-disk-0,efitype=4m,pre-enrolled-keys=1,size=4M'
scsi0: successfully created disk 'local-lvm:vm-102-disk-1,iothread=1,size=60G'
pinning machine type to 'pc-q35-10.0' for Windows guest OS
  WARNING: Sum of all thin volume sizes (<590.97 GiB) exceeds the size of thin pool pve/data
  and the size of whole volume group (237.47 GiB).
```

Both disks provisioned without error. The machine type pinned automatically, which is expected for
a Windows-typed guest and locks the ABI against a later host upgrade. The overcommit warning
reports allocated virtual size, not consumption. Real usage stayed at the 78.63% above.

**The guest agent, and the only command here with an exit code.**
`evidence/guest-agent-verified.json`.

```
Command 1: qm agent 102 ping
Output: (empty -- no output is success for this subcommand)

Command 2: qm guest exec 102 --timeout 30 -- cmd.exe /c hostname
{
   "exitcode" : 0,
   "exited" : 1,
   "out-data" : "ENTRACONNECT01\r\n"
}
```

`exitcode: 0` and the returned hostname prove the automation channel works against VM 102. Both
commands failed before `vioserial` was loaded, with "QEMU guest agent is not running".

**What the box did not say.** Everything between the start of Windows Setup and the domain join
was read from Proxmox console screenshots: the edition selection, three VirtIO driver loads, the
computer rename, the DHCP lease, the static address, and Server Manager's post-join state. No
command output backs any of it. Those claims are Recalled and cannot enter the ledger.

## What broke, and why

**A wrong claim, made and corrected in real time.** After the disk-selection screen, Raymond's status update ("disk showed up, installing now") didn't confirm whether a driver load had occurred. That ambiguity was read as "it auto-detected without one," stated as a small finding ("no driver load needed — worth noting, since I expected that step to be necessary"), and it was wrong — Raymond clarified he had in fact loaded the driver. The lesson isn't really about VirtIO drivers; it's that an ambiguous status update should prompt a direct question about the actual mechanism, not an inference dressed up as an observation. This project's whole premise is not letting exactly this kind of gap stand, and it happened anyway, inside the same session — corrected as soon as caught, not smoothed over.

**One underlying problem wearing three costumes.** The storage driver, the network driver, and the serial-channel driver are three separate packages on the same VirtIO ISO, and each one only became visible as a blocker once it actually blocked something — no disk visible, then no network adapter visible, then a guest agent that "installed" but wouldn't run. All three are instances of the same fact: Windows Setup and a stock install only handle the one VirtIO driver that's immediately necessary (storage, to complete the install at all); everything else in the VirtIO family needs to be found and loaded manually, and Device Manager's "Other devices" list would have shown all of them at once, the very first time it was opened, rather than one at a time as each became a blocker.

## What I'd do differently

Open Device Manager once, immediately after first boot, and load every VirtIO driver showing as an unrecognized device in a single pass — storage, network, and serial together — instead of discovering each one reactively when it blocks the next step. This build hit the same class of gap three separate times before learning the pattern; the fix was known after the second occurrence and should have been applied preemptively rather than a third time reactively.

Ask directly what happened at an ambiguous checkpoint instead of inferring a mechanism from a status update and stating it as a finding. The corrected "no driver load needed" claim cost nothing here because it was caught within the same exchange, but a version of this that isn't caught is exactly the failure mode this whole project exists to prevent.

## Open questions

- **Entra Connect itself has not been installed.** This exercise built the prerequisite; installing and configuring Connect (sync scope, filtering, PHS vs. PTA, the UPN suffix work still pending from the hybrid-identity exercise) is separate, later work.
- **3GB RAM is below Microsoft's documented 4GB minimum for Entra Connect.** Untested whether this actually causes a problem once Connect is installed and running a real sync cycle against 13 users — flagged as a live risk, not a settled non-issue.
- **DC01's `ostype: l26` mismatch was found, not fixed.** Correcting it (to whatever Proxmox recommends for Server 2022 — plausibly `win11`, matching the choice made for the new VM) is a separate, low-risk cleanup task, not addressed here because it wasn't what this exercise was building.
- **Whether the vioserial/NetKVM driver gaps also existed on DC01's original build, unnoticed, is unknown.** DC01 has a working guest agent today, so if the same gaps existed there they were resolved at some point in the October build — but nothing in this project's evidence trail documents how, since that build predates this skill's capture discipline.
- **The activated Product ID status was observed, not investigated.** It's plausible (KMS-style activation once the machine had domain/network connectivity) but not confirmed against any specific activation mechanism.
