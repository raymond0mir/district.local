# Building an issuing CA, and four sessions spent debugging the wrong layer

## What I set out to do

Stand up a two-tier PKI in `district.local` — an offline root and an enterprise issuing CA — and
issue a client-authentication certificate to a real user, as the on-premises half of
certificate-based authentication.

**Closed 2026-09-08.** A certificate issued to `jsmith` at 14:34Z, and the full chain verifies
with revocation checked at every level. The exercise took five sessions. Four of them debugged the
wrong layer, and that method failure is the more useful of the two findings here. The first draft of
this report was written before issuance and said so; the sections below now carry the outcome.

**The HTTP CDP gap closed 2026-09-08, later the same day.** The CA's `CRLPublicationURLs` HTTP
entry carried no flags and put nothing into issued certificates. Setting `CSURL_ADDTOCERTCDP`
fixed that; a fresh enrollment, request 7, carries both an LDAP and an HTTP CDP, and the full chain
verifies. The on-premises half is done. The tenant half is not: the verify that passed used LDAP,
since CA01 is domain-joined, so it does not prove the HTTP-only path Entra will actually need, and
Entra CBA still needs public hosting for `crl.districtsafetyphoto.com`, named in Open questions.

## The setup

Proxmox host, 15 GiB. Container 106 (`rootca-offline`, 512 MB) holds a hand-built OpenSSL root CA,
started only when needed. VM 107 (`ca01`, 2048 MB) runs Windows Server 2022 Standard Evaluation with
Desktop Experience, chosen because certificate template management needs a GUI and DC01 has no
interactive logon path. VM 100 (DC01, 10000 MB) is the domain controller. All three sit on `vmbr1`,
`10.0.0.0/24`, a host-internal bridge.

Pre-flight at 2026-09-07T22:28:10Z: thin pool `Data%` 82.91, metadata 4.03, about 3.2 GiB under the
85% gate. Host memory 13 GiB available with everything stopped, about 1.4 GiB with DC01, CA01 and
the Vaultwarden container running. `evidence/30-host-power-loss-and-restart-state.txt`.

The lab lost power mid-way through, on 2026-09-07 at about 14:17 PDT. Only the Vaultwarden container
carries `onboot: 1`, so the domain came back down. That is recorded as an exposure, not as part of
this exercise.

## What I did

Across five sessions, 2026-09-05 to 2026-09-08.

1. Built the offline root in container 106 with OpenSSL, with `basicConstraints`, `keyUsage`, SKI
   and AKI, and **no CRL distribution point** — a deliberate choice, recorded below.
2. Installed AD CS on CA01, generated `ca01.req`, signed it against the root, and installed the
   certificate with `certutil -installcert`. This blocked indefinitely under `qm guest exec`, and
   the cause was a modal revocation-check dialog with no desktop to render it in
   (`evidence/23`). Run at the console it returned in seconds.
3. Granted `tmp-cainstall` Enterprise Admins for the duration of the install, because
   `-installcert` on an enterprise subordinate CA writes into the Configuration container, and
   removed it the same session. `evidence/24`, `evidence/25`.
4. Created `PKI-CBA-Pilot`, added `jsmith` as its only member, duplicated the built-in `User`
   template, trimmed the EKU to Client Authentication only, and published it to the CA.
   `evidence/28`, `evidence/29`.
5. Failed to enroll. Then spent four sessions ruling out, by capture: template ACL, template EKU,
   CA permissions, `jsmith`'s live token, RPC reachability, CertSvc stability, the client's
   enrollment-policy cache, template publication, the NTAuth and Root trust stores, chain trust and
   time validity, CRL publication, CA setup state, and the CA certificate AD advertises.
   `evidence/32`, `33`, `34`, `36`, `37`, `38`.
6. Submitted a certificate request directly, bypassing the enrollment UI:

       certreq -new C:\c2\req.inf req.req
       certreq -submit req.req cert.cer

   This returned the CA's own policy-module verdict in two commands. `evidence/39`.
