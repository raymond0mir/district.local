# Carryover

Open items only, as of **2026-09-02**, at the close of four exercises today —
`exercises/2026-09-02-dc01-eval-license-status`, `exercises/2026-09-02-a2-gpo-surface-and-domain-root-link`,
and `exercises/2026-09-02-a3-entra-free-ceiling` (plus its same-day non-gallery follow-up).
Overwritten at each session close per `.claude/skills/tech-compass/SKILL.md` — resolved work
lives in `report.md` files, `evidence-log.md` files, and `verified-claims.md`, not here.

---

## Start here (written as a handoff to a fresh session)

**Read first, in this order:** the `tech-compass` skill (the repo copy at
`.claude/skills/tech-compass/SKILL.md` is canonical), then this file, then `EXPOSURES.md`.
`verified-claims.md` is the ledger — check it before labelling anything Inherited or Recalled.

**You have no live access to DC01/VM 102.** Both have no WinRM, RDP, or PowerShell remoting by
design, and that is a finding worth keeping, not an obstacle to route around. Everything reaches
them as `qm guest exec` from the Proxmox host shell, and **Raymond runs the commands and pastes
the output back.** Give him one self-contained block at a time; keep all four JSON fields
(`out-data`, `err-data`, `exitcode`, `exited`) when they come back.

**Tenant-side (Entra/Graph) work is different: no `qm guest exec` involved at all.** Capture path
is Graph Explorer (for API calls) and the Entra admin center (for portal-only flows like SAML/SCIM
setup), both run by Raymond as `breakglass@raytakosharkygmail.onmicrosoft.com`, same
one-block-at-a-time discipline. A Graph Explorer session token can go stale even when a scope is
already tenant-consented (Modify Permissions shows "Unconsent" but the call still 403s) — the fix
is signing out and back in, not re-consenting. Screenshots of portal UI state are **Recalled**,
not Captured, unless followed up with a Graph read against the actual object.

**`qm guest exec` has no attached TTY.** Anything that expects interactive input — or that opens a
GUI dialog on the guest, which is what `slmgr` does under its default `wscript` host — hangs until
the timeout and orphans a process on the guest (this happened once, pid 4624, since confirmed
closed by a later reboot). Prefer native PowerShell/CIM over VBScript wrappers, always pass
`-NonInteractive`, and when `slmgr` is genuinely needed, force the console host explicitly
(`cscript.exe //NoLogo //B`) rather than letting the default association pick `wscript`.

**GroupPolicy module gotchas:** `New-GPLink` returns nothing to the pipeline on success — empty
output is not a failure signal, verify via `Get-GPOReport`'s own `LinksTo` field instead of
trusting cmdlet silence. `Remove-GPLink` and `New-GPLink` do **not** accept the same target-string
format for the domain root: `New-GPLink` took the DNS form (`"district.local"`); `Remove-GPLink`
needed the distinguishedName form (`"DC=district,DC=local"`) and failed outright on the DNS form.
Getting this wrong on a live domain controller briefly recreated a real lockout exposure on
2026-09-02 — see A2 below. Verify a cmdlet's actual accepted input before trusting an assumption
carried over from its counterpart.

**Every capture block should self-timestamp** with `date -u` on the host; snapshot names and
exercise directories should be derived the same way (the host runs America/Los_Angeles).

**Git state at close:** commit `24c29d3` on `main`, pushed to
`git@github.com:raymond0mir/district.local.git`, working tree clean. Push key is
`~/.ssh/id_ed25519_github`. Run a credential scan before any commit — a literal password reached
report prose once, on 2026-08-31.

**Lab state at close (VM state last independently verified ~17:14 UTC 2026-09-02; today's session
was entirely tenant-side and touched no VM state):** thin pool ~70.9% (healthy, under the 85%
gate). VM 100 (DC01) **running** — rearmed 2026-09-02, ~10 days of licensing runway, see below.
VM 104 (pfsense-fw) running. VM 102 (entraconnect01) **stopped** — Entra Connect is not syncing
while it's down. VM 101 stopped. VM 105 no longer exists (destroyed in A1). Host RAM was tight at
last reading — 422Mi free, 2.9Gi available, 1.2Gi in swap, with only DC01 and pfSense running —
worth a fresh `free -h` before assuming headroom for anything heavier.

---

## Time-sensitive: DC01's license runway

**DC01 is running Windows Server 2022 evaluation media, confirmed expired, rearmed 2026-09-02.**
`wlms.exe` was found to be the direct cause of a recurring crash pattern going back to at least
8/31 (it force-shuts-down DC01 on an irregular schedule once the eval is past grace). Rearmed via
`slmgr /rearm` (forced through `cscript`): `LicenseStatus` moved from 5 (Notification/expired) to
2 (OOB Grace), `GracePeriodRemaining` exactly 10 days, `RemainingWindowsReArmCount` now 5 of an
original 6.

**Put a reminder on ~2026-09-12.** That's when DC01 goes back to Notification and the shutdown
cycle resumes, unless rearmed again (5 rearms left, ~50 more days of runway if stretched to the
limit) or replaced with real activation / a rebuild. That larger decision — activate, keep
rearming, rebuild, or accept and work around it — is still not made. Full investigation in
`exercises/2026-09-02-dc01-eval-license-status/report.md`.

