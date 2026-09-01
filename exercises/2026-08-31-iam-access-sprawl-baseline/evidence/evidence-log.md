# Evidence log

Capture path: `qm guest exec 100` from the Proxmox host shell (root@proxmox), virtio serial channel, pasted in by Raymond after running interactively.

| Evidence file | Command (verbatim) | Approx. time filed (UTC) |
|---|---|---|
| `all-users-memberof-enumeration.json` | `qm guest exec 100 --timeout 30 -- powershell.exe -Command "Get-ADUser -Filter * -Properties MemberOf,Enabled,whenCreated,LastLogonDate,adminCount \| Select-Object Name,SamAccountName,Enabled,whenCreated,LastLogonDate,adminCount,MemberOf \| ConvertTo-Json -Depth 4"` | ~2026-08-31T22:00Z |
| `all-groups-enumeration.json` | `qm guest exec 100 --timeout 30 -- powershell.exe -Command "Get-ADGroup -Filter * -Properties Description,whenCreated,GroupCategory,GroupScope \| Select-Object Name,Description,whenCreated,GroupCategory,GroupScope \| ConvertTo-Json -Depth 4"` | ~2026-08-31T22:00Z |

Note on timestamps: pasted in by Raymond after running interactively, same as every other exercise's evidence log — the time above is when Claude filed the evidence, not a per-command server-side clock reading.

Note on `whenCreated`/`LastLogonDate`: both fields serialize as .NET `/Date(<epoch-ms>)/` strings inside the JSON, not as plain timestamps. Every date cited in `report.md` was converted from the raw epoch-ms value with `date -u -r $((ms/1000))`, not eyeballed — the raw millisecond values are preserved as-is in the two evidence files above for anyone who wants to re-derive them.

Note on group count: `Get-ADGroup -Filter *` returned **55** groups (`python3 -c "import json; print(len(json.loads(json.load(open('all-groups-enumeration.json'))['out-data'])))"` against the filed evidence). The inherited BloodHound write-up (`~/Downloads/district-lab-bloodhound-writeup.md`, 2026-06-17 capstone session) states district.local has "59 groups." That's a 4-group discrepancy against an inherited, unverified figure — not reconciled in this exercise, flagged as-is in Open Questions rather than assumed to be either number's error.

## Remediation: revoking mlee and ajones's Site1 access

Raymond's call, made directly rather than inferred — see report's "Where Raymond was consulted." Four more commands, all `qm guest exec 100`, run 2026-08-31, filed ~22:11Z:

| Evidence file | Command (verbatim) |
|---|---|
| `mlee-removal-from-site1-rw.json` | `qm guest exec 100 --timeout 30 -- powershell.exe -Command "Remove-ADGroupMember -Identity 'SG_Share_Site1_RW' -Members 'mlee' -Confirm:\$false"` |
| `ajones-removal-from-site1-read.json` | `qm guest exec 100 --timeout 30 -- powershell.exe -Command "Remove-ADGroupMember -Identity 'SG_Share_Site1_Read' -Members 'ajones' -Confirm:\$false"` |
| `site1-rw-membership-post-removal.json` | `qm guest exec 100 --timeout 30 -- powershell.exe -Command "Get-ADGroupMember -Identity 'SG_Share_Site1_RW' \| Select-Object Name,SamAccountName,objectClass \| ConvertTo-Json"` |
| `site1-read-membership-post-removal.json` | `qm guest exec 100 --timeout 30 -- powershell.exe -Command "Get-ADGroupMember -Identity 'SG_Share_Site1_Read' \| Select-Object Name,SamAccountName,objectClass \| ConvertTo-Json"` |

Both removals used the pre-corrected `-Confirm:\$false` escaping from the start (exercise 1's attempt-1 quoting bug, applied as a lesson learned rather than re-discovered). Both succeeded on the first try, exit code `0`, no output — expected shape for a successful `Remove-ADGroupMember`, same as exercise 1's successful attempt.

**Gap, named rather than smoothed over:** the pre-flight infra check (`qm status 100`, `lvs`, `free -h`) specified in the skill's standing pre-flight step was requested before this remediation but was not run or pasted back. This exercise's own report is partly what's establishing that step as a norm, and it wasn't followed here. No indication anything was actually wrong with headroom — but "no indication of a problem" and "checked" are different claims, and only the second belongs in a report as fact. Filed as a **Recalled/skipped** gap, not asserted as checked.

No pre-change snapshot was taken for this remediation, unlike exercise 1's `sysadmin` removal — a deliberate call (see report), not an oversight, on the reasoning that reverting a file-share group membership is a one-line `Add-ADGroupMember` versus the lockout risk of removing an active admin credential.