7. Read the template's `msPKI-Certificate-Name-Flag`, decoded it against Microsoft's
   `X509CertificateTemplateSubjectNameFlag` enumeration, and read `jsmith`'s `mail` attribute.
8. Changed the flag from `-1509949440` to `-2113929216` at CA01's console as `tmp-cainstall`, using
   ADSI, and bumped `msPKI-Template-Minor-Revision` from 4 to 5 in the same write.
9. Restarted `CertSvc` and resubmitted. The request failed on a different error.

10. Read the state the plan rested on, and found it wrong. `SetupStatus` was 1, so no request was
    pending and `certutil -installcert` had nothing to complete. Read `CRLPublicationURLs` and found
    the HTTP entry already present with no flags, `0:`, applied to nothing. `evidence/41`.
11. Built the `openssl ca` database the root never had — `[ ca ]`, `[ CA_default ]`, `index.txt`,
    `serial`, `crlnumber` — because `ca01.req` had been signed with `openssl x509 -req`. Generated
    the root CRL and converted it to DER. `evidence/42`.
12. Published the CRL and the root certificate over HTTP from IIS on CA01, and created a
    domain-replicated primary zone `crl.districtsafetyphoto.com` on DC01 with an apex A record to
    10.0.0.12. CA01 fetched the CRL, status 200, 697 bytes. `evidence/43`.
13. Renewed the CA certificate reusing the key:

        certutil -renewcert ReuseKeys

    It wrote `ca01(3).req` and then hung. `SetupStatus` moved to 9. `evidence/44`.
14. Signed the renewal against the offline root with the CDP and AIA extensions, and confirmed the
    subject key identifier matched the 2026-09-05 certificate. `evidence/45`.
15. Verified the chain before installing anything:

        certutil -urlfetch -verify C:\ca01-3.cer

    It fetched both HTTP URLs and passed. The install attempt then failed in under 90 seconds with
    `ERROR_DS_INSUFF_ACCESS_RIGHTS` instead of hanging. `evidence/46`.
16. Added `tmp-cainstall` to `Enterprise Admins`, installed the certificate at CA01's console under
    a fresh logon, restarted `CertSvc`, resubmitted request 5, published the CRL, and removed the
    grant. Elapsed time under the grant: about three minutes. `evidence/47`, `48`.
17. Set `CSURL_ADDTOCERTCDP` on the CA's HTTP `CRLPublicationURLs` entry, pointed at
    `crl.districtsafetyphoto.com/pki/`, restarted `CertSvc`, and confirmed the change with
    `certutil -getreg`. The default `%3%8%9` filename template produced a CRL named
    `district.local Issuing CA+.crl`; IIS refused to serve it with a 404.11 double-escape error.
    Fixed with a literal filename, `issuingca.crl`, instead of loosening IIS's request filtering.
    `evidence/50`.
18. Forced a fresh enrollment to prove the fix on an actually-issued certificate, not just on the
    CA's own CRL file. At CA01's console, as `jsmith`:

        certreq -new C:\c2\req.inf req3.req
        certreq -submit req3.req cert3.cer

    Request 7 issued. Its `CRL Distribution Points` extension carries both the LDAP URL and
    `http://crl.districtsafetyphoto.com/pki/issuingca.crl`. `certutil -urlfetch -verify` returns
    `dwErrorStatus=0` on all three chain elements. `evidence/51`.

## Where Raymond was consulted
- **Placement of the CA.** New VM, VM 102, or DC01. I recommended a new VM and rejected DC01.
  Raymond chose a new VM.
- **Server Core or Desktop Experience.** I leaned Desktop Experience, because template management
  needs a GUI and DC01 has no console path. Raymond chose Desktop Experience.
