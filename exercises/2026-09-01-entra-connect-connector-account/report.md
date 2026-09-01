# Entra Connect connector account — a GPO lockout, a false domain-join claim, and the wizard finally clears

## What I set out to do

Pick back up the two open items `entra-connect-install` (2026-08-31) closed on: retest the
untested "stale wizard state" hypothesis by fully exiting and relaunching Entra Connect, and —
the more interesting one — pre-provision a dedicated, least-privilege AD DS connector account
instead of handing the wizard Enterprise Admin credentials directly. That second item is
squarely on the permission-sprawl thesis: an account provisioned by copying broad access versus
one built with only the rights it actually needs.

Neither goal survived first contact with the lab in its current state. Getting to either one
required first finding out why nobody could log into DC01 at all, then why VM102 couldn't either,
then why a scheduled task hung indefinitely with no error. This report is written after all of
that happened, in the same continuous session, compiled from the working log and evidence rather
than reconstructed from memory — noted per the capture contract rather than presented as a live
narrative.

## The setup

DC01 (VM 100, `district.local`, `10.0.0.10`) and `entraconnect01` (VM 102, `10.0.0.11`), both on
the Proxmox host. DC01 has all remoting disabled by design — the only path in is `qm guest exec`
over the QEMU guest agent, or the Proxmox noVNC console for anything that genuinely needs an
interactive session. VM 102's guest agent works, same capture path.

State at session start, per `verified-claims.md` and the prior exercise's close-out:
`Administrator` on DC01 disabled (reverted at the close of `entra-connect-install`),
`LDAPServerIntegrity` back to `2`, and VM 102 recorded as domain-joined — that last one turned
out to be false, see below. Infrastructure preflight (thin pool `Data%` and host RAM) was **not**
checked before the first state change this session — a gap named plainly in "What I'd do
differently," not smoothed over. It was run retroactively and came back clean: pool at 75.78%,
under the 85% caution threshold; host RAM tight (1.1Gi available) but not itself a stop condition
(`evidence/proxmox-preflight-status.txt`).

## What I did

Roughly in order, condensed — full detail and every exit code is in the numbered evidence files:

1. Attempted DC01 console login as `sysadmin` (which turned out to display as "System Admin") —
   failed with "The sign-in method you're trying to use isn't allowed."
2. Checked `verified-claims.md`, found `sysadmin`'s `BUILTIN\Administrators` grant had been
   removed as sprawl in `constrained-admin-path`, leaving no account able to log on interactively
   to DC01 at all — not even the built-in `Administrator`, which was disabled.
3. Bootstrap re-enabled `Administrator` via `qm guest exec` (throwaway password, immediately
   rotated at the console) — same login error persisted.
4. Diagnosed via `gpresult`: found `Secure Admin WS`, a GPO linked at the **domain root** with no
   Domain Controllers exclusion, denying `Domain Admins` interactive and remote logon everywhere,
   including DC01. Fixed with a Deny-Apply ACE for the Domain Controllers group.
5. Login still failed. Diagnosed further via `secedit`: the deny right had **tattooed** into
   DC01's local LSA policy and didn't clear when the GPO stopped applying. Cleared it directly
   with `secedit /configure`. Login succeeded.
6. Created `svc-entraconnect` at the console (Raymond deliberately deviated from the given
   command: `PasswordNeverExpires: False`, no UPN), moved it to the `Service Accounts` OU.
7. Attempted to log into VM102 as `Administrator` — same class of error. Diagnosed: VM102 was
   **never actually domain-joined**, despite the record. Fixed via `Add-Computer`, verified on
   both the machine and directory side.
8. Delegated AD DS connector permissions (`Set-ADSyncBasicReadPermissions`,
   `Set-ADSyncMsDsConsistencyGuidPermissions`, `Set-ADSyncPasswordHashSyncPermissions`) to
   `svc-entraconnect` via a one-shot scheduled task running under batch logon — VM102, now
   properly domain-joined, applies `Secure Admin WS` too, and batch logon isn't denied where
   interactive is. First attempt stalled indefinitely; diagnosed as an unanswerable
   `ShouldProcess` confirmation prompt, fixed with `-Confirm:$false`, re-ran clean.
