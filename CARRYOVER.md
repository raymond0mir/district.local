# Carryover

Open items only, as of **2026-09-02**, at the close of
`exercises/2026-09-02-thin-pool-headroom-reclaim` (Exercise A1). Overwritten at each session
close per `.claude/skills/tech-compass/SKILL.md` — resolved work lives in `report.md` files,
`evidence-log.md` files, and `verified-claims.md`, not here.

---

## Start here (written as a handoff to a fresh session)

**Read first, in this order:** the `tech-compass` skill (the repo copy at
`.claude/skills/tech-compass/SKILL.md` is canonical), then this file, then `EXPOSURES.md`.
`verified-claims.md` is the ledger — check it before labelling anything Inherited or Recalled.

**You have no live access to the lab.** DC01 has no WinRM, RDP, or PowerShell remoting by design,
and that is a finding worth keeping, not an obstacle to route around. Everything reaches the lab
as `qm guest exec` from the Proxmox host shell, and **Raymond runs the commands and pastes the
output back.** Give him one self-contained block at a time; keep all four JSON fields
(`out-data`, `err-data`, `exitcode`, `exited`) when they come back.

**`qm guest exec` has no attached TTY.** Anything that expects interactive input — or that opens a
GUI dialog on the guest, which is what `slmgr` does under its default `wscript` host — hangs until
the timeout and orphans a process on the guest. This has already happened once (pid 4624, still
unconfirmed as terminated). Prefer native PowerShell/CIM over VBScript wrappers, and always pass
`-NonInteractive`.

**Every capture block should self-timestamp** with `date -u` on the host. See the convention note
below for why.

**Git state at close:** commit `7599e7e` on `main`, pushed to
`git@github.com:raymond0mir/district.local.git`, working tree clean. Push key is
`~/.ssh/id_ed25519_github`. Run a credential scan before any commit — a literal password reached
report prose once, on 2026-08-31.

**Lab state at close:** thin pool **70.86%** (under the 85% gate, 21.95 GiB margin).
VM 100 (`winserver2022`/DC01) running. VM 104 (`pfsense-fw`) running. **VM 102
(`entraconnect01`) is stopped** — shut down deliberately to recover host RAM. VM 101
(`win11-client01`) stopped. VM 105 (`kali-red`) **no longer exists** — backed up and destroyed
during A1.

---

## DC01's crash root cause: found and mitigated (temporarily) today

**`wlms.exe` (Windows License Manager) was repeatedly, deliberately shutting DC01 down** because
its evaluation license expired — confirmed from DC01's own System event log (Event 1074), not
inferred. It crashed once during today's session; `qm start 100` brought it back, and the event
log pull off DC01 (once back up) pinned the mechanism precisely.

**Decided and applied same day: rearmed.** `RemainingWindowsReArmCount` was 6; checked via CIM
(no `slmgr` needed for that read), then `slmgr /rearm` run through explicit `cscript //NoLogo //B`
(`slmgr.vbs` carries the same `wscript`-GUI-hang risk as `/dlv` — forced the console host rather
than assuming `/rearm` avoids it). Required a restart to apply; confirmed post-restart:
`LicenseStatus` 5 → 2 (OOB Grace), `GracePeriodRemaining` 14400 min = **exactly 10 days**,
`RemainingWindowsReArmCount` now 5.

**This is a reprieve, not a fix — put a reminder on it.** DC01 goes back to Notification state
and the shutdown cycle resumes around **2026-09-12** unless rearmed again (5 left, ~50 more days
of runway if stretched to the limit) or replaced with real activation / a rebuild. That larger
decision is still not made — just deferred with room to breathe. Full investigation and the rearm
sequence in `exercises/2026-09-02-dc01-eval-license-status/report.md`.

