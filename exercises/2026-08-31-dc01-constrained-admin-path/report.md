# DC01 — constrained admin path, exercise 1: baseline capture and standing-privilege removal

## What I set out to do

Before touching anything on DC01, get a ground-truth read of its current admin surface — who/what actually holds administrative capability on the box today, captured live rather than carried forward from the October build. This exercise doubles as a test of the capture mechanism itself: does a check against `verified-claims.md` actually happen before anything gets labeled inherited, does evidence land where the skill says it should, does the write-up cite exit codes instead of paraphrasing them. If the mechanism is broken, better to find that on exercise one than three write-ups in.

The scope grew mid-exercise: the baseline capture surfaced a personal admin account (`sysadmin`) holding standing, undocumented `BUILTIN\Administrators` membership outside the groups a first-pass audit would check. Raymond's call was to fix it rather than just write it up, so this report also covers taking DC01 from "sysadmin has standing DC-admin rights via a path two of three queries missed" to "sysadmin does not" — snapshot, remediation, verification, all captured the same way as the read-only work above.

On the mechanism question this exercise opened with: it held. The empty ledger was checked before anything got labeled inherited (see The setup); every evidence file landed in `evidence/` named for what it proves; every claim in this report cites an exit code rather than a summary — including the two failures (a truncated paste, a bash-quoting bug) that a summary-first pass would have been the easiest place to hide. Whether that holds up over more exercises is still an open question, but exercise one didn't break it.

## The setup

Single-DC forest, `district.local`, DC01 = VM 100 (Windows Server 2022, `10.0.0.10` on the isolated `vmbr1` lab bridge). Boot order is 104 (pfSense) → 100 (DC01) → 105 (Kali). DC01 has all remoting disabled by design — no WinRM, RDP, or PS remoting — so the only path in is `qm guest exec` from the Proxmox host over the virtio serial channel. The exercise started as a read-only capture; it stopped being one once the `sysadmin` finding turned into a remediation (see Remediation, below) — a Proxmox snapshot was taken first, and the only live change made was the one `Remove-ADGroupMember` call, snapshot-backed and fully verified before and after.

`verified-claims.md` was checked before running anything. Its Confirmed table is empty — nothing about DC01's admin surface has been verified in a prior exercise. So nothing here gets cited from the ledger; every claim below is either freshly captured in this session or explicitly left open.

## What I did

Four commands, run in order from the Proxmox host shell, each wrapped in `qm guest exec 100 --timeout 30 -- powershell.exe -Command "..."`:

1. `Get-ADGroupMember -Identity 'Domain Admins' | Select-Object Name,SamAccountName,objectClass | ConvertTo-Json`
2. `Get-ADGroupMember -Identity 'Enterprise Admins' | Select-Object Name,SamAccountName,objectClass | ConvertTo-Json`
3. `Get-LocalGroupMember -Group 'Administrators' | Select-Object Name,ObjectClass,PrincipalSource | ConvertTo-Json`
4. `Get-Service ADWS | Select-Object Name,Status,StartType | ConvertTo-Json`

A fifth command was added as a follow-up once command 3 failed, to query the AD-native group instead of the nonexistent local one:

5. `Get-ADGroupMember -Identity 'Administrators' | Select-Object Name,SamAccountName,objectClass | ConvertTo-Json`

Once command 5 surfaced `sysadmin` as a direct member outside Domain Admins/Enterprise Admins, Raymond confirmed it's his own working admin credential and asked to move it toward least-privilege rather than just document it as-is. Before drafting any change, two more read-only commands to see the account's full picture:

6. `Get-ADUser -Identity 'sysadmin' -Properties MemberOf,adminCount | Select-Object Name,SamAccountName,adminCount,MemberOf | ConvertTo-Json`
7. `Get-ADGroup -Identity 'SG_admin_tier0_domain' -Properties memberOf,Description | Select-Object Name,Description,memberOf | ConvertTo-Json`

Command 6 was pasted twice — the first paste was cut off mid-JSON with no closing brackets and was discarded rather than filed as evidence; the complete repaste is what's in `evidence/`.

With `sysadmin`'s only confirmed AD-nested path to DC01 admin rights being the direct `BUILTIN\Administrators` grant, and Raymond having asked to fix rather than just document it, the remaining steps took a snapshot before making any change and then removed the grant:

