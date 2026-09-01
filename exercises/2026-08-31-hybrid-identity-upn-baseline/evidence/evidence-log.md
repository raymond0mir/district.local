# Evidence log

Capture path: `qm guest exec 100` from the Proxmox host shell (root@proxmox) for guest queries; direct host shell for the pre-flight. Pasted in by Raymond after running interactively.

| Evidence file | Command (verbatim) | Approx. time filed (UTC) |
|---|---|---|
| `proxmox-preflight-headroom.txt` | `qm status 100; lvs -a -o+lv_name,data_percent,metadata_percent,lv_size; free -h` (host shell) | ~2026-08-31T22:20Z |
| `forest-upn-suffixes-baseline.json` | `qm guest exec 100 --timeout 30 -- powershell.exe -Command "Get-ADForest \| Select-Object Name,ForestMode,UPNSuffixes,DomainNamingMaster,SchemaMaster \| ConvertTo-Json"` | ~2026-08-31T22:20Z |
| `domain-identity-baseline.json` | `qm guest exec 100 --timeout 30 -- powershell.exe -Command "Get-ADDomain \| Select-Object Name,DNSRoot,NetBIOSName,DomainMode,PDCEmulator \| ConvertTo-Json"` | ~2026-08-31T22:20Z |
| `all-users-upn-state-baseline.json` | `qm guest exec 100 --timeout 30 -- powershell.exe -Command "Get-ADUser -Filter * -Properties UserPrincipalName,mail,proxyAddresses \| Select-Object SamAccountName,UserPrincipalName,mail,proxyAddresses \| ConvertTo-Json -Depth 4"` | ~2026-08-31T22:20Z |
| `dc01-entra-endpoint-reachability-failed.json` | `qm guest exec 100 --timeout 60 -- powershell.exe -Command "Test-NetConnection -ComputerName login.microsoftonline.com -Port 443 \| Select-Object ComputerName,RemoteAddress,TcpTestSucceeded,PingSucceeded \| ConvertTo-Json"` | ~2026-08-31T22:20Z |

Note on timestamps: pasted in by Raymond after running interactively; the time above is when Claude filed the evidence, not a per-command server-side clock reading. Same methodology as every prior exercise's log.

**Note on `dc01-entra-endpoint-reachability-failed.json` — exit code 0 does not mean success here.** `Test-NetConnection` returns exit code `0` even when the connectivity test fails; the failure is reported *in the payload* (`TcpTestSucceeded: false`, `PingSucceeded: false`) and in a `WARNING:` line, not in the exit code. Every prior exercise in this series has leaned on the exit code as the trustworthy field. This is the first captured case where that rule would mislead if applied mechanically — filed deliberately as a counterexample to the series' own convention.

**Note on the same file — the paste was truncated by one character.** The pasted block ended after the `out-data` value's closing quote without the outer JSON's final `}`. All three fields that the guest-agent envelope produces for this command (`exitcode`, `exited`, `out-data`) are present and complete, and the `out-data` payload itself is intact through its trailing `\r\n"`, so nothing substantive is missing — but the file as reconstructed here has the closing brace restored by Claude rather than pasted. Flagged rather than silently repaired, per the truncated-paste incident in the constrained-admin-path exercise.

**Note on the WARNING line's stream.** The `WARNING: Name resolution ... failed` text arrived inside `out-data`, not `err-data`, and there is no `err-data` key on this capture at all. That is PowerShell's warning stream being folded into stdout by the guest-agent wrapper, not evidence that no warning was raised.

**Note on enum decoding.** `ForestMode: 7` and `DomainMode: 7` are raw enum ordinals, not text. `7` decodes to `Windows2016Forest` / `Windows2016Domain` against the standard `ADForestMode` / `ADDomainMode` enums. That decode is Claude's read of documented .NET enum values, **interpretation, not something the box printed as text** — same labeling as the ADWS `Status=4`/`StartType=2` decode in the constrained-admin-path exercise.