9. Ran `Set-ADSyncRestrictedPermissions` interactively to harden the account object itself.
10. Relaunched the Entra Connect wizard fresh. It cleared "Connect Directories" — the exact step
    that blocked the entire prior exercise — using `svc-entraconnect`.
11. Hit an unexplained "Not Added" status on the tenant's own verified `.onmicrosoft.com` domain
    during the sign-in configuration step. Chased three hypotheses; two ruled out, one (mine)
    proposed and disproven. Proceeded via the wizard's own override.
12. Installed with **staging mode enabled** — first-ever sync from this DC, deliberately
    previewed rather than exported live.
13. Reviewed the staging preview in Synchronization Service Manager: confirmed `sysadmin`'s
    computed UPN looks correct, and identified precisely why `bhound` will likely fail real
    export.
14. Set up a GitHub remote for the repo (none existed before), pushed via a newly generated SSH
    key, committed today's work, pushed again.

## Where Raymond was consulted

**1. How to unblock DC01 console access**, once it was clear no account could log in at all.
Offered three options — re-enable `Administrator`, restore `sysadmin`'s admin path, or something
else. Raymond: **"Re-enable Administrator"** — temporarily, password rotated first via a
channel that minimizes disclosure, with the intent to disable it again at close. **That last
part didn't happen.** A same-day check (`evidence/administrator-close-out-check.json`) found
`Administrator` still `Enabled: True`, `PasswordLastSet` matching this session's bootstrap
re-enable — no capture anywhere in this exercise shows a `Disable-ADAccount` call. This report
originally stated it was "disabled again at close" as fact; that was Recalled, not Captured, and
the capture now shows it was never done. Retracted here rather than silently corrected.

**2. Whether to investigate the GPO's scope before touching it, bypass it, or fix it directly**,
once the Domain-Admins deny rule was found. Raymond: **"Check GPO scope first"** — investigation
only. Once the domain-root link with no DC exclusion was confirmed: **"Fix the GPO scope"** — a
direct security-posture change, not a workaround.

**3. How to handle the VM102 domain-join discovery**, given how much ground the session had
already covered. Offered fix-now vs. stop-and-write-up. Raymond: **"Fix it now."**

**4. Which permission set to grant `svc-entraconnect`, and whether to harden the object.** Rather
than pick from the offered options, Raymond asked for a synthesis: *"let's consider best industry
practice and also what is going to make this join happen for this lab case, explain both and
lets get a go forward."* Answer given: basic read + ConsistencyGuid + Password Hash Sync is both
the industry-standard PHS deployment pattern *and* what this lab specifically needs, with the
DCSync-equivalent rights it grants named explicitly as the interesting part to document, not
avoid. Raymond confirmed hardening via `Set-ADSyncRestrictedPermissions` as well: **"Yes, harden
it."**

**5. How to obtain a Domain Admin execution context on VM102**, once `Secure Admin WS` was found
to deny `Administrator` there too (correctly, once VM102 was actually domain-joined). Raymond
didn't pick from the offered options directly — he posed a real stakeholder-pressure scenario:
*"i am sysadmin, director of help desk wants this working, my manager the networking manager, is
saying do the best practice, the cio wants this project off the board, my senior coworker
suggests i just 'get it done' i want to ensure i maintain the posture that we been working
towards... whats my move?"* Recommendation given: the scheduled-task/batch-logon path — no
standing posture change, bounded and reversible exposure, defensible on scope rather than on
being risk-free — plus writing up the `Secure Admin WS`/vendor-procedure conflict as a proposal
for someone above him to decide, rather than quietly working around it. Raymond proceeded with
that recommendation.

