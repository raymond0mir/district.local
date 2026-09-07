# AD CS issuing CA build for Entra certificate-based authentication — evidence log

Exercise date derived from `date -u` on the Proxmox host: 2026-09-05T21:09:59Z.

## Captured

- **Host pre-flight state at 2026-09-05T21:09:59Z.** Thin pool `Data%` 69.96, metadata 3.53.
  Host memory 15Gi total, 8.4Gi available. VM 100 stopped, VM 101 running, VM 102 stopped,
  VM 104 running. `evidence/01-preflight-host-state.txt`.
- **Server 2022 Desktop Experience consumes about 18.62 GiB of real pool data on this host.**
  Derived from VM 102's 60G volume at 31.03%. Same file.
- **Container 106 (`rootca-offline`) exists, runs, and has no network interface.** Debian 12,
  unprivileged, 512 MB, 4 GB rootfs on `local-lvm`. `pct config 106` shows no `net0` line.
  OpenSSL 3.0.17 is present in the template, so the container needs no package install and no
  network to build a CA. Pool moved 69.96 to 70.37 percent. Container consumes 0.62 GiB of real
  pool data. `evidence/02-offline-root-container-created.txt`.

- **The root CA key and self-signed root certificate exist on container 106.** RSA 4096,
  SHA-256, valid 2026-09-05T21:16:21Z to 2036-09-02T21:16:21Z. Subject and issuer are both
  `O = district.local, CN = district.local Root CA`, so the certificate is self-signed. SHA-256
  fingerprint `DF:BC:F1:E6:25:09:E0:6B:77:3E:A1:00:DF:91:E4:37:04:DA:B1:F3:49:33:00:68:05:6D:9B:36:A2:63:43:1D`.
  The private key is mode 400, owner root, and has no passphrase.
  `evidence/03-root-ca-key-and-certificate.txt`.

- **The root certificate carries every extension the design requires.** `basicConstraints` is
  `critical, CA:TRUE, pathlen:1`, so the issuing CA below it may sign end-entity certificates.
  `keyUsage` is `critical, Certificate Sign, CRL Sign`. Subject Key Identifier and Authority Key
  Identifier are both `95:64:33:9E:6C:1A:7F:45:F5:C6:9D:1D:50:C0:78:F9:FF:06:BB:82`, equal
  because the certificate is self-signed. `openssl verify` returns `OK`. This closes the gap
  recorded in Corrections. `evidence/04-root-cert-extensions-and-vm-configs.txt`.
- **DC01 is configured with `ostype: l26`.** DC01 runs Windows Server 2022, and Proxmox has it
  typed as Linux 2.6+. VM 102, built later, is correctly typed `win11`. DC01 also still has
  `lab.iso` mounted at `ide2` and carries `localtime: 0` and `numa: 0`, none of which VM 102 has.
  Found while reading configs to mirror a known-good Windows build. Same file.

- **VM 107 (`ca01`) exists and runs.** 2048 MB, 2 cores, OVMF, `machine pc-q35-10.0`,
  `ostype win11`, 60G SCSI volume with iothread, virtio NIC on `vmbr1` with the Proxmox firewall
  flag set, guest agent enabled, both the Server 2022 evaluation ISO and
  `virtio-win-0.1.285.iso` attached. Config mirrors VM 102, not DC01. Pool 70.47 percent. The 60G
  volume reads 0.00 percent, so Windows has written nothing yet. Host memory 8.2Gi available with
  VMs 101, 104 and 107 running. `evidence/05-issuing-ca-vm-created.txt`.

- **Windows Server 2022 Standard Evaluation is installed on VM 107, and the guest agent
  answers.** Version 10.0.20348, 64-bit, installed 2026-09-05T21:27:26Z. `qm agent 107 ping`
  returned exit 0 after two prior attempts returned "QEMU guest agent is not running", so the
  agent starts several minutes after the desktop is usable. `evidence/06-ca01-post-install-state.txt`.
