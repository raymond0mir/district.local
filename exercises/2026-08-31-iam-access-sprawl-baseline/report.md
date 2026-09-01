# IAM access-sprawl baseline — does the `sysadmin` pattern generalize?

## What I set out to do

Exercise 1 found one account (`sysadmin`) holding standing administrative access through a path a first-pass audit missed — not through Domain Admins or Enterprise Admins, but through a direct `BUILTIN\Administrators` grant nobody had documented. That's the specific shape of the permission-sprawl thesis: access provisioned outside the group whose name would show up in a quick audit, left in place because removing it feels risky and nobody's forced to justify it.

This exercise asks whether that was a one-off or a pattern: enumerate every user's group membership and every group's identity across all of district.local, and look for the two signatures of copy-based, sprawl-prone provisioning — accounts whose access was granted in a batch by cloning a peer rather than assigned per-role, and groups that exist as named containers without anything actually checking them (the `SG_admin_tier0_domain` shape, generalized).

**The answer is no**, and this report says so rather than dressing up the near-miss. The one candidate pattern the enumeration surfaced turned out, on asking, to be arbitrary lab-setup activity with no process behind it. What the exercise does establish is narrower but real: a measurable case of dormant standing access, the queries that surface it, and — more useful than either — a clear statement of what a self-built lab can and cannot prove about how access sprawl actually arises. See Finding 1 and the section following it.

## The setup

Same lab, same constraint: DC01 (VM 100, `district.local`, Windows Server 2022) has no remoting, so `qm guest exec` from the Proxmox host is the only path in — Raymond ran both commands and pasted results back. `verified-claims.md` was checked first; nothing in the ledger yet covers a full user or group enumeration, so this is new ground rather than something to cite from a prior exercise.

One inherited artifact is relevant background, not evidence: `~/Downloads/district-lab-bloodhound-writeup.md`, a write-up of a 2026-06-17 BloodHound CE session against this same domain, states district.local has "13 users, 59 groups." Per the capture contract, that figure is **inherited** — carried forward from a prior, unverified document — not something this exercise treats as fact until re-derived. It turned out to matter: see What the box said.

## What I did

Two commands, both from the Proxmox host shell, wrapped in `qm guest exec 100 --timeout 30 -- powershell.exe -Command "..."`:

1. `Get-ADUser -Filter * -Properties MemberOf,Enabled,whenCreated,LastLogonDate,adminCount | Select-Object Name,SamAccountName,Enabled,whenCreated,LastLogonDate,adminCount,MemberOf | ConvertTo-Json -Depth 4`
2. `Get-ADGroup -Filter * -Properties Description,whenCreated,GroupCategory,GroupScope | Select-Object Name,Description,whenCreated,GroupCategory,GroupScope | ConvertTo-Json -Depth 4`

Both are read-only, direct membership only (no `-Recursive`), and both returned exit code `0`. Full commands and filing timestamps are in [`evidence/evidence-log.md`](evidence/evidence-log.md).

Both fields that matter most for this analysis — `whenCreated` and `LastLogonDate` — come back from `ConvertTo-Json` as .NET `/Date(<epoch-ms>)/` strings, not readable timestamps. Every date cited below was converted with `date -u -r $((ms/1000))`, not eyeballed — see the evidence-log note on this, since the last exercise's whole "what broke" section was about a case where looks-complete and is-complete diverged.

## Where Raymond was consulted

Two points.

**1. Scope.** After exercise 1's constrained-admin-path work and the crash detour closed out, I asked what to run next and offered a few options scoped to open questions from prior exercises. Raymond redirected: *"let's keep to the goal, IAM"* — pointing back at the permission-sprawl through-line rather than any of the specific open items I'd offered. This exercise's scope (full user/group enumeration, not a narrower follow-up) is downstream of that redirect, not something I picked unprompted.

