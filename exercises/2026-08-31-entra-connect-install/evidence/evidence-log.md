# Evidence log

Capture path: `qm guest exec 102` from the Proxmox host (VM 102's guest agent is functional, per the member-server-build exercise), plus direct Proxmox host shell for infrastructure checks. All pasted by Raymond.

## Round 1: VM 102 connectivity check, confounded by a concurrent DC01 crash

| Evidence file | Command | Result |
|---|---|---|
| (not separately filed, see below) | `Test-NetConnection -ComputerName login.microsoftonline.com -Port 443` | Failed: `WARNING: Name resolution of login.microsoftonline.com failed` |
| `vm102-dns-config-baseline.json` | `Get-DnsClientServerAddress -AddressFamily IPv4` | Confirmed DNS server = `10.0.0.10` |
| `vm102-dns-port53-hang.txt` | `Test-NetConnection -ComputerName 10.0.0.10 -Port 53` | **Hung** — guest-agent's own 30s exec timeout expired, returned bare `{"pid": 1412}` rather than a result |
| `vm102-resolve-dc01-failed.json` | `Resolve-DnsName -Name dc01.district.local -Type A` | Failed cleanly, `exitcode 1` |
| `vm102-egress-1111-hang.txt` | `Test-NetConnection -ComputerName 1.1.1.1 -Port 443` | **Hung** — same timeout/bare-PID shape, `{"pid": 3648}` |

**Working hypothesis at the time, tested and disproven: Proxmox's own per-VM firewall (the `firewall=1` flag copied from DC01's config into VM 102's `qm create`) was blocking traffic.** Checked directly rather than assumed:

```
pve-firewall status
Status: disabled/running
```
```
cat /etc/pve/firewall/cluster.fw   -> no cluster-wide ruleset file
cat /etc/pve/firewall/102.fw       -> no per-VM ruleset file for 102
cat /etc/pve/firewall/100.fw       -> no per-VM ruleset file for 100
```

Firewall enforcement is disabled entirely, no ruleset exists for either VM. This hypothesis is **conclusively ruled out** by direct evidence, not reasoned away.

**The actual likely explanation, surfaced by Raymond mid-diagnosis: DC01 crashed at approximately the same time these four tests ran.** See `exercises/2026-08-31-dc01-unexpected-shutdown/evidence/second-occurrence-crash-signature.txt` for the full host-side diagnosis (same `qmeventd`/"Connection reset by peer" signature as that exercise's original occurrence). Two of the four failures above (`Resolve-DnsName dc01.district.local` failing outright, and the port-53 hang against DC01 itself) are fully consistent with DC01 being down or mid-crash during the test — a DNS server that isn't there to answer explains both without any VM 102 misconfiguration needed. The `1.1.1.1` egress hang is less directly explained (that path doesn't route through DC01), but a transient bridge-level disruption from an ungraceful VM teardown on the same host is a plausible shared mechanism — not confirmed, not chased further, since the practical next step is simply to retest once DC01 is stable.

**Conclusion: none of Round 1's four results are trusted as characterizing VM 102's actual configuration.** They were captured during a confound (a concurrent DC01 outage of unknown precise duration) discovered only after the fact. Filed as historical record of what was observed and why it's not being acted on, not as evidence of a VM 102 problem.

## Round 2: retest against a confirmed-stable DC01

| Evidence file | Command | Result |
|---|---|---|
| `vm102-egress-confirmed-post-dc01-restart.json` | `Test-NetConnection -ComputerName login.microsoftonline.com -Port 443` (identical to the Round 1 command that opened this investigation) | **Clean success** — `TcpTestSucceeded: true`, `PingSucceeded: false` |

**Confirmed: the Round 1 confound theory holds.** The exact same command that failed with a DNS resolution error in Round 1 now succeeds cleanly, with no changes made to VM 102's own configuration between the two attempts — the only thing that changed is DC01 being stable again. `PingSucceeded: false` alongside a successful TCP test is the same pattern DC01 itself showed after its own connectivity fix in the hybrid-identity exercise (ICMP blocked/dropped somewhere on the path while TCP/443 works); not treated as a new concern, consistent with the earlier precedent.

**Net effect: VM 102 has working outbound HTTPS to Microsoft's endpoints.** No VM 102-specific misconfiguration was ever real — the Proxmox firewall hypothesis was disproven, and the actual explanation was a concurrent DC01 outage. VM 102 is network-ready for an Entra Connect install from a connectivity standpoint.

## UPN re-stamp

Per Raymond's decision earlier in this exercise (stamp real users on the tenant's permanent `onmicrosoft.com` suffix, not the uncertain `districtsafetyphoto.com` domain) and his direct instruction to proceed. Snapshot taken first — see `upn-restamp-snapshot.txt` — same standard as the `sysadmin` removal in the constrained-admin-path exercise.

| Evidence file | Action | Result |
|---|---|---|
| `upn-restamp-snapshot.txt` | `qm snapshot 100 pre-upn-restamp-20260831` | Confirmed registered, correctly positioned |
| `upn-suffix-added-and-verified.json` | `Set-ADForest -UPNSuffixes @{Add='raytakosharkygmail.onmicrosoft.com'}` | Exit `0`; `Get-ADForest` confirms the suffix is now present, was empty before |
| `upn-restamp-final-verification.json` | `Get-ADUser -Filter * -Properties UserPrincipalName` (full enumeration) | All 9 target accounts show the new suffix; `Administrator`/`Guest`/`krbtgt`/`bhound` correctly still `null` |

**Gap, named rather than smoothed over: the nine individual `Set-ADUser` commands' own outputs were not captured.** Raymond ran all nine and went straight to the final verification query rather than pasting each command's own result. This is the same shape of gap flagged in the original crash exercise's first snapshot-pruning round — and notably, the *lesson* from that gap (capture each destructive call's own output) was actually applied earlier in this same session, for the second pruning round. It wasn't applied here. The final aggregate check is strong evidence — a full enumeration of every user object, confirming both that all nine changed correctly and that nothing else was touched, which is more complete than a simple before/after count would be — but it is not nine individually-captured exit-code confirmations, and that distinction is preserved here rather than treated as equivalent.

**Result: forest UPN suffix added, nine real user accounts re-stamped from `@district.local` to `@raytakosharkygmail.onmicrosoft.com`.** `dumbuser2`, `dumbuser3`, `dumbhelpdesk1`, `jsmith`, `ajones`, `mlee`, `khan`, `sysadmin`, `bingbong`. `bhound` deliberately excluded (has no UPN at all — a separate, unresolved open question, not something to invent a value for here). `Administrator`, `Guest`, `krbtgt` deliberately excluded (no UPN by design).

## Entra Connect install attempt — components installed, configuration never completed

The installer ran and its "Install required components" phase completed (SQL Server Express LocalDB, the sync service). Wizard configuration reached the **"Connect your directories" / AD forest account** step and never got past it. Five hypotheses were tested against that one error message: *"The domain specified in the credentials does not exist or cannot be contacted."*

| Hypothesis | Test | Evidence | Verdict |
|---|---|---|---|
| Username not domain-qualified | Re-entered as `DISTRICT\Administrator` | Console screenshot showing the qualified string in the field | **Disproven** — format was correct, error unchanged |
| `Administrator` account disabled | `Enable-ADAccount`, then password reset | `administrator-account-state-diagnostic.json` | **Real problem, not this problem** — account genuinely *was* disabled (per the IAM exercise's enumeration), enabling it was correct hygiene, error unchanged |
| DNS / DC-locator failure | `nltest /dsgetdc`, `_ldap._tcp.dc._msdcs` SRV lookup | `vm102-dc-locator-and-srv-success.json` | **Disproven** — DC01 discovered cleanly with full capability flags |
| LDAP signing required (`LDAPServerIntegrity=2`) rejecting an unsigned bind | Read the registry value, lowered to `1`, verified | `ldap-signing-found-and-lowered.json` | **Plausible, evidenced, and insufficient** — value really was `2`, lowering it verified, error unchanged |
| AD service ports blocked | `Test-NetConnection` to 389 and 3268 | `vm102-ldap-gc-ports-open.json` | **Disproven** — both open |

**The credential line was ultimately closed by timestamp evidence, not by guessing.** `PasswordLastSet` decodes to 17:50:34 PDT; the wizard dialog was submitted ~17:54 with the account `Enabled: true`, `LockedOut: false`, `PasswordExpired: false`. Valid credentials, usable account, same error. That retroactively invalidates the whole credential-focused detour — including two changes made to DC01 in service of it.

**Remaining untested hypothesis at close: stale wizard state.** The wizard marked this connection failed early, before any real fix had landed, and may not genuinely re-validate on each retry within the same session. A full application exit and relaunch was recommended but not performed — Raymond called the exercise before trying it. This is the single most likely next step, and it is untested, not disproven.

## State changes left behind on DC01 by this exercise

Two security-relevant changes were made in pursuit of an install that never completed. Both are documented here because they leave `district.local` in a weaker posture than it started, for no gained functionality:

1. **`Administrator` is enabled** (it was `Enabled: false` before this session) **and its password is a value that was disclosed in-session.** A rotation was requested and instructions given; `PasswordLastSet` proves it never ran. The account is a member of Domain Admins, Enterprise Admins, and Schema Admins.
2. **`LDAPServerIntegrity` is `1`** (was `2` — deliberate hardening, part of the `win2022servLOCK` "Microsoft Official Security Baseline for DCs" posture). Lowered as a hypothesis test that did not resolve the problem.

Both are carried into the report's Open Questions with recommended reversion commands. Neither was reverted before close.
