# Carryover

Open items only, as of **2026-09-02**, at the close of three exercises —
`exercises/2026-09-02-dc01-eval-license-status`, `exercises/2026-09-02-a2-gpo-surface-and-domain-root-link`,
and `exercises/2026-09-02-a3-entra-free-ceiling`. Overwritten at each session close per
`.claude/skills/tech-compass/SKILL.md` — resolved work lives in `report.md` files,
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
the timeout and orphans a process on the guest (this happened once, pid 4624, since confirmed
closed by a later reboot). Prefer native PowerShell/CIM over VBScript wrappers, always pass
`-NonInteractive`, and when `slmgr` is genuinely needed, force the console host explicitly
(`cscript.exe //NoLogo //B`) rather than letting the default association pick `wscript`.

**GroupPolicy module gotchas, learned today, worth remembering:** `New-GPLink` returns nothing to
the pipeline on success — empty output is not a failure signal, verify via `Get-GPOReport`'s own
`LinksTo` field instead of trusting cmdlet silence. `Remove-GPLink` and `New-GPLink` do **not**
accept the same target-string format for the domain root: `New-GPLink` took the DNS form
(`"district.local"`); `Remove-GPLink` needed the distinguishedName form
(`"DC=district,DC=local"`) and failed outright on the DNS form. Getting this wrong on a live
domain controller briefly recreated a real lockout exposure today — see below. Verify a cmdlet's
actual accepted input before trusting an assumption carried over from its counterpart.

**Every capture block should self-timestamp** with `date -u` on the host; snapshot names and
exercise directories should be derived the same way (the host runs America/Los_Angeles).

**Git state at close:** commit `0614436` on `main`, pushed to
`git@github.com:raymond0mir/district.local.git`, working tree clean. Push key is
`~/.ssh/id_ed25519_github`. Run a credential scan before any commit — a literal password reached
report prose once, on 2026-08-31.

**Lab state at close (last verified ~17:14 UTC today):** thin pool ~70.9% (healthy, under the 85%
gate). VM 100 (DC01) **running** — rearmed today, ~10 days of licensing runway, see below. VM 104
(pfsense-fw) running. VM 102 (entraconnect01) **stopped** — its AD computer object was moved into
`OU=Application Servers` today, but the VM itself was not started this session; Entra Connect is
not syncing while it's down. VM 101 stopped. VM 105 no longer exists (destroyed in A1). Host RAM
was tight at last reading — 422Mi free, 2.9Gi available, 1.2Gi in swap, with only DC01 and pfSense
running — worth a fresh `free -h` before assuming headroom for anything heavier.

---

## Time-sensitive: DC01's license runway

**DC01 is running Windows Server 2022 evaluation media, confirmed expired, rearmed today.**
`wlms.exe` was found to be the direct cause of a recurring crash pattern going back to at least
8/31 (it force-shuts-down DC01 on an irregular schedule once the eval is past grace) — this also
explains the previously-unresolved root cause from `2026-08-31-dc01-unexpected-shutdown`'s
"occurrence 2". Rearmed via `slmgr /rearm` (forced through `cscript`): `LicenseStatus` moved from
5 (Notification/expired) to 2 (OOB Grace), `GracePeriodRemaining` exactly 10 days,
`RemainingWindowsReArmCount` now 5 of an original 6.

**Put a reminder on ~2026-09-12.** That's when DC01 goes back to Notification and the shutdown
cycle resumes, unless rearmed again (5 rearms left, ~50 more days of runway if stretched to the
limit) or replaced with real activation / a rebuild. That larger decision — activate, keep
rearming, rebuild, or accept and work around it — is still not made. Full investigation in
`exercises/2026-09-02-dc01-eval-license-status/report.md`.

**Do not use `slmgr /dlv`** — same `wscript`-GUI-hang risk noted above.

**Loose threads from this investigation, genuinely unexplained, not the same finding as the above:**
- A shutdown at 9/1 1:46:15 PM that Windows itself flagged as *unexpected* — no `wlms.exe` entry
  near it in the event log.
- Whether the *original* 8/31 09:38:11 crash was also `wlms.exe`-driven — a 20-event query didn't
  reach back that far.