8. `qm listsnapshot 100` (host shell, confirm no naming collision) then `qm snapshot 100 pre-sysadmin-admin-removal-20260831 --description "..."` (host shell)
9. `qm listsnapshot 100` again, to confirm the snapshot actually registered rather than trusting the LV-creation log lines
10. `Remove-ADGroupMember -Identity 'Administrators' -Members 'sysadmin' -Confirm:$false` — **failed** on the first attempt (see What broke, and why) and was re-run with corrected quoting: `-Confirm:\$false`
11. `Get-ADGroupMember -Identity 'Administrators' | Select-Object Name,SamAccountName,objectClass | ConvertTo-Json` and `Get-ADUser -Identity 'sysadmin' -Properties adminCount | Select-Object Name,SamAccountName,adminCount | ConvertTo-Json`, both run twice — once after the failed attempt (to confirm nothing changed), once after the successful one (to confirm it did)

Full commands, exact timestamps, and evidence filenames are in [`evidence/evidence-log.md`](evidence/evidence-log.md).

## Where Raymond was consulted

Four points, one from the original session this report was drafted in, three from a follow-up session picking the exercise back up.

**1. Whether to fix `sysadmin`'s standing access or just document it.** This is the fork that turned a read-only baseline capture into a remediation — covered in What I set out to do and Remediation, below. It predates the current session: the only record of it is this report's own prose ("Raymond's call was to fix it rather than just write it up"), not a captured exchange, so it's represented here as a paraphrase rather than a verbatim quote. Worth being explicit about that distinction rather than presenting it as something it isn't.

**2. Where to pick the exercise back up.** In a later session, once this report and `verified-claims.md` were already in sync with no obvious loose end, I asked: *"Where do you want to pick this up?"* — offering chasing an open question, starting a new exercise, polishing for publication, or something else. Raymond's answer: *"Chase an open question."* That's why this exercise continued rather than a fresh one starting.