**6. Whether to reset `svc-entraconnect`'s forgotten password via `qm guest exec`**, flagged as a
different disclosure pattern than every prior reset this session (this one has to persist as the
account's live credential, not get rotated away immediately). Raymond: **"Yes, reset it."**

**7. Whether to pause and diagnose the unexplained UPN "Not Added" status, or proceed and
diagnose after.** Raymond had already checked the wizard's override box before this question was
asked — flagged plainly rather than let slide. Raymond: **"Pause, run the diagnostic first."**

**8. Whether to enable staging mode** for the first-ever sync from this DC. Raymond: **"Yes,
enable staging first."**

**9. Whether to continue into promoting out of staging and the live sign-in test, or stop.**
Raymond: **"Stop here for today."**

**10. Git remote setup.** Initially asked what "set up git" meant given local git already
existed with no remote — Raymond dismissed the question and returned with a screenshot of his
GitHub profile instead. Confirmed repo name/visibility (`district.local`, public) and
authentication method (a new SSH key, since he'll be committing often) before creating anything.

## What the box said

Full command-level detail across four phases, each already captured in its own evidence file —
summarized here with the load-bearing exit codes and outputs; nothing below is asserted without
a file behind it.

**Phase 1 — DC01 lockout.** `Get-ADUser -Identity sysadmin` (in the earlier `constrained-admin-path`
exercise) showed `sysadmin`'s only AD-nested admin path was a direct `BUILTIN\Administrators`
grant, removed that same exercise. `gpresult /r /scope:computer` on DC01 returned **five** applied
GPOs where a prior capture had only found two: `Default Domain Controllers Policy`,
`DC - Secure LDAP`, `Default Domain Policy`, `District Lockdown`, `Secure Admin WS`.
`Get-GPOReport -Name "Secure Admin WS" -ReportType Xml`, grepped for logon-rights keywords,
showed `SeDenyInteractiveLogonRight` and `SeDenyRemoteInteractiveLogonRight` both targeting
`DISTRICT\Domain Admins` (SID `...-512`); grepped for `LinksTo`, showed a single link —
`SOMPath: district.local`, the domain root, `Enabled: true`, no OU-level scoping. After adding a
Deny-Apply ACE for the `Domain Controllers` group (`exitcode 0`, `"ACE added"`), `gpupdate /force`
+ `gpresult` confirmed `Secure Admin WS` moved to "GPOs not applied because they were filtered
out — Filtering: Denied (Security)." Login still failed. `secedit /export /areas USER_RIGHTS`
showed `SeDenyInteractiveLogonRight = Domain Admins` still present in local policy despite the
GPO no longer applying. `secedit /configure` against a copy of that export with the two deny
lines blanked returned `"The task has completed successfully"`; a fresh export then showed
neither deny line present at all. Console login succeeded immediately after
(`evidence/secure-admin-ws-scope-fix.json`, `evidence/user-rights-tattoo-and-clear.json`).

**Phase 2 — VM102 domain join.** `(Get-CimInstance Win32_ComputerSystem)` on VM102 returned
`PartOfDomain: False`, `Domain: DISTRICT.LOCAL`, `Workgroup: DISTRICT.LOCAL` — the same string in
both fields, which is the actual tell (that field reports the *workgroup* name when unjoined).
`nltest /sc_verify:district.local` failed `RPC_S_SERVER_UNAVAILABLE` (`exitcode 1`) while raw
TCP/389 to DC01 succeeded — a genuine secure-channel failure, not a network gap. `Get-Service
Netlogon` showed `Stopped`/`Manual`; `Start-Service` failed outright. System event log:
`NETLOGON` event `3095`, `"This computer is configured as a member of a workgroup, not as a
member of a domain."` On DC01, `Get-ADComputer -Identity ENTRACONNECT01` returned
`ADIdentityNotFoundException`; a broader `-Filter {Name -like "*entra*"}` returned `exitcode 0`
with zero objects. After `Add-Computer -DomainName "district.local" -Credential (Get-Credential)
-Restart`: `PartOfDomain: True`, `Workgroup` empty, Netlogon `Running`/`Automatic`,
`nltest /sc_verify` returned `NERR_Success` for both connection and trust status via
`\\DC01.district.local`, and `Get-ADComputer -Identity ENTRACONNECT01` on DC01 now returned a
real object (`whenCreated: 9/1/2026 8:22:46 AM`). The `Microsoft Azure AD Sync` service, which
had been logging `"terminated with the following service-specific error: Unspecified error"`
every few minutes in the same event-log window, came up `Running`/`Automatic` on its own as a
side effect (`evidence/vm102-not-domain-joined.json`).

**Phase 3 — delegation.** `AdSyncConfig.psm1`'s delegation cmdlets were confirmed to have no
general `-Credential` parameter (only `TargetForestCredential`, for cross-forest use) via
`(Get-Command <cmd>).Parameters.Keys`. `gpresult` on VM102 post-join confirmed `Secure Admin WS`
now applies there too; `secedit` export showed `SeDenyInteractiveLogonRight` targeting Domain
Admins with **no** `SeDenyBatchLogonRight` at all, and `SeBatchLogonRight` including
`BUILTIN\Administrators` (544). A scheduled task run under batch logon produced a transcript
header reading `RunAs User: DISTRICT\Administrator` and `RUNNING AS: district\administrator` —
proof the mechanism worked even where interactive logon for that account is denied. First
delegation attempt stalled indefinitely (`LastTaskResult: 267009`, `SCHED_S_TASK_RUNNING`,
transcript frozen at `"Retrieving list of Domains in the Forest..."` across repeated queries
minutes apart). Isolated `Get-ADForest` alone: `0.13s`, ruling out DNS/enumeration as the cause.
Read `AdSyncConfig.psm1` directly and found `$PSCmdlet.ShouldProcess($domain, $Message)` gating
the per-domain export loop — PowerShell's default `$ConfirmPreference` (`High`) triggers an
interactive confirmation prompt with no console to answer it under a scheduled task. Adding
`-Confirm:$false` to all three cmdlets fixed it: re-run returned `LastTaskResult: 0`, transcript
completed to `=== DONE ===`. The before/after ACL dump inside that same transcript showed
`svc-entraconnect` gaining `Replicating Directory Changes` and `Replicating Directory Changes
All` at the domain root specifically after `PasswordHashSync` ran, not before —
direct confirmation, not inference from a clean exit code. `Set-ADSyncRestrictedPermissions`,
run separately with a real `-Credential`, produced only a single ambiguous status line at the
console; verified against the live object instead: `Get-Acl -Path "AD:\CN=svc-entraconnect,..."`
returned `AreAccessRulesProtected: True` with a tight, correct explicit ACL — inheritance from
the OU genuinely blocked (`evidence/delegation-attempt-stalled.json`,
`evidence/delegation-complete.json`).

**Phase 4 — the wizard and the staging preview.** The wizard cleared "Connect Directories" using
`svc-entraconnect` on the first relaunch after all of the above — the exact step
`entra-connect-install` never got past. The "Microsoft Entra sign-in configuration" step showed
`raytakosharkygmail.onmicrosoft.com` as "Not Added" despite the Entra admin center's own Domain
names blade confirming it `Available`, spelled identically. Ruled out via evidence: a full
wizard relaunch produced the identical result (not a cache); `Test-NetConnection` from VM102
confirmed `login.microsoftonline.com`, `graph.microsoft.com`, and `graph.windows.net` all
reachable on 443 (not a connectivity gap). One hypothesis — a missing
`provisioningapi.microsoftonline.com` endpoint — was proposed from memory, tested, and
**disproven**: `Resolve-DnsName` for that hostname returned nothing both via DC01's forwarder
and via `1.1.1.1` directly, meaning the hostname doesn't exist in public DNS at all. Root cause
of the "Not Added" status remains unexplained. Installed with staging enabled; Synchronization
Service Manager's Operations tab showed only Full Import/Full Synchronization runs, zero Export
runs — staging mode confirmed working by absence of the export step entirely, not just a
"nothing changed" claim. `district.local`'s Full Synchronization statistics: `26 Projections`,
`0 Joins`, `203 Disconnectors`, `Export Attribute Flow: 20`, `Provisioning Adds: 20` — matching
exactly the 20 objects retrieved via Search Connector Space on the AAD connector. Opening a
staged object's Pending Export properties directly (not trusting the grid's own
`userPrincipalName`/`displayName` columns, which displayed blank for every row despite real
underlying values) showed `sysadmin`'s computed `userPrincipalName:
sysadmin@raytakosharkygmail.onmicrosoft.com` — correct — and, separately, `bhound`'s computed
`userPrincipalName: bhound@district.local` — Entra Connect's fallback for a missing source UPN,
constructing `sAMAccountName@<on-prem domain>` rather than leaving it blank, landing on a
suffix that will never be verifiable in this tenant (`evidence/wizard-cleared-connect-directories.txt`,
`evidence/upn-suffix-not-added-unexplained.json`, `evidence/wizard-install-complete.txt`,
`evidence/staging-preview-findings.txt`).

## What broke, and why

**I stated something as fact that I hadn't verified, and it happened to become true for a
different reason later.** When `Administrator` couldn't log into VM102, I asserted `Secure Admin
WS` was "legitimately blocking Domain Admins there, working as intended" — reasonable-sounding,
and wrong at the time, because VM102 wasn't domain-joined yet and couldn't process any domain
GPO at all. It became true only after the join was fixed. I retracted this explicitly rather
than let the earlier claim stand uncorrected once the real cause was found.

**I invented a hostname from memory and presented it as a plausible real endpoint.**
`provisioningapi.microsoftonline.com` was named as a likely cause of the UPN "Not Added" mystery
without being checked against any actual source. It doesn't exist — `Resolve-DnsName` against an
independent resolver confirmed no record anywhere. Retracted on the record rather than smoothed
into the evidence log as if it had been a real finding.

**A sequencing gap, not a wrong removal.** `constrained-admin-path` treated `sysadmin`'s direct
`BUILTIN\Administrators` grant as undocumented sprawl and removed it — correctly. A named
account with a standing direct Administrators grant on a domain controller, provisioned the same
way as the other sprawl this series documents, is exactly what should come out. An earlier draft
of this report read the fact that removing it broke console access as proof the removal itself
was wrong, calling the grant "load-bearing, not excess." That's the sprawl excuse in different
words — a grant being in use doesn't make it appropriate, and every piece of standing sprawl is
load-bearing for someone.

What actually went wrong is sequencing: by the time this exercise started, `Administrator` was
disabled, `Secure Admin WS` denied Domain Admins everywhere including DC01, and `sysadmin`'s
grant had already been removed with no verified replacement — three closures stacking into a
lab with zero working admin paths to its own domain controller. The fix applied same day was to
restore the missing step, not reverse the removal: add `sysadmin` to Domain Admins as a
deliberate, on-the-record decision, prove the login actually works interactively before touching
anything else, and only then disable `Administrator` again
(`evidence/sysadmin-domain-admins-and-administrator-disabled.json`). The lesson is verify a
break-glass path before removing the last one, not that removing sprawl was the mistake.

**A security setting doesn't revert just because the policy that set it stops applying.**
User-rights assignments tattoo into local LSA policy. Filtering `Secure Admin WS` off DC01 via a
Deny-Apply ACE was necessary and correctly targeted, but it only stops the setting from being
*re-pushed* — it does nothing to what's already written. This cost a full extra diagnostic round
(a `secedit` export, then a targeted `secedit /configure`) that a naive "the GPO doesn't apply
anymore, so it should be fine now" assumption would have missed entirely.

**A multi-line paste into PowerShell ISE silently truncated a command.** Handing Raymond a
multi-line scheduled-task registration block to paste produced a command that dropped
`-Password` and `-RunLevel Highest` without any visible warning — it just truncated at a trailing
`-`. Two failed attempts resulted before switching to writing the command into a script file and
invoking it as a single line, which doesn't have this failure mode. My fault for handing over
something that needed pasting multi-line into an interactive shell.

**Two separate bash-quoting bugs, one Raymond's environment and one mine.** The bootstrap
Administrator reset first failed because `$_` inside a double-quoted `-Command` argument got
expanded by bash before PowerShell ever saw it — fixed by wrapping the whole thing in single
quotes. Later, I made the identical class of mistake myself, escaping inner double quotes that
were already protected by outer single quotes, breaking a `Get-ADComputer -Filter` call. Same
lesson, learned twice.

## What I'd do differently

**Run the infrastructure preflight before the first state change, not after.** The Administrator
bootstrap re-enable happened before any pool/RAM check this session, breaking the pattern the
scoped skill establishes specifically because of this project's crash history. It came back
clean, but that was luck, not process.

**Flag an inference as an inference the moment I make it, not after being proven wrong.** The
`Secure Admin WS`/VM102 assertion and the invented endpoint hostname were both stated with more
confidence than the evidence behind them warranted. Both got caught and retracted, but the
pattern — state a plausible thing, discover it's wrong, retract — is exactly the failure mode
this whole project's discipline exists to prevent, and it happened twice in one session anyway.

**Don't skip a wizard screen without reviewing it just because momentum is high.** The
"Filtering" step got clicked through without a screenshot, unlike every other step. Lower-stakes
than Domain/OU scope, probably, but "probably" isn't the standard this project holds everything
else to.

**Commit and push more than once per session on a day this dense.** Fifteen files accumulated
locally before the first commit of the day happened, triggered by a tangential "let's set up git"
rather than as part of the exercise's own workflow. Not a data-loss risk given local git existed
throughout, but worth building in as a habit going forward now that a remote exists.

## Open questions

- **`bhound`'s fate is resolved** — see the addendum below. It was disabled after its Key Admins
  membership turned out to grant a live shadow-credentials path, which also moots the export
  question below it in an earlier draft of this list.
- **The authoritative test for the "Not Added" UPN mystery is still untested**: whether a real
  synced account can actually sign in to Microsoft Entra ID with its on-premises credential.
  Staging mode's positive signal (a correctly-computed UPN for `sysadmin`) is not proof.
- **Root cause of the "Not Added" status itself is still unknown.** Two hypotheses were ruled
  out (stale cache, missing connectivity); one was proposed and disproven. No replacement
  hypothesis exists yet.
- **Whether the tattooed deny right on DC01 could re-tattoo on a future GPO refresh cycle** was
  never observed over time — only immediately after the fix, once.
- **Origin of `Secure Admin WS`'s domain-root scope** — deliberate design choice or setup-time
  scope creep — was never established, only its current effective scope.
- **`constrained-admin-path`'s remediation itself was correct** — see the corrected "What broke"
  entry above and the addendum below. What still needs a formal addendum on that older report is
  narrower: the *sequencing* gap across later exercises that stacked into a full lockout, not the
  original removal decision.
- **AD Recycle Bin is not enabled on `district.local`** — flagged by the wizard's own completion
  screen, not addressed this session.
- **The "Filtering" wizard step was never actually reviewed** — screenshot skipped, contents
  unknown.
- **`districtsafetyphoto.com` verification never happened**, and the roughly-one-month
  registration window flagged in `entra-connect-install` (2026-08-31) has now nearly elapsed.
- **This report covers what's easily two exercises' worth of material** — infrastructure/GPO
  work and Entra Connect delegation work are only loosely related, and splitting them would have
  made each easier to navigate. Noted for next time rather than retroactively split now.

## Addendum — same-day close-out correction

After this report's first draft, a requested follow-up capture
(`evidence/administrator-close-out-check.json`) found the "disabled again at close" claim above
was false — `Administrator` was still `Enabled: True`. Rather than quietly re-disable it, the
gap it exposed was fixed properly: `sysadmin` was added to Domain Admins, the login was proven
by an actual interactive console session on DC01 (not inferred from group membership), and only
then was `Administrator` disabled again — this time with a verified second admin path already in
place (`evidence/sysadmin-domain-admins-and-administrator-disabled.json`). `Administrator`'s
password, previously typed into a Task Scheduler credential store on VM 102 during this
exercise, was then rotated (`evidence/administrator-password-rotated-no-disclosure.json`); the
new value was never returned to any channel or recorded anywhere, since the account is disabled
and no one needs it right now. The first rotation attempt failed on the same bash `$_`
double-quoting bug documented earlier in this exercise's own evidence — fixed the same way, by
single-quoting the whole `-Command` argument.

A follow-up capture on `Key Admins`'s domain-root rights (requested per the review's follow-up
list) turned "possible shadow-credentials path" into a captured finding: Key Admins holds
`SPECIAL ACCESS for msDS-KeyCredentialLink` at the domain root, and `bhound` — the aging
BloodHound-capstone throwaway, still enabled and logging on as recently as 2026-08-27 — was its
only member (`evidence/key-admins-domain-root-rights.json`). That's domain-wide write access to
the shadow-credentials attribute sitting on a forgotten account, a live escalation path rather
than a theoretical one. Raymond's call was to remove it from Key Admins and disable it, both done
and verified same day (`evidence/bhound-remediated.json`).