- **A fresh install from this media starts in OOB Grace with about 10 days, not a 180-day
  evaluation.** `LicenseStatus` 2, `GracePeriodRemaining` 14396 minutes, which is 9.99 days and
  expires about 2026-09-15. This is the same 10-day figure DC01 reached after `slmgr /rearm`, not
  the 180-day evaluation period the media implies. Same file.
- **VM 107 has no usable IP address.** `Get-NetIPAddress` returns 169.254.57.194 with
  `PrefixOrigin` 2, which is APIPA. The lab subnet serves no DHCP to this interface. VM 102
  (10.0.0.11) and container 103 (10.0.0.20) are both static, so static addressing is the lab's
  convention. Same file.
- **The Windows install consumed 9.56 GiB of real pool data, not the 18.62 GiB predicted.** The
  60G volume reads 15.94 percent. Pool is 76.63 percent, or 118.95 GiB of 155.23 GiB. Headroom to
  the 85 percent gate is about 13.0 GiB. Same file.

- **VM 107 holds a static address, DC01 as its resolver, and a pending rename to CA01.**
  `New-NetIPAddress` returned 10.0.0.12/24, `Set-DnsClientServerAddress` set 10.0.0.10, and
  `Rename-Computer` returned `HasSucceeded: true` with `OldComputerName WIN-7BF20JAR8KR` and
  `NewComputerName CA01`, plus Windows' own warning that the change needs a restart. The restart
  was issued. `evidence/07-ca01-network-and-rename.txt`.

- **The rename took effect and the addressing is clean.** After the restart,
  `Win32_ComputerSystem` returns `Name: CA01`, still `PartOfDomain: false`. Exactly one IPv4
  address is bound, 10.0.0.12/24, `PrefixOrigin: 1` meaning manual. The APIPA address is gone, so
  the duplicate entry `New-NetIPAddress` printed was an artefact of its own return value, not two
  bound addresses. VM 101 confirmed stopped before DC01 was started.
  `evidence/08-ca01-verified-dc01-started.txt`.

- **DC01 is serving, and 10.0.0.10 is confirmed as DC01 by a live read.** ADWS, DNS, Netlogon
  and NTDS all return `Status: 4`, meaning Running. `Win32_ComputerSystem` returns `Name: DC01`
  with the single address 10.0.0.10, which confirms the figure previously derived from older
  evidence files. From CA01, `nltest /dsgetdc:district.local` returns
  `DC01.district.local`, `10.0.0.10`, forest `district.local`, flags including
  `PDC GC DS LDAP KDC WRITABLE`, and TCP 389 succeeds.
  `evidence/09-dc01-reachable-and-temp-account-created.txt`.
- **`tmp-cainstall` exists on DC01, enabled, in Enterprise Admins only.** Not Domain Admins. Its
  description names the exercise and its deletion condition. The generated password was redacted
  before the output was pasted, so the value never entered the session. Same file.

- **CA01 is domain-joined and its secure channel verifies.** `PartOfDomain: true`,
  `Domain: district.local`. `nltest /sc_verify:district.local` returns `NERR_Success` for both
  the DC connection and the trust, against `DC01.district.local`. The object exists at
  `CN=CA01,CN=Computers,DC=district,DC=local`, created 2026-09-05T21:57:20Z, with
  `OperatingSystem: Windows Server 2022 Standard Evaluation`. The join ran at CA01's console as
  `DISTRICT\tmp-cainstall`. `evidence/10-ca01-joined-and-adcs-role-installed.txt`.
- **The temp account holds local administrator rights on CA01 only.** CA01's local
  Administrators group contains `CA01\Administrator`, `DISTRICT\Domain Admins` and
  `DISTRICT\tmp-cainstall`. The account is not in Domain Admins, so this grant is scoped to one
  machine. Same file.
- **The AD CS role binaries are installed.** `Install-WindowsFeature ADCS-Cert-Authority
  -IncludeManagementTools` returned `Success: true`, `ExitCode: 0`. The role install needed no
  Enterprise Admins rights; it ran through `qm guest exec` as SYSTEM. Only the configuration step
  requires the forest-level write. Same file.