**3. Which open question to chase.** I listed the open questions that were actually actionable at that moment (flagging that the `adminCount` SDProp self-clear check specifically wasn't ready yet — it needed roughly an hour past the 16:15 UTC removal and only ~20 minutes had passed) and asked which to pursue. Raymond's answer: *"GPO Restricted Groups on SG_admin_tier0_domain."* That's the follow-up captured below and the reason the SDProp question is still open rather than closed in this report — it was never the one selected, not an oversight.

**4. Whether to keep chasing the SDProp question or stop.** After the T+49min recheck came back unchanged (`adminCount` still `1`), I offered a fork: keep waiting and recheck later, pivot to the crash's unresolved root cause, or something else. Raymond's answer: *"ehh not worth chasing tail right now, lets just wrap up."* That's a deliberate stop, not an abandoned thread — the SDProp question stayed open past that point because it was paused on purpose, with a real data point on record (T+49min, still `1`), not because the session ran out of time before getting to it.

**5. Closing out the SDProp question.** In a later session, Raymond asked directly to close out the SDProp open question with a fresh recheck. Same command, run by Raymond and pasted back: `adminCount` still `1`, ~5 hours 40 minutes after the removal — see Open Questions for what that does and doesn't settle.

## What the box said

**Domain Admins** (`evidence/domain-admins-membership.json`, exit code `0`) — one direct member:

```json
{
    "Name":  "Administrator",
    "SamAccountName":  "Administrator",
    "objectClass":  "user"
}
```

**Captured.** `Get-ADGroupMember` without `-Recursive` returns direct members only — this confirms the direct membership is a single built-in user account, not that there's no nested path in (see Open Questions).

**Enterprise Admins** (`evidence/enterprise-admins-membership.json`, exit code `0`) — same result, one direct member, same account:

```json
{
    "Name":  "Administrator",
    "SamAccountName":  "Administrator",
    "objectClass":  "user"
}
```

**Captured**, same caveat on `-Recursive` as above.

**Local Administrators group on DC01** (`evidence/local-administrators-group-lookup.json`, exit code `1`) — this one failed:

```
Get-LocalGroupMember : Group Administrators was not found.
At line:1 char:1
+ Get-LocalGroupMember -Group 'Administrators' | Select-Object Name,Obj ...
+ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : ObjectNotFound: (Administrators:String) [Get-LocalGroupMember], GroupNotFoundException
    + FullyQualifiedErrorId : GroupNotFound,Microsoft.PowerShell.Commands.GetLocalGroupMemberCommand
```

**Captured** as a failure — see below.

**ADWS service state** (`evidence/adws-service-state.json`, exit code `0`):

```json
{
    "Name":  "ADWS",
    "Status":  4,
    "StartType":  2
}
```

`Status` 4 and `StartType` 2 decode against the standard `ServiceControllerStatus` / `ServiceStartMode` enums to Running / Automatic. **Captured** for the raw values; the enum decode is my read of documented .NET enum values, not something the box itself printed as text, so I'm labeling it interpretation rather than raw capture.

**BUILTIN\Administrators** (`evidence/builtin-administrators-membership.json`, exit code `0`) — four direct members, not one:

```json
[
    {
        "Name":  "System Admin",
        "SamAccountName":  "sysadmin",
        "objectClass":  "user"
    },
    {
        "Name":  "Domain Admins",
        "SamAccountName":  "Domain Admins",
        "objectClass":  "group"
    },
    {
        "Name":  "Enterprise Admins",
        "SamAccountName":  "Enterprise Admins",
        "objectClass":  "group"
    },
    {
        "Name":  "Administrator",
        "SamAccountName":  "Administrator",
        "objectClass":  "user"
    }
]
```

**Captured**, and this is the finding the earlier two queries missed. `sysadmin` (display name "System Admin") is a direct member of `BUILTIN\Administrators` on DC01. It is **not** a direct member of Domain Admins, **not** a direct member of Enterprise Admins — the two queries this exercise started with — and it reaches administrative rights on the DC through a third path neither of them checked. Whatever else this exercise proves, it proves that "who's in Domain Admins" is not the same question as "who can administer DC01," and answering only the first would have shipped a wrong baseline with a clean exit code.

**`sysadmin`'s own group memberships** (`evidence/sysadmin-memberof-precheck.json`, exit code `0`) — three groups, complete list:

```json
{
    "Name":  "System Admin",
    "SamAccountName":  "sysadmin",
    "adminCount":  1,
    "MemberOf":  [
                     "CN=SG_Share_Site1_RW,OU=Resources,OU=Security,OU=Groups,DC=district,DC=local",
                     "CN=SG_admin_tier0_domain,OU=Admins,DC=district,DC=local",
                     "CN=Administrators,CN=Builtin,DC=district,DC=local"
                 ]
}
```

**Captured.** `SG_Share_Site1_RW` is a file-share group, unrelated to admin rights. `SG_admin_tier0_domain` is a custom group whose name suggests an intentional tiered-administration design. `CN=Administrators,CN=Builtin` confirms the direct membership already seen in the previous capture, this time from the user side rather than the group side. `adminCount: 1` confirms AdminSDHolder has already stamped this account as a protected-group member, as expected for anything in `BUILTIN\Administrators`.

**`SG_admin_tier0_domain` itself** (`evidence/sg-admin-tier0-domain-lookup.json`, exit code `0`, run twice by Raymond with identical output both times):

```json
{
    "Name":  "SG_admin_tier0_domain",
    "Description":  null,
    "memberOf":  []
}
```

**Captured.** Empty `memberOf` and no description. Via AD group nesting, this group is not a member of Domain Admins, `BUILTIN\Administrators`, or anything else — it grants nothing today through that mechanism. Combined with the two captures above, `sysadmin`'s only confirmed AD-nested path to admin rights on DC01 is the direct `BUILTIN\Administrators` membership; `SG_admin_tier0_domain` is a named container without a wired path. Whether it's referenced by a GPO Restricted Groups setting instead of AD nesting — which this query wouldn't show — is not ruled out (see Open Questions).

### Follow-up: does GPO wire `SG_admin_tier0_domain` onto anything?

Run as a same-exercise follow-up once the question above was flagged. Two captures, both from DC01 directly (not via UNC, to sidestep any SYSVOL-replication-latency questions).

**SYSVOL grep for the group name** (`evidence/sysvol-restricted-groups-sg-admin-tier0-grep.json`, exit code `0`) — searched every `GptTmpl.inf` (classic Restricted Groups) and `Groups.xml` (Group Policy Preferences) under `C:\Windows\SYSVOL\domain\Policies`, domain-wide, for a literal match on `SG_admin_tier0_domain`:

```json
{
   "exitcode" : 0,
   "exited" : 1
}
```

**Captured.** No `out-data` key is the expected shape for zero `Select-String` matches — `ConvertTo-Json` on an empty pipeline emits nothing, not `[]`. Zero hits across every GPO in the domain, not just the ones linked to DC01.

**GPOs actually linked to the Domain Controllers OU** (`evidence/dc-ou-linked-gpos.json`, exit code `0`) — run to scope which GPOs even apply to DC01, in case the grep above needed narrowing:

```json
[
    {
        "DisplayName":  "Default Domain Controllers Policy",
        "GpoId":  "6ac1786c-016f-11d2-945f-00c04fb984f9",
        "Enabled":  true,
        "Enforced":  false,
        "Order":  1
    },
    {
        "DisplayName":  "DC - Secure LDAP",
        "GpoId":  "ff616993-b76d-4b9b-b314-2ad143fb37c3",
        "Enabled":  true,
        "Enforced":  false,
        "Order":  2
    }
]
```

**Captured.** Two GPOs link to the Domain Controllers OU: the built-in Default Domain Controllers Policy and a locally-named "DC - Secure LDAP." Neither name suggests a Restricted Groups purpose, and the domain-wide grep above already found zero references to the group in any GPO's policy files, so this doesn't change the answer — it just confirms the grep's zero-hit result wasn't hiding a scoping gap.

**Net effect (name-based check):** `SG_admin_tier0_domain` has no confirmed path onto DC01 through either AD nesting (prior capture) or GPO Restricted Groups / Preferences referencing it by name (this capture). One caveat remained: classic Restricted Groups entries in `GptTmpl.inf` are keyed by SID, and GPMC only writes the friendly name in as a comment when the setting was authored through the UI — a hand-edited or scripted entry could reference the group by bare SID with no name string anywhere in the file, which a text-pattern grep on the name would not catch.

**Closing the SID gap** (`evidence/sysvol-restricted-groups-sg-admin-tier0-sid-grep.json`, exit code `0`) — resolved the group's SID first, then re-ran the same SYSVOL search for that literal SID instead of the name:

```json
{
    "Sid":  "S-1-5-21-2288391267-384259729-2991373820-1111",
    "Hits":  {}
}
```

**Captured.** `Hits` comes back as an empty object rather than `null` — this is `ConvertTo-Json`'s serialization of a `$null` pipeline variable produced by zero `Select-String` matches, the same shape-of-absence quirk as the earlier name-based grep, just rendered slightly differently by the wrapping `[PSCustomObject]`. Either way, the result is the same: zero matches for the group's SID, domain-wide, across every `GptTmpl.inf` and `Groups.xml` in SYSVOL.

This capture was interrupted the first time it was attempted — DC01 went down unexpectedly mid-session before it could run (see `exercises/2026-08-31-dc01-unexpected-shutdown/`) — and was re-issued unchanged once the VM was confirmed back up.

**Net effect, fully resolved:** `SG_admin_tier0_domain` has no confirmed path onto DC01 through AD nesting, GPO Restricted Groups, or GPO Preferences, whether referenced by name or by SID. As far as both mechanisms this exercise checked can show, it is a named container with nothing wired to it anywhere in district.local. The one caveat still standing — noted rather than chased further — is that this only rules out `GptTmpl.inf` and `Groups.xml` specifically; it doesn't rule out every conceivable way a group could gain effective rights (e.g. a scheduled task or logon script referencing it), which was never this exercise's scope to begin with.

### Remediation: removing sysadmin's standing BUILTIN\Administrators membership

**Pre-change snapshot** (`evidence/vm100-pre-removal-snapshot.txt`, host shell, no exit-code envelope since this didn't go through `qm guest exec`) — `qm snapshot 100 pre-sysadmin-admin-removal-20260831` created `Logical volume` entries for both `drive-scsi0` and `drive-efidisk0`, then confirmed present via a second `qm listsnapshot 100` showing it registered correctly, positioned right before `current`, description intact. **Captured**, host-side, not guest-agent JSON — noted as a different evidence shape in the file itself.

One unrelated thing this surfaced: the LVM warnings on snapshot creation say the thin pool's total allocated snapshot volumes are **864.93 GiB against a 237.47 GiB volume group** — about 3.6x overcommitted, across all seven snapshots now on VM 100. Not part of this exercise's scope, flagged to Raymond directly, carried into Open Questions rather than investigated here.

**Removal attempt 1** (`evidence/sysadmin-removal-attempt-1-failed.json`, exit code `1`) — **failed**:

```
Parameter -Confirm: requires an argument.
    + CategoryInfo          : ParserError: (:) [], ParentContainsErrorRecordException
    + FullyQualifiedErrorId : ParameterRequiresArgument
```

**Captured** as a failure. Cause: the command as first given used `-Confirm:$false` inside a bash double-quoted string. Bash interpolates `$false` as an unset variable (empty string) before `qm guest exec` ever sees it, so PowerShell received a bare `-Confirm:` with nothing after it. This is a capture-tooling bug, not an AD or DC01 behavior — worth keeping in the record anyway per the "a failure is evidence" principle, and because it's exactly the kind of gotcha that would resurface in any future command built the same way.

**Verification after the failed attempt** (`evidence/builtin-administrators-membership-post-attempt1.json` and `evidence/sysadmin-admincount-post-attempt1.json`, both exit code `0`) confirmed no change had occurred: `sysadmin` was still listed in `BUILTIN\Administrators`, `adminCount` still `1`. DC01's state matched the pre-attempt baseline exactly.

**Removal attempt 2** (`evidence/sysadmin-removal-attempt-2-succeeded.json`, exit code `0`) — succeeded, using the corrected `-Confirm:\$false` (backslash-escaped so bash passes the literal `$false` through):

```json
{
   "exitcode" : 0,
   "exited" : 1
}
```

No output on success is expected behavior for `Remove-ADGroupMember`, not a partial result.

**Post-removal verification** (`evidence/builtin-administrators-membership-post-removal.json`, exit code `0`) — `sysadmin` is gone, three members remain:

```json
[
    {"Name": "Domain Admins", "SamAccountName": "Domain Admins", "objectClass": "group"},
    {"Name": "Enterprise Admins", "SamAccountName": "Enterprise Admins", "objectClass": "group"},
    {"Name": "Administrator", "SamAccountName": "Administrator", "objectClass": "user"}
]
```

**`adminCount` post-removal** (`evidence/sysadmin-admincount-post-removal.json`, exit code `0`) — still `1`:

```json
{
    "Name":  "System Admin",
    "SamAccountName":  "sysadmin",
    "adminCount":  1
}
```

**Captured**, and expected: AdminSDHolder/SDProp stamps `adminCount=1` and disables ACL inheritance on protected-group members, and doesn't clear it automatically the moment membership is removed — it's cleaned up on the SDProp background cycle (documented as roughly hourly, run from the PDC emulator), not synchronously. Whether this account's `adminCount` actually clears on that cycle, or needs a manual reset, is unverified — see Open Questions.

**Net effect, as of this exercise's last capture:** `sysadmin` no longer holds standing membership in `BUILTIN\Administrators` on DC01, and (per the earlier `MemberOf` capture, `SG_admin_tier0_domain` and `SG_Share_Site1_RW`) has no other confirmed AD-nested path to DC01 admin rights. Practically, that means **`sysadmin` currently has no way to administer DC01 through AD group membership** until either the direct grant is restored or a real tiered-access path is built through `SG_admin_tier0_domain` or something equivalent — flagged to Raymond directly, not just left in the write-up.

## What broke, and why

The local-group query is the interesting failure, not a throwaway one. `Get-LocalGroupMember -Group 'Administrators'` failing with `GroupNotFoundException` on a domain controller is consistent with a DC not carrying a local SAM-based "Administrators" group the way a member server does — administrative rights on a promoted DC live in the directory (`BUILTIN\Administrators` as a domain-local AD object), not in a local security database, because DCPROMO removes the local SAM. That's a plausible, well-documented explanation, but I want to flag it as **interpretation, not something this session verified directly** — I didn't run anything against DC01 that confirms the SAM-removal mechanism specifically, I'm reasoning from the error plus general Windows AD architecture. If this claim needs to hold weight later, it needs its own capture (see Open Questions).

Practically: querying a DC's "local" admin surface with the local-group cmdlets is the wrong tool for the box. The right query is the AD-native `BUILTIN\Administrators` group, not attempted in this pass.

The second break wasn't a command failure at all — it was a transcription one. The first paste of `sysadmin`'s `MemberOf` result cut off mid-array with no closing brackets, no `exitcode`, no `exited`. It looked plausible (three groups, nothing obviously wrong) and it would have been easy to write the report against it and never notice a fourth group had been truncated out. It got caught only because the capture contract requires all four JSON fields present before anything counts as evidence — the missing `exitcode`/`exited` were the tell, not the content. Worth keeping as a reminder that "looks complete" and "is complete" aren't the same check.

The third break was mine, directly: the `-Confirm:$false` quoting bug that failed removal attempt 1. I wrote a command that worked fine as a string but broke the moment it passed through an actual bash shell — `$false` looks like inert PowerShell syntax if you're only thinking about the PowerShell side of the pipe. Caught immediately by exit code `1` rather than a silent partial failure, which is the whole reason exit codes are non-negotiable in this capture contract — a `$false` silently turning into nothing could just as easily have left `-Confirm` defaulting to interactive-prompt behavior and hung, or worse, done something other than what was asked, and a summarized "ran it, done" would never have caught it.

## What I'd do differently

Start from "this is a DC, not a member server" and go straight to `Get-ADGroup -Identity 'Administrators' | Get-ADGroupMember` instead of trying the local-group cmdlet first — the failure was informative but cost a round trip I could've skipped by thinking about DC01's role before picking the command. I'd also run the Domain Admins / Enterprise Admins queries with `-Recursive` from the start rather than as a follow-up, since "who's in Domain Admins" is exactly the kind of claim where a nested group hiding a second identity is the whole point of a constrained-admin-path exercise.

More broadly: I'd make "check the group that actually gates the resource, not the group with the recognizable name" the default starting query for any admin-surface capture, not something arrived at after a failure. `sysadmin` sitting in `BUILTIN\Administrators` outside both of the obviously-named privileged groups is the same shape as the permission-sprawl pattern from the help-desk years — access that exists because someone got added directly to whatever actually granted the right, not through the group whose name would show up in a quick audit. The two-query baseline this exercise started with is exactly the kind of audit that would have missed it.

I'd also test any command with shell-metacharacters (`$`, backticks, unescaped quotes) against the actual bash-then-PowerShell pipe before handing it over, instead of finding the escaping bug via a failed exit code on the live box. It cost one round trip here because the failure was caught cleanly — it wouldn't always be that cheap.

## Open questions

- **`sysadmin`'s ownership is Raymond-stated, not captured.** Raymond identifies it as his own working credential for administering DC01. That resolves "is this an unexplained account" — it isn't — but it's testimony, not evidence: nothing in `evidence/` or `verified-claims.md` backs it, so it's logged here as **Recalled** rather than promoted to the Confirmed table. If it matters later (e.g. in a published report), it needs something the box itself produced — a last-logon timestamp against `sysadmin`, or a `whoami` from an active session — not just this statement.
- **Resolved this exercise:** being outside Domain Admins / Enterprise Admins didn't make `sysadmin` constrained — direct `BUILTIN\Administrators` membership on a DC is functionally domain-admin-equivalent. Raymond's call was to reduce standing privilege rather than just document the gap; that's done (see Remediation above), and confirmed by post-removal capture rather than assumed.
- **`sysadmin` currently has no confirmed AD path to administer DC01.** With `BUILTIN\Administrators` membership removed and `SG_admin_tier0_domain` unwired, there's no standing access left — this is the direct, expected consequence of the removal, not a surprise, but it's a real operational state change worth its own line: `sysadmin` needs either a restored grant or a real tier-0 path before it can administer DC01 again through AD.
- **Closed this session: `sysadmin`'s `adminCount` does not self-clear on its own.** It read `1` immediately post-removal (16:15:52Z, expected — SDProp doesn't clear synchronously), still `1` at T+49min (17:05:03Z, `evidence/sysadmin-admincount-recheck-t-plus-49min.json`), and still `1` at a further recheck roughly 5 hours 40 minutes after the removal (`evidence/sysadmin-admincount-recheck-t-plus-5h40m.json`, exit code `0`) — the same identical command, same result, three reads apart. Five-plus hours is several multiples of AD's documented ~60-minute SDProp cycle interval, so this isn't "not enough time has passed" territory anymore: if the cycle were going to clear `adminCount` on its own, it should have run several times over by now and hasn't touched it. What this closes: **`adminCount` does not self-clear as a side effect of removing protected-group membership** — it's sticky by design, and reverting it requires deliberate action (a manual `Set-ADUser -Clear adminCount` / re-inheritance, or an SDProp-aware cleanup script), not just waiting. What stays open, narrower than before: the ~60-minute interval itself is still textbook Microsoft documentation, not something this domain's PDC emulator was directly observed running on — this exercise never caught the cycle firing, only confirmed it doesn't clear this attribute when it does. `sysadmin` will keep showing `adminCount: 1` until someone clears it by hand, even though the account has had no admin path since the removal earlier in this exercise. Whether the associated ACL-inheritance-disabled flag is similarly sticky was never independently queried in this exercise (see the earlier interpretation note above) — only `adminCount` itself was rechecked.
- **Rollback snapshot exists but was never exercised.** `pre-sysadmin-admin-removal-20260831` was created and confirmed registered; it was not restored from, since the removal succeeded on attempt 2. Its existence is captured; whether a restore from it actually works has not been tested.
- **The thin-pool overcommit (864.93 GiB allocated against a 237.47 GiB volume group) is a real risk, not investigated in this exercise.** Surfaced as a side effect of taking the pre-change snapshot, unrelated to DC01's admin surface. If any of the seven snapshots on VM 100 grows enough to exhaust the pool, it can affect every VM on that storage, not just DC01.
- **Fully resolved this exercise.** A domain-wide grep of every GPO's `GptTmpl.inf`/`Groups.xml`, first for the literal string `SG_admin_tier0_domain` and then (after DC01's unexpected shutdown interrupted the first attempt) for the group's actual SID (`S-1-5-21-2288391267-384259729-2991373820-1111`), both returned zero matches. Combined with the empty `memberOf` from AD nesting, `SG_admin_tier0_domain` has no confirmed path onto DC01 or anywhere else in district.local through any mechanism this exercise checked — it's a named container with nothing wired to it, full stop, not a caveat.
- **`SG_Share_Site1_RW` and `sysadmin` being non-admin, unrelated to DC01 access — noted, not investigated further.** Included for completeness of the `MemberOf` capture, not part of the admin-surface question this exercise is scoped to.
- **Whether `sysadmin` has interactively logged into DC01, and when, is not captured.** Group membership tells us it *can* administer the box; Raymond's statement tells us it *does*, but as testimony. A logon-event or last-logon capture would move this from Recalled to Captured.
- **Nested group membership in Domain Admins / Enterprise Admins is still unproven.** Both queries used `Get-ADGroupMember` without `-Recursive`; a nested group carrying additional identities into either privileged group would not have shown up. This matters less now that `BUILTIN\Administrators` is the group that actually governs the DC, but it's still open for the two groups themselves.
- **Why the local-group cmdlet fails (SAM removed by DCPROMO) is asserted, not verified in this session.** Flagged as interpretation above; would need something like `Get-CimInstance -ClassName Win32_Group -Filter "LocalAccount=True"` or a WinNT-provider query on DC01 to confirm directly rather than by inference from Microsoft's documented DC behavior.
- **AdminSDHolder / protected-group ACL state was not captured** and is part of "admin surface" in any real sense — not attempted this pass. Given `sysadmin` is a direct member of a protected group, its `adminCount` / SDProp state would be worth checking.
- **No October baseline document exists to diff against.** This report is establishing DC01's current admin surface for the first time in the ledger, not confirming or correcting an inherited claim — there was nothing on record to correct.

## Addendum — a correction from a later exercise, 2026-09-01

The removal of `sysadmin`'s direct `BUILTIN\Administrators` grant, the central remediation of
this report, was correct — a named account with a standing DC-level admin grant outside the
groups a first-pass audit checks is exactly the sprawl pattern this series exists to find and
remove. That conclusion still holds. What this report's own "What I'd do differently" didn't
anticipate: three exercises later, the lab reached a session where `Administrator` was disabled,
a domain-root-linked GPO (`Secure Admin WS`, discovered in that exercise) denied Domain Admins
interactive logon everywhere including DC01, and this removal — with no verified break-glass
path left in its place — combined into a full lockout. No account could log into DC01 at all.

That's a sequencing defect, not a reason to reverse the removal, and it's worth stating plainly
because the report that found the lockout initially read it the other way — concluding the
grant had been "load-bearing" and the removal itself a mistake. That was also wrong, corrected
on the record in the same session it was made. The actual lesson, from both corrections
together: verify a real break-glass admin path exists before removing the last one, not that
standing sprawl earns a pass just because removing it broke something later. See
`exercises/2026-09-01-entra-connect-connector-account/report.md`'s "What broke, and why" section
for the full account, and `verified-claims.md` for the corrected ledger rows.
