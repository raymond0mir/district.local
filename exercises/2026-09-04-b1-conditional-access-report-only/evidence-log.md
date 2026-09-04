# Evidence log — B1: Conditional Access, report-only to enforced (setup phase)

Setup and device-join phase only. CA policy work (CURRICULUM.md steps 1-6) not yet started.

## Plan (per CURRICULUM.md Exercise B1, setup step)

Characterize VM 101: OS, domain state, contents. Ledger already had OS and name Confirmed
(2026-09-02, `qm list` output). Domain state was not.

## VM 101 characterization

- RAM headroom checked before touching VM 101: thin pool 72.13%, host available 3.5Gi. VM 101
  downsized 4096→3072 MB before starting (routine default, flagged, not asked). Reversible via
  `qm set 101 --memory 4096`.
- VM 101 started. `qm agent 101 ping` failed on two separate waits (120s interrupted, then a
  clean 90s). Host-level signals (PID 48847, RSS 3.04 GiB of 3 GiB assigned, elapsed 7m34s) ruled
  out a stalled early boot. Console screenshot (Recalled) confirmed a real Windows 11 lock screen
  at 8m12s uptime.
- **Finding: VM 101's config carries `agent: 1` but has no working in-guest QEMU Guest Agent
  service.** The `qm guest exec` pattern used throughout this project for DC01 does not work on
  this client. Not fixed this exercise — Graph-based verification (below) made it unnecessary for
  this specific goal.
- Local account on VM 101 ("bing bong") had a forgotten password — closed that login path
  entirely, with no working guest agent as a fallback.

## Decision: roll back and rejoin fresh, not recover the old account

Raymond's call, given in session. Rolled back to the `win11-ootb` snapshot rather than pursue an
offline password reset on an unknown local account. Console after restart showed real OOBE
license/region screens, not the same lock screen — the snapshot held no baked-in account.
Rejoined as `jsmith@raytakosharkygmail.onmicrosoft.com`, chosen for its already-registered MFA
method (Microsoft Authenticator, per carryover) and Entra join, not hybrid — VM 102's Entra
Connect device sync was already known stopped, so Entra join sidesteps that dependency entirely
per CURRICULUM.md's own framing.

## jsmith password reset — three dead ends before the fix

1. **Vaultwarden**: not stored there. Checked before touching anything privileged.
2. **Entra admin center cloud reset**: refused. "Unfortunately, the current licensing does not
   allow you to reset this user's password... licensing requirements for password writeback."
   Extends A3's Free-tier ceiling finding to a fourth control (Identity Protection, CA, PIM, now
   writeback for a synced user). Recalled only (screenshot-sourced) — not yet converted to a
   Graph-based error code the way A3's other three refusals were.
3. **On-prem reset via DC01 console, as `sysadmin`**: Raymond recalled `sysadmin` as disabled.
   Captured check (`Get-ADGroupMember`/`Get-ADUser` via `qm guest exec`, read-only, no secret)
   showed the opposite: `Administrator` is `Enabled: false`, `sysadmin` is `Enabled: true` and
   holds Domain Admins. **Recalled-vs-Captured mismatch, not a real lockout at this step.**
   Console logon still failed anyway: "The sign-in method you're trying to use isn't allowed."
   Same generic text ledger row 59 already logged once before, for the opposite reason
   (`verified-claims.md:59`) — this error text does not identify its own cause.

## Root cause of the console logon failure

Targeted, read-only capture (`SmartcardLogonRequired`, `userAccountControl`, `LockedOut`,
`AccountExpirationDate`, plus a `secedit /export /areas USER_RIGHTS`) on DC01 ruled out
smart-card requirement, account lockout, and expiration, and found the real cause:
**`SeDenyInteractiveLogonRight = Domain Admins`** on DC01. An explicit local deny for the entire
Domain Admins group at the console. Deny overrides `sysadmin`'s separate allow via
`BUILTIN\Administrators` nesting. Likely sourced from the `District Lockdown` GPO already flagged
in `EXPOSURES.md` for its inert Restricted Groups setting — not yet confirmed which GPO actually
sets this line. This is CURRICULUM.md's own named "sequencing lesson from `sysadmin`" recurring
live, mid-exercise: a real hardening control now blocking the account meant to administer the box.
**Deferred to the next exercise, Raymond's call** — not fixed here.