- **A valid pre-change rollback point exists for CA01.** `pre-adcs-config`, taken
  2026-09-05T22:02:01Z, covering `drive-scsi0` and `drive-efidisk0`. Disk only, no vmstate.
  Same file.
- **No reboot was pending on CA01 after the role install.** Both the Component Based Servicing
  and Windows Update pending-reboot keys return false. `Install-WindowsFeature` had reported
  `RestartNeeded: 1`, and whatever that enum value means, no restart was actually required.
  Same file.


### Session 2, resumed 2026-09-05T23:55Z

- **Resume pre-flight at 2026-09-05T23:55:32Z.** Thin pool `Data%` 78.42, metadata 3.84, under
  the 85 percent gate with about 10.2 GiB of margin. Host memory 6.6Gi available. VM 100, VM 107
  and container 106 all running. `evidence/18-resume-preflight-and-orphan-identity.txt`.
- **`tmp-cainstall` is out of Enterprise Admins.** `Groups` is empty and `PrimaryGroupID` is 513,
  Domain Users. The account stays enabled and keeps local administrator rights on CA01 through a
  machine-local group. `evidence/19-tmp-cainstall-removed-from-enterprise-admins.txt`.
- **Enterprise Admins now holds exactly one member, and that member is disabled.**
  `Get-ADGroupMember 'Enterprise Admins'` returns `Administrator` alone, and
  `Get-ADUser Administrator` returns `Enabled: false`. No enabled account holds Enterprise Admins
  in `district.local`. The removal ran as SYSTEM through `qm guest exec` on DC01, so the same path
  can re-add the account without an interactive Enterprise Admins logon. Same file.
- **`SetupStatus` 525 decoded by `certutil` itself.** `certutil -getreg CA\SetupStatus` prints
  `SETUP_SERVER_FLAG -- 1`, `SETUP_SUSPEND_FLAG -- 4`, `SETUP_REQUEST_FLAG -- 8`,
  `SETUP_UPDATE_CAOBJECT_SVRTYPE -- 200 (512)`. The CA is installed, suspended, holding a pending
  request, and needs its AD object updated. Captured from the tool, not decoded by Claude.
- **`RequestFileName` is `C:\ca01%4.req`.** `%4` is the certificate index token, empty for a
  first certificate, so it expands to `C:\ca01.req`, the file on disk. This supports the earlier
  correction that event 27's doubled extension is a message artefact.
- **`certutil -installcert` blocks on an established LDAP connection to DC01.** Pid 4864 holds
  `10.0.0.12:57664 -> 10.0.0.10:389`, `State 5`, which is Established, with 0.046875 seconds of
  CPU across 5 threads. The process is blocked on a wait, not computing, and not drawing a dialog.
  `evidence/20-installcert-blocked-on-established-ldap-to-dc01.txt`.
- **The hang reproduces against a clean machine and without a shell wrapper.** Every orphan from
  the two earlier attempts was killed first, and the retry ran `certutil.exe` directly rather than
  through `cmd.exe`. It hung identically. Locks from earlier attempts are ruled out. Same file.
- **LDAP bind and read from CA01 as `CA01$` succeed.** An ADSI read of
  `CN=Public Key Services,CN=Services,CN=Configuration,DC=district,DC=local` returns all seven
  child containers: AIA, CDP, Certificate Templates, Certification Authorities, Enrollment
  Services, KRA, OID. `evidence/21-ca01-ldap-read-succeeds-write-denied.txt`.
- **LDAP write from CA01 as `CA01$` is denied, and denied fast.**
  `certutil -dspublish -f C:\ca01.cer SubCA` returns exit `-2147024891`, which is `0x80070005`,
  with `LDAP_INSUFFICIENT_RIGHTS: 00000005: SecErr: DSID-03152E29, problem 4003`. It returned in
  under a second. Same file.
- **No object for the issuing CA exists in AD.** A subtree search of Public Key Services for
  `*Issuing CA*` or `*Root CA*` returns only the offline root, twice, in
  `CN=Certification Authorities` and `CN=AIA`. No Enrollment Services object exists for CA01.
  Same file.