- **DC01 memory.** I asked whether to reduce the untested 10000 MB allocation to make room. Raymond
  chose to leave it. Stated consequence: VM 101 must be stopped for the CA and DC01 to run together.
- **Root key passphrase.** I recommended no passphrase and named the tradeoff: anyone with host root
  can start the container and read the key. Raymond chose no passphrase.
- **Enterprise Admins on a member server.** I named the tier-rule violation. Raymond accepted it for
  the install window.
- **CRL distribution point.** Option A, no public HTTP endpoint and therefore no working revocation,
  or a published CRL. Raymond chose Option A on 2026-09-05, with the consequence recorded as
  "a revoked certificate will not be blocked." That consequence turned out to be the smaller one.
- **Which machine `jsmith` enrolled from.** `CARRYOVER.md` said VM 101. Raymond: "CA01 console,
  jsmith was logged in there." The carryover line was Recalled and wrong, and it would have sent the
  next test to a machine on the wrong subnet with no guest agent.
- **Template change, or populate `mail` on the user objects.** I recommended the template change,
  citing Microsoft's smart-card certificate requirements ("E-mail ID isn't required for smart card
  sign-in"), Entra CBA's default binding of SAN Principal Name to `userPrincipalName`, and its
  classification of address-based mappings as low affinity. Populating `mail` would treat the
  symptom and break again on `adm-jsmith` and service accounts. Raymond: "good lets go with the
  template change."
- **Reissue with a CDP, or relax revocation checking on the CA.** I recommended the reissue, because
  Microsoft documents that Entra CBA accepts one CDP per trusted CA and it must be an HTTP URL, with
  LDAP and OCSP unsupported. A workaround would issue one certificate and still block the goal.
  Raymond: "lets go with the reissue for next session."

- **Internal CDP name, or the public one.** I named the cost of each: an internal name unblocks
  issuance immediately and forces a second reissue when Entra CBA needs a public HTTP CDP. Raymond:
  "use the public name so we don't have to reissue twice." He owns the domain and has no hosting
  yet, so I built split-horizon DNS on DC01. The baked URL resolves inside the lab now, and needs no
  certificate change when hosting exists.
- **Re-grant `Enterprise Admins` to `tmp-cainstall`.** Raymond volunteered before I asked: "Ready to
  grant tmp-cainstall Enterprise Admins again if needed." I confirmed it was needed and named the
  limit: the grant does not help `qm guest exec`, which authenticates as `CA01$`. The install ran at
  CA01's console. The grant was removed the same session.
- **A fixed CRL filename, or loosen IIS's request filtering.** The default filename template
  produced a `+` character that IIS's double-escape guard rejected. I named the tradeoff: a fixed
  filename costs a rename on every future copy; `allowDoubleEscaping`, Microsoft's own cited
  workaround for this exact error, disables a request-filtering protection for every request under
  `/pki`, not only this filename. Raymond: "go with option A and we document the reasoning against
  B." No queued exercise needs the default delta-CRL naming preserved on that path.
- **Retire `tmp-cainstall` by deletion, or disable it.** I first recommended delete. Raymond asked
  whether that was Microsoft best practice, and it was not: Microsoft's general guidance is
  disable, then delete after a retention window, because a deleted object's SID can persist
  unresolvable in other ACLs, and because `district.local` has AD Recycle Bin disabled, so a
  delete here would not be reversible. I revised the recommendation on that question. Disabling
  closes the practical risk the same way a delete would, since a disabled account cannot exercise
  its standing Full Control ACE. Raymond: "disable it."

## What the box said
The enrollment wizard, at CA01's console, for both the custom template and the built-in `User`
template. This is a screenshot and stays Recalled:

    district.local Client Authentication -- STATUS: Unavailable
    "The permissions on this certification authority do not allow the current user to enroll for
     certificates. A valid certification authority (CA) configured to issue certificates based on
     this template cannot be located, or the CA does not support this operation, or the CA is not
     trusted."

