# The group's default member activation policy: no MFA, no approval

## Source and claim label

Two portal screenshots, Microsoft Entra admin center, signed in as the break-glass account,
2026-09-09 at about 19:17 and 19:18 local (PDT). **Recalled, not Captured.** The equivalent Graph
read was attempted first and could not be completed — see `evidence-log.md`, Not captured.

Path: ID Governance → Privileged Identity Management → Groups → `PIM-UserAdmin-Pilot` →
Settings → Member.

## What the settings list showed

| Role | Modified | Last updated | Last updated by |
| --- | --- | --- | --- |
| Member | No | - | - |
| Owner | No | - | - |

`Modified: No` on both rows is the portal stating these are untouched defaults, not merely that
nobody recorded a change. Nothing in this exercise has configured either policy.

## What the Member activation settings showed

- **Activation maximum duration: 8 hours.**
- **On activation, require: None.** The radio group offers None / Azure MFA / Microsoft Entra
  Conditional Access authentication context. `None` is selected.
- **Require justification on activation: checked.**
- Require ticket information on activation: unchecked.
- Require pre-approval custom extension to activate (Preview): unchecked.
- Require post-approval custom extension to activate (Preview): unchecked.
- **Require approval to activate: unchecked. No approver selected.**

## What this shows

- **This group's default is weaker than the Entra role default B4 captured.** `EXPOSURES.md`
  records the untouched role management policy as requiring MFA, requiring justification, and
  capping activation at PT8H, with `isApprovalRequired` false. This group's member policy matches
  on justification, matches on the 8-hour cap, matches on no approval — and **drops the MFA
  requirement entirely**.
- Read together with `evidence/02`, the practical effect of the untouched defaults is: an eligible
  member activates membership with no second factor and no human approval, and the group carries
  standing `User Administrator` tenant-wide. Justification is a text box, not a control.
- The two PIM surfaces disagree in both directions, which is the more interesting finding than
  either default alone. PIM for Groups is **stricter** than PIM for roles on assignment duration —
  it refused the permanent eligible assignment that the role-level policy accepted, `evidence/03` —
  and **looser** on activation controls, dropping MFA. Neither default is simply "weaker"; they
  are differently shaped, and an administrator who reasons from one to the other will be wrong.
- The group appearing in the PIM → Groups list at all independently corroborates the correction in
  `evidence-log.md`: no explicit onboarding step was performed, and the eligibility request in
  `evidence/03` onboarded it.

## What this does not show

The Owner policy's detail. The settings list reports it unmodified, but its activation tab was not
opened, so its individual values are not recorded. Also not established: whether activation is
genuinely possible for `adm-jsmith` under these settings, which is the transaction this exercise
still has to test.
