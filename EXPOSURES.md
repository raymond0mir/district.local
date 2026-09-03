# Known exposures

A standing list of what's actually still wrong or open in `district.local`, built only from
captured facts in `verified-claims.md` and the exercises' own evidence files — nothing here is
inferred or remembered without a citation. Doubles as the queue for what the next exercise
should be. Updated as of 2026-09-02; check `verified-claims.md` for anything more recent before
trusting a line here.

## Identity and access

**`Key Admins` and `Enterprise Key Admins` hold domain-wide write rights over
`msDS-KeyCredentialLink`** — the shadow-credentials attribute. Any current or future member of
either group can add a key credential to any account in the domain, including Domain Admins, and
authenticate as it without ever touching a password. This is standard AdminSDHolder-templated
behavior, not a misconfiguration, and there's nothing to "fix" about the right itself — but it
means membership in either group is Tier 0-equivalent and should be treated that way. `bhound`
held this path until 2026-09-01 (see Recently closed, below); nothing else currently holds it.
*Evidence:* `exercises/2026-09-01-entra-connect-connector-account/evidence/key-admins-domain-root-rights.json`.

**`svc-entraconnect` holds `Replicating Directory Changes` + `Replicating Directory Changes All`
at the domain root** — DCSync-equivalent rights, granted deliberately for Password Hash Sync, by
Microsoft's documented design rather than a misconfiguration. Its blast radius if the credential
were ever compromised is full domain compromise. Mitigations in place: the account has no admin
group membership, its object is hardened via `Set-ADSyncRestrictedPermissions`, and its password
has never been disclosed to any channel. *Evidence:*
`exercises/2026-09-01-entra-connect-connector-account/evidence/delegation-complete.json`.

**`sysadmin`'s `adminCount` is stuck at `1` and will not self-clear.** Per Microsoft's own AskDS
guidance, this is by design once an account has been a member of a protected group — it doesn't
revert automatically, even after removal, and blocks ACL inheritance from the account's OU until
manually cleared. Not a security exposure on its own, but a standing piece of directory hygiene
debt: `sysadmin` currently has legitimate standing access (Domain Admins, added 2026-09-01) so
clearing it isn't urgent, but it's worth remembering the flag exists independent of current group
membership. *Evidence:* `exercises/2026-08-31-dc01-constrained-admin-path/evidence/sysadmin-admincount-recheck-t-plus-5h40m.json`.

**Two of the five GPOs applying to DC01 have never been fully read.** `Default Domain Policy` and
`District Lockdown` are both in DC01's effective RSoP but weren't examined in the same detail as
`Secure Admin WS`, `DC - Secure LDAP`, and `Default Domain Controllers Policy` — an unread policy
surface on a domain controller. *Evidence:*
`exercises/2026-09-01-entra-connect-connector-account/evidence/secure-admin-ws-scope-fix.json`
(the RSoP count).

