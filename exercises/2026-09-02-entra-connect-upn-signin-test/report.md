# The UPN sign-in test — resolving "Not Added" the only way that actually settles it

## What I set out to do

The 09-01 connector-account exercise installed Entra Connect in staging mode and hit an
unexplained anomaly: the wizard displayed the tenant's own `raytakosharkygmail.onmicrosoft.com`
suffix as "Not Added," despite the Entra admin center's own domain list showing it verified.
Staging mode's preview computed a correct UPN for `sysadmin` anyway, but per Microsoft Learn's
UPN-population rules, a correctly-computed value in preview can't distinguish a verified suffix
from an unverified one that happens to compute the same result by coincidence. Raymond's
instruction at that exercise's close was explicit: "stop here for today," with promoting out of
staging and the live sign-in test named as the next step, not yet run. Today's goal was to run
that authoritative test: promote out of staging, export a real object, and have it actually sign
in to Entra ID with its on-premises credential.

## The setup

Same lab — DC01 (VM 100) and `entraconnect01` (VM 102), same capture path (`qm guest exec` from
the Proxmox host shell; DC01 has no remoting by design). Pre-flight was run, but not gated
correctly — see What broke, and why. The reading itself: thin pool `Data%` at 92.01% (above the
skill's 85% stop-threshold) and host RAM at 169Mi available, both **before** any state change in
this exercise (`evidence/preflight-thin-pool-and-memory-20260902.txt`).

One judgment call made before any command ran: which restamped account to use for the sign-in
test. `sysadmin` was the account the 09-01 staging preview had already validated, but it's
Domain Admins-tier, and pushing a Tier 0 credential through a browser-based cloud auth flow when
a non-privileged account proves the identical mechanism seemed like avoidable exposure. Raymond's
call: a non-privileged user. `jsmith` was picked as that account.

## What I did

Roughly in order: a pre-flight/snapshot sequencing mistake and its recovery; three rounds of
thin-pool remediation; confirming the staging-mode toggle has no PowerShell path; disabling
staging via the wizard GUI; a real export sync; a password reset that had to be redone on the
right capture path; and the sign-in itself, which ran into two dead ends (a Graph Explorer query
mixup, then a genuine tenant-license limit) before landing on the actual proof.

## Where Raymond was consulted

**1. Which account for the sign-in test.** `sysadmin` (continuity with the 09-01 staging
preview, but Domain Admins) versus a non-privileged restamped user. Raymond: **a non-privileged
user** — `jsmith`.

**2. Prune snapshots or extend the thin pool, once pre-flight showed 92.01%.** I offered both,
plus a third option Raymond raised himself: whether the pool could be grown with a physical
SD card or USB stick he could insert into the laptop. I recommended against using removable
media as a live PV — a thin pool spans PVs, so a failed/unplugged USB stick risks corrupting
the *whole* pool, not just its own capacity, and SD/USB sustained-write performance is a poor
match for the exact disk-pressure pattern that caused this lab's prior crash. I suggested it
instead as a `vzdump` backup target (freeing on-pool space safely, after an independent backup
exists) as a separate, unhurried follow-up. `vgs`/`pvs` showed the VG itself had only 2.00 GiB
free regardless, closing off a simple `lvextend` either way. Raymond's actual decision: prune
now. Two already-superseded pairs (`pre-upn-restamp-20260831`, `pre-domain-join-fix-20260901`)
came down first (92.01% → 88.99%), then a third (`pre-secure-admin-ws-scope-fix-20260901`,
88.99% → 88.47%) on a second go-ahead.

**3. Proceed at 88.47%, pull VM101's snapshot into scope, or stop for today.** VM101's
`win11-ootb` snapshot is the pool's single largest real consumer (64GB LV, 62% actual data), but
it's outside this project's tracked VM set and is VM101's only rollback point — I declined to
treat it as a default prune candidate. Raymond: **proceed** (his framing: "go ahead with option
2"), on the stated reasoning that the next operation (`Start-ADSyncSyncCycle` over ~13 directory
objects) is a light incremental write, not the sustained OS-install-class I/O that caused the
earlier crash. Logged plainly as a judgment call under residual risk, not a claim that 88.47% is
actually under the skill's threshold.

**4. Reset `jsmith`'s password.** Raymond: "we should reset it." The first attempt used
`qm guest exec` with `Set-ADAccountPassword -Reset` and no `-NewPassword` — it hung, because that
capture path has no TTY for the interactive secure-string prompt, the same class of problem the
project's own `-NonInteractive` convention for scheduled tasks exists to prevent. Corrected by
having Raymond run the identical command directly on DC01's own console instead, where the
prompt could actually be answered. The password value itself was never typed into a command line,
disclosed to this conversation, or pasted anywhere — only Raymond knows it, which is also the
whole point: he needed to type it into a real sign-in page next.

**5. Sign-in log versus completing MFA registration**, once Entra Free's Security Defaults
stopped `jsmith`'s sign-in at a mandatory "set up another way to verify it's you" gate. I offered
the sign-in log route first as non-destructive; it hit a real license wall (see What the box
said). Fell back to completing MFA registration for `jsmith`, which Raymond did.

**6. Leave Entra Connect promoted out of staging, or revert; stop for today or keep going.**
Raymond: **"leave it promoted, call it for today, write it up."**

## What the box said

**Pre-flight, before any state change** (`evidence/preflight-thin-pool-and-memory-20260902.txt`)
— `Data%: 92.01%`, host RAM available `169Mi` of 15Gi. Both readings predate this exercise's own
snapshots; the snapshot step should have been gated on this result and wasn't (see What broke).

**Thin-pool extend path checked and closed** — `vgs pve -o+vg_free` / `pvs` (not filed as a
separate evidence file; a single interactive exchange, not a scripted capture) showed the sole PV
(`/dev/nvme0n1p3`, 237.47 GiB) with only `2.00g` `VFree`. No `lvextend` was possible without new
storage.

**Post-prune pool state** (`evidence/postprune-thin-pool-and-memory-20260902.txt`) — `Data%`
92.01% → 88.99% → 88.47% across two prune rounds; RAM recovered substantially, 169Mi → 1.7Gi
available. Diminishing returns each round (3.02 points, then 0.52), consistent with newer
snapshots having accumulated less divergence from their origin than the two-day-old pair did.

**Staging-mode toggle has no PowerShell path**
(`evidence/staging-mode-toggle-not-in-powershell.json`) — `Get-Command -Module ADSync -Name
'*Staging*'` returned genuinely empty output twice (no `out-data`/`err-data` keys at all, not a
paste artifact — reproduced identically on request). `(Get-Command
Set-ADSyncScheduler).Parameters.Keys` listed 18 parameters, none named `StagingModeEnabled`.
`Get-ADSyncScheduler` itself confirmed the then-current state: `StagingModeEnabled: True`.

**Staging mode disabled** (`evidence/staging-mode-disabled.json`) — via the Azure AD Connect
wizard's GUI "Configure staging mode" task (screen capture of "Configuration complete... Staging
mode has been successfully disabled" is Recalled, not filed as evidence). The real proof is
`Get-ADSyncScheduler` read again after: `StagingModeEnabled: False`.

**First real export sync** (`evidence/initial-sync-cycle-success.json`) —
`Start-ADSyncSyncCycle -PolicyType Initial` returned `Result: Success`. This confirms the run
didn't fail outright, not any specific object's individual outcome.

**`jsmith` landed in Entra ID** (`evidence/jsmith-exported-to-entra-id.json`) — Graph
`GET /users?$filter=userPrincipalName eq 'jsmith@raytakosharkygmail.onmicrosoft.com'` returned
one object: `onPremisesSyncEnabled: true`, `onPremisesSamAccountName: jsmith`,
`accountEnabled: true`, `id: 03b0f0f4-1230-42c1-983c-9bb5ecb1a2c8`. First captured evidence that
the "Not Added" domain didn't block a real export.

**Password reset, first attempt hung, second attempt confirmed**
(`evidence/jsmith-password-reset-confirmed.json`) — `qm guest exec`'s attempt at
`Set-ADAccountPassword -Identity jsmith -Reset -Server DC01` returned `"timeout reached,
returning pid"` / `pid: 4624` and had to be interrupted. Re-run directly on DC01's console
(interactive, value never disclosed), confirmed via `Get-ADUser -Properties PasswordLastSet`:
`10/3/2025 9:25:36 PM` (the untouched October 2025 baseline) → `9/1/2026 5:10:41 PM`.

**Sign-in logs blocked by license, not permissions**
(`evidence/signin-logs-blocked-by-license.json`) — `GET /auditLogs/signIns` first hit a plain
403 consent gap (not filed separately), then, after consenting to `AuditLog.Read.All`, a
distinctly different and more specific error: `Authentication_RequestFromNonPremiumTenantOrB2CTenant`
— "Tenant is not a B2C tenant and doesn't have premium license." A real, named constraint, not
a workaround-able gap.

**The authoritative result** (`evidence/jsmith-authenticated-session-confirmed.json`) — after
signing in interactively at `login.microsoftonline.com` with the freshly-reset on-premises
password and completing MFA registration to satisfy Security Defaults, `GET /me` as `jsmith`
returned a clean `200`: `id: 03b0f0f4-1230-42c1-983c-9bb5ecb1a2c8` (matching the export-check
object exactly), `userPrincipalName: jsmith@raytakosharkygmail.onmicrosoft.com`,
`displayName: "John Smith"` — synced attributes populated, not the bare stub `breakglass`'s own
`/me` call showed in an earlier exercise. `jsmith` genuinely authenticated to Entra ID with an
on-premises AD credential via Password Hash Sync, on the domain the wizard called "Not Added."

## What broke, and why

**I bundled a pre-flight gate with the state change it was supposed to gate.** Phase 0
(pre-flight) and Phase 1 (snapshot) were handed to Raymond in the same instruction block instead
of waiting for the pre-flight result before authorizing the snapshot. `Data%` was already 92.01%
— above the skill's own 85% stop-threshold — before either of this exercise's snapshots existed,
and the snapshot step ran anyway, adding four more thin-provisioned LVs on top of an
already-overcommitted pool. This is my mistake, caught and stated here rather than left implicit
in a quietly-adjusted later paragraph, per the project's standing rule that my own errors get
said plainly and immediately.

**The thin pool's real capacity problem is still not solved, only patched enough to proceed
today.** `EXPOSURES.md` already flagged that the overcommit ratio (last measured at ~3.6x) was
never rechecked after the 08-31 extension-and-prune. This exercise adds a second data point in
the same direction: pruning three already-superseded snapshot pairs bought back only 3.54
percentage points combined, and the VG itself has essentially no free space to extend into
(2.00 GiB on a single 237.47 GiB PV) without adding real storage. The pool is structurally tight,
not just cluttered with prunable snapshots.

**`qm guest exec` cannot service an interactive password prompt.** `Set-ADAccountPassword
-Reset` with no `-NewPassword` blocked on a secure-string prompt that had nothing to answer it,
because the guest-agent execution path has no attached TTY — the same underlying reason
scheduled-task PowerShell in this project always runs `-NonInteractive`. This wasn't a fluke; in
hindsight it was predictable from that existing convention, and I should have named the
constraint before the first attempt rather than after it hung.

**A stale Graph Explorer query looked like a fresh result.** The first "sign-in logs" paste back
was actually the cached `jsmith` user-lookup query from two steps earlier — Graph Explorer had
re-run the query already in its editor rather than the new URL typed into the address bar. Same
class of "looks like it ran, didn't" gap the `hybrid-identity-upn-baseline` exercise's
Request-Body/URL-field mixup already demonstrated once; it recurred in a different shape.

## What I'd do differently

**Never bundle a pre-flight check and the first state-changing command in one instruction
block again.** Gate explicitly: hand over the pre-flight command alone, wait for the actual
number, then decide whether to proceed — not "here are the next three steps" with the gate
buried in the middle.

**Check `vgs`/`pvs`, not just `lvs`, as a standing part of pre-flight going forward.** Learning
"there's no VG free space to extend into" only after already committing to a prune-vs-extend
conversation wasted a round trip that a slightly wider pre-flight check would have avoided.

**For any DC01 password reset whose value a human actually needs to use, go straight to the
console.** The `qm guest exec` attempt was a predictable dead end given the project's own
established `-NonInteractive` lesson — I should have named that up front instead of discovering
it by making Raymond wait through a 30-second hang.

## Open questions

- **Root cause of the wizard's "Not Added" domain status is still unknown.** This exercise made
  it practically moot — sign-in and export both work regardless — but did not explain why the
  wizard displays it that way. Worth chasing if it ever resurfaces as something that *does*
  block a real operation.
- **The thin pool's headroom problem is unresolved, not just deferred.** 88.47% `Data%`, 2.00 GiB
  `VFree` in the VG, no easy extend path without new physical/virtual storage or a materially
  riskier live shrink of the host's own `root` LV. The `vzdump`-to-external-media-then-prune
  approach was discussed as the right shape of fix but not executed this session.
- **Whether the hung `qm guest exec` process (pid 4624) on DC01 was actually terminated was
  never confirmed.** Asked, not answered — worth a quick `Get-Process -Id 4624` check.
- **Entra Connect is now genuinely out of staging for the first time — every future sync from
  this DC is a real export, not a preview.** That changes the stakes of any future change to
  UPNs, group memberships, or the connector account's delegation; nothing in this exercise
  assumes otherwise, but it's worth stating as a standing fact for future sessions.
- **`jsmith` now carries a registered MFA method and a live Entra ID identity** — the first
  restamped account to actually be tested end-to-end. Whether the other eight restamped accounts
  should eventually get the same treatment, or whether `jsmith` stays the project's single test
  case, hasn't been decided.
- **Sign-in logs are unavailable on this tenant's Entra Free license.** Any future exercise
  wanting sign-in-log evidence needs either a licensing decision (Entra ID P1/P2) or a different
  capture method — `GET /me`-as-the-user, as used here, is the fallback that's already proven to
  work.
