# A2: reading the unread GPO surface, and de-fragilizing the Secure Admin WS domain-root link

**Exercise:** A2 from `CURRICULUM.md`, run and completed 2026-09-02.
**Result:** `Secure Admin WS` no longer touches DC01 through any mechanism — relinked to
`OU=Workstations` and `OU=Servers/OU=Application Servers`, domain-root link removed, the 09-01
Deny-Apply exception removed as no longer needed. VM 102 moved into the OU structure it always
should have been in. The relink itself briefly recreated the exact lockout exposure this exercise
set out to eliminate — caught, understood, and fixed within about 90 seconds; see *What broke*.
Only the final half of step 4's tattoo observation remains open, since that needs more elapsed
time than one session provides.

## What I set out to do

`CURRICULUM.md`'s hypothesis: `Secure Admin WS`'s domain-root link with a Deny-Apply exception for
Domain Controllers can be replaced by linking at the OUs it actually means to govern, removing the
lockout mechanism entirely rather than fencing it off. Before touching that, the exercise calls for
reading `Default Domain Policy` and `District Lockdown` — two of DC01's five effective GPOs never
examined at the same depth as the other three — and establishing, or explicitly failing to
establish, why `Secure Admin WS` was linked at the domain root in the first place.

## The setup

DC01 running, pool at 70.91% (healthy), host RAM tight (422Mi free, 2.9Gi available, 1.2Gi in
swap — noted, not treated as blocking for read-only work). DC01's nine domain GPOs, per RSoP:
`Default Domain Controllers Policy`, `DC - Secure LDAP`, `Default Domain Policy`,
`District Lockdown` currently applying; `Secure Admin WS` filtered out via the 09-01 Deny-Apply
fix.

## What I did

1. `Get-GPO -All` for timestamps and ownership across all nine domain GPOs — cheap, decisive test
   for the origin question.
2. Full `Get-GPOReport -ReportType Xml` for `Default Domain Policy` and `District Lockdown`.
3. `gpresult /r` (failed — no logged-on user in a `qm guest exec`/SYSTEM context), corrected to
   `gpresult /r /scope:computer`.
4. `secedit /export /cfg ... /areas USER_RIGHTS`, first pass ambiguous (empty grep, unclear if
   real), corrected with exit-code and file-existence verification and a full dump instead of a
   targeted grep.
5. `Get-ADGroup` exact-match and `*Admin*`-wildcard sweep, to test whether `District Lockdown`'s
   Restricted Groups target ("Admins") is a real security principal.
6. Full OU inventory (`Get-ADOrganizationalUnit -Filter *`) and every AD computer object's
   placement, to find a real relink target and check nothing unexpected sits where the new links
   would reach.
7. Pre-change snapshot of DC01 (`pre-secure-admin-ws-relink-20260902`), per CURRICULUM's explicit
   instruction for this change class.
8. Stage 1 (additive): `Move-ADObject` for `ENTRACONNECT01` into `OU=Application Servers`;
   `New-GPLink` for `Secure Admin WS` onto `OU=Application Servers` and `OU=Workstations`.
9. Stage 2: `Remove-GPLink` for the domain-root link (failed once, fixed — see *What broke*); the
   Deny-Apply ACE removed by reversing 09-01's exact `ActiveDirectoryAccessRule` mechanism rather
   than improvising new ACL syntax.
10. Verification throughout: `Get-GPOReport`'s own `LinksTo` as ground truth (not just cmdlet exit
    status), `gpupdate /force /target:computer` + `gpresult /r /scope:computer` on DC01 before and
    after.

## Where Raymond was consulted

Step 3 needed his input twice, both handled before any change ran:

1. **The relink plan itself.** Reading the OU structure surfaced that VM 102 sits in the default
   `Computers` container, not the custom `Servers`/`Workstations` OUs — meaning a straight relink
   would silently drop `Secure Admin WS` from VM 102 entirely, which CURRICULUM's step 3 explicitly
   wants preserved. Asked which way to handle it: move VM 102 into the OU structure and relink
   there plus Workstations, relink to Workstations only and accept the loss, or hold off and
   question whether the GPO should apply to a member server at all. **Decided: move VM 102 into
   `OU=Application Servers`, relink to that plus `Workstations`.**