Every one of those candidate causes is captured as correct. The CA's own security descriptor, from
`evidence/36-ca-security-allows-authenticated-users-to-enroll.txt`:

    Allow CA Administrator      BUILTIN\Administrators
    Allow Certificate Manager   BUILTIN\Administrators
    Allow CA Administrator      DISTRICT\Domain Admins
    Allow Certificate Manager   DISTRICT\Domain Admins
    Allow CA Administrator      DISTRICT\Enterprise Admins
    Allow Certificate Manager   DISTRICT\Enterprise Admins
    Allow Enroll                NT AUTHORITY\Authenticated Users

The direct submit, from `evidence/39-root-cause-template-required-email-and-no-user-has-one.txt`:

```
RequestId: 4
Certificate not issued (Denied) Denied by Policy Module The EMail name is unavailable and cannot
be added to the Subject or Subject Alternate name. 0x80094812 (-2146875374
CERTSRV_E_SUBJECT_EMAIL_REQUIRED)
```

The template attribute behind it, and the identical value on the built-in it was duplicated from:

```
cn                                 msPKI-Certificate-Name-Flag  msPKI-Template-Schema-Version
User                                               -1509949440                              1
district.localClientAuthentication                 -1509949440                              4
```

`-1509949440` is `0xA6000000`. Per Microsoft's `X509CertificateTemplateSubjectNameFlag` enumeration,
that is `SubjectNameRequireDirectoryPath` (`0x80000000`), `SubjectNameRequireEmail` (`0x20000000`),
`SubjectAlternativeNameRequireEmail` (`0x04000000`) and `SubjectAlternativeNameRequireUPN`
(`0x02000000`).

And the user:

```
SamAccountName    : jsmith
UserPrincipalName : jsmith@raytakosharkygmail.onmicrosoft.com
mail              :
```

After the fix, the same submit path:

```
RequestId: 5
Certificate not issued (Denied) Error Constructing or Publishing Certificate The revocation
function was unable to check revocation for the certificate. 0x80092012 (-2146885614
CRYPT_E_NO_REVOCATION_CHECK)
```


After the reissue, the same request:

```
Certificate issued.
CertUtil: -resubmit command completed successfully.

  Issued Request ID: 0x5
  Request Disposition: 0x14 (20) -- Issued
  Request Disposition Message: "Issued  Resubmitted by DISTRICT\CA01$"
  Request Status Code: 0x0 (WIN32: 0) -- The operation completed successfully.
```

The chain, with revocation fetched at every level:

```
CertContext[0][0]: dwInfoStatus=102 dwErrorStatus=0
  Subject: CN=John Smith, OU=Site 1, OU=Test Users, DC=district, DC=local
  SubjectAltName: Other Name:Principal Name=jsmith@...onmicrosoft.com
  Template: district.local Client Authentication
CertContext[0][1]: dwInfoStatus=102 dwErrorStatus=0
  Subject: CN=district.local Issuing CA, DC=district, DC=local
  ----------------  Certificate CDP  ----------------
  Verified "Base CRL (1000)" Time: 0
    [0.0] http://crl.districtsafetyphoto.com/pki/district-root.crl
...
Leaf certificate revocation check passed
CertUtil: -verify command completed successfully.
```

`evidence/47`, `evidence/49`.

Request 7, after the CDP fix, carries two CDP entries instead of one:

```
2.5.29.31: CRL Distribution Points
    [1]CRL Distribution Point
         URL=ldap:///CN=district.local Issuing CA,CN=CA01,CN=CDP,...
         URL=http://crl.districtsafetyphoto.com/pki/issuingca.crl
```

And its chain still verifies:

```
Verified Application Policies:
    1.3.6.1.5.5.7.3.2 Client Authentication
Leaf certificate revocation check passed
CertUtil: -verify command completed successfully.
```

`evidence/51`.

`Domain Users`' Allow Enroll ACE, before removal, on the client-auth template:

