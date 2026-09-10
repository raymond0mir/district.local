# The activation transaction, run partway

## Source and claim label

Portal screenshots across two browser sessions — break-glass in a normal window, `adm-jsmith` in
a private window — Microsoft Entra admin center, 2026-09-09 evening PDT. **Recalled, not
Captured.** Times below are given in the portal's local PDT and in UTC; PDT is UTC-7, so every
UTC time falls on 2026-09-10.

**This transaction is incomplete.** The final step — proving activated membership grants effective
`User Administrator` — was not run. What follows records what happened, not a closed hypothesis.

## Sequence

| Local (PDT) | UTC | Event |
| --- | --- | --- |
| 19:30 | 02:30 | Before-state: `adm-jsmith` denied on `dumbuser2` password reset |
| 19:32 | 02:32 | Stray request: `User Administrator` **direct** role, B4's path |
| 19:36:03 | 02:36:03 | Group member activation requested, `PIM-UserAdmin-Pilot` |
| ~19:42 | ~02:42 | Stray direct-role request **approved** in error |
| 19:50 | 02:50 | Group request approved |
| 19:50:54 | 02:50:54 | Group membership shows `Activated` |

## The before-state holds

As `adm-jsmith`, with both paths eligible-not-active, Entra ID → Users → `dumbuser2` → Reset
password returned: *"The password can not be reset. This may be due to an incorrect level of
administrative privilege or if trying to reset your own password."* `Edit properties` and `Delete`
were greyed out alongside it.

This is the control case the exercise needed: the account cannot perform a `User Administrator`
action while holding only eligibility.

## What the activation demanded, and did not

Requesting activation from **My roles → Groups** produced a justification field and a duration
selector. It did **not** produce an MFA prompt, despite `On activation, require: Azure MFA` being
set in `evidence/05`.

This is documented behavior, not a broken control. Microsoft states that users may not be prompted
if they authenticated with strong credentials or completed MFA earlier in the session, and that
forcing a fresh authentication at activation requires `On activation, require Microsoft Entra
Conditional Access authentication context` together with Authentication Strengths
([Configure PIM for Groups settings](https://learn.microsoft.com/entra/id-governance/privileged-identity-management/groups-role-settings#role-settings)).

**The setting's name implies a prompt and delivers a claim check.** An administrator who sets
"require MFA" and expects step-up authentication at the moment of elevation has not got one. The
sign-in already satisfied it.

## The justification requirement is not a control

The request was accepted with a single arbitrary word as its business justification — no ticket
reference, no context, nothing validated. `Require ticket information on activation` is `No`, so
the `Ticket number` and `Ticket system` fields on the approval record are both empty.

The approver's reason box is separately mandatory, marked with a required-field asterisk, and is
equally unvalidated.

Both sides of this gate demand text. Neither side checks it. The audit trail records that two
people typed something, which is not the same as recording why access was granted.

## The approval gate fired

The request landed in `Pending approval` rather than activating, and stayed there until approved.
Request details, from the approver's panel:

- Role `member`, Resource `PIM-UserAdmin-Pilot`, Resource type `Group`
- Requestor `Admin - John Smith`
- Request type `selfActivate`
- Ticket number and Ticket system both empty

This is the hardened policy from `evidence/05` working as configured. Approval is the one control
in this stack that behaved exactly as its name suggests.

## Unresolved: when the two-hour clock starts

The approver's panel displayed `Start time: Sep 9, 2026, 7:36 PM` and `End time: Sep 9, 2026,
9:36 PM` — request time plus two hours, implying the ~14 minutes spent pending came out of the
requester's window.

The resulting assignment, read afterward from the group's own Assignments blade, shows
`Start time 9/9/2026, 7:50:54 PM` — approval time. Its End time was not read.

These two readings disagree, and this file does not resolve which governs. If the end time is
21:36 the pre-approval panel was accurate; if it is 21:50 the panel displayed a schedule the
platform did not honour, which is the more interesting outcome and the one worth chasing.

**A retraction belongs here.** Claude asserted in session, from the approval panel alone, that the
activation clock runs from request time and that a slow approver silently shortens the granted
access. The assignment record contradicts that. The claim was stated before the confirming read
existed and is withdrawn pending the End time.

## The stray activation, and why it is on the record

At 19:32 an activation was requested against B4's **direct** `User Administrator` eligibility
rather than the group, and at ~19:42 it was approved in error before the mistake was caught.

The audit trail for this tenant therefore shows a `User Administrator` direct activation in the
middle of this exercise. It is recorded here so no reader concludes the group test was run while
that role was active — and equally, so no reader assumes it was not. **Whether that direct
assignment was deactivated before the session ended was never confirmed.** Both assignments were
time-boxed to two hours and expire on their own.

## What this does not show

That activated group membership grants effective `User Administrator`. The after-state test — the
same `dumbuser2` password reset that was denied at 19:30 — was never run. Without it, this
exercise has proven that PIM's gates fire, and has **not** proven that the access being gated
actually arrives. That is the transaction, and it remains untested.