## Workaround used

`qm guest exec` runs as SYSTEM on the guest — a service logon, not interactive, so
`SeDenyInteractiveLogonRight` does not apply to it. Used it to run `Set-ADAccountPassword` for
jsmith directly, Raymond supplying the new value inline in the command (no interactive prompt, so
the No-TTY hang risk doesn't apply here — that rule is about commands that wait for typed input,
not about passing a literal value as a parameter).

New password still failed at OOBE. Correctly diagnosed before assuming the reset failed: the
on-prem change hadn't reached Entra ID yet. Password Hash Sync runs through VM 102
(entraconnect01), stopped per carryover — no sync had run since the reset.

- VM 102 started, downsized 3072→2048 MB (routine default, flagged) given available RAM was 3.1Gi
  before start, the same thin margin VM 101 had already shown real risk at.
- VM 102's guest agent responded (`qm agent 102 ping` produced no "not running" error — the
  success case for that command is silence). Unlike VM 101, this client's agent works.
- `Start-ADSyncSyncCycle -PolicyType Delta` run via `qm guest exec 102`: `Result: Success`.
- jsmith's new password worked at OOBE after the sync. Entra join completed.

## Captured: VM 101's join state and jsmith's WHfB registration

Graph Explorer, signed in as the new native break-glass account (name withheld per repo policy).

- **`GET /users/jsmith.../registeredDevices`**: VM 101 (`DESKTOP-O860UU9`) is
  `trustType: "AzureAd"` — Entra-joined, cloud-native, not hybrid. `domainName` and
  `onPremisesSyncEnabled` both null confirms no on-prem link.
  `evidence/jsmith-registered-devices-vm101-entra-join-20260904T0035Z.json`.
- **`GET /users/jsmith.../authentication/methods`**: a
  `windowsHelloForBusinessAuthenticationMethod` entry, `displayName: "DESKTOP-O860UU9"`,
  `keyStrength: "normal"`, created 2026-09-04T00:37:56Z. Windows set this up automatically during
  Entra join provisioning, with no explicit CA or Intune policy pushing it — confirms real WHfB,
  not a local convenience PIN, and lands the phishing-resistant auth decision made earlier this
  session without extra configuration work.
  `evidence/jsmith-authentication-methods-whfb-confirmed-20260904T0038Z.json`.

## Claude's own errors, caught this session

- Used `ConvertTo-Json -Compact` — a PowerShell 7 parameter. DC01 runs Windows PowerShell 5.1,
  which does not have it. Caused the first two guest-exec failures.
- Misdiagnosed the resulting garbled output as a stale terminal paste. Wrong. The real cause: `$_`
  inside a double-quoted `-Command` string is expanded by the host's own bash/zsh shell before
  `qm` ever sees it, substituting the last argument of the previous command. Retracted on the
  record. Fixed first by escaping `$`, then by single-quoting the whole `-Command` string, which
  avoids the entire class of bug and should be the default pattern going forward.

## Open, not resolved this exercise

- Which GPO sets `SeDenyInteractiveLogonRight = Domain Admins` on DC01, and whether to change it.
- The Entra cloud password-reset licensing refusal is Recalled only — no Graph-based error code
  captured yet, unlike A3's other three refusals.
- Host RAM: all four VMs plus container 103 now running concurrently. Available was 1.2Gi at last
  check, the tightest this session. Recheck before further work.
- B1 steps 1-6 (Security Defaults baseline, report-only policies, break-glass exclusion,
  telemetry, enforcement) not started.