**2. The remediation itself.** Once Finding 1 surfaced `mlee`'s and `ajones`'s dormant standing access, I left the decision open rather than acting — same pattern as exercise 1's `sysadmin` fork. Raymond's answer: *"revoke mlee and ajones's access."* That's what Remediation, below, covers. I did make one unilateral call within that instruction: not taking a pre-change VM snapshot, on the reasoning that reverting a file-share group membership is a one-line `Add-ADGroupMember` versus the lockout risk that justified snapshotting before exercise 1's admin-rights removal — flagged to Raymond at the time, not silently decided.

**3. The origin of the account batch — and the correction it forced.** After the remediation was filed, Raymond volunteered what the four-account batch actually was: *"it was just random shit i was doing when i first stood up the DC."* That directly contradicted this report's own Finding 1 interpretation, which I had written and filed. I raised the conflict rather than leaving the published reading to stand, and asked how to handle it; Raymond's call was to correct it to a negative result and to add the series-level note about seeded findings. Both are in this report now. Worth recording as a consultation point precisely because the correction ran *against* the report's more impressive claim — the interesting version of this exercise was the wrong one.

## What the box said

**All 13 users** (`evidence/all-users-memberof-enumeration.json`, exit code `0`) — full list with direct `MemberOf`, `Enabled`, `whenCreated`, `LastLogonDate`, `adminCount`:

| SamAccountName | Enabled | Created (UTC) | Last logon (UTC) | adminCount | Direct MemberOf |
|---|---|---|---|---|---|
| Administrator | false | 2025-09-30T21:11:34Z | 2025-09-30T21:15:10Z | 1 | Group Policy Creator Owners, Domain Admins, Enterprise Admins, Schema Admins, Administrators |
| Guest | false | 2025-09-30T21:11:34Z | never | — | Guests |
| krbtgt | false | 2025-09-30T21:12:15Z | never | 1 | Denied RODC Password Replication Group |
| dumbuser2 | true | 2025-10-01T00:34:24Z | 2025-10-01T00:34:57Z | — | *(none)* |
| dumbuser3 | true | 2025-10-03T06:27:28Z | 2025-10-03T06:28:50Z | — | *(none)* |
| dumbhelpdesk1 | true | 2025-10-04T03:57:41Z | 2025-10-04T03:59:08Z | — | SG_admin_tier1_helpdesk |
| jsmith | true | 2025-10-04T04:22:00Z | 2025-10-04T04:25:36Z | — | SG_Share_Site1_RW |
| ajones | true | 2025-10-04T04:22:01Z | **never** | — | SG_Share_Site1_Read |
| mlee | true | 2025-10-04T04:22:01Z | **never** | — | SG_Share_Site1_RW |
| khan | true | 2025-10-04T04:22:01Z | 2025-10-04T04:28:01Z | — | *(none)* |
| sysadmin | true | 2025-10-09T05:22:49Z | 2026-08-26T23:11:28Z | 1 | SG_Share_Site1_RW, SG_admin_tier0_domain |
| bhound | true | 2026-06-17T07:03:56Z | 2026-08-27T01:17:34Z | 1 | Key Admins |
| bingbong | true | 2026-08-28T00:42:37Z | 2026-08-28T02:29:55Z | — | *(none)* |

**Captured.** Thirteen users, matching the inherited BloodHound figure exactly — this is the first independent re-derivation of that number, so it moves from inherited to **confirmed**.

**All groups** (`evidence/all-groups-enumeration.json`, exit code `0`) — **55 groups returned**, not 59. The extra four groups the BloodHound write-up counted are not accounted for in this exercise; not reconciled. Group naming and creation timestamps otherwise line up with a standard Windows Server 2022 baseline plus five custom `SG_` groups: `SG_admin_tier0_domain`, `SG_admin_tier1_helpdesk`, `SG_admin_tier2_desktop` (all created within 51 seconds of each other, 2025-10-04T03:52:14–03:53:05Z, all with `Description: null`), and `SG_Share_Site1_RW` / `SG_Share_Site1_Read` (created together, 2025-10-04T04:17:18Z, also `Description: null`).