2. **Four undocumented AD computer objects** (`DESKTOP-O860UU9`, `testdumb`, `DESKTOP-PRPTMFO`,
   `BUTT`) turned up in the inventory taken to find VM 101 — two of them already sitting in
   `Workstations`, meaning they'd start receiving `Secure Admin WS`'s restrictions the moment the
   new link went in. Asked whether these were recognized, since I had no context for them and
   didn't want to widen a GPO's reach onto something neither of us could identify. **Raymond's
   answer, quoted: "everything in there was done recently or at inception, nothing that will break
   anything, we can move them, use them, relabel them, they are all open resources for us to test
   with."** Proceeded on that basis.

## What the box said

Full output in `evidence/`. Headline results:

- **GPO origin (step 2): answered, circumstantially but with real evidence.** Eight of nine domain
  GPOs are owned by `DISTRICT\Domain Admins`, created 9/30–10/4/2025 (the initial build window).
  `Secure Admin WS` alone is owned by the individual account `DISTRICT\sysadmin`, created
  10/8/2025 — 4 to 8 days after everything else. Points toward "added later, individually," not
  "part of the deliberate initial baseline."
- **Tattoo recurrence (step 4, baseline): no recurrence observed.** Full, verified
  `[Privilege Rights]` export shows `SeDenyInteractiveLogonRight` and
  `SeDenyRemoteInteractiveLogonRight` both genuinely absent, after the most recent GPO refresh and
  multiple reboots since the 09-01 fix. Holding across everything observed so far.
- **Two new findings from actually reading these GPOs for the first time:**
  - `Default Domain Policy` sets `LockoutBadCount = 0` — no account-lockout threshold exists
    anywhere in this domain.
  - `District Lockdown`'s Restricted Groups setting targets a group named "Admins," which does not
    exist anywhere in `district.local` (confirmed against all 13 real `*Admin*` groups). Currently
    inert — Windows can't restrict membership on a group that isn't there — but dead configuration
    in a domain-root-linked GPO nobody had verified before. The OU inventory found a likely
    explanation never available before: two OUs literally named `Admins` exist in this domain
    (`OU=Admins,DC=district,DC=local` and a nested one under `Groups/Security`) — Restricted Groups
    can only target a security group, not an OU, so this looks like whoever wrote the setting
    confused the two, not a reference to something that was ever real.
- **The relink (step 3): done, verified, final state confirmed.** `Secure Admin WS` now links only
  to `OU=Workstations` and `OU=Servers/OU=Application Servers`. `gpresult /r /scope:computer` on
  DC01 post-change shows `Applied Group Policy Objects`: `Default Domain Controllers Policy`,
  `DC - Secure LDAP`, `Default Domain Policy`, `District Lockdown`, `Local Group Policy` —
  `Secure Admin WS` doesn't appear at all, not even filtered, because nothing links it to DC01's OU
  chain any more. `ENTRACONNECT01` (VM 102) now lives in `OU=Application Servers`, so it keeps
  receiving `Secure Admin WS` through the new direct link instead of the old domain-root cascade.

## What broke, and why

Two of my own commands failed on the first attempt, both worth recording rather than quietly
fixing and moving on:

**`gpresult /r` failed** with `"The user DISTRICT\DC01$ does not have RSoP data."` — `qm guest
exec` runs as SYSTEM with no interactively logged-on user, so user-scoped RSoP has nothing to
report. `/scope:computer` is what's needed in this execution context; worth remembering for any
future `gpresult` call through this channel.