- A `pveproxy` `root@pam` auth logged 45 seconds before DC01's crash today — confirmed not Raymond
  (terminal-only, hadn't touched the dashboard). Source never checked against the access log.

## A2 done: Secure Admin WS de-fragilized

`Secure Admin WS` no longer touches DC01 through any mechanism. Relinked to `OU=Workstations` and
`OU=Servers/OU=Application Servers`; domain-root link and the 09-01 Deny-Apply exception both
removed; VM 102's computer object moved into the OU structure so it keeps receiving the GPO via
the new direct link instead of the old domain-root cascade. `gpresult` on DC01 confirms it's
absent entirely now, not even filtered.

**The relink briefly recreated the exact lockout exposure it was fixing** — ~90 seconds, caused by
the `Remove-GPLink` target-format issue noted above, caught and fixed the same session. Full
account, including what would have discriminated a real lockout from a config-only exposure, in
that exercise's report.

**Two findings surfaced along the way, filed in `EXPOSURES.md`, not yet acted on:**
- `Default Domain Policy` sets `LockoutBadCount = 0` — no account-lockout threshold exists
  anywhere in this domain.
- `District Lockdown`'s Restricted Groups setting targets a group named "Admins" that doesn't
  exist (likely confused with one of two OUs literally named "Admins" — Restricted Groups can't
  target an OU). Currently inert. Whether it logged an error anywhere was never checked.

**Still open from A2 itself:** the final, later-in-time half of CURRICULUM's step-4 tattoo
observation — the baseline (no recurrence, checked today) is real evidence but not the full
before/after the exercise asked for.

## Immediate, still open from A1

- **VM 102 is stopped and Entra Connect is not syncing.** `qm start 102` before anything
  sync-dependent.
- **The restore path has never been verified.** The one archive in the lab
  (`vzdump-qemu-105-2026_09_02-08_55_49.vma.zst`) passed `zstd -t` only — proves not corrupt, not
  restorable. 21.95 GiB of pool margin exists to test this in.
- **Host RAM is over-committed and nobody has rebalanced it.** DC01 alone is assigned 10000 MB;
  whether it needs that is untested. A free config change, not a purchase — and today's tight
  readings (422Mi free with only two VMs running) make this more pressing than it was at A1's
  close.
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

## A3 done: the Entra ID Free ceiling, measured

Full report in `exercises/2026-09-02-a3-entra-free-ceiling/report.md`. Captured, with real error
bodies, that Entra Free refuses Conditional Access (write only — read is open), PIM, and Identity
Protection, each with a *different* HTTP status/error-code shape (403/`Forbidden`,
403/`AccessDenied`, 400/`AadPremiumLicenseRequired` respectively). Security Defaults confirmed
enabled tenant-wide with no scoping property on the object at all.

**Genuine surprise: gallery-app federated SAML SSO and SCIM provisioning *setup* hit no Free-tier
gate.** Tested against Salesforce from the gallery — SAML saved cleanly with a real live signing
cert; SCIM's admin-credentials screen showed no upsell, and "Test connection" failed on
Salesforce's own invalid-credentials check, not an Entra refusal. This corrects the plan's working
assumption, but only partly — that assumption (`CURRICULUM.md` step 3) was specifically about
**non-gallery** custom SAML/SCIM apps, which this exercise did not test at all.

## Decision owed: is A3 step 3 answered enough to open the trial?

`CURRICULUM.md`'s calendar table gates opening the P1/P2 trial on "A3 step 3 has answered the
SAML/SCIM licensing question" — see line ~430, now marked **PARTIALLY DONE**. What's actually
known: gallery apps are free for both SSO and provisioning setup. What's still unknown: whether a
**non-gallery** custom app (the case the original plan's Recalled note was actually about) hits a
P1 wall that the gallery template's pre-built connector skips. This changes whether B2 (SAML/SCIM
against one application) sits inside or outside the 30-day trial window.

**Not decided:** whether to (a) run one more quick capture — add a non-gallery custom SAML app
and repeat the same SSO/provisioning attempt, closing the actual gap, before opening the trial, or
(b) treat the gallery result as good enough signal and default B2 to running outside the trial
window (the safer assumption if the non-gallery case turns out to need P1 after all), or (c) some
other call Raymond wants to make himself. Genuinely his to decide, not inferred.

## Decision owed before Phase B starts

- **The published break-glass account**, `breakglass@raytakosharkygmail.onmicrosoft.com` —
  captured deliberately as evidence across several reports, not a leak, but `CURRICULUM.md`
  exercise B1 would make it load-bearing for Conditional Access. **Rotate the identity
  (recommended)**, create and verify the replacement before touching the published one. Not yet
  decided or executed.

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

**Depends on the decision above.** Either close the non-gallery SAML/SCIM gap first (quick, no
license, same Graph Explorer/admin-center pattern as A3), or — if Raymond decides gallery-app
evidence is sufficient — open the P1/P2 trial and start **B1** (Conditional Access, report-only to
enforced) per `CURRICULUM.md`. Not yet chosen.