**Finding 1 — a four-account batch with unevenly-exercised access, origin known and non-organic.** `jsmith`, `ajones`, `mlee`, and `khan` were all created within the same one-second window, five minutes after the two `SG_Share_Site1_*` groups themselves were created. Of the four: `jsmith` got RW and logged on once, `mlee` got the identical RW grant and has **never logged on in the ~11 months since**, `ajones` got Read and has also never logged on, and `khan` got no group membership at all despite being the only one of the four with a later, non-immediate logon. All of that is **Captured**.

The interpretation is where this has to be careful. The pattern *looks* exactly like batch provisioning — a script or template creating a cohort at once, some members getting access they never use. An earlier draft of this report said so, and called it the strongest data point for the sprawl thesis. **That reading is wrong, and the correction is on the record rather than quietly edited out.** Asked directly, Raymond identified these accounts as arbitrary activity from when he first stood up the DC — not a provisioning process, not a template, no intent behind which account got which group. The same-second creation is him clicking through ADUC, not automation.

So what survives is narrower and worth stating exactly: **dormant standing access is real and measurable here** (`mlee` held write access to a shared resource for eleven months without ever authenticating, and the directory recorded enough to prove it), and **the query that surfaces it works**. What does not survive is any claim that this demonstrates organic permission sprawl. It demonstrates a detection method against a condition the lab's own builder created — see the section below.

### On seeded findings, across this series

This exercise set out to test whether exercise 1's `sysadmin` finding generalized into a pattern. The honest answer is **no** — the one candidate pattern turned out to be lab noise with a known, mundane origin.

That negative result is worth more to this series than the false positive would have been, because it exposes a structural limit that applies to every report here: **district.local cannot supply authentic permission sprawl, because Raymond built all of it.** Every misconfiguration these exercises "find" — `sysadmin`'s undocumented `BUILTIN\Administrators` grant, the tier groups wired to nothing, this account batch — is a condition he created himself, mostly while learning the tooling. A reader who asks "where did this misconfiguration come from?" gets "I made it."

That does not make the work worthless, and the distinction matters for how these are read: the *detection technique* is genuine and transferable. Querying the group that actually gates the resource rather than the one with the recognizable name is a real skill, it caught a real thing on this DC, and it would catch the same thing in a production domain. What the lab cannot do is supply evidence that such conditions arise organically in the wild — that claim rests on Raymond's help-desk experience, which is testimony, not something district.local proves. Going forward these findings are framed as **seeded**: *here is a condition, here is how you find it*, not *here is sprawl I discovered*.

**Finding 2 — `sysadmin`'s tier0 grant arrived five days after the (already-empty) container it names.** `SG_admin_tier0_domain` was created 2025-10-04T03:52:14Z. `sysadmin` itself wasn't created until 2025-10-09T05:22:49Z, five days later, joining tier0 at creation. Per exercise 1, tier0 grants nothing — empty `memberOf`, no GPO Restricted Groups wiring, checked by name and by SID. So for the entire time `sysadmin` existed, its *real* admin path was the direct, undocumented `BUILTIN\Administrators` grant found and removed in exercise 1 — not the tiered-access group it was actually assigned to. **Captured** (the creation-order timing) plus a cross-reference to exercise 1's already-confirmed finding, not a new claim about tier0 itself.

**Finding 3 — `bhound`'s `adminCount=1` doesn't match its only current group.** `bhound` — created 2026-06-17T07:03:56Z, matching the BloodHound write-up's stated capstone session exactly — carries `adminCount: 1`, but its only listed `MemberOf` is `Key Admins`. Key Admins is not on the classic AdminSDHolder-protected-groups list. Two explanations are both live and neither is confirmed here: either this domain's actual SDProp configuration protects Key Admins (not independently checked), or `bhound` was at some point a member of a genuinely protected group that was later removed — which, per exercise 1's now-closed finding that `adminCount` does not self-clear, would explain a stuck `1` perfectly. **Captured** as a raw fact (the mismatch); the explanation is open, not asserted either way.

