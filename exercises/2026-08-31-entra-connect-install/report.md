# Entra Connect install — UPN re-stamp done, sync configuration blocked

## What I set out to do

Install and configure Microsoft Entra Connect on the member server built in the previous exercise, completing the on-prem-to-cloud sync that the whole hybrid-identity thread has been building toward. Two prerequisites had to land first: confirming VM 102 could actually reach Microsoft's endpoints, and re-stamping every user's UPN off the non-routable `@district.local` suffix.

**Outcome: the prerequisites succeeded, the install did not.** Entra Connect's components installed, but wizard configuration never got past connecting to Active Directory. The exercise is being closed with that step unresolved rather than left running indefinitely — and with two security-relevant changes to DC01 still un-reverted, which is the most important thing in this report.

## The setup

DC01 (VM 100) and the new `entraconnect01` (VM 102, `10.0.0.11`), both on the isolated `10.0.0.0/24` lab bridge. Capture path for both is `qm guest exec` — VM 102's guest agent became functional at the end of the member-server-build exercise, so unlike that build, this exercise has real captured command output rather than console screenshots for the infrastructure work. The Entra Connect wizard itself is GUI-only and was observed via console screenshots, which are informational, not filed evidence.

## What I did

Roughly in order: a VM 102 connectivity check that failed and turned out to be a confound; a pre-change snapshot and the UPN re-stamp; the Entra Connect install; and five rounds of hypothesis-testing against a single wizard error that was never resolved.

## Where Raymond was consulted

**1. UPN suffix strategy.** Raymond initially chose a routable domain he owns (`districtsafetyphoto.com`), and a screenshot of its Namecheap DNS panel showed it fronting a live Shopify storefront. I flagged two consequences — a domain can only be verified in one Entra tenant at a time, and committing a live business domain to a lab tenant with a single MSA-backed admin is harder to undo than to do — and recommended a subdomain. His answer went past both options: *"business is kaput, no need keep it separate, lets just run it for testing, we got a month or so before i consider renewing, so what you consider is best recommended for our lab."* Given the registration itself is uncertain past roughly a month, **my recommendation, stated as mine**: stamp real UPNs on the tenant's permanent `onmicrosoft.com` suffix, and separately verify `districtsafetyphoto.com` in the tenant as its own small captured exercise before it lapses. An identity foundation the series builds on shouldn't be anchored to a namespace with a known expiry.

**2. Proceeding with the re-stamp.** Highest-blast-radius action in the thread — every real user account touched. Snapshot first, exact commands reviewed, explicit go-ahead, same standard as the `sysadmin` removal.

**3. Re-enabling `Administrator`.** When the disabled-account hypothesis surfaced, Raymond's instruction was *"reenable and reset pw."* I provided both commands and deliberately did not generate a password value — see What broke.

**4. Lowering LDAP signing.** Presented as a genuine security-posture decision with two options (lower `LDAPServerIntegrity` to `1`, or stand up real LDAPS on 636). I recommended the former as the pragmatic unblock, flagging it as the same trade-off already made once on this DC. Raymond: *"yeah lower it to 1."*

**5. Calling the exercise.** After the fifth hypothesis failed, Raymond: *"meh lets call it."* A deliberate stop with one hypothesis still untested (stale wizard state), not an exhausted investigation.

## What the box said