- **Clock skew and LDAP signing are both ruled out.** CA01 and DC01 differ by 1.69 s across two
  sequential reads, which bounds skew well inside Kerberos tolerance. DC01 sets
  `LDAPServerIntegrity 2` and `LdapEnforceChannelBinding 2`, and the signed ADSI read above
  succeeds against both. DC01's ADWS, DNS and NTDS were all Running at the time of the test.
  Same file.
### Session 3, resumed 2026-09-07

- **`tmp-cainstall`'s password was reset for console access.** `PasswordLastSet` moved from
  2026-09-05's account-creation value to 2026-09-07T13:52:14Z. Account stayed enabled and
  unlocked. The value was redacted before pasting and saved to the lab's Vaultwarden instance.
  `evidence/22-tmp-cainstall-password-reset-for-console-access.txt`.
- **The 2026-09-05 hang is resolved. It was a modal dialog, not a rights-driven retry.** Run
  interactively at CA01's console, `-installcert` raised "Cannot verify certificate chain,"
  `CRYPT_E_NO_REVOCATION_CHECK`, a direct consequence of the no-CRL decision. Dismissing it let
  the command return in seconds. `qm guest exec`'s session 0 has no desktop to render this
  dialog in, which is why it hung indefinitely there. `evidence/23`.
- **`tmp-cainstall`, logged on interactively with only local administrator on CA01, gets the
  same `0x80070005 ERROR_ACCESS_DENIED` that `CA01$` got.** Local administrator on the CA
  machine does not reach the AD write `-installcert` needs. Only a forest-level grant does.
  `SetupStatus` stayed at 525 after this attempt, unchanged from 2026-09-05. `evidence/23`.
- **`-installcert` succeeded once `tmp-cainstall` held Enterprise Admins again.**
  `SetupStatus` moved from 525 to 769: `SETUP_SUSPEND_FLAG` and `SETUP_REQUEST_FLAG` cleared,
  `SETUP_FORCECRL_FLAG` appeared. `CertSvc` started clean, `Status: 4` (Running).
  `evidence/24-installcert-succeeds-with-enterprise-admins.txt`.
- **The issuing CA is live and published in AD.** `certutil -ping` answers in 16ms. An
  Enrollment Services object named "district.local Issuing CA" now exists under
  `CN=Public Key Services,CN=Services,CN=Configuration` — evidence/09 found none there on
  2026-09-05. `evidence/25-ca-confirmed-live-published-and-enterprise-admins-cleanup.txt`.
- **Enterprise Admins cleanup and second rotation, same session.** `tmp-cainstall` removed from
  Enterprise Admins; the group holds only the disabled `Administrator` again. Its password was
  rotated a second time, invalidating the console-access password from earlier in this session.
  Same evidence file.
- **A client-authentication certificate template exists, scoped correctly.** Duplicated from
  "User," EKU trimmed to Client Authentication only (`1.3.6.1.5.5.7.3.2`), Subject built from AD
  with UPN in the alternate subject name. A new group, `PKI-CBA-Pilot`, holds the
  Certificate-Enrollment extended right; `jsmith` is its only member. All confirmed by direct
  LDAP read of the template object and its `nTSecurityDescriptor`, not from the console screen.
  Group creation is in `evidence/24`; template state is `evidence/28`.
- **A revoked Enterprise Admins grant stayed live in an open session for at least 22 minutes.**
  `tmp-cainstall` created and fully controlled the new template object while holding no
  Enterprise Admins in AD — the console session's Kerberos ticket, issued before the removal,
  still carried the group SID. `whoami /groups` proved it present, then absent after a fresh
  logon. The templates container's own ACL rules out a default-permissions gap: only SYSTEM,
  Enterprise Admins, and Domain Admins can create children there. `evidence/26`, `evidence/27`.

## Not captured, and why

- **`InstallState: 1` is an unresolved enum, exactly like `RestartNeeded: 1`.**
  `ConvertTo-Json` renders the enum as an integer and Claude will not guess the mapping. The role
  is known installed from other evidence, not from this value. Re-read it as a string.