```
IdentityReference      : DISTRICT\Domain Users
ActiveDirectoryRights  : ReadProperty, WriteProperty, ExtendedRight
AccessControlType      : Allow
ObjectType             : 0e10c968-78fb-11d2-90d4-00c04f79dc55
```

After removal, at the console that made the change and independently from DC01:

```
--- after ---
No Domain Users ACE remains on this object.
```

`evidence/52`.

`tmp-cainstall`, before and after the disable, both reads run as `DISTRICT\DC01$` over
`qm guest exec`:

```
SamAccountName Enabled
-------------- -------
tmp-cainstall     True
```

```
SamAccountName Enabled
-------------- -------
tmp-cainstall    False
```

`evidence/53`.

## What broke, and why
**The template required an attribute no account in the domain has.** It was duplicated from the
built-in `User` template, and duplication copies the subject-name flags verbatim. `User` requires
the e-mail attribute in both the subject and the subject alternative name. Nobody read that page of
the properties, because nobody was changing it. The CA denied every request during subject
construction, before it ever attempted to build a certificate.

**That defect also produced the strongest piece of misdirection in the whole exercise.** The
built-in `User` template holds the identical flag value, so testing it as a control returned the
same `Unavailable` status. That reads as a CA-wide fault and it excluded every template-specific
theory at once — template ACL, EKU, schema version, the Windows Server 2016 compatibility idea. All
of those were correctly excluded. The conclusion drawn from excluding them, that the problem must
therefore be in the CA or its trust, was wrong. Two templates sharing one requirement is not the
same thing as a CA-wide fault, and I did not consider that reading until the direct submit made it
unnecessary.

**The error message describes causes the developer anticipated, not the cause that occurred.** It
names CA permissions, CA location, CA support for the operation, and CA trust. Each of those was
verified and each was correct. It says nothing about subject construction, which is what actually
failed. Four sessions of accurate, well-captured work went into verifying candidates supplied by a
string.

**The no-CDP decision had a second consequence nobody stated.** On 2026-09-05 the recorded
consequence of Option A was that a revoked certificate would not be blocked once CBA was live. The
unstated consequence is that the CA cannot validate revocation on its own chain while constructing a
certificate, so it will not issue at all. `evidence/32` captured
`CERT_TRUST_REVOCATION_STATUS_UNKNOWN` as the only chain error hours before the direct submit
returned `CRYPT_E_NO_REVOCATION_CHECK`. I recorded that finding as real but not the blocker, which
was true while the e-mail requirement failed first, and false the moment it was fixed.

**Four of my own claims were wrong and are retracted on the record.** I passed unquoted Windows
paths through `qm guest exec` and bash consumed the backslashes, so an evidence file records a path
that never executed. I proposed that `jsmith`'s console token was stale, by analogy with this
exercise's own stale-ticket finding; `whoami /groups` disproved it. I proposed that the CA had never
published a base CRL and that `SETUP_FORCECRL_FLAG` was still set; both CRLs exist and `SetupStatus`
is 1. I proposed that AD advertised a stale CA certificate, because `CertEnroll` held three `.crt`
files with two timestamps; the thumbprint in AD matches the running CA exactly.

**A credential reached a channel that keeps a record, for the second time in two days.** On
2026-09-08 a screenshot included an open password-manager entry showing a password in clear text. It
is in no artifact. The control that failed is the same one the 2026-09-07 exercise was about. There
the channel was a public repository; here it was a screenshot. The account is most likely
`tmp-cainstall`, whose password was rotated into the vault on 2026-09-07.


**`certutil -renewcert` hangs for the same reason `-installcert` did, and the hang is harmless.**
The process wrote its request file and its registry state within the first second, then blocked
until the 240-second timeout. Pid 3192 held 0.03 CPU seconds and zero TCP connections. Near-zero CPU
with no socket is a user-interface wait, which rules out the network and matches the confirmed
`-installcert` behavior. The output that mattered already existed on disk. I nearly read the timeout
as a failure; the state read is what showed it had succeeded.