**My own PowerShell quoting broke a `Get-ADGroup -Filter` call.** I tried to smuggle a literal
single-quote into a filter string using `$(0x27)` inside a bash single-quoted `qm guest exec`
argument — that evaluates `0x27` as the *integer* 39 and interpolates the text "39", not a quote
character. Fixed by using a PowerShell script-block filter (`-Filter {Name -eq "Admins"}`) instead
of a quoted string, which needs no inner single-quote at all and sidesteps the bash-quoting
conflict entirely. Noting this because the same trap is live for any future filter needing a
literal value inside this specific quoting chain (bash single-quotes wrapping a PowerShell
`-Command` string).

**The most significant thing that broke: `Remove-GPLink` briefly recreated the exact lockout
condition this exercise exists to eliminate.** `New-GPLink -Target "OU=..."` had worked fine with
distinguishedName-form targets. For the domain root, I used `"district.local"` — the same string
`Get-GPOReport`'s own `SOMPath` field displays, and the form the rest of this project's tooling
treats as the domain root's normal name. `Remove-GPLink` rejected it: *"There is no such object on
the server (0x80072030)."* In the same script, on the same run, the Deny-Apply ACE removal
(a separate, independent call) succeeded. Net effect: for roughly 90 seconds — bounded by the
`gpupdate` timestamp in the failed attempt (10:13:08 AM local) and the `gpupdate` timestamp in the
fix (10:14:45 AM local) — `Secure Admin WS`'s domain-root link was fully live on DC01 with nothing
filtering it out. `gpresult`'s own "Applied Group Policy Objects" list for that exact window
includes `Secure Admin WS` — Captured, not inferred. Fixed by retrying `Remove-GPLink` with the
distinguishedName form (`"DC=district,DC=local"`) instead, which succeeded immediately.

**Root cause: `Remove-GPLink` and `New-GPLink` don't accept the same target string format for the
domain root**, at least not consistently — an inconsistency in the GroupPolicy module itself, not
a mistake in identifying the right target. No interactive or RDP logon as a Domain Admin was
attempted during the exposure window — everything this session ran through `qm guest exec`
(SYSTEM context via the QEMU guest agent), a different logon type entirely, unaffected by
`SeDenyInteractiveLogonRight`/`SeDenyRemoteInteractiveLogonRight`. Whether an actual lockout would
have occurred if someone had tried an interactive logon in that window is not tested and is not
being claimed either way — stating what's known, not extending it into what would be convenient to
believe.

## What I'd do differently

Should have reached for the script-block filter syntax first — it's the standard way to avoid
exactly this class of quoting problem in AD cmdlets, and I overcomplicated it on the first attempt.

**On the bigger one:** should have verified the domain-root removal would work — with a
`-WhatIf`, or by checking `Remove-GPLink`'s accepted target formats before running it for real —
rather than assuming a target string that worked for `New-GPLink` would work identically for
`Remove-GPLink`. Two cmdlets in the same module accepting different formats for conceptually the
same target isn't an intuitive failure mode, but "assume the counterpart cmdlet behaves the same
way" is exactly the kind of assumption this project's whole capture discipline exists to catch,
and I made it anyway, on a live domain controller, in the class of change already known to be
capable of a lockout. The recovery was fast because the fallback logic was already written into
the same script *before* running it — that part worked as designed. The lesson is upstream of
that: verify a cmdlet's actual accepted input before trusting an assumption about it, especially
in this exact risk category.

## Open questions

- **Whether `District Lockdown`'s dead Restricted Groups reference logged an error anywhere** (the
  Group Policy operational event log would confirm the "can't resolve, does nothing" reading more
  directly than inference from the group simply not existing).
- **The final half of step 4's observation** — CURRICULUM asks for a reading at the end of the
  exercise too, not just this baseline. Worth checking again after a few days now that the relink
  itself is done and DC01's policy surface has changed again.
- **`LockoutBadCount = 0`** — filed in `EXPOSURES.md`, not yet evaluated for whether it's in scope
  to fix as part of a future exercise or stays a standing documented gap.
- **Whether the ~90-second domain-root exposure had any real effect.** No interactive/RDP Domain
  Admin logon was attempted during it, as far as this session's own activity goes — but that's not
  the same as confirming nothing else touched DC01 in that window.
