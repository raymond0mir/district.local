# Command gotchas

Standing behaviors captured in past exercises. Read before the first command on DC01 or in the tenant. Each line is Captured unless marked Recalled. Source exercises are named.

Write the condition that makes each line true. A behavior that depends on a license tier, a build, or a service state says so. Update this file at every session close.

## qm guest exec (DC01, VM 102)

- No TTY. A prompt for input hangs until timeout and orphans a process on the guest. Found 2026-09-02.
- `Set-ADAccountPassword -Reset` without `-NewPassword` hangs. Run it on the VM console.
- `slmgr` runs under `wscript` by default and opens a GUI dialog that hangs. Run `cscript.exe //NoLogo //B slmgr.vbs <args>`. Do not run `slmgr /dlv` at all. Source: `exercises/2026-09-02-dc01-eval-license-status`.
- Prefer native PowerShell and CIM over VBScript wrappers.
- `Get-ADDomain` fails while ADWS initializes after boot. Wait and re-run.

## GroupPolicy module

- `New-GPLink` returns nothing on success. Empty output is not a failure. Verify with `Get-GPOReport` and read `LinksTo`.
- `New-GPLink` accepts the DNS form for the domain root: `"district.local"`.
- `Remove-GPLink` needs the distinguishedName form: `"DC=district,DC=local"`. The DNS form fails. Getting this wrong on 2026-09-02 recreated a lockout exposure for about 90 seconds. Source: `exercises/2026-09-02-a2-gpo-surface-and-domain-root-link`.
- Verify a cmdlet's accepted input before you reuse an assumption from its counterpart.

## Graph Explorer and Entra

- A stale session token returns 403 on a scope that is already consented. Modify Permissions shows "Unconsent". Sign out and sign in. Do not re-consent.
- Sign-in logs (`GET /auditLogs/signIns`) need a paid tier. On Entra Free the call returns `Authentication_RequestFromNonPremiumTenantOrB2CTenant`. The call works while the P2 trial runs. `GET /me` as the user is the proven fallback on Free. Source: `exercises/2026-09-02-entra-connect-upn-signin-test`.
- The tenant's original Global Administrator is a Microsoft Account. Graph directory endpoints reject it. Use the current native Global Administrator, whose name Raymond supplies in session.
- `GET /auditLogs/signIns` on **v1.0** returns interactive user sign-ins and successful federated sign-ins only. Non-interactive events need `beta` with `$filter=signInEventTypes/any(t: t eq 'nonInteractiveUser')`. Source: `exercises/2026-09-05-b1-breakglass-exclusion-verification`.
- Use `beta` for any Conditional Access question. Only beta returns `conditionsSatisfied`, `conditionsNotSatisfied`, `includeRulesSatisfied`, and `excludeRulesSatisfied`. On v1.0 a `reportOnlyNotApplied` result names no cause, so an exclusion can only be inferred. Source: `exercises/2026-09-05-b1-breakglass-exclusion-verification`.
- Conditional Access evaluates the user condition before the client app type. An exclusion short-circuits evaluation, so a break-glass exclusion on a block-legacy-auth policy is verifiable from an ordinary browser sign-in. Source: `exercises/2026-09-05-b1-breakglass-exclusion-verification`.
- A failed sign-in returns `appliedConditionalAccessPolicies: []`. Credential validation precedes policy evaluation. Test an exclusion with a sign-in that succeeds. Source: `exercises/2026-09-05-b1-breakglass-exclusion-verification`.
- Desktop single sign-on issues tokens through the primary refresh token and lands in the non-interactive stream. A Windows client browsing to a cloud app produces no interactive log entry. Source: `exercises/2026-09-05-b1-breakglass-exclusion-verification`.
- Sign-in log writes lag. An empty read is not evidence. Re-read at a later time before concluding anything from nothing. Latency not measured. Source: `exercises/2026-09-05-b1-breakglass-exclusion-verification`.
- Documented, not lab-captured: sign-ins that obtain a refresh token with FIDO2 keys log as non-interactive since 2025-04-11. Relevant if phishing-resistant auth is built. Source: Microsoft Learn, "What are interactive user sign-ins in Microsoft Entra".
- An Entra-side password reset is not the operation for a synced account. Check `onPremisesSyncEnabled` first. Source: `exercises/2026-09-05-b1-breakglass-exclusion-verification`.

## Proxmox host

- The host clock runs America/Los_Angeles. `qm listsnapshot` prints local time. Derive names from `date -u`.
- The volume group has about 2 GiB free on one NVMe. `lvextend` on the thin pool has no room. Freed thin blocks return to the pool, not the volume group. Source: `exercises/2026-09-02-thin-pool-headroom-reclaim`.
- Do not add the spare SD card or USB stick as a physical volume in the `pve` group. A thin pool can span physical volumes, so one unplugged device can corrupt the whole pool. Use removable media as a `vzdump` target instead. Decision 2026-09-02.
- Docker inside an unprivileged LXC needs `lxc.apparmor.profile: unconfined`. `nesting=1,keyctl=1` alone is not enough. Source: `exercises/2026-09-03-vaultwarden-secrets-store`.
- `docker restart` does not re-read `--env-file`. Recreate the container to apply env changes. A bind-mounted Caddyfile is re-read on restart.
- A Caddy site block written as bare `:443` has no hostname for a certificate. Handshakes fail with `internal_error` and no log line.
