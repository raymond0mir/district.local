# Evidence log — A2: GPO surface and the Secure Admin WS domain-root link

Completed 2026-09-02, written as the exercise ran. Steps 1, 2, 3, and the baseline half of step 4
(per `CURRICULUM.md`) are done. Only the final, later-in-time half of step 4's tattoo observation
remains genuinely open.

## Captured

1. `evidence/gpo-origin-timestamps-and-full-reports-20260902T1656Z.txt` — pre-flight
   (`qm status`/`lvs`/`free -h`), `Get-GPO -All` timestamps/owners for all 9 domain GPOs, full
   `Get-GPOReport` XML for `Default Domain Policy` and `District Lockdown` (both previously unread
   at this depth), first (failed) `gpresult /r` attempt, first (ambiguous) `secedit` attempt.
2. `evidence/gpresult-and-secedit-verified-20260902T1700Z.txt` — corrected re-run:
   `gpresult /r /scope:computer` (works without a logged-on user, unlike the first attempt) and a
   verified `secedit` export (exit code checked, file existence confirmed, full
   `[Privilege Rights]` section dumped rather than grepped).
3. `evidence/admins-group-existence-check-20260902T1701Z.txt` — `Get-ADGroup` exact-match and
   `*Admin*`-wildcard sweep, to test whether `District Lockdown`'s Restricted Groups target
   ("Admins") is a real security principal.

## Derived from the captures (analysis, not new observation)

**GPO origin — CURRICULUM's step 2, answered with circumstantial but real evidence.** Every GPO in
the domain except one is owned by `DISTRICT\Domain Admins` and was created in a tight cluster,
9/30–10/4/2025 (the initial build window — `Default Domain Policy`'s creation, 9/30 2:11 PM, lands
hours after DC01's own `InstallDate` of 9/30 12:36 AM). `Secure Admin WS` breaks both patterns:
created 10/8/2025, 4–8 days after everything else, and owned by the individual account
`DISTRICT\sysadmin` rather than the Domain Admins group. This points toward "added later,
individually" rather than "part of the deliberate initial baseline" — not a change ticket, but a
real, non-obvious signal from metadata nobody had looked at before. Its `ModificationTime`
(9/1/2026 7:25:40 AM) matches this project's own 09-01 Deny-Apply ACE fix exactly, as expected.

**CURRICULUM's step 4 (does the tattoo recur) — a real answer, not just a first-pass check.** The
first `secedit` attempt was ambiguous (empty grep result could mean "absent" or "export failed").
The corrected capture confirms the export succeeded (exit 0, file present) and dumps the entire
`[Privilege Rights]` section: `SeDenyInteractiveLogonRight` and `SeDenyRemoteInteractiveLogonRight`
are both genuinely absent. This is after the most recent GPO refresh (9:58:07 AM today) and
multiple full reboots since the 09-01 fix (the crash, the rearm restart) — real elapsed time and
several refresh cycles, not an immediate post-fix reading. The fix is holding. Framed as "holding
across everything observed so far," not "permanently impossible" — a future GPO edit could still
reintroduce it.

**New finding, not previously on record anywhere: `Default Domain Policy` sets
`LockoutBadCount = 0`.** No account-lockout threshold exists anywhere in this domain — password
complexity and history are enforced, but no number of bad password attempts ever locks an account.
Independent of this exercise's actual hypothesis; surfaced only because step 1 required actually
reading a GPO nobody had read before.

**New finding: `District Lockdown`'s Restricted Groups setting targets a group that does not
exist.** Its Computer\Security extension defines Restricted Groups membership for a group named
literally "Admins," with zero members listed. `Get-ADGroup` confirms no group by that exact name
exists in `district.local` — the 13 real `*Admin*` groups are `Administrators`, `Domain Admins`,
`Enterprise Admins`, `Schema Admins`, `Key Admins`, `Enterprise Key Admins`, `Hyper-V
Administrators`, `Storage Replica Administrators`, `DnsAdmins`, `DHCP Administrators`, and the
three `SG_admin_tier*` groups — none is a bare "Admins." Since Windows can't enforce Restricted
Groups membership on a name that doesn't resolve, this setting is currently inert, not an active
risk — but it's dead configuration in a domain-root-linked GPO that nobody had verified before,
exactly the kind of thing the skill's capture-contract preamble (imported October 2025 baseline,
built with another assistant, unverified in places) warns about.

## Step 3 executed: snapshot, OU inventory, relink, and a real incident

4. `evidence/admins-group-existence-check-20260902T1701Z.txt` (already listed above) also fed the
   relink plan — same capture answered two different questions.
5. Full OU inventory + AD computer-object placements, captured inline in the consultation with
   Raymond rather than a separate evidence file (the output is quoted in `report.md`'s
   "Where Raymond was consulted" and "What broke" sections). Found `ENTRACONNECT01` in the default
   `Computers` container, not the custom OU structure, and four previously-undocumented computer
   objects — Raymond confirmed all four as known, open test resources.
6. Pre-change snapshot: `pre-secure-admin-ws-relink-20260902`, verified via `qm listsnapshot`.
7. `evidence/relink-execution-and-recovery-20260902T1711-1714Z.txt` — the full stage 1 (additive:
   move VM102, add two GPO links) / stage 1 verification (New-GPLink prints nothing on success;
   confirmed via GPOReport ground truth and a retry that failed with "already linked") / stage 2
   attempt 1 (FAILED: `Remove-GPLink -Target "district.local"`, domain-root link stayed live for
   ~90 seconds with the Deny-Apply ACE already removed in the same run — a real, Captured exposure,
   not just a close call) / stage 2 fix (`Remove-GPLink -Target "DC=district,DC=local"` succeeded)
   sequence, with `gpresult` verification before and after.

**Do not trust `New-GPLink`'s silence as failure.** It returns nothing to the pipeline on success.
Confirmed the hard way — via `Get-GPOReport`'s own `LinksTo` field and a retry that surfaced
"already linked" errors — after initially treating the blank output as ambiguous.

**`Remove-GPLink` and `New-GPLink` do not accept the same target string for the domain root.**
`"district.local"` (the same string `Get-GPOReport`'s `SOMPath` displays) worked for creating a
link elsewhere but `Remove-GPLink` rejected it outright. The distinguishedName form
(`"DC=district,DC=local"`) is what `Remove-GPLink` actually needs. Worth remembering for any
future domain-root GPO link removal through this channel.

## Not yet done

- Whether `District Lockdown`'s Restricted Groups setting logged an error in the Group Policy
  operational event log when it failed to resolve "Admins" — would confirm the dead-reference
  reading more directly, not done this round.
- The final, "read at the end" half of step 4's observation (checking again after more elapsed
  time / another deliberate GPO change) — the baseline reading above is real evidence but not the
  full before/after CURRICULUM asks for.