**VM 102 connectivity, round 1 — a confound, not a finding.** `Test-NetConnection` to `login.microsoftonline.com` failed on name resolution; follow-up tests hung until the guest agent's own exec timeout expired, returning bare PIDs. I hypothesized Proxmox's per-VM firewall (the `firewall=1` flag copied mechanically from DC01's config) and tested it directly: `pve-firewall status` returned `disabled/running` with no cluster or per-VM ruleset for either VM (`proxmox-firewall-check-disproven.txt`). **Disproven.** The actual explanation surfaced when Raymond mentioned DC01 had gone down — a second crash, same `qmeventd`/"Connection reset by peer" signature as the original crash exercise, filed there rather than here since it continues that exercise's own unresolved question. Two of the four failures are fully explained by "the DNS server wasn't running." The identical test succeeded cleanly (`TcpTestSucceeded: true`) once DC01 was stable, **with no change made to VM 102 in between** (`vm102-egress-confirmed-post-dc01-restart.json`). Round 1's results characterize a confound, not a configuration.

**UPN re-stamp — clean success.** Snapshot `pre-upn-restamp-20260831` created and verified positioned. `Set-ADForest -UPNSuffixes @{Add=...}` succeeded; `Get-ADForest` confirmed `raytakosharkygmail.onmicrosoft.com` present where `UPNSuffixes` had been empty. Nine `Set-ADUser` calls re-stamped every real account. Final verification (`upn-restamp-final-verification.json`) enumerated all 13 user objects: nine correct, and `Administrator`/`Guest`/`krbtgt`/`bhound` correctly still `null`. **Captured** — with one gap named in the evidence log: the nine individual command outputs weren't captured, only the aggregate enumeration. That enumeration is unusually strong aggregate evidence (it proves both success *and* that nothing else changed), but it is not nine exit codes, and the lesson to capture individually had been successfully applied earlier in this same session for snapshot pruning. It wasn't applied here.

**The install, and five hypotheses.** Components installed fine. Configuration stopped at the AD forest account step with *"The domain specified in the credentials does not exist or cannot be contacted."* The full hypothesis table is in `evidence/evidence-log.md`; in summary: username format (disproven — was already correctly qualified), disabled account (a real problem, genuinely fixed, but not this one), DNS/DC-locator (disproven — `nltest` resolved DC01 with full `PDC GC DS LDAP KDC` flags, SRV records clean), LDAP signing (real, evidenced, insufficient), and AD service ports (disproven — 389 and 3268 both open).

**The credential line was closed by a timestamp, not by another guess.** `PasswordLastSet` decoded to 17:50:34 PDT; the dialog was submitted around 17:54 with the account `Enabled: true`, `LockedOut: false`, `PasswordExpired: false`. Valid credentials, usable account, identical error. That single capture invalidated a whole branch of investigation — including two changes to DC01 made in service of it.

## What broke, and why

**I disclosed a credential by designing a bad placeholder.** Asked to reset the Administrator password, I correctly declined to generate a password value myself and supplied a template with `YOUR-NEW-PASSWORD-HERE` in it. Raymond appended a few characters to that placeholder string rather than replacing it, ran it, and pasted the full command back — so the live Domain Admin password became a trivial derivative of my own placeholder text (value deliberately not reproduced here), and it entered this conversation. Two failures, both mine: the placeholder read as something to *edit* rather than *delete*, and I never said "don't paste this back." I flagged it immediately and gave rotation instructions. `PasswordLastSet` later proved the rotation never ran. **The password is still that value at exercise close.**

**I chased credentials for three rounds when the evidence didn't support it.** The error text says *domain cannot be contacted*, not *bad credentials*. I anchored on the account-disabled finding — real, and satisfying, because it came from this project's own captured evidence — and kept iterating on that theme (enable, reset, re-format the username) instead of testing what the message actually described. The DC-locator and port tests that would have moved things along came fourth and fifth. The account genuinely *was* disabled and enabling it was correct hygiene; it just wasn't the problem, and a plausible finding from good evidence is still a hypothesis, not an answer.

**I weakened a deliberately-hardened DC for nothing.** Lowering `LDAPServerIntegrity` from `2` to `1` was a well-reasoned hypothesis — the inherited BloodHound write-up documented that exact behavior on that exact DC, and I verified the value directly rather than trusting the document. It also didn't work. The security reduction bought zero functionality, and it's still in place.

**A rediscovered lesson: `firewall=1` was copied from DC01's config without checking whether Proxmox's firewall was even enabled.** Mechanical config-mirroring produced a plausible-but-wrong hypothesis later. Same class as the `ostype: l26` mismatch found in the previous exercise — copying a working config without understanding each field.

## What I'd do differently

**Read the error message literally before pattern-matching to a known finding.** "Cannot be contacted" describes a connectivity/discovery failure. I had a satisfying credential-shaped finding in hand and spent three rounds there. Testing what the error actually said — DC locator, service ports — would have come first, and would have cleared the field for the LDAP hypothesis faster.

**Never hand over a fill-in-the-blank credential template.** The correct pattern is: have the user run an interactive prompt that never puts the secret on a command line at all — e.g. `Set-ADAccountPassword -Identity Administrator -Reset` with no `-NewPassword`, which prompts securely — rather than a string to edit. That eliminates both the paste-back risk and the shell-history exposure in one move.

**Revert a failed hypothesis's changes immediately when it's disproven, not at close-out.** `LDAPServerIntegrity` should have gone back to `2` the moment the wizard error persisted. Leaving it lowered turned a bounded test into a standing posture change, and it's only in this report as an open item because it was never undone.

## Open questions

- **RESOLVED 2026-09-01, `entra-connect-connector-account`.** Entra Connect installed successfully in staging mode on that date; the wizard cleared "Connect Directories" on the first relaunch after that exercise fixed an unrelated GPO lockout and properly domain-joined VM 102. Left below in its original form for the record — at the time this report closed, both bullets below were accurate.
- ~~**Entra Connect is not installed.**~~ Components were on VM 102; no sync was configured, no directory connected, no object had ever synced.
- ~~**The one untested hypothesis: stale wizard state.**~~ It turned out not to be the actual blocker — the real cause was VM 102 never having been genuinely domain-joined, discovered 2026-09-01 — but relaunching the wizard after that fix is exactly what finally cleared it, so the hypothesis wasn't wrong about the mechanism, just early.
- **RESOLVED at close — both security changes reverted and verified** (`evidence/security-reversions-confirmed.json`). `Administrator` is back to `Enabled: false`, its pre-session state; `LDAPServerIntegrity` is back to `2`. The lab's security posture matches where it started.
- ~~**Residual from the disclosure: the Administrator password is still the value that entered this conversation.**~~ **RESOLVED 2026-09-01.** Rotated without the new value ever being disclosed to any channel, this time via `qm guest exec` with the value generated and consumed entirely server-side rather than console-only as recommended here — see `exercises/2026-09-01-entra-connect-connector-account/evidence/administrator-password-rotated-no-disclosure.json`.
- **Untested: whether `LDAPServerIntegrity` self-reverts on reboot.** The inherited BloodHound write-up claims `1 → 2` on every DC restart independent of GPO. Now moot for this exercise (the value is deliberately back at `2`), but that inherited claim remains unverified in this project's own evidence and would be worth confirming if the value is ever lowered again.
- ~~**`bhound` still has no UPN and would fail sync.**~~ **RESOLVED 2026-09-01**, differently than any of the three options this report named. `bhound` turned out to hold a live shadow-credentials path via Key Admins membership — it was disabled entirely rather than given a UPN or excluded from scope, closing both problems at once.
- **`districtsafetyphoto.com` verification never happened**, and the registration window flagged here is now nearly elapsed as of 2026-09-01 — still open, see `CARRYOVER.md`.
- ~~**The AD DS connector account was never created**~~ — **RESOLVED 2026-09-01.** `svc-entraconnect` was pre-provisioned by hand with least-privilege delegation (basic read, `ms-DS-ConsistencyGuid` write, Password Hash Sync), exactly the on-thesis follow-up this bullet asked for — see `exercises/2026-09-01-entra-connect-connector-account/report.md`.