**Do not use `slmgr /dlv`** to investigate further — same `wscript`-GUI-hang risk as above (the
pid 4624 failure mode, closed as of today, but the trap is still live for any future `slmgr`
invocation that doesn't force `cscript` explicitly).

**Two threads left genuinely open, not the same finding:**
- A 9/1 1:46:15 PM shutdown Windows itself flagged as *unexpected* on the next boot — no
  `wlms.exe` entry near it. Doesn't fit the pattern above; still unexplained.
- Whether the *original* 08-31 09:38:11 crash was also `wlms.exe`-driven — unconfirmed, a 20-event
  query didn't reach back that far.
- An unexplained `root@pam` Proxmox auth logged 45 seconds before today's crash — confirmed not
  Raymond (he was terminal-only, hadn't touched the dashboard). Not yet checked against
  `pveproxy`'s access log for a source.

---

**Resolved 2026-09-02, DC01 licensing capture:** `LicenseStatus: 5` (Notification/expired),
`GracePeriodRemaining: 0` — confirms, independent of date arithmetic, that DC01 is running expired
Windows Server 2022 evaluation media. `EvaluationEndDate` came back as a null-`FILETIME` sentinel,
not a usable date. `InstallDate` (9/30/2025) is one day off the ISO/`clean-install` date
(2025-09-29) — consistent with this host's already-documented clock-offset artifact, not a
contradiction. **pid 4624 is closed**: `LastBootUpTime` postdates the hang that created it. Full
writeup in `exercises/2026-09-02-dc01-eval-license-status/report.md`; ledger rows added to
`verified-claims.md`; `EXPOSURES.md` updated.

---

**Resolved 2026-09-02, for the record:** the thin-pool headroom crisis that had blocked Phase A
since 2026-09-01 is closed. `Data%` 91.06% → **70.86%**, by backing up and destroying VM 105
(`kali-red`) — no hardware purchased, no external media used. The overcommit ratio is now measured
(3.25x against the pool, not 3.6x against the VG). VM 101 is confirmed as `win11-client01`.
Full detail in `exercises/2026-09-02-thin-pool-headroom-reclaim/report.md`.

The same exercise retracted two of my own mid-session claims and one inherited ledger error; all
three are documented in that report's "What broke, and why" rather than edited away. A fresh
session should read that section before trusting derived figures elsewhere in the repo.

## Immediate, from today's exercise

- **VM 102 is stopped and Entra Connect is not syncing.** Shut down to recover RAM during storage
  work. Must be restarted before anything sync-dependent. `qm start 102`.
- **The restore path has never been verified.** The one archive in the lab
  (`/var/lib/vz/dump/vzdump-qemu-105-2026_09_02-08_55_49.vma.zst`) passed `zstd -t`, which proves
  it is not corrupt, not that it restores to a bootable VM. There is now 21.95 GiB of pool margin
  to test this in. Testing it also decides whether to keep the ~10-11 GiB archive at all.
- **DC01 is confirmed running expired Windows Server evaluation media.** No longer "may be" — see
  *Resolved 2026-09-02, DC01 licensing capture* above. Decision (activate/rearm/rebuild/accept) not
  yet made; possibly connected to an hourly-restart hypothesis also not yet confirmed.
- **Host RAM is over-committed by 3.77 GiB and nobody has rebalanced it.** DC01 alone is assigned
  10000 MB. Whether it needs that for a lab domain of this size is untested. Rebalancing is free
  and would let three or four VMs coexist; it is a config change, not a purchase.
- **21.93 GiB of pool consumption is unattributed.** The retained `clean-install` and `win11-ootb`
  snapshot sets are the likely holders but carry the `k` skip-activation flag and were never read.
  `lvchange -K -ay` on them would close it.
- **pfSense still has zero snapshots** — but now there is both pool headroom and a proven backup
  target, so the reason it stayed open no longer applies. Cheapest outstanding win in the repo.

## Deferred by Raymond's decision, not lost

- **Hardware.** He asked whether the lab is hardware-limited, then decided: *"lets put aside the
  purchases, it can be something, lets just run lean on what we got."* A1 completed with no
  purchase, so this is genuinely deferred rather than blocking. The captured facts if it comes
  back up: Dell Latitude 5420, i5-1145G7 4C/8T; **`DIMM B` is empty**, one 16 GB DDR4-3200 in
  `DIMM A`, so RAM can double without removing anything; **one M.2 slot**, so disk means replacing
  the 256 GB NVMe; `pve-root` is 68G holding 23G, of which 19G is ISOs.
  A second physical host remains worth doing for *architecture* reasons a single node cannot
  demonstrate — a second DC with real replication, or an attacker box off the domain's own
  hypervisor — but not as a storage fix.
- **B5 — split `exercises/2026-09-01-entra-connect-connector-account/report.md` in two.**
  Explicitly held, Raymond's call: needs real narrative rework (separate framing for the
  GPO-lockout/tattoo half vs. the connector-account/wizard half), not mechanical cut-and-paste.
  Drop step 14 and consultation point 10 (GitHub setup) when this happens — that content now
  lives in `README.md`.

## Decision owed before Phase B starts

- **The published break-glass account.** `breakglass@raytakosharkygmail.onmicrosoft.com` appears
  in `verified-claims.md`, `exercises/2026-08-31-hybrid-identity-upn-baseline/report.md`, and four
  evidence files — with its object GUID, its confirmed Global Administrator role, and its
  single-device Authenticator MFA dependency. None of it was a leak; it was captured deliberately
  as evidence and should stay readable as that. The forward-looking problem is that `CURRICULUM.md`
  exercise B1 designs the Conditional Access baseline around this account as the exclusion that
  prevents lockout — turning a published identity into the thing standing between the tenant and
  an unrecoverable state. Unlike the on-prem lab, this exposure does not depend on the Proxmox box
  being powered on.

  Options weighed 2026-09-02: scrub git history (rejected — unreliable once pushed public, and it
  would destroy load-bearing evidence); disable the published account (rejected alone — a disabled
  break-glass is not a break-glass); **rotate the identity (recommended)**. The sequencing rule
  this project already learned expensively applies directly: **create and verify the replacement
  before touching the published one.** Not yet decided or executed.

## Convention change adopted today

- **Dated names must come from the host's clock, not the session's.** The host is
  `America/Los_Angeles` (PDT, -0700); both snapshots named `pre-staging-promotion-20260902` were
  actually created 2026-09-01 23:35 UTC, and `2026-09-02-entra-connect-upn-signin-test` carries
  the same one-day offset. Every capture block now self-timestamps with `date -u`; snapshot names
  and exercise directories should be derived the same way. Existing directory names are left
  alone — renaming them would break every citation in the ledger for no gain.

## Still open from before today

- **`svc-entraconnect`'s password expires approximately 2026-10-13** (42-day default max age,
  `PasswordLastSet` 2026-09-01 07:54:57 AM). Rotate before then or set up a fine-grained password
  policy exemption — not yet decided which.