**Reissuing the CA certificate fixed less than the exposure claimed it would.** `EXPOSURES.md` said
the reissue would fix on-premises issuance and the tenant path together. It fixed the first. The
certificate the CA now issues still carries an LDAP CRL distribution point only, because the CA's
HTTP entry in `CRLPublicationURLs` reads `0:` — present, no flags, applied to nothing. Putting a CDP
on the CA's own certificate and putting one on the certificates it issues are two different changes,
and I wrote a plan that conflated them. Caught by inspecting the issued certificate rather than by
stopping at "Certificate issued."

**The CA's own machine account can issue certificates.** The disposition message reads "Issued
Resubmitted by `DISTRICT\CA01$`". `qm guest exec` runs as SYSTEM, so it authenticates as the machine
account, and that identity holds enough CA rights to approve a pending request. It does not hold
enough to install a CA certificate, which is a forest write. Two different permissions, and the same
session hit both boundaries within four minutes.

**Two Microsoft defaults collided, and neither side was misconfigured.** AD CS's default CRL
filename template appends a `+` when delta CRLs are enabled. IIS's default request filtering treats
that `+`, adjacent to a space-containing name in the same path segment, as a double-escaped
sequence and refuses to serve it. Each default is documented and sensible on its own; together they
produce a 404 that names neither cause. The fix was a filename, not a setting on either system.

**I repeated a gotcha already written down, and it cost two rounds of misdiagnosis.**
`references/gotchas.md` has carried, since 2026-09-07, an entry on quoting Windows paths through
`qm guest exec`. I sent an unquoted path to `certutil.exe -dump` anyway; bash stripped the
backslash, and `certutil` correctly reported a file missing that had existed the whole time. I
first attributed the result to a hung `certreq -retrieve` process, before checking the command
that actually failed. Having the gotcha on file did not stop me from making it again — only
rereading my own command did.

## What I'd do differently
**Issue one certificate before building anything on top of the CA.** This is the whole lesson and
everything else in this section is a consequence of it.

On 2026-09-05 the CA was declared live on component health: `certutil -installcert` completed,
`SetupStatus` moved from 525 to 769, `CertSvc` reported Running, `certutil -ping` answered in 16 ms,
and an Enrollment Services object appeared in AD. Every one of those readings is accurate. Not one
of them is issuance. A CA that has never issued a certificate is installed, not working.

On top of that unproven layer I then built a group, a template, an EKU trim, an ACL and a
publication. Four more components, each verified correctly and in isolation, each resting on a
foundation nobody had exercised. When the failure surfaced at the top of the stack, where the user
is, I debugged downward through layers that were all healthy.

The smoke test is two commands and it belongs immediately after `-installcert`, before any custom
template exists:

    certreq -new <inf> req.req
    certreq -submit req.req cert.cer

Against a built-in machine template it would have been sharper still. Machine templates build their
subject from DNS and SPN rather than e-mail, so that request would have passed straight over the
defect that consumed four sessions and returned `CRYPT_E_NO_REVOCATION_CHECK` on 2026-09-05 — the
same day the no-CDP decision was made, while the reasoning for it was still in front of me. No
custom template would have existed, so there would have been nothing to blame it on.

**Test the transaction, not the components.** Component health answers "is this object configured
correctly." It cannot answer "does the thing the user needs actually happen." Those are different
questions and only the second one has a user on the other end of it. Every check in sessions two
through five answered the first question, correctly, about a different component each time.

**The same gap is open in three other places in this lab, and I should say so rather than only fix
it here.** Entra Connect was declared working on a successful export sync; no account has been
proven to authenticate through it end to end. The VM restore path has never been exercised — one
archive passed `zstd -t`, which proves the file is not corrupt and nothing about whether it boots.
Conditional Access policy `75882b6a` enforces, and no legacy-authentication client has ever been
pointed at it. Each is the same shape: component verified, transaction not.

