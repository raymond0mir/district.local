# B1 (setup) — getting a domain-joined Windows 11 client, the hard way

## What I set out to do

CURRICULUM.md's B1 setup step asked one question: characterize VM 101's domain state, so B1's
Conditional Access work has a real client to test against instead of needing a new VM built from
scratch. OS and name were already Confirmed (2026-09-02); domain state was not. That should have
been a short check. It became the exercise, and CA policy work itself (CURRICULUM.md steps 1-6)
did not start this session — this report covers only the path to a working, Entra-joined client.

## The setup

Lab slice: DC01 (VM 100), VM 101 (`win11-client01`), VM 102 (`entraconnect01`), pfSense (VM 104),
all on the Proxmox host. Pre-flight before touching VM 101: thin pool `Data%` 72.13%, under the
85% gate; host RAM available 3.5Gi. VM 101 downsized 4096→3072 MB before starting, a routine
sizing default given that headroom, not a deliberate rebalancing exercise.

## What I did

1. Started VM 101. `qm agent 101 ping` failed twice, across a 120s and a 90s wait. Cross-checked
   against the qemu process directly (`ps -o pid,etime,rss,vsz`) and the Proxmox console: real
   memory use (3.04 GiB RSS) and a genuine Windows 11 lock screen at 8m12s uptime ruled out a
   stalled boot. **VM 101's config carries `agent: 1` but has no working in-guest QEMU Guest
   Agent service** — the `qm guest exec` pattern used for DC01 all session does not work on this
   client.
2. The local account on VM 101 had a forgotten password, and no working agent to fall back on.
   Raymond's call: roll back to the `win11-ootb` snapshot and rejoin fresh, rather than pursue an
   offline recovery of an unknown account. Console after restart showed real OOBE screens, not the
   same lock screen — confirmed the snapshot held no baked-in account.
3. Rejoined as `jsmith@raytakosharkygmail.onmicrosoft.com` — Entra join, not hybrid, chosen
   specifically because VM 102's device sync was already known stopped (carryover), and Entra join
   does not depend on it.
4. `jsmith`'s password was also unknown. Checked Vaultwarden first — not stored there. Tried the
   Entra admin center's cloud password reset — refused, licensing wall (see "What broke," below).
   Fell back to an on-prem reset via DC01's console — blocked by a second, unrelated wall (also
   below). Worked around both by running `Set-ADAccountPassword` through `qm guest exec` against
   DC01, which executes as SYSTEM and is not subject to interactive-logon restrictions.
5. The new password still failed at OOBE. Correctly diagnosed before assuming the reset itself was
   bad: the change was on-prem only, and Password Hash Sync (VM 102, stopped) had not run since.
   Started VM 102 (downsized 3072→2048 MB, same routine-default pattern), confirmed its guest
   agent worked, and ran `Start-ADSyncSyncCycle -PolicyType Delta` — `Result: Success`.
6. Retried OOBE sign-in. Succeeded. Windows prompted for and completed Windows Hello setup
   automatically as part of join provisioning — not something this exercise configured.
7. Confirmed both the join and the Windows Hello outcome via Graph Explorer, not the console
   screenshot: `GET /users/jsmith.../registeredDevices` and
   `GET /users/jsmith.../authentication/methods`.

## Where Raymond was consulted

- **Phishing-resistant auth method for B1's later CA policy.** Asked to choose between a FIDO2
  key, Windows Hello for Business, and certificate-based auth. Raymond's actual answer:
  *"what's going to demonstrate knowledge and stay within the constraints of our lab?"* —
  handed the tradeoff back rather than picking blind. Recommended Windows Hello for Business:
  FIDO2 needs a purchase, already ruled out by carryover's "run lean, no purchases" decision;
  certificate-based auth is CURRICULUM.md's own "more work" no-hardware fallback; WHfB is the
  common real-world control and needed no purchase or extra build. Raymond did not object, and
  the OOBE flow independently confirmed the choice was workable — Windows set up real WHfB on its
  own during join, unprompted by any CA policy.
- **Recover VM 101's forgotten account, or roll back and rejoin fresh.** Raymond: *"yes, jsmith"*
  — confirmed both the rollback and the account to join as, in one answer.
- **`SeDenyInteractiveLogonRight` finding — investigate now or defer.** Raymond: *"lets keep for
  next one"* — deferred to a future exercise rather than unwinding a security control mid-session
  to fix a password reset.
- **Close the session here, before starting CA policy work.** Recommended given the setup phase
  alone produced report-worthy material, RAM was down to 1.2Gi available, and CURRICULUM.md
  already expects two reports for B1. Raymond: *"yes, close it out and wrap session."*

## What the box said

- Domain Admins membership, read-only, before the lockout diagnosis:
  `{"SamAccountName":"Administrator","Enabled":false},{"SamAccountName":"sysadmin","Enabled":true}`
  — contradicted Raymond's stated recollection that `sysadmin` was the disabled one.
  `evidence/dc01-domain-admins-membership-enabled-status.txt`.
