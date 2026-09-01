# Working log — connector account + wizard relaunch

Continuation of `2026-08-31-entra-connect-install`, picked back up per two of that
report's Open Questions: the untested "stale wizard state" hypothesis, and the
never-created least-privilege AD DS connector account (the wizard was previously
going to be handed Enterprise Admin credentials directly).

Nothing in this file is fact until a capture backs it. Steps below are the plan;
each gets a status and, once run, an evidence file.

## Infrastructure pre-flight

Not run before the first state change this exercise (the Administrator bootstrap re-enable) —
should have been, per the scoped skill's pre-flight guidance. Running it now, retroactively,
rather than pretending it happened first. Noting that ordering gap here rather than smoothing it.

## Where Raymond was consulted

1. **Which account to use for DC01 console access.** I initially assumed "System Admin" in the
   login screen might be a renamed built-in Administrator; Raymond corrected: *"this is the account
   i created to admin the dc01, what other account are we using to login and admin"* — a genuine
   question back, not an answer to my question. That's what led to checking `verified-claims.md`
   and finding `sysadmin` had been deliberately stripped of `BUILTIN\Administrators` two exercises
   ago, leaving no account able to log in interactively at all.
2. **How to unblock console access**, given no account could log in. Offered three options
   (re-enable Administrator / restore sysadmin's admin path / something else) as a standing-privilege
   decision, not a unilateral call. Raymond: **"Re-enable Administrator"** — temporarily, rotate
   password first via a channel that minimizes disclosure, do the work, disable again at close.
3. **Whether to check GPO scope first, bypass, or fix directly** once the Domain-Admins deny rule
   was found. Raymond: "Check GPO scope first" (investigation only), then after the domain-root
   link with no DC exclusion was confirmed: **"Fix the GPO scope"** — a direct security-posture
   change, not a workaround.
4. **Password rotation and OU placement for svc-entraconnect**, confirmed by Raymond directly
   without prompting: bootstrap Administrator password was rotated via Ctrl+Alt+Del before any
   further work (value never disclosed to this channel), and svc-entraconnect was moved from the
   default Users container to the existing Service Accounts OU on his own initiative.

## Plan

1. **[ ] Create `svc-entraconnect`** — DC01 console, interactive password prompt
   (not `qm guest exec`, per the credential-disclosure lesson from the prior
   exercise). No admin group membership.
2. **[ ] Verify account state** — safe to capture via `qm guest exec` (no secret
   in the command).
3. **[ ] Delegate AD DS connector permissions to it** — VM102 console, interactive,
   using an Enterprise/Domain Admin session one time to grant the delegation
   (`Set-ADSyncBasicReadPermissions` / `Set-ADSyncRestrictedPermissions`). Exact
   module path/command to be confirmed on the box, not assumed.
4. **[ ] Verify the delegation landed** — `dsacls` against the domain root,
   filtered to the account name. Safe via `qm guest exec`.
5. **[ ] Fully exit and relaunch the Entra Connect wizard** on VM102, choosing
   "Customize" → use existing AD account → `svc-entraconnect`. This is also the
   test of the stale-wizard-state hypothesis.
6. **[ ] Capture wizard outcome** — screenshot(s), informational not filed evidence
   per the prior exercise's convention, plus whatever `qm guest exec` can confirm
   afterward (sync scheduler service state, connector status).

## Addendum — same-day follow-up capture

Requested per `CARRYOVER.md` section A item 1, to check the report's claim that `Administrator`
was "disabled again at close." First `Get-ADUser` attempt failed transiently (`Get-Service ADWS`
confirmed Running/Automatic immediately after; retry succeeded clean — treated as the class of
ADWS-not-ready blip the skill already documents, not investigated further). The retry showed
`Administrator` still `Enabled: True`. The report's claim was wrong; corrected in `report.md` and
`verified-claims.md` rather than silently edited. See
`evidence/administrator-close-out-check.json` for both raw captures.