- **A2 done, closed 2026-09-02.** `exercises/2026-09-02-a2-gpo-surface-and-domain-root-link/`.
  `Secure Admin WS` relinked to `OU=Workstations` + `OU=Servers/OU=Application Servers`, domain-
  root link and Deny-Apply ACE both removed, VM 102 moved into the OU structure. `gpresult`
  confirms it no longer touches DC01 at all. **Worth remembering: the relink itself briefly
  recreated the exact lockout exposure it was fixing** — `Remove-GPLink` needed the
  distinguishedName form of the domain root (`"DC=district,DC=local"`), not the DNS form
  (`"district.local"`) that worked for `New-GPLink`; ~90 seconds of real exposure before the fix
  landed, no interactive Domain Admin logon attempted during it. Full account in that exercise's
  report. Two findings surfaced along the way, not part of A2's original hypothesis, filed in
  `EXPOSURES.md`: `Default Domain Policy` has `LockoutBadCount = 0` (no account-lockout threshold
  anywhere in the domain), and `District Lockdown`'s Restricted Groups setting targets a group
  named "Admins" that doesn't exist (likely confused with one of two OUs actually named "Admins").
  **Still open from A2:** the final, later-in-time half of step 4's tattoo observation (baseline
  confirmed no recurrence; a second check after more elapsed time was never done).
- **AD Recycle Bin is not enabled on `district.local`** — flagged by the Entra Connect wizard's
  own completion screen, never independently captured via `Get-ADOptionalFeature`.
- **The wizard's "Filtering" step was never actually reviewed** — screenshot skipped, contents
  unknown.
- **`districtsafetyphoto.com` verification never happened.** The roughly one-month registration
  window flagged 2026-08-31 has nearly elapsed.
- **Root cause of the Entra Connect wizard's "Not Added" domain status.** Practically moot (both
  sign-in and export work regardless) but never explained.
- **`jsmith` is still the only restamped account taken end-to-end.** Whether the other eight get
  the same treatment, or `jsmith` stays the single test case, is undecided.
- **Sign-in logs (`GET /auditLogs/signIns`) are unavailable on Entra Free**
  (`Authentication_RequestFromNonPremiumTenantOrB2CTenant`) — a named licensing constraint, not a
  permissions gap. Any exercise wanting sign-in-log evidence needs a licensing decision or the
  `GET /me`-as-the-user fallback already proven here.
## Next exercise

**A3 — the Entra ID Free ceiling, measured.** Per `CURRICULUM.md`. A2 is done (see above). A3
needs no license and no new VM, same as A1/A2.