**Read an error message as a list of candidates, not as a diagnosis.** The wizard's text sent three
sessions to verify things that were already correct. The habit worth building is to reach for the
layer that returns a specific error code — here the CA's policy module — before working through a
list of plausible causes supplied by a UI string.

**Capture the decision's consequences, not just the decision.** Option A was recorded properly, with
a stated consequence. The stated consequence was the wrong one, and it was wrong because nobody
tested the decision against issuance. A recorded tradeoff is only as good as the test that
established what the tradeoff actually is.

## Open questions

- ~~Is revocation the last blocker?~~ Answered 2026-09-08. It was. Request 5 issued as soon as the
  CA could fetch a CRL for its own certificate, with no further defect behind it.
- ~~Does setting `CSURL_ADDTOCERTCDP` require reissuing certificates already issued, including
  request 5?~~ Answered 2026-09-08. No. Request 5's certificate still carries an LDAP-only CDP;
  the flag only affects certificates issued after the change.
- **Does Entra CBA succeed against the HTTP-only CDP path alone?** The chain verify that passed
  used LDAP, since CA01 is domain-joined. It never independently exercised the HTTP path the way
  Entra — which cannot use LDAP at all — actually would. The HTTP fetch itself works; whether
  revocation checking succeeds with LDAP genuinely unavailable is untested.
- The public CDP URL is baked into the CA certificate and nothing public serves it. Inside the lab
  it resolves only because DC01 holds an overriding zone. Standing up hosting on
  `districtsafetyphoto.com` is now a dependency of tenant CBA, not an optional step.
- Why did a second `certreq -retrieve` against an already-retrieved request ID orphan a process on
  CA01 — 0.125 CPU seconds, no TCP connections, never exited within 60 seconds? Did not block the
  exercise; the first retrieval attempt's file was valid throughout.
- Why did the renewal create two CA certificate indices rather than one, and which one does the CA
  sign with? `CA cert count` moved from 3 to 5.
- Four of five CA certificates report `CRL[n]: 1 -- Error: No CRL for this Cert` after a successful
  `certutil -CRL`. All five share one key, so one CRL may be the complete and correct state. Nothing
  observable is broken. The reading is not explained.
- `district-root.crl` expires 2027-03-07. The root is an offline container that is normally stopped.
  Nothing in the lab regenerates or republishes it.
- Does any user object in `district.local` have `mail` populated? Only `jsmith` was checked. The
  domain-wide answer bears on which other templates are affected.
- ~~`DISTRICT\Domain Users` holds Allow Enroll on the client-auth template, inherited from
  `ClientAuth` the same way the e-mail requirement was. It needs its own before-and-after.~~
  Answered 2026-09-09. Removed, at CA01's console as `tmp-cainstall`, and confirmed from two
  vantages. `evidence/52`. Untested: whether `PKI-CBA-Pilot` alone now gates enrollment
  end to end — no non-member enrollment attempt has been made either before or after.
- ~~`DISTRICT\tmp-cainstall` holds standing Full Control over the template and is now the only
  non-tier-0 identity that can write it.~~ Disabled 2026-09-09, not deleted — `district.local` has
  no AD Recycle Bin, so a delete would not be reversible; disabling closes the practical risk the
  same way, since a disabled account cannot exercise the ACE. `evidence/53`. Deletion deferred to
  a retention window.
- What does `flags = 10` mean on the `pKIEnrollmentService` object? A Microsoft Learn search returned
  the schema definition and no value table. Recorded undecoded.
- Was the credential shown in the 2026-09-08 screenshot rotated? Recommended in session, unconfirmed.
- Is tenant certificate-based authentication P2-gated? `CURRICULUM.md` flags it as not captured, and
  it needs a read before the trial ends 2026-10-04.