- **The AD CS configuration result is Recalled, not Captured.** It exists only as a screenshot of
  CA01's console, transcribed in `evidence/11-adcs-configuration-console-recalled.md`. The
  `Install-AdcsCertificationAuthority` run reported `ErrorId 398`, the documented
  "installation is incomplete" result for a subordinate CA awaiting its issuer certificate, and
  `0x0 (WIN32: 0)`. A first attempt failed with `MissingMandatoryParameter` because the
  `Get-Credential` dialog was dismissed. Re-read through the guest agent before any of this is
  cited.

- ISO inventory and the next free VMID. The pasted command stopped at `free -h`. The ISO and
  `pvesh get /cluster/nextid` sections did not run.
- **Resolved.** A Server 2022 evaluation build does repeat the licence pattern, and the captured
  figure is sharper than the prediction: 10 days of OOB Grace, not a 180-day evaluation. See
  Captured.
- Whether pre-staging AD CS objects removes the Enterprise Admins requirement at install.
  Claude raised this option and could not support it. It stays out of the plan.
- **The root certificate's X509v3 extensions.** Claude piped the inspection through
  `sed -n '1,32p'`. The 4096-bit modulus fills those lines, so the output stops before the
  extensions block. `basicConstraints`, `keyUsage`, `subjectKeyIdentifier` and
  `authorityKeyIdentifier` were requested in the config and are unverified in output. Re-read
  before the root certificate is trusted anywhere.

## Where Raymond was consulted

1. **Revocation.** Question: publish a CRL through a public HTTP endpoint, or register the CA in
   Entra with no CRL and lose revocation. Claude recommended no public endpoint. Raymond chose
   Option A, no CRL. Consequence: revocation will not work, and Entra will not block
   authentication with a revoked certificate. This becomes a captured finding and an exposure row.
2. **Placement.** Question: new VM, VM 102, or DC01. Claude recommended a new VM and rejected
   DC01. Raymond chose a new VM.
3. **Windows install type.** Question: Server Core or Desktop Experience for the issuing CA.
   Claude leaned Desktop Experience, because certificate template management needs a GUI and
   DC01 has no console login path. Raymond chose Desktop Experience.
4. **DC01 memory.** Question: reduce the untested 10000 MB allocation to make room. Raymond
   decided to leave DC01 at 10000 MB. Consequence: VM 101 must be stopped before the issuing CA
   and DC01 run together.
6. **Root key passphrase.** Question: protect the root private key with a passphrase stored in
   Vaultwarden, or leave it unprotected inside an offline container. Claude recommended no
   passphrase and named the tradeoff: anyone with host root can start the container and read the
   key. Raymond chose no passphrase.
5. **Enterprise Admins on a member server.** Question: accept the tier-rule violation for the
   AD CS install window, or build a standalone CA and lose autoenrollment. Raymond chose to
   accept it and rotate the account password afterward. The rotation is now a required step of
   this exercise, not an optional one.


7. **The standing Enterprise Admins grant.** Question: delete `tmp-cainstall` now, remove it from
   Enterprise Admins and re-add only when a step proves it needs the forest write, or leave it.
   Claude recommended the middle option. Raymond said "remove tmp-cainstall from Enterprise
   Admins". Consequence: Enterprise Admins now has no enabled member, and the next install attempt
   became the test of which operation actually needs the grant.

8. **PIM-style activation for the Enterprise Admins grant, 2026-09-07.** Raymond asked whether a
   real org would activate-and-log this kind of grant instead of a manual add/remove. Claude laid
   out two paths: finish today with the plain add/-installcert/remove/rotate sequence already
   accepted on 2026-09-05, or detour to confirm AD Recycle Bin's state and consider enabling it to
   use native expiring group membership (`Add-ADGroupMember -MemberTimeToLive`), which Entra PIM
   for Groups cannot reach here since none of this tenant's synced groups are role-assignable
   (EXPOSURES.md). Raymond chose to finish C2 today. The expiring-membership option and the
   Recycle Bin prerequisite are unexplored, named here for a future exercise.