**Do not use `slmgr /dlv`** — same `wscript`-GUI-hang risk noted above.

**Loose threads from this investigation, genuinely unexplained:**
- A shutdown at 9/1 1:46:15 PM that Windows itself flagged as *unexpected* — no `wlms.exe` entry
  near it in the event log.
- Whether the *original* 8/31 09:38:11 crash was also `wlms.exe`-driven — a 20-event query didn't
  reach back that far.
- A `pveproxy` `root@pam` auth logged 45 seconds before DC01's crash on 2026-09-02 — confirmed not
  Raymond (terminal-only, hadn't touched the dashboard). Source never checked against the access
  log.

---

## A2 done: Secure Admin WS de-fragilized

`Secure Admin WS` no longer touches DC01 through any mechanism. Relinked to `OU=Workstations` and
`OU=Servers/OU=Application Servers`; domain-root link and the 09-01 Deny-Apply exception both
removed; VM 102's computer object moved into the OU structure so it keeps receiving the GPO via
the new direct link. `gpresult` on DC01 confirms it's absent entirely now, not even filtered.

**The relink briefly recreated the exact lockout exposure it was fixing** — ~90 seconds, caused by
the `Remove-GPLink` target-format issue noted above, caught and fixed the same session. Full
account in that exercise's report.

**Two findings surfaced along the way, filed in `EXPOSURES.md`, not yet acted on:**
- `Default Domain Policy` sets `LockoutBadCount = 0` — no account-lockout threshold exists
  anywhere in this domain.
- `District Lockdown`'s Restricted Groups setting targets a group named "Admins" that doesn't
  exist. Currently inert. Whether it logged an error anywhere was never checked.

**Still open from A2 itself:** the final, later-in-time half of CURRICULUM's step-4 tattoo
observation — the baseline (no recurrence) is real evidence but not the full before/after the
exercise asked for.

## A3 done, including its non-gallery follow-up: the Entra ID Free ceiling, measured

Full report in `exercises/2026-09-02-a3-entra-free-ceiling/report.md`. Captured, with real error
bodies, that Entra Free refuses Conditional Access (write only — read is open), PIM, and Identity
Protection, each with a *different* HTTP status/error-code shape (403/`Forbidden`,
403/`AccessDenied`, 400/`AadPremiumLicenseRequired`). Security Defaults confirmed enabled
tenant-wide with no scoping property on the object at all.

**Genuine surprise, tested both ways: neither gallery-app nor non-gallery-app SAML SSO or SCIM
provisioning *setup* hits any Free-tier gate.** Tested against Salesforce (gallery) and a
from-scratch custom app (`A3-nongallery-test`) — both SAML configs saved cleanly with real live
signing certs; both provisioning admin-credentials screens showed no upsell, and "Test connection"
failed on the target's own error (Salesforce's `InvalidCredentials`; the custom connector's
`CredentialValidationUnavailable`, a real network attempt against a nonexistent endpoint) — never
an Entra refusal. **This retracts, not just extends, `CURRICULUM.md`'s original Recalled note**
that non-gallery SAML/SCIM needs P1 — tested directly, it did not hold. Retraction recorded on the
record in the report, `CURRICULUM.md` (struck through in place), and `verified-claims.md`.

**Two test enterprise app objects were created and left in place by Raymond's explicit call this
session** (`Salesforce`, `A3-nongallery-test`) — both inert (no user/group assignments,
`appRoleAssignmentRequired: true`, placeholder or non-resolving endpoints). **Revisit next
session: decide whether to delete them or document them as intentional lab fixtures** — not
decided, deliberately deferred rather than forgotten.

## Decision owed: B2's placement, one residual risk left

`CURRICULUM.md`'s calendar table is updated to reflect A3's result — the SAML/SCIM licensing
question is substantively answered for *setup*, both app types. What's still genuinely untested:
whether an actual provisioning *run* (past "Test connection," which is B2's real deliverable —
deliberate failure injection against a live sync) hits a P1 gate that setup alone doesn't surface.
No live third-party tenant exists in this lab to test that directly.

**Not decided:** whether to (a) run B2 outside the trial window on the strength of A3's setup
results, accepting the residual risk that the live-sync step might need P1 after all and force a
rerun inside a trial later, or (b) keep B2 inside the trial as a safety margin despite that
evidence, since a 30-day trial with no second chance is an expensive place to discover "needs P1"
too late. Genuinely Raymond's call.

---

## Also done 2026-09-03: a self-hosted secrets store, and the first verified restore

Vaultwarden 1.37.2 in Docker inside **LXC container 103** (Debian 12, unprivileged,
`10.0.0.20/24` on `vmbr1`) behind a Caddy TLS reverse proxy — **the lab's first container**, every
prior guest being a full VM. Access: `ssh -L 8443:10.0.0.20:443 root@192.168.1.100` then
`https://localhost:8443`, one-time trust exception for Caddy's internal CA. No standing inbound
exposure. Signups closed. Backups daily 03:00 to `/var/lib/vz/dump/vaultwarden`, and **the restore
was actually verified** — integrity check, expected row count, and a throwaway instance booting on
the restored data — a first for this lab.