## Connectivity diagnosis, round 2 — the DNS-only hypothesis was wrong

| Evidence file | Command (verbatim) | Approx. time filed (UTC) |
|---|---|---|
| `dc01-dns-forwarder-ipv6-dead.json` | `qm guest exec 100 --timeout 30 -- powershell.exe -Command "Get-DnsServerForwarder \| ConvertTo-Json"` | ~2026-08-31T22:40Z |
| `dc01-dns-client-server-address.json` | `qm guest exec 100 --timeout 30 -- powershell.exe -Command "Get-DnsClientServerAddress -AddressFamily IPv4 \| Select-Object InterfaceAlias,ServerAddresses \| ConvertTo-Json"` | ~2026-08-31T22:40Z |
| `dc01-egress-to-1111-failed-host-unreachable.json` | `qm guest exec 100 --timeout 60 -- powershell.exe -Command "Test-NetConnection -ComputerName 1.1.1.1 -Port 443 \| Select-Object ComputerName,RemoteAddress,TcpTestSucceeded,PingSucceeded \| ConvertTo-Json"` | ~2026-08-31T22:40Z |

Note: `Get-DnsServerForwarder` was run twice by Raymond with byte-identical output both times, filed once — same handling as the duplicate `sg-admin-tier0-domain-lookup.json` run in the constrained-admin-path exercise.

**The working hypothesis going into this round — "pfSense egress is fine, DC01's DNS forwarder is the whole problem" — is falsified by this round's evidence, not confirmed.** Three findings:

1. `Get-DnsServerForwarder` shows the forwarder is not empty and not misconfigured to a wrong-but-routable address — it's a single **IPv6** address (`2600:6c50:5940:587:ea9f:80ff:fe81:22f7`). Nothing in this lab's documented network topology (an IPv4-only `10.0.0.0/24` bridge) suggests IPv6 has ever been routable here. If that holds, this forwarder has been dead since it was configured, independent of anything pfSense does.
2. `Get-DnsClientServerAddress` confirms DC01 points at itself (`10.0.0.10`) for DNS on its only real interface — expected, standard DC self-referential DNS, not itself a finding.
3. `Test-NetConnection -ComputerName 1.1.1.1 -Port 443` — a raw-IP test that bypasses DNS resolution entirely — also failed, and failed with `PingSucceeded: false, status: DestinationHostUnreachable`. That specific ICMP result is generated by the sender's own routing stack when it has no path to the destination, not typically what a remote firewall rejection produces. This points at DC01's own default-gateway or routing configuration, a layer more basic than DNS and one this exercise had not checked yet.

**Not concluded from this data alone: whether DC01 truly has no default gateway, or has one that's misconfigured, or whether pfSense itself is the actual blocker one hop further out.** `DestinationHostUnreachable` is suggestive of a local routing gap but is not definitive proof without also checking DC01's actual gateway configuration and testing the single hop to pfSense's LAN interface directly. Next round of diagnostics targets exactly that, before any conclusion is written up.

## Connectivity diagnosis, round 3 — root cause found

| Evidence file | Command (verbatim) | Approx. time filed (UTC) |
|---|---|---|
| `dc01-net-ip-configuration-full.json` | `qm guest exec 100 --timeout 30 -- powershell.exe -Command "Get-NetIPConfiguration \| Select-Object InterfaceAlias,IPv4Address,IPv4DefaultGateway \| ConvertTo-Json -Depth 4"` | ~2026-08-31T22:55Z |
| `dc01-gateway-to-101-ping-success.json` | `qm guest exec 100 --timeout 30 -- powershell.exe -Command "Test-Connection -ComputerName 10.0.0.1 -Count 2 \| Select-Object Address,StatusCode,ResponseTime \| ConvertTo-Json"` | ~2026-08-31T22:55Z |
| `dc01-default-route-wrong-gateway.json` | `qm guest exec 100 --timeout 30 -- powershell.exe -Command "Get-NetRoute -DestinationPrefix '0.0.0.0/0' \| Select-Object DestinationPrefix,NextHop,InterfaceAlias,RouteMetric \| ConvertTo-Json"` | ~2026-08-31T22:55Z |

