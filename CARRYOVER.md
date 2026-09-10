# Carryover

## Last verified
2026-09-10T22:02:35Z, guest-agent reads on DC01 and CA01,
`exercises/2026-09-10-domain-time-skew/evidence/04-event-4616-dates-every-step-and-certutil-prints-local.md`.
Pool reading 2026-09-10T18:10:11Z.

## Next safe action
Audit the repository for claims dated from a guest clock instead of `date -u`. DC01 and CA01 are
five and seven hours ahead of real time. Search evidence files for guest-rendered timestamps used
as fact. It needs no lab access and changes no state.

## Lab state
VM 100 (DC01) and VM 107 (CA01) running, both booted 2026-09-09T14:19:31Z. VM 101, 102, 104
stopped. CT 103 running, CT 106 stopped. Pool Data% 80.11, Meta% 3.84. VM 100 holds `clean-install`
only; VM 107 holds `pre-adcs-config` only. Tenant unchanged: `PIM-UserAdmin-Pilot` holds `User
Administrator` standing. `adm-jsmith` is eligible to 2026-12-08.
**Clocks are wrong.** DC01 is +5h 06m 12s from real UTC and drifting. CA01 is +7h 00m 00s and
holding. See `EXPOSURES.md` and `exercises/2026-09-10-domain-time-skew/report.md`.

## Stop conditions
Pool Data% at 85 or higher. Headroom 4.89 points. Run pre-flight before the next state change.
Do not issue a certificate from CA01 until the clock is fixed. It stamps `NotBefore` seven hours
ahead of real time.

## Hard deadlines
- P2 trial ends 2026-10-04T00:00:00Z. Verified.
- `svc-entraconnect` password expires about 2026-10-13. Unverified.
- `adm-jsmith` eligible membership expires 2026-12-08. Verified.
- `district-root.crl` expires 2027-03-07. Nothing regenerates it.
- `districtsafetyphoto.com` may lapse this month. Unverified.

## Pending decisions
- **Which time fix to apply. Asked 2026-09-10. Default: none, ask first.** Three candidates, all
  changing the domain controller. `report.md` names them.
- `101 win11-ootb` snapshot, 18.31 GiB. Default: keep.
- Non-root Proxmox user to test `PVEVMUser` against `qm guest exec`. Default: do not create one.
- Two `AllPrincipals` consent grants. Default: leave, remove before teardown.
- Stripping IP addresses from captures. Default: redact case by case.
- Capture headers for the PIM exercise `evidence/04` to `06`. Default: leave the WARNs.
- `tmp-cainstall` deletion. Default: leave disabled.
- Credential-scan patterns file absent. Default: leave absent.
- B4's direct eligibility on `adm-jsmith`. Default: leave, remove before teardown.

## Blockers
Entra CBA needs `crl.districtsafetyphoto.com` over public HTTP, and is now also blocked by the
certificate post-dating above. Owner: Raymond.
`Connect-MgGraph` times out on both auth flows. Graph Explorer works; see `gotchas.md`.

## Uncommitted and staged work
Tree clean, nothing staged, three commits ahead of `origin/main`. Not pushed. Raymond has not
asked.
