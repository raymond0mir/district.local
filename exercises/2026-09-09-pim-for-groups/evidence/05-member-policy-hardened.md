# The member activation policy, hardened

## Source and claim label

Portal screenshots, Microsoft Entra admin center, signed in as the break-glass account.
**Recalled, not Captured**, for the same reason as `evidence/04`: the Graph read that would make
these values Captured could not be completed this session. See `evidence-log.md`, Not captured.

Change saved 2026-09-09 19:23:09 PDT, which is **2026-09-10T02:23:09Z** — the change lands on the
following day in UTC. Both forms are recorded here deliberately. `EXPOSURES.md` already tracks the
inverse of this hazard for snapshot and directory names.

## Before and after

Before, from `evidence/04`. After, from the Role setting details view.

| Setting | Before | After |
| --- | --- | --- |
| Activation maximum duration | 8 hours | **2 hours** |
| On activation, require | **None** | **Azure MFA** |
| Require justification on activation | Yes | Yes |
| Require ticket information on activation | No | No |
| Require approval to activate | **No** | **Yes** |
| Approvers | none selected | **1 Member(s), 0 Group(s)** |
| Require pre-approval custom extension (Preview) | No | No |
| Require post-approval custom extension (Preview) | No | No |

The Settings list corroborates the change independently of the detail view: the Member row moved
from `Modified: No` with an empty `Last updated` to `Modified: Yes`, `9/9/2026, 7:23:09 PM`, with
the break-glass account named as `Last updated by`. The Owner row remains `Modified: No` — it was
deliberately left at its default, and no claim is made about its values.

The 2-hour window matches what B4 set for the `User Administrator` role itself, PT8H to PT2H
(`exercises/2026-09-06-b4-pim-eligible-role/evidence/11-approval-required-and-window-tightened.md`).
The two governance paths to the same role now differ only in mechanism, not in window.

## The Assignment tab explains evidence/03's refusal

The same view reports, under Assignment:

- **Allow permanent eligible assignment: No**
- **Expire eligible assignments after: 1 year(s)**
- Allow permanent active assignment: No

This is the rule that refused `evidence/03`'s first valid-scope attempt with
`RoleAssignmentRequestPolicyValidationFailed — ExpirationRule — The policy does not allow permanent
assignment`. The refusal was not a quirk of the API; it is a stated default of this policy, visible
in the portal. The 90-day expiration chosen for `adm-jsmith`'s eligibility sits well inside the
1-year ceiling.

## Stated limitation: one operator on both ends of the approval

`Require approval to activate` is now `Yes` with exactly one approver, the break-glass account.
That is the only account in this tenant that can approve, and it is also the account that
administers the tenant day to day. Raymond's decision, taken with the limitation named in session
rather than discovered later.

**This configures the control correctly and does not demonstrate separation of duties.** In a real
deployment the requester and the approver are different humans, and the control's value comes from
that gap. Here they are the same person. Microsoft additionally recommends at least two approvers
for redundancy, which a single-operator tenant cannot satisfy — with one approver, that approver
becoming unavailable blocks every activation.

What this exercise can honestly show is that the approval gate exists, fires, and is recorded.
What it cannot show is that approval constrains anyone. Any report drawn from this evidence must
say so.

## What this does not show

Whether activation actually works under these settings. The policy is configured; the transaction
has not been run. That is the next step, and it is the one that tests the hypothesis rather than
the configuration.