**Filing note on `dc01-net-ip-configuration-full.json`: not verbatim.** The raw pasted output for this one command ran to roughly 250 lines, almost all of it repeated `MSFT_NetIPAddress`/`MSFT_NetRoute` CIM class metadata (property lists, qualifiers, method signatures) that PowerShell's default `ConvertTo-Json` serialization includes around every object when the underlying type is a CIM instance rather than a plain object. The four load-bearing values — `IPv4Address: 10.0.0.10`, `PrefixLength: 24`, `NextHop: 192.168.1.1`, `RouteMetric: 256` — are copied unedited from that output; the surrounding CIM plumbing was stripped for legibility. This is the first capture in this series where the raw paste was trimmed rather than filed whole, and it's flagged here rather than silently presented as a verbatim capture, per the capture contract's own standard. The full untrimmed paste exists in the session transcript but is not separately filed.

**Root cause identified.** `DC01`'s default route sends `0.0.0.0/0` traffic to next-hop `192.168.1.1` — the home network's gateway address (`vmbr0`, per the inherited BloodHound write-up), not `10.0.0.1` (pfSense's LAN interface on the lab's own `vmbr1`/`10.0.0.0/24` bridge, which DC01 actually sits on). `192.168.1.1` is not on `10.0.0.10/24`'s subnet at all — Windows cannot ARP for a next-hop outside the local subnet, so every off-subnet packet from DC01 has had nowhere to go, independent of anything pfSense's firewall does or doesn't permit. This fully explains the `DestinationHostUnreachable` result against `1.1.1.1` from round 2: the failure was generated by DC01 itself, before the packet could ever reach pfSense.

**The direct hop to pfSense's actual LAN address works.** `Test-Connection -ComputerName 10.0.0.1` succeeded twice, 0ms response, `StatusCode: 0` — confirming pfSense's LAN interface is live and reachable on the local subnet. The break is specifically and only the gateway pointing at the wrong address, not a broken link to pfSense, not (as far as this diagnosis goes) a pfSense firewall rule.

**Untested implication, not yet run:** DC01's DNS forwarder configuration includes `UseRootHint: true` (see `dc01-dns-forwarder-ipv6-dead.json`, round 2). If the gateway is corrected to `10.0.0.1`, DC01 may recover full external name resolution via root-hint queries directly to the public root server system, without the dead IPv6 forwarder needing to be touched at all. This is a hypothesis to test after the gateway fix, not a conclusion.

## Remediation: default-route fix, and the root-hints hypothesis falsified

