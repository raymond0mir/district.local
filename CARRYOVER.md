# Carryover

Open items only, as of **2026-09-02**, at the close of
`exercises/2026-09-02-thin-pool-headroom-reclaim` (Exercise A1). Overwritten at each session
close per `.claude/skills/tech-compass/SKILL.md` — resolved work lives in `report.md` files,
`evidence-log.md` files, and `verified-claims.md`, not here.

**Resolved today, for the record:** the thin-pool headroom crisis that had blocked Phase A since
2026-09-01 is closed. `Data%` 91.06% → **70.86%**, under the 85% gate with 21.95 GiB of margin,
by backing up and destroying VM 105 (`kali-red`) — no hardware purchased, no external media used.
The overcommit ratio is now measured (3.25x against the pool, not 3.6x against the VG). VM 101 is
confirmed as `win11-client01`. Full detail in that exercise's `report.md`.

## Immediate, from today's exercise

- **VM 102 is stopped and Entra Connect is not syncing.** Shut down to recover RAM during storage
  work. Must be restarted before anything sync-dependent. `qm start 102`.
- **The restore path has never been verified.** The one archive in the lab
  (`/var/lib/vz/dump/vzdump-qemu-105-2026_09_02-08_55_49.vma.zst`) passed `zstd -t`, which proves
  it is not corrupt, not that it restores to a bootable VM. There is now 21.95 GiB of pool margin
  to test this in. Testing it also decides whether to keep the ~10-11 GiB archive at all.
- **DC01 may be running on expired Windows Server evaluation media.** `SERVER_EVAL_x64FRE...iso`
  and DC01's `clean-install` snapshot share the date 2025-09-29; a 180-day eval from then elapsed
  around 2026-03-28. This is inference from matching dates, **not captured**. One command settles
  it: `qm guest exec 100 -- powershell.exe -Command "slmgr /dlv"` (note `slmgr` is cscript-based;
  may need `cscript //nologo C:\Windows\System32\slmgr.vbs /dlv` to return output non-interactively).
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
- **Origin of `Secure Admin WS`'s domain-root GPO link** — deliberate design choice or setup-time
  scope creep — was never established, only its current effective scope.
- **Whether the tattooed `SeDenyInteractiveLogonRight` could re-tattoo DC01** on a future GPO
  refresh cycle was never observed over time, only immediately after the one fix applied.
- **Two of the five GPOs applying to DC01 have never been fully read** — `Default Domain Policy`
  and `District Lockdown`, per `EXPOSURES.md`.
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
- **Whether the orphaned `qm guest exec` process (pid 4624) on DC01 was ever terminated.** Not
  checked today. DC01's uptime was never read, so whether it rebooted since 09-02 is undetermined —
  if it did, this closes itself.

## Next exercise

**A2 — read the unread policy surface, and de-fragilize the `Secure Admin WS` domain-root link.**
Per `CURRICULUM.md`. Its prerequisite (pool headroom, so a snapshot can be taken before a GPO
change) is now satisfied. Note A2 opens with a snapshot — name it from `date -u` on the host.