**Resolved 2026-09-02 (A2).** `Secure Admin WS`'s domain-root link with the Deny-Apply exception is
gone. Relinked to `OU=Workstations` and `OU=Servers/OU=Application Servers` (with VM 102 moved
into the OU structure to keep receiving it); domain-root link and the 09-01 Deny-Apply ACE both
removed; `gpresult` on DC01 confirms it no longer applies through any mechanism. The link's origin
also got a real answer along the way — 8 of 9 domain GPOs are owned by `Domain Admins` and built in
the 9/30–10/4/2025 window, while `Secure Admin WS` alone is owned by the individual account
`sysadmin` and created 10/8/2025, days later, pointing at a later, individual addition rather than
deliberate initial design. **Worth keeping on record even though closed:** the relink itself
briefly recreated this exact exposure for ~90 seconds mid-fix (`Remove-GPLink`'s domain-root target
format differs from `New-GPLink`'s) — caught and fixed the same session, full account in
`exercises/2026-09-02-a2-gpo-surface-and-domain-root-link/report.md`'s "What broke, and why."
*Evidence:* `exercises/2026-09-02-a2-gpo-surface-and-domain-root-link/evidence/relink-execution-and-recovery-20260902T1711-1714Z.txt`.

**`Default Domain Policy` sets `LockoutBadCount = 0` — no account-lockout threshold exists
anywhere in district.local.** Password complexity and history are enforced; no number of failed
password attempts ever locks an account out. Surfaced 2026-09-02 while reading this GPO in full
for A2, unrelated to that exercise's actual hypothesis. *Evidence:*
`exercises/2026-09-02-a2-gpo-surface-and-domain-root-link/evidence/gpo-origin-timestamps-and-full-reports-20260902T1656Z.txt`.

**`District Lockdown`'s Restricted Groups setting targets a group that doesn't exist.** Linked at
the domain root (same pattern `Secure Admin WS` had), it defines Restricted Groups membership for
a group named literally "Admins" — confirmed against all 13 real `*Admin*` groups in the domain,
none of which is a bare "Admins." Currently inert, since Windows can't restrict membership on an
unresolvable name, but it's dead configuration in a domain-root-linked GPO nobody had verified
before — exactly the class of thing the imported October 2025 baseline is known to carry.
*Evidence:*
`exercises/2026-09-02-a2-gpo-surface-and-domain-root-link/evidence/admins-group-existence-check-20260902T1701Z.txt`.

## Infrastructure

**Host RAM is over-committed by 3.77 GiB — a configuration problem, not a hardware ceiling.**
`qm list` shows 10000 MB assigned to VM 100 (DC01), 4096 MB to VM 101, 3072 MB to VM 102 and
2048 MB to VM 104: **18.77 GiB committed on a 15 GiB host**. All four cannot run at once, and
three of them drove available memory to **113Mi** on 2026-09-02 — the worst reading this lab has
captured. Shutting down VM 102 alone recovered it to 2.8Gi. Whether DC01 needs 10 GB for a lab
domain of this size is untested and looks unlikely; rebalancing is free and has not been done.
Separately, `DIMM B` on the Latitude 5420 is empty and the board takes a second module, so the
hardware ceiling is 2x what is installed. *Evidence:*
`exercises/2026-09-02-thin-pool-headroom-reclaim/evidence/destroy-vm105-pool-reclaimed-20260902T1607Z.txt`,
`exercises/2026-09-02-thin-pool-headroom-reclaim/evidence/host-hardware-and-root-usage-20260902T1548Z.txt`,
`exercises/2026-09-02-thin-pool-headroom-reclaim/evidence/vm102-shutdown-and-snapshot-names-20260902T1533Z.txt`.

**The volume group cannot be extended, and no amount of reclaim changes that.** `VFree` is
2.00 GiB on the sole PV (`/dev/nvme0n1p3`, 237.47 GiB) and it did **not** move when 28.13 GiB was
reclaimed from the pool — freed thin blocks return to the *pool*, not to the VG. The Latitude 5420
has a single M.2 slot, so the only disk expansion path is replacing the 256 GB NVMe. Structural,
permanent until hardware changes, and unrelated to how full the pool is. *Evidence:*
`exercises/2026-09-02-thin-pool-headroom-reclaim/evidence/destroy-vm105-pool-reclaimed-20260902T1607Z.txt`,
`exercises/2026-09-02-thin-pool-headroom-reclaim/evidence/host-hardware-and-root-usage-20260902T1548Z.txt`.

**29% of the disk is assigned to a host OS that uses a third of it.** `pve-root` is 68G with 23G
used — and 19G of that 23G is `/var/lib/vz` (ISOs and templates), so the Proxmox OS itself
occupies roughly 4G. That allocation was made at install and never revisited. It is not currently
binding and reclaiming it means an offline `resize2fs`/`lvreduce` with real risk of an unbootable
host, so it is recorded as a known inefficiency rather than a queued action. *Evidence:*
`exercises/2026-09-02-thin-pool-headroom-reclaim/evidence/host-hardware-and-root-usage-20260902T1548Z.txt`.

**There is effectively no backup posture.** Before 2026-09-02 this lab had **never taken a
backup** — `/var/lib/vz/dump/` was empty. It now holds exactly one archive, of a VM that no longer
exists. Nothing protects DC01, VM 101, VM 102 or pfSense. Note also that `local` lives on the same
physical NVMe as the thin pool, so anything backed up there is a rollback point, not disaster
recovery: a drive failure takes both. *Evidence:*
`exercises/2026-09-02-thin-pool-headroom-reclaim/evidence/storage-config-iso-inventory-vm105-config-20260902T1551Z.txt`,
`exercises/2026-09-02-thin-pool-headroom-reclaim/evidence/vzdump-vm105-to-local-verified-20260902T1555Z.txt`.

**The restore path has never been verified.** The one archive that exists passed `zstd -t`
(exit 0, decompressed 27.13 GiB), which proves the file is not corrupt. It does not prove a
restore produces a bootable VM. There is now 21.95 GiB of pool margin to test this in, and it was
not tested. *Evidence:* `exercises/2026-09-02-thin-pool-headroom-reclaim/evidence/vzdump-vm105-to-local-verified-20260902T1555Z.txt`.

**VM 104 (pfSense) still has zero snapshots**, after all three were pruned during the 08-31
thin-pool crisis response. If a firewall change goes wrong there is no rollback point for the
router — and unlike on 08-31, there is now both pool headroom and a working backup target, so
this is a gap that is cheap to close and simply hasn't been. *Evidence:*
`exercises/2026-08-31-dc01-unexpected-shutdown/evidence/pool-extended-and-pruned.txt`.

**21.93 GiB of pool consumption is unattributed.** Before the 2026-09-02 destroy, named volumes
summed to 116.15 GiB against a pool reporting 138.08 GiB consumed. The retained `clean-install`
and `win11-ootb` snapshot sets are the likely holders, but both carry the `k` skip-activation
attribute and were never activated with `lvchange -K` to read their `Data%`. Note also that
per-volume `Data%` counts referenced blocks that can be shared with an origin, so these figures
bound the picture rather than partition it. *Evidence:*
`exercises/2026-09-02-thin-pool-headroom-reclaim/evidence/inactive-volume-consumption-20260902T1537Z.txt`.

**What actually happens when the Proxmox thin pool hits 100% is still unknown.** It has come close
three times (96.49%, 86.48%, 92.01%) but the boundary itself has never been crossed and observed
directly. *Evidence:* `exercises/2026-08-31-dc01-unexpected-shutdown/report.md`, "Open questions."

**AD Recycle Bin is not enabled on `district.local`.** Flagged by the Entra Connect wizard's own
completion screen; means an accidentally deleted object (user, group, computer) has no clean
recovery path short of an authoritative restore. *Evidence: flagged in
`exercises/2026-09-01-entra-connect-connector-account/report.md`'s Open questions — not yet
independently captured via a direct `Get-ADOptionalFeature` read.*

**Dated artifact names in this repo do not derive from the lab's clock.** The host is
`America/Los_Angeles` (PDT, -0700), NTP synchronized, RTC in UTC, and `qm listsnapshot` prints
local time. Both snapshots named `pre-staging-promotion-20260902` were created **2026-09-01
23:35 UTC** — 09-01 in both bases. The exercise directory
`2026-09-02-entra-connect-upn-signin-test` carries the same one-day offset. Anyone correlating
this repo against host-side logs will land a day off. *Evidence:*
`exercises/2026-09-02-thin-pool-headroom-reclaim/evidence/vm102-shutdown-and-snapshot-names-20260902T1533Z.txt`.

## Time-sensitive

**`svc-entraconnect`'s password expires approximately 2026-10-13.** 42-day default domain max
password age; `PasswordLastSet` 2026-09-01 07:54:57 AM. If it lapses, Entra Connect sync starts
failing on connector authentication, likely surfacing as an import/export error rather than an
obvious "password expired" message. Rotate before then or set up a fine-grained password policy
exemption — not yet decided which. *Evidence:*
`exercises/2026-09-01-entra-connect-connector-account/evidence/svc-entraconnect-password-expiry.json`.

**`districtsafetyphoto.com` domain verification has never happened**, and the roughly one-month
registration window flagged 2026-08-31 is nearly elapsed as of this writing. *Evidence:*
`exercises/2026-08-31-entra-connect-install/report.md`, Open questions.

**DC01's expired evaluation license is actively shutting it down, and this has been happening
since at least 2026-08-31.** `LicenseStatus` 5 (Notification/expired), `GracePeriodRemaining` 0
minutes, confirmed directly off DC01 via CIM 2026-09-02 — no longer an inference from two matching
ISO/snapshot dates. Mid-session the same day, DC01 crashed; its own System event log named the
exact mechanism: `wlms.exe` (Windows License Manager) initiating a full shutdown, logged as *"The
license period for this installation of Windows has expired. The operating system is shutting
down"* — six seconds before the host-side crash signature. The same message recurs at irregular
intervals (60 minutes to 16+ hours apart, not a fixed timer) reaching back to at least 8/31 4:52 PM,
which lands seven seconds before the exact timestamp `exercises/2026-08-31-dc01-unexpected-
shutdown/report.md` logged as its own unexplained "occurrence 2" crash — a root cause that
investigation could not pin down at the time, because nobody yet knew the license was expired.
**Mitigated same day, not resolved.** DC01 was rearmed (`slmgr /rearm` via `cscript`, avoiding the
same `wscript` GUI-hang risk `/dlv` has), moving `LicenseStatus` from 5 (Notification/expired) to 2
(OOB Grace) with `GracePeriodRemaining` 14400 minutes — **exactly 10 days, not a reset of the full
180-day evaluation window.** `RemainingWindowsReArmCount` is now 5 of an original 6. **The
underlying exposure is unchanged**: this is a temporary extension of an evaluation build running a
production domain controller, not a licensed one, and the shutdown cycle resumes on schedule
around **2026-09-12** unless rearmed again or replaced with real activation. Two threads remain
genuinely open and separate from this finding: a 9/1 1:46:15 PM shutdown Windows itself flagged as
*unexpected* (no `wlms.exe` entry near it), and whether the original 08-31 09:38:11 crash was also
license-driven (unconfirmed — the event-log query didn't reach back that far). *Evidence:*
`exercises/2026-09-02-dc01-eval-license-status/evidence/os-and-licensing-status-20260902T1626Z.txt`,
`exercises/2026-09-02-dc01-eval-license-status/evidence/system-eventlog-1074-6006-6008-41-1076-20260902T1644Z.txt`,
`exercises/2026-09-02-dc01-eval-license-status/evidence/rearm-and-post-restart-verification-20260902T1650Z.txt`,
full analysis in `exercises/2026-09-02-dc01-eval-license-status/report.md`.

## Recently closed (for contrast, not action)

- **The published break-glass account (`breakglass@raytakosharkygmail.onmicrosoft.com`), and two
  more Global Administrators nobody had accounted for, all rotated out 2026-09-03.** A new native
  break-glass account now holds Global Administrator, its identity deliberately kept out of every
  published artifact. Reading the full role-membership list to confirm its assignment surfaced
  `labadmin` and a guest `#EXT#` account (`R M`) — both inherited from the October 2025 baseline,
  neither previously documented anywhere in this repo. All three legacy admins are de-privileged
  and disabled (objects retained). Full account, including the naming near-miss caught mid-exercise
  and the consult points with Raymond, in `exercises/2026-09-03-breakglass-rotation/report.md`.
- `bhound` — an enabled BloodHound-capstone throwaway holding a live shadow-credentials path via
  Key Admins — was disabled and removed from the group, 2026-09-01.
- A second, forgotten instance of the `OneShotDelegation` scheduled task on VM 102 was found
  still holding a live `DISTRICT\Administrator` credential and removed, 2026-09-01.
- `Administrator`'s password, previously typed into that same scheduled task, was rotated without
  the new value ever being disclosed to any channel, 2026-09-01.
- The thin pool's headroom crisis, open since 2026-08-31, closed 2026-09-02: `Data%` 91.06% ->
  70.86%, under the 85% gate with 21.95 GiB of margin, achieved by destroying VM 105 (`kali-red`)
  after a verified backup rather than by buying storage.
- The overcommit ratio, flagged as never rechecked, is now measured: **3.25x** (505.02 GiB of thin
  allocation against a 155.23 GiB pool). The prior ~3.6x figure was computed against the volume
  group, which is the wrong denominator for thin provisioning.
- VM 101's purpose is no longer a Recalled claim — `qm list` names it **`win11-client01`**,
  a stopped Windows 11 client with a 64 GB boot disk.