**Finding 4 — `bhound` outlived its stated purpose without being decommissioned.** The BloodHound write-up describes `bhound` as a throwaway collector credential for a single session, explicitly flagged for scrubbing "before any public repo." Its `LastLogonDate` is 2026-08-27T01:17:34Z — over two months after the 2026-06-17 capstone, and one day before `sysadmin`'s own most recent recorded logon. The account is still enabled. **Captured**; whether that later logon was Raymond re-using the credential deliberately or something left running is not something this data can distinguish — see Open Questions.

### Remediation: revoking mlee's and ajones's Site1 access

Raymond's call (see Where Raymond was consulted). Two `Remove-ADGroupMember` calls, both exit code `0`, no output — the expected shape for success, same as exercise 1's corrected removal attempt. The escaping bug that cost exercise 1 a failed first try (`-Confirm:$false` getting bash-interpolated to an empty string before `qm guest exec` ever saw it) was applied as a fix from the start here, not re-discovered: both commands used `-Confirm:\$false` and both succeeded on the first attempt.

**Post-removal verification** (`evidence/site1-rw-membership-post-removal.json`, exit code `0`) — `SG_Share_Site1_RW` now has two members: `jsmith` and `sysadmin`. **Captured**, and worth flagging directly rather than letting it pass quietly: `sysadmin` also holds this RW grant (visible in the original enumeration table above) — untouched by this remediation, since it wasn't part of what was asked, but it means the account whose *admin* access this lab already spent a full exercise removing still has standing write access to a file share, unexamined. Not acted on here — see Open Questions.

**Post-removal verification, `SG_Share_Site1_Read`** (`evidence/site1-read-membership-post-removal.json`, exit code `0`, no `out-data`) — `ajones` was the group's only member, so removing her leaves it **empty**. Same zero-result JSON shape as the SYSVOL greps in exercise 1: no `out-data` key at all is `ConvertTo-Json`'s serialization of nothing, not a fetch failure.

**Net effect:** `mlee` and `ajones` no longer hold standing access to Site1. Finding 1's dormant-access half is resolved. The "why were these four provisioned this way" half is not resolved by the remediation but is no longer open either — Raymond answered it directly (arbitrary DC-setup activity, no process behind it), which is what prompted the Finding 1 correction above.

**Finding 5 — `bingbong` is unexplained.** Created 2026-08-28T00:42:37Z, three days before this exercise, no group membership, one recorded logon about two hours after creation, no description captured anywhere. Nothing in this session's evidence says who created it or why. **Captured**, flagged rather than guessed at.

## What broke, and why

Nothing broke at the command level — both queries ran clean on the first attempt, exit code `0` each. What could have broken quietly is the date handling: `ConvertTo-Json`'s `/Date(<ms>)/` serialization is exactly the kind of thing that's easy to eyeball-approximate ("that's sometime in October 2025") and move on. Converting every value precisely with `date -u -r` gave a sharp fact — "created within the same one-second window" instead of "created around the same time" — and that fact held up.

**The interpretation built on it did not, and that's the more useful failure.** Precise data made me *more* confident in the wrong conclusion, not less: the tighter the timestamp clustering looked, the more it read as automation, and the first draft of this report called it the strongest evidence for the sprawl thesis. It took Raymond saying "that was just me messing around on a new DC" to kill it. The lesson isn't about date parsing — it's that rigor about *what the data says* provides no protection against over-reading *what the data means*, and the capture contract only covers the first half. An evidence file can't tell you why a human did something. Where intent is the claim, the only source is the human, and that has to be labeled testimony rather than laundered into a finding because the surrounding numbers were captured precisely.

One caveat worth naming rather than treating as settled: `LastLogonDate` reading `null` means "no value replicated to this DC," which is the same thing as "never logged on" only because district.local is a single-DC forest. In a multi-DC domain the same null could mean "logged on somewhere else and it hasn't replicated here yet." That distinction doesn't change any conclusion in this exercise, but relying on single-DC-ness without saying so out loud is exactly the kind of unstated assumption that stops being true the moment the lab grows a second DC.