9. **Client-auth template scope, 2026-09-07.** Two questions: keep or trim the inherited
   Encrypting File System and Secure Email EKUs, and grant Enroll broadly (Domain Users /
   Authenticated Users) or narrowly. Claude recommended trimming to Client Authentication only
   (no Key Recovery Agent exists for this CA, so an EFS-capable cert with no key archival is a
   latent data-loss risk) and building a scoped group, `PKI-CBA-Pilot`, rather than a
   wholesale-group Enroll grant, naming it the fix side of the permission-sprawl thesis rather
   than only the finding side. Raymond said "lets go." Both landed as designed; see
   `evidence/28`.
## Corrections

- **Claude's LDAP query for the new template guessed `cn` equals `displayName`. Wrong.**
  `Get-ADObject` returned "Directory object not found" for
  `CN=district.local Client Authentication,...`. AD CS strips spaces and periods from a display
  name to generate the object's `cn`; the actual value is `district.localClientAuthentication`.
  Corrected by searching on `displayName` instead. `evidence/28`.
- **Claude's first password-reset command failed on bash quoting, not PowerShell.** The
  `-Command` argument was wrapped in bash double quotes, so bash expanded `$p` and `$_` as its
  own empty variables before PowerShell ever ran. Exit code 1, no AD write happened. Retried
  with the PowerShell command single-quoted at the bash level. `evidence/22`.

- **Claude's stdin-prompt explanation for the `certutil -installcert` hang was wrong.** Claude
  attributed the hang to the recorded no-TTY behaviour and predicted that redirecting stdin from
  `NUL` would make any prompt fail fast. The command hung again and orphaned a second process,
  pid 2996. The no-TTY explanation is disproven for this command. The real cause is unknown.
  `evidence/17-installcert-hangs-with-stdin-closed.txt`.