**Open on it, all detailed in `EXPOSURES.md`:** `ADMIN_TOKEN` still plain text (`vaultwarden hash`
won't take a piped password); container 103 runs `lxc.apparmor.profile: unconfined`; backups share
a disk with what they protect; cron never seen firing. **And nothing is stored in the vault yet** —
the new break-glass password, `svc-entraconnect`'s, and the admin token all still live outside it.

**Topology change to carry forward:** `vmbr1` had no host-side IPv4 address, so the host could not
reach `10.0.0.0/24` at all. It now holds `10.0.0.5/24`, persisted but not `ifreload`-applied, so
unproven until the next reboot. pfSense is no longer the sole path between host side and lab side.

Full account in `exercises/2026-09-03-vaultwarden-secrets-store/report.md`.

## Immediate, still open from A1

- **VM 102 is stopped and Entra Connect is not syncing.** `qm start 102` before anything
  sync-dependent.
- **The restore path has never been verified.** The one archive in the lab
  (`vzdump-qemu-105-2026_09_02-08_55_49.vma.zst`) passed `zstd -t` only — proves not corrupt, not
  restorable. 21.95 GiB of pool margin exists to test this in.
- **Host RAM is over-committed and nobody has rebalanced it.** DC01 alone is assigned 10000 MB;
  whether it needs that is untested. A free config change, not a purchase — and the tightest
  reading so far (422Mi free with only two VMs running) makes this worth doing soon.
- **21.93 GiB of pool consumption is unattributed** — the retained `clean-install` and
  `win11-ootb` snapshot sets are the likely holders, never read (`lvchange -K -ay` would close it).
- **pfSense still has zero snapshots.** Cheapest outstanding win in the repo.

## Deferred by Raymond's decision, not lost

- **Hardware.** *"lets put aside the purchases, it can be something, lets just run lean on what
  we got."* Dell Latitude 5420, i5-1145G7 4C/8T; `DIMM B` empty (RAM can double), one M.2 slot
  (disk means replacing the 256 GB NVMe).
- **B5 — split `exercises/2026-09-01-entra-connect-connector-account/report.md` in two.** Needs
  real narrative rework, not mechanical cut-and-paste. Drop step 14 / consultation point 10
  (GitHub setup) when this happens — now lives in `README.md`.
- **The two A3 test enterprise app objects** — see above, revisit best practice next session.

## Resolved 2026-09-03: break-glass rotation, plus a bigger finding than planned

`breakglass@raytakosharkygmail.onmicrosoft.com` is rotated out. A new native, cloud-only Global
Administrator exists in its place — **its UPN and display name are deliberately not written
anywhere in this repo**, including in this file; that's a decision Raymond made this session, not
an oversight. Verified from its own signed-in session (not just from another admin's view): holds
Global Administrator per `/me/memberOf`, and proved it by creating and deleting a real user object.

**The rotation surfaced two more Global Administrators nobody currently working on this lab had
accounted for**, found while reading the full role-membership list (a step the plan already
needed for an unrelated reason): `labadmin@raytakosharkygmail.onmicrosoft.com` and a guest
`#EXT#` account (`R M`). Raymond confirmed both predate these sessions — inherited from the
October 2025 paired-build baseline. Consulted before touching either; both are now de-privileged
and sign-in-disabled, same as `breakglass` itself. **Exactly one Global Administrator remains in
the tenant.** Full account, including a naming near-miss caught mid-exercise (a validation error
pushed toward falling back to an obvious `emergencyaccess2@...` name, caught and renamed before
any role was attached), in `exercises/2026-09-03-breakglass-rotation/report.md`.

B1 can now safely make the new account load-bearing for Conditional Access.

## Still open from before this session

- **`svc-entraconnect`'s password expires approximately 2026-10-13.** Rotate before then or set
  up a fine-grained password policy exemption.
- **AD Recycle Bin is not enabled on `district.local`** — flagged by the Entra Connect wizard,
  never independently captured via `Get-ADOptionalFeature`.
- **The wizard's "Filtering" step was never actually reviewed.**
- **`districtsafetyphoto.com` verification never happened** — the ~one-month window flagged
  2026-08-31 has nearly elapsed.
- **Root cause of the Entra Connect wizard's "Not Added" domain status** — practically moot, never
  explained.
- **`jsmith` is still the only restamped account taken end-to-end.**
- **Sign-in logs are unavailable on Entra Free** — licensing constraint, not a permissions gap;
  `GET /me`-as-the-user is the proven fallback.

## Next exercise

**A3 is done, including the non-gallery follow-up.** Next is opening the P1/P2 trial and starting
**B1** (Conditional Access, report-only to enforced) per `CURRICULUM.md` — gated only on the B2
placement decision above, which doesn't block B1 itself starting. Consider the break-glass
rotation decision before B1 makes that account load-bearing.