Raymond ran the fix directly (see report's Where Raymond was consulted). Four commands, `qm guest exec 100`:

| Evidence file | Command (verbatim) |
|---|---|
| `dc01-gateway-removal-old-route.json` | `qm guest exec 100 --timeout 30 -- powershell.exe -Command "Remove-NetRoute -DestinationPrefix '0.0.0.0/0' -NextHop '192.168.1.1' -Confirm:\$false"` |
| `dc01-gateway-new-route-added.json` | `qm guest exec 100 --timeout 30 -- powershell.exe -Command "New-NetRoute -DestinationPrefix '0.0.0.0/0' -NextHop '10.0.0.1' -InterfaceAlias 'Ethernet'"` |
| `dc01-egress-1111-success-after-gateway-fix.json` | `qm guest exec 100 --timeout 30 -- powershell.exe -Command "Test-NetConnection -ComputerName 1.1.1.1 -Port 443 \| Select-Object ComputerName,TcpTestSucceeded,PingSucceeded \| ConvertTo-Json"` |
| `dc01-dns-still-fails-after-gateway-fix.json` | `qm guest exec 100 --timeout 30 -- powershell.exe -Command "Resolve-DnsName -Name login.microsoftonline.com -Type A \| Select-Object Name,IPAddress \| ConvertTo-Json"` |

**Filing note on `dc01-gateway-new-route-added.json`: reformatted, not verbatim.** The raw terminal paste had the console table header (`Policy`, `Store`) wrapped character-by-character due to a narrow terminal width at capture time (e.g. `Po`/`li`/`cy` split across lines). The data rows and every value are unchanged; only the header's line-wrapping was normalized for legibility. Flagged per the same standard as the two other non-verbatim files this exercise.

**Result 1 — the gateway fix worked.** `Get-NetRoute` confirms `NextHop: 10.0.0.1` (already filed in round 3 as `dc01-default-route-wrong-gateway.json`'s counterpart-after-fix, not re-filed separately since it's identical to the verification query already run). `Test-NetConnection` to `1.1.1.1:443` now returns `TcpTestSucceeded: true` — DC01 has working raw IP egress for the first time in this exercise.

**Result 2 — `PingSucceeded: false` on the same test, unexplained and not chased.** TCP succeeded, ICMP echo did not, against the same target (`1.1.1.1`). Possible causes (pfSense blocking outbound ICMP while permitting TCP, Cloudflare's anycast dropping this specific echo, something else) are not distinguished here. Doesn't block anything downstream — TCP/443 is what Entra Connect and Graph actually need — but named rather than silently ignored.

**Result 3 — DNS resolution still fails, falsifying the round-3 hypothesis.** `Resolve-DnsName -Name login.microsoftonline.com` returns `RCODE_SERVER_FAILURE`, exit code `1`. The hypothesis that `UseRootHint: true` would let DC01 fall back to public root servers once the gateway was fixed **did not hold** — DNS is still fully broken. The dead IPv6 forwarder (or DC01's DNS service's handling of it) is an active blocker, not a configuration that gets silently bypassed. Next step: replace the forwarder with a reachable IPv4 address and retest — not yet run as of this filing.

## Remediation: forwarder replaced, full resolution confirmed

| Evidence file | Command (verbatim) |
|---|---|
| `dc01-forwarder-replaced-ipv4.json` | `qm guest exec 100 --timeout 30 -- powershell.exe -Command "Set-DnsServerForwarder -IPAddress 1.1.1.1,8.8.8.8 -PassThru \| ConvertTo-Json"` |
| `dc01-dns-resolution-restored.json` | `qm guest exec 100 --timeout 30 -- powershell.exe -Command "Resolve-DnsName -Name login.microsoftonline.com -Type A \| Select-Object Name,IPAddress \| ConvertTo-Json"` |

**Filing note on both files: trimmed / cleaned, not verbatim.**
- `dc01-forwarder-replaced-ipv4.json` — the raw paste was the same CIM-metadata-heavy shape as `dc01-dns-forwarder-ipv6-dead.json` in round 2. Trimmed to the five load-bearing fields for the same legibility reason, same standard applied.
- `dc01-dns-resolution-restored.json` — the raw paste had `www.tm.a.prd.aadg.akadns.net` wrapped in markdown link syntax (`[www.tm.a.prd.aadg.akadns.net\](https://www.tm.a.prd.aadg.akadns.net\)`), repeated across all six A-record rows that resolved to that CNAME target. `Resolve-DnsName`'s JSON output has no mechanism that produces markdown — this is paste/render-pipeline contamination introduced somewhere between the terminal and the message reaching this session, not something the box printed. The domain string and every IP address are otherwise unedited; only the markdown wrapper was stripped.

**Result: DNS resolution fully restored.** `login.microsoftonline.com` resolves through its real CNAME chain (`login.mso.msidentity.com` → `ak.privatelink.msidentity.com` → `www.tm.a.prd.aadg.akadns.net`) to eight live Microsoft/Akamai-fronted IPv4 addresses. This is the same hostname that failed at the very start of this exercise (`dc01-entra-endpoint-reachability-failed.json`, round 1) — the investigation is now closed on the same target it opened on.

**Two independent misconfigurations, both now fixed:** (1) DC01's default gateway pointed at the home network instead of pfSense's LAN interface — fixed via `Remove-NetRoute`/`New-NetRoute`. (2) DC01's DNS forwarder was a dead, unreachable IPv6 address — fixed via `Set-DnsServerForwarder`. Neither was the diode rule; pfSense was never the blocker at any point in this investigation.

## Tenant-side capture via Graph Explorer — MSA identity finding

Capture path change for this section: Microsoft Graph via the browser (Graph Explorer), signed in as `raytakosharky@gmail.com`, run by Raymond and pasted back — same paste-and-file discipline as every `qm guest exec` capture, different tool.

| Evidence file | Query (verbatim) | Result |
|---|---|---|
| `graph-me-msa-id-format.json` | `GET https://graph.microsoft.com/v1.0/me` | `200 OK` |
| `graph-organization-query-msa-blocked.json` | `GET https://graph.microsoft.com/v1.0/organization` | `400 BadRequest` |

**Filing note on `graph-me-msa-id-format.json`:** the same response was pasted three times before the actual four target queries were run — a UI mixup (see below), not three separate captures. Filed once.

**UI mixup, named rather than smoothed over:** the first three attempts at the target queries (`organization`, `directoryRoles`, `domains`, `users`) all returned the same unchanged `/me` response, because the query text was pasted into Graph Explorer's **Request Body** panel (for POST/PATCH payloads, ignored on a GET) rather than the actual URL field next to the `v1.0` dropdown. Caught via a screenshot showing the URL field still reading `.../v1.0/me` while the Request Body panel held the intended query text. Fixed once pointed at the correct field.

**Finding: the tenant's Global Administrator identity is an MSA (Microsoft Account), not a native Entra work/school account.** `GET /organization` — a basic, standard directory read — failed with `BadRequest`: *"This API is not supported for MSA accounts (no addressUrl for Microsoft.DirectoryServices,False)."* This is not a permissions/consent problem; it's the API refusing to treat this identity as a directory principal at all.

**This also explains an anomaly flagged two exchanges earlier and left unresolved at the time.** `graph-me-msa-id-format.json`'s `id` field is `27701766a4468e98` — 16 hex characters, no dashes. Real Entra/Azure AD object IDs are always full GUIDs (36 characters, dashed). At the time this was flagged as possibly a paste-truncation artifact; it is not. A short, dash-less ID in this shape is consistent with an MSA identifier, not a directory object ID. Two independent pieces of evidence (the malformed ID, and the explicit `BadRequest` naming "MSA accounts") now corroborate the same underlying fact.

**Why this matters beyond a failed query:** the October screenshot (informational, not filed as evidence per the capture contract) showed this identity as the tenant's sole Global Administrator, with no visible break-glass account. An MSA-backed Global Admin is a more fragile configuration than "single admin, no backup" alone — it means the tenant's top role is held by an account type some of Microsoft's own directory APIs partially refuse to treat as a first-class principal, as directly demonstrated here.

### Confirming the restriction is blanket, not endpoint-specific

| Evidence file | Query | Result | request-id |
|---|---|---|---|
| `graph-directoryroles-query-msa-blocked.json` | `GET /directoryRoles?$filter=displayName eq 'Global Administrator'` | `400 BadRequest`, same MSA message | `a34578aa-753c-40c2-a4f8-43a96e69571f` |
| `graph-domains-query-msa-blocked.json` | `GET /domains` | `400 BadRequest`, same MSA message | `e68573bb-92e8-4d68-936e-4ed23620c0a1` |
| `graph-users-query-first-attempt-malformed.json` | `GET /users?$select=...` (1st attempt) | Malformed — see below | `54f09da2-f055-4225-9a27-b7cf67cd51de` |
| `graph-users-query-msa-blocked-retry.json` | `GET /users?$select=...` (2nd attempt, identical query) | `400 BadRequest`, same MSA message | `db1820ae-1b62-47a3-a862-af85790cd808` |

All four `request-id` values are distinct, confirming four independent server-side calls rather than a cached or repeated response. **The restriction is blanket across basic directory reads for this identity** — `organization`, `directoryRoles`, `domains`, and (on retry) `users` all fail with the identical `BadRequest`/"not supported for MSA accounts" message.

### Remediation: break-glass Global Administrator created

Raymond's action, per his own direct request (not something I proposed unilaterally) — see report's Where Raymond was consulted. Account created through the Entra admin center UI directly, not Graph (account creation and password-setting are actions Claude does not perform — see the report). Two Graph captures verify the result:

| Evidence file | Query | Result |
|---|---|---|
| `graph-me-breakglass-account-clean.json` | `GET /me`, signed in as `breakglass@raytakosharkygmail.onmicrosoft.com` | `200 OK`, clean response, real GUID `id` |
| `breakglass-global-admin-role-confirmed.json` | `GET /me/memberOf`, same session | `200 OK` |

**Direct contrast with the MSA finding.** `breakglass`'s `GET /me` succeeds cleanly with `id: de938dc8-feb7-4140-9a01-8e32649b8fd6` — a proper 36-character dashed GUID, unlike the MSA identity's malformed 16-character `27701766a4468e98`. Same tenant, same query, structurally different identity type, structurally different result. This is the clean version of the same test that failed four ways for the MSA account.

**Role confirmed via `roleTemplateId`, not `displayName`.** The single object in `/me/memberOf` has `roleTemplateId: 62e90394-69f5-4237-9190-012177145e10` — the fixed, well-known template ID Microsoft documents for the built-in Global Administrator role (stable across every tenant; this is public, documented Microsoft reference data, not something derived from this session's own captures). **Labeled as interpretation, not raw box output**, same convention as the `ForestMode`/`DomainMode` enum decodes earlier in this exercise. One anomaly worth naming rather than smoothing over: this object's `displayName` came back `null` rather than `"Global Administrator"` — plausibly because the built-in role object is freshly instantiated in this tenant and hasn't had its display metadata populated yet, but that's inference, not confirmed.

**MFA registration: promoted from Recalled to Captured.** First attempt at `GET /me/authentication/methods` (`evidence/breakglass-mfa-check-scope-denied.json`) failed with `accessDenied`/"Request Authorization failed" — a scope-consent gap in Graph Explorer, not the MSA restriction and not evidence of anything wrong with the account itself; distinct error code from every prior failure in this exercise, correctly identified as such rather than lumped in with the MSA errors. After consenting to `UserAuthenticationMethod.Read` in Graph Explorer's Modify Permissions tab, the retry (`evidence/breakglass-mfa-confirmed.json`) succeeded: two methods on file, a `passwordAuthenticationMethod` and a `microsoftAuthenticatorAuthenticationMethod` (`displayName: "iPhone"`, `deviceTag: SoftwareTokenActivated`). Raymond's earlier statement ("yes mfa on my phone") is now independently corroborated by a real API response, not just standing as testimony.

**`/users`'s first attempt failed in a distinct, worse-shaped way, and that shape did not reproduce.** Instead of a clean top-level `error` object, the response was a `200`-shaped envelope — `@odata.context` and a `value` array, the normal signature of a successful list response — whose single array element was itself an error object: `{"error": {"code": "InternalServerError", "message": "Invalid response. Expected list response must have value property."}}`. That message is self-contradictory on its face (the response does have a `value` property); it reads as a downstream directory-services failure (the same underlying MSA cause) getting incorrectly wrapped by a Graph gateway layer instead of surfaced as a clean error. **The exact HTTP status banner for this first attempt was not confirmed** — Raymond was asked directly and the anomaly did not reproduce before an answer was given; a second, identical query returned a clean `400` instead. Logged as an intermittent failure mode, not a stable characteristic of the `/users` endpoint specifically — worth knowing this exists (a caller that trusts a 200-shaped envelope and blindly iterates `value` would mishandle this), but not reproducible on demand with the evidence gathered here.