- **Claude's key-mismatch theory for event 27 was wrong.** Claude suggested a separate
  `C:\ca01.req.req` might exist, holding a request for a different key than the certificate we
  signed. A directory listing of `C:\` returns only `ca01.req`, `ca01.cer` and `root.cer`. No
  second request file exists. The doubled extension in event 27 is a message artefact. Same
  file.

- **Claude wrongly claimed the pre-change snapshot was never taken. Retracted.** The claim was
  written from the order the outputs arrived in the session, not from timestamps. The host block
  ran at 2026-09-05T22:02:01Z and the console configuration at about 22:08Z, so
  `pre-adcs-config` predates the change by roughly six minutes and is a valid rollback point.
  `qm listsnapshot 107` confirms it exists.
  `evidence/12-snapshot-and-feature-state.txt`.

- **Claude misread a redacted password line as a failed password generation.** The output showed
  `"PASSWORD \r\n"`. Claude concluded the generator had produced an empty string and that an
  enabled Enterprise Admins account with an unknown credential existed in the domain. Raymond had
  simply removed the secret before pasting, which is what the instruction asked for. No
  remediation was needed and none was performed. The wrong claim was retracted in the same
  session, before any action followed from it.

- **The machine is not named CA01.** Raymond reported "CA01 is up". `hostname` returns
  `WIN-7BF20JAR8KR`, and `Win32_ComputerSystem` agrees. The rename step was not applied during
  setup. Caught before the domain join, which would have written the wrong name into AD.
- **Claude's pool prediction was wrong by 6 points.** Claude predicted about 82 percent after the
  install, extrapolating from VM 102's 18.62 GiB. The actual figure is 76.63 percent, because
  VM 102's volume also carries Entra Connect and its update history. The error was conservative,
  and the gate never came close, but the prediction was stated too confidently.

- **Claude's two-tier recommendation did not fit the pool gate, and was wrong when written.**
  The prior turn recommended an offline Windows root CA plus a Windows issuing CA. Two Server
  2022 Desktop installs cost about 37 GiB of real pool data. Headroom under the 85% gate is
  23.35 GiB. The plan exceeded the gate before the second install finished. Corrected in session,
  before any VM was created.
- **Claude truncated its own verification and had to say so.** The root certificate inspection
  was piped through `sed -n '1,32p'`, which cut the output before the extensions block. The
  command proved the certificate exists and is self-signed. It did not prove the extensions the
  design depends on. Recorded as not captured rather than assumed.
- **Carryover's Lab state block is stale.** It records VMs 100, 101 and 102 stopped at
  2026-09-05T19:16:42Z, and pool `Data%` 66.28 at 18:45:01Z. Pre-flight at 21:09:59Z shows VM 101
  running and `Data%` 69.96. The rise is 3.68 points in under three hours.


### Session 2

- **Claude wrote "there is one hung attempt to explain, not two." That was wrong.** Claude read
  only two PIDs, saw `cmd` and `conhost`, and concluded the first attempt had been cleared. A
  full process read found both attempts' `certutil` processes still alive: pid 1032 from
  22:17:37Z and pid 3412 from 22:29:23Z, both session 0. Retracted the same session.
  `evidence/18-resume-preflight-and-orphan-identity.txt` and the process read that followed.
- **`Stop-Process` on the PID that `qm guest exec` returns kills the shell, not the work.** The
  guest agent returns the PID of the process it launched, which was `cmd.exe`. Killing it left
  `certutil` running and orphaned. This happened twice before it was noticed. The fix is to
  invoke the target binary directly through the guest agent, with no `cmd.exe` wrapper.
- **Windows reused PID 3628, and Claude read the reuse as continuity.** Old pid 3628 was `cmd`
  started 22:17:37Z. Current pid 3628 is `conhost` started 22:29:23Z. Claude compared PIDs across
  sessions without comparing start times first. Decoding `StartTime` resolved it.
- **Claude misnamed `SetupStatus` bit `0x200` as "DCOM security updated".** `certutil -getreg`
  names it `SETUP_UPDATE_CAOBJECT_SVRTYPE`. The other three bits Claude named were right. The
  claim was flagged as Claude's own reading before it was checked, and the check corrected it.
- **Claude's session-0 dialog theory for the hang is disproven.** Claude carried it as the
  leading explanation for three turns. Against it: `certutil -addstore` on CA01 and
  `certutil -dspublish` on DC01 both ran to exit 0 in the same session-0 context, both
  `certutil` processes reported an empty `MainWindowTitle`, and the blocked process holds an
  established LDAP socket. The empty `MainWindowTitle` was visible in the first process read and
  should have weakened the theory a turn earlier than it did.
- **`evidence/09` cited a report.md that has never existed.** Its note read "its full syntax is
  in report.md with the generator intact." No report has been written for this exercise, so the
  citation pointed at nothing, and a reader following it would have found the account-creation
  syntax nowhere. Corrected in the file 2026-09-06 to say what is true: the full syntax is not
  captured in this repo and exists only in session scrollback, which is Recalled. Caught while
  running the credential scan over the exercise directory, which had never been scanned because
  it had never been tracked.
- **Redirecting a hung process's output to a file yielded nothing.** `Start-Process` with
  `-RedirectStandardOutput` produced a zero-byte file after 40 seconds, because the C runtime
  block-buffers a redirected handle. Claude flagged the risk before running it. Recorded as a
  failed technique, not as a result.
## Open questions

- **What `RestartNeeded: 1` and `InstallState: 1` mean.** Both are enums rendered as integers.
  The practical question behind the first is answered: no reboot was pending. The enum mappings
  themselves are still unresolved, and no claim in this exercise rests on them.
- **Where CA01 belongs in the OU structure.** `Add-Computer` placed it in the default
  `CN=Computers` container. VM 102 was deliberately moved into `OU=Servers/OU=Application
  Servers` during A2 so it would keep receiving `Secure Admin WS`. CA01 receives no such policy
  where it sits. Not moved. Raymond's decision.

- **LVM's own thin-volume sum disagrees with the ledger's overcommit figure.** The create warning
  printed 409.01 GiB before the 60G volume and 469.01 GiB after. `verified-claims.md` records
  505.02 GiB of thin allocation, measured 2026-09-02. Subtracting this exercise's roughly 64 GiB
  leaves about 405 GiB before today, not 505 GiB. The two figures may count snapshots
  differently. Neither is retired here. Re-derive before either is cited again.

- What caused the 3.68-point pool rise between 18:45:01Z and 21:09:59Z. VM 101 running is the
  obvious candidate. It is not captured.
- Whether Server Core is available in the ISO store, and what a Core install actually consumes
  on this host. No lab figure exists for Core.
- Whether Entra CBA itself is gated by licence tier, separate from the Conditional Access policy
  that would consume it.
- **CA01's licence grace expires about 2026-09-15.** Decide whether to rearm, activate, or accept
  that the CA stops within ten days. Not decided.
- What `ostype: l26` has actually cost DC01. The setting suppresses the Hyper-V enlightenments
  Proxmox applies to `win*` guests. Whether it contributed to any observed DC01 behaviour, the
  crashes included, is unknown and is not claimed here. Correcting it needs a DC01 shutdown and
  its own exercise.


- **Resolved 2026-09-07.** Why a denied write becomes an indefinite block inside `-installcert`
  under `qm guest exec`: it doesn't. The block was a revocation-check dialog with no desktop to
  render it in. A plain rights denial, tested at the console as `tmp-cainstall`, returns in
  seconds like `-dspublish` always did. See `evidence/23`.
- **Unresolved.** CA01's local `Administrator` password still does not work. Not investigated
  further, since `tmp-cainstall` provided a working console path instead.
- **Why `jsmith` cannot enroll from `district.local Client Authentication`, 2026-09-07.** Every
  permission layer checked out correct: the template's EKU and ACL by direct LDAP read
  (`evidence/28`), the CA's own Security tab (Authenticated Users holds Request Certificates),
  `jsmith`'s live token (carries `PKI-CBA-Pilot`, confirmed by `whoami /groups`), and RPC
  reachability (`certutil -ping` succeeds as `jsmith`). Ruled out: a CertSvc restart mid-flap
  (confirmed stable well before the last two attempts, via the Application log), and a stale
  local enrollment-policy cache (cleared, retried, same result). The console UI's exact message —
  "a valid certification authority (CA) configured to issue certificates based on this template
  cannot be located, or the CA does not support this operation" — differs from the plain
  template-permission message shown for other unavailable templates in the same list (e.g.
  "Domain Controller"), suggesting the client's CA-to-template compatibility match is failing,
  not a rights check. Leading unverified hypothesis: the template's Compatibility setting
  (Certification Authority: Windows Server 2016, schema version 4) doesn't match something this
  CA actually supports, though the CA is Windows Server 2022 and should exceed that floor. Not
  testable by editing the existing template — its Compatibility dropdown only offers 2012+ once
  created at schema version 4; testing this needs a fresh duplicate built with a lower
  compatibility level chosen at creation, not attempted today.
## Paused

Session 1 paused 2026-09-05T22:29:21Z at Raymond's request, with the CA built but not running.

Session 2 paused 2026-09-06T00:1xZ at Raymond's request, blocked on console access to CA01.

Session 3, 2026-09-07: console access restored, the hang diagnosed, the certificate installed,
the client-auth template built and published, and a stale-ticket exposure found and confirmed.
Paused at Raymond's request ("stop here for today"), blocked on why `jsmith` cannot enroll from
the published template — see Open questions. Not a natural stopping point chosen by Claude; three
diagnostic branches (restart timing, policy cache, schema compatibility) were tried in one
session before Raymond called it. Next session should not repeat those three without new
information.

## Not started

- Determining why `jsmith`'s enrollment fails. See Open questions for what's ruled out and the
  one untested hypothesis.
- Uploading the root to Entra with no CRL, and enabling CBA.
- The revocation test that Option A exists to demonstrate.
- Deleting `tmp-cainstall`, which consultation point 5 requires. It still exists, disabled from
  Enterprise Admins twice now but not removed from the domain.
- AD-native expiring group membership as an alternative to manual add/remove for future
  privileged-access windows. Needs AD Recycle Bin enabled first; not currently enabled. Raised
  and deferred 2026-09-07, consultation point 8.
- `report.md` for this exercise. Three sessions of work, still unwritten. Should wait for the
  enrollment question to resolve rather than report a known-incomplete mechanism as done.