- User-rights export, same session: `SeInteractiveLogonRight = *S-1-5-32-544,*S-1-5-32-549,
  *S-1-5-32-550,*S-1-5-32-551,*S-1-5-9` and `SeDenyInteractiveLogonRight = Domain Admins`.
  `evidence/dc01-sysadmin-deny-interactive-logon-secedit.txt`.
- Delta sync: `Result: Success`, exit code 0, no error output.
- Graph, post-join: `"trustType": "AzureAd"`, `"domainName": null`, `"onPremisesSyncEnabled":
  null` for `DESKTOP-O860UU9`. `evidence/jsmith-registered-devices-vm101-entra-join-20260904T0035Z.json`.
- Graph, authentication methods: a `#microsoft.graph.windowsHelloForBusinessAuthenticationMethod`
  entry, `"displayName": "DESKTOP-O860UU9"`, `"keyStrength": "normal"`, created
  `2026-09-04T00:37:56Z`. `evidence/jsmith-authentication-methods-whfb-confirmed-20260904T0038Z.json`.

## What broke, and why

- **VM 101 has no working in-guest agent, despite `agent: 1` in its config.** The config flag only
  tells Proxmox to try the channel; it does not install `qemu-ga` inside the guest. Cost two full
  wait cycles before the console screenshot settled it. Worth checking directly (`qm agent ping`)
  before trusting a VM's config flag on any future client build.
- **The cloud password reset is blocked by licensing, not error.** Entra admin center: "the
  current licensing does not allow you to reset this user's password... licensing requirements for
  password writeback." `jsmith` is synced from on-prem AD; writing a cloud-initiated password
  change back down requires P1/P2. This extends A3's Free-tier ceiling to a fourth control
  (Identity Protection, CA, PIM, now writeback) — Recalled only here, screenshot-sourced, not yet
  converted to a Graph error code the way A3's other three refusals were.
- **DC01's console rejected every account, for a reason its own error text does not reveal.**
  "The sign-in method you're trying to use isn't allowed" appeared for `sysadmin`, holding a
  verified Domain Admins path and enabled. `verified-claims.md:59` already logged this same text
  once before, for `sysadmin` lacking any grant at all — same message, opposite cause, twice. The
  actual cause this time: an explicit `SeDenyInteractiveLogonRight = Domain Admins` on DC01,
  likely from the still-unread `District Lockdown` GPO. CURRICULUM.md had already named this
  pattern for B1 before it happened: enforce a control before the break-glass path is proven, and
  the failure mode is the sequencing, not the control. It recurred anyway, live, on the very
  account meant to fix a different problem.
- **My own errors, three of them:**
  - `ConvertTo-Json -Compact` — a PowerShell 7 parameter. DC01 runs Windows PowerShell 5.1. Two
    wasted guest-exec calls before I caught it.
  - Misdiagnosed the resulting garbled command as a stale terminal paste. Wrong, and stated wrong
    to Raymond before being corrected. The real cause: `$_` inside a double-quoted `-Command`
    string is expanded by the host's own bash/zsh shell before `qm` ever sees it, substituting the
    last argument of the previous command. Retracted on the record once found.
  - Ran two diagnostic `qm guest exec` commands against DC01 without a paired `date -u` capture,
    breaking the project's own evidence-file convention. Both evidence files say so plainly rather
    than inventing a timestamp.

## What I'd do differently

Single-quote the whole `-Command` string by default on any `qm guest exec` call carrying a
PowerShell variable, from the first attempt, not after two failed escaping attempts — it avoids
the entire class of bug rather than patching around individual `$` signs. Pair every guest-exec
diagnostic with `date -u` in the same command block, no exceptions, rather than treating it as
optional for "quick" reads. And check `qm agent <vmid> ping` on any VM before relying on its
`agent: 1` config flag, including ones the ledger already calls "guest agent enabled."

## Open questions

- Which GPO actually sets `SeDenyInteractiveLogonRight = Domain Admins` on DC01 — likely
  `District Lockdown`, not confirmed. Whether to change it, remove it, or design around it with a
  dedicated break-glass path is still open, deferred by Raymond's own decision.
- The password-writeback licensing refusal needs a proper Graph-based capture (error code, not a
  screenshot) if it is going to sit in the ledger the way A3's other refusals do.
- Host RAM: four VMs plus the container now run concurrently, available RAM as low as 1.2Gi at
  last check. Still roughly 1.77 GiB over-committed even after this session's downsizing. Not
  rebalanced deliberately.
- Whether VM 101's missing in-guest agent is worth fixing for future exercises, now that Graph
  verification proved sufficient for this one's actual goal.
- B1 steps 1 through 6 — the actual Conditional Access baseline, report-only policies, break-glass
  exclusion, telemetry, and enforcement — have not started.
