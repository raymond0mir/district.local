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

**`Secure Admin WS`'s domain-root link, with a Deny-Apply exception for the current Domain
Controllers group, is fragile.** It works, and it's the fix actually applied 2026-09-01, but a
future GPO edit that drops the exception — or a new domain controller added without checking for
it — silently reintroduces the exact lockout this project already hit once. The cleaner fix
(relink at the workstation/member-server OUs it actually means to govern, drop the exception
entirely) is still open, see `CARRYOVER.md`.

## Infrastructure

**Proxmox host RAM was at 1.1 GiB available as of the last check.** Out of 15 GiB total, with
2.1 GiB already in swap. Not itself a stop condition per the skill's pre-flight rule, but tight
enough to be worth watching, especially alongside the thin-pool history below.
*Evidence:* `exercises/2026-09-01-entra-connect-connector-account/evidence/proxmox-preflight-status.txt`.

**The Proxmox thin pool's overcommit ratio hasn't been rechecked since the extension and prune
that fixed it.** An earlier capture found it at roughly 3.6x overcommitted (864.93 GiB allocated
against a 237.47 GiB volume group); since then the pool was extended (+14 GiB) and multiple
snapshots across three VMs were pruned, which should have improved that ratio significantly —
but the ratio itself was never recaptured after those changes, only `Data%` was (see below).
Worth a fresh `lvs`/`vgs` read before treating the overcommit question as closed.
*Evidence (stale figure, cited for context only):*
`exercises/2026-08-31-dc01-constrained-admin-path/report.md`, "What broke, and why."

**Thin pool `Data%` was last captured at 88.47%** (2026-09-02, after this session's own
pruning brought it down from 92.01%), above the skill's 85% caution threshold — not below it.
This session proceeded past the threshold anyway on Raymond's explicit judgment call (the
planned operation was a light incremental sync, not disk-heavy), not because the pool was
actually safe. The VG behind it (`pve`, single PV `/dev/nvme0n1p3`, 237.47 GiB) had only
2.00 GiB `VFree` — there is essentially no room to `lvextend` without adding real physical or
virtual storage. This is a harder constraint than the earlier "overcommit ratio never
rechecked" note below: the pool isn't just cluttered with prunable snapshots, it's structurally
near its ceiling. *Evidence:*
`exercises/2026-09-02-entra-connect-upn-signin-test/evidence/preflight-thin-pool-and-memory-20260902.txt`,
`exercises/2026-09-02-entra-connect-upn-signin-test/evidence/postprune-thin-pool-and-memory-20260902.txt`
(the `vgs`/`pvs` free-space reading itself was not filed as a separate evidence capture — see
that exercise's `CARRYOVER.md` entry).

**VM 104 (pfSense) has zero snapshots**, after all three were pruned during the 08-31 thin-pool
crisis response. If a future firewall configuration change goes wrong, there is currently no
rollback point for the router. *Evidence:*
`exercises/2026-08-31-dc01-unexpected-shutdown/evidence/pool-extended-and-pruned.txt`.

**What actually happens when the Proxmox thin pool hits 100% is still unknown.** It's come close
twice (96.49%, then 86.48%) but the boundary itself has never been crossed and observed directly.
*Evidence:* `exercises/2026-08-31-dc01-unexpected-shutdown/report.md`, "Open questions."

**AD Recycle Bin is not enabled on `district.local`.** Flagged by the Entra Connect wizard's own
completion screen; means an accidentally deleted object (user, group, computer) has no clean
recovery path short of an authoritative restore. *Evidence: flagged in
`exercises/2026-09-01-entra-connect-connector-account/report.md`'s Open questions — not yet
independently captured via a direct `Get-ADOptionalFeature` read.*

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

## Recently closed (for contrast, not action)

- `bhound` — an enabled BloodHound-capstone throwaway holding a live shadow-credentials path via
  Key Admins — was disabled and removed from the group, 2026-09-01.
- A second, forgotten instance of the `OneShotDelegation` scheduled task on VM 102 was found
  still holding a live `DISTRICT\Administrator` credential and removed, 2026-09-01.
- `Administrator`'s password, previously typed into that same scheduled task, was rotated without
  the new value ever being disclosed to any channel, 2026-09-01.