## What I'd do differently

Pull `Get-ADGroupMember -Recursive` for the three `SG_admin_tier*` groups and both `SG_Share_Site1_*` groups in the same pass, rather than stopping at direct `MemberOf` from the user side. Exercise 1 needed a whole follow-up round to discover tier0 was an empty container; this exercise surfaced tier1 and tier2 memberships without checking whether either group is wired to anything, which just reproduces the same gap one exercise later instead of closing it while the session was already open.

I'd also pull `LastLogonTimestamp` (the replicated, cross-DC-safe attribute) alongside `LastLogonDate` as a standing habit, even on a single-DC forest where it wouldn't change today's answer — the caveat in What Broke shouldn't have to be a caveat next time.

## Open questions

- **Resolved this exercise: `mlee` and `ajones`'s standing Site1 access has been revoked.** Raymond's call, made directly; see Remediation above and `evidence/site1-rw-membership-post-removal.json` / `evidence/site1-read-membership-post-removal.json` for the confirmed after-state.
- **New from the remediation: `sysadmin` also holds standing RW access to `SG_Share_Site1_RW`, unexamined.** Surfaced by the post-removal membership check, not something this exercise set out to look at. `sysadmin` already had its *admin* path removed in exercise 1; this is a separate, non-admin grant that was never in scope for that removal and wasn't part of what Raymond asked revoked here either. Whether it's still needed is not something this session can answer — flagged rather than assumed either way.
- **The pre-flight infra check (`qm status 100`, `lvs`, `free -h`) specified before this remediation was not run.** The skill's own standing pre-flight step, added after exercise 2's crash, was requested but not followed here — logged as a gap, not smoothed over. Nothing suggests headroom was actually a problem, but that's a different claim from having checked it.
- **Closed by testimony, not capture: the four-account batch has a known, non-organic origin.** Asked directly, Raymond identified `jsmith`/`ajones`/`mlee`/`khan` as arbitrary activity from first standing up the DC — which explains both the same-second creation and why `khan` got no group at all (no reason; nothing was being followed). Logged as **Recalled**: it's the account creator stating what he did, which is authoritative in a way a query isn't, but it is testimony and nothing in `evidence/` backs it. It does not need re-running — there is no command that would capture intent — but it should not be cited as though the box printed it. It is the basis for the Finding 1 correction above.
- **`bhound`'s `adminCount=1` origin is unresolved.** Either Key Admins is protected in this domain's real SDProp configuration (untested) or the account once held a protected grant that was later pulled (consistent with, but not proven by, exercise 1's sticky-`adminCount` finding).
- **Should `bhound` be disabled or removed?** It's a stated throwaway account, still enabled, holding a non-trivial group membership (Key Admins governs `msDS-KeyCredentialLink`, a Shadow Credentials attack primitive), with a recorded logon two months past its documented purpose. Raymond's call, not assumed here.
- **What is `bingbong` and who created it?** No group membership, no description, created three days before this exercise. Unexplained.
- **The 55-vs-59 group count discrepancy against the inherited BloodHound figure is not reconciled.** Could be the inherited figure being wrong, a filtering difference in how the two counts were produced, or four groups genuinely deleted since June — not distinguished here.
- **Whether `SG_admin_tier1_helpdesk` or `SG_admin_tier2_desktop` are wired to anything is untested.** Same two mechanisms that turned out to grant `SG_admin_tier0_domain` nothing (AD nesting, GPO Restricted Groups/Preferences) were never re-run against these two. `SG_admin_tier2_desktop` currently has zero members among all 13 accounts — a tier of the access model that exists on paper only.
- **Nested/recursive group membership was not checked anywhere in this exercise**, same caveat as exercise 1's Domain Admins/Enterprise Admins queries — every `MemberOf` here is direct-only.
