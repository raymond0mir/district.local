# PIM policy authoring for Exchange Administrator and Teams Administrator — evidence log

Opened 2026-09-10, right after `2026-09-09-pim-for-groups`. That exercise built PIM for Groups from
the requester's side. This one is policy authoring: Raymond held PIM-governed eligibility for
Exchange Administrator and Teams Administrator at a prior employer, as a requester, and never
authored the policy behind it. The hypothesis: these two roles warrant different activation windows
and approvers, and `district.local` needs a real second approver — its only approver anywhere in
this tenant is currently the Global Administrator.

## Captured

- **Both roles' ids, and a clean starting state for both.** Exchange Administrator
  `29232cdf-9323-42fd-ade2-1d097af3e4de`, Teams Administrator `69091246-20e8-4a56-aa4d-066075b2a7a8`.
  Neither holds an eligible or active assignment, for any principal.
  `evidence/01-clean-baseline-and-role-ids.md`.
- **The two roles' untouched default policies differ on MFA, not only in theory.** Exchange
  Administrator's default requires MFA and justification to self-activate; Teams Administrator's
  requires justification only. Cross-checked against User Administrator's 2026-09-06 default, which
  matches Exchange Administrator. Neither policy has ever been modified (`lastModifiedDateTime`
  null on both). `evidence/02-default-activation-policies-diverge.md`.
- Both defaults agree on no approval (`isApprovalRequired: false`, empty `primaryApprovers`) and no
  Conditional Access authentication context — the same no-approval default already found on User
  Administrator and on PIM for Groups.

## Not captured, and why

- Which account is signed into Graph Explorer for these reads. Precedent from
  `2026-09-06-b4-pim-eligible-role` and `2026-09-09-pim-for-groups` is the native Global
  Administrator, carried into the evidence file headers on that assumption. Writing a role
  management policy for a role other than one already held needs Privileged Role Administrator or
  Global Administrator; User Administrator alone cannot do this write, so `adm-jsmith`'s current
  eligibility cannot be the account regardless. Confirm before the first write.
- Who the real second approver should be. This is the exercise's central design question and is not
  a capture — see Where Raymond was consulted.

## Where Raymond was consulted

- Not yet reached. The next decision is the second approver's identity, which needs his answer
  before any policy write.

## Corrections

- **The first re-run of the eligibility and assignment reads used
  `88d8e3e3-8f55-4a1e-953a-9b9898b8876b`, not either target role's id.** Both role definitions carry
  that value under `inheritsPermissionsFrom`, next to the role's own `id` field, and the instruction
  to "substitute each role's `id`" did not rule out the nested one. Re-run against the correct ids
  is what `evidence/01` records. Not wasted: the wrong-id read surfaced a direct, standing
  (non-PIM) assignment of role `88d8e3e3…` to principal `88eb396a-9074-4bc7-b710-85da2c9c0c27`, with
  no eligibility record — named in Open questions, not investigated here.
- **A Graph Explorer response did not match the query that produced it, again.** The first attempt
  at Exchange Administrator's policy read returned a `/users/$entity` lookup for an unrelated id
  instead. Matches the standing gotcha recorded 2026-09-09: a stale response body against a freshly
  edited URL. Re-run produced the correct response. `evidence/02` uses the re-run only.

## Open questions

- Who should the second approver be. `district.local`'s only approver anywhere is the Global
  Administrator. A real second approver needs an identity capable of approving without also being
  the requester or the sole existing approver.
- What role `88d8e3e3-8f55-4a1e-953a-9b9898b8876b` is, and who principal
  `88eb396a-9074-4bc7-b710-85da2c9c0c27` is. Surfaced by accident in the first, wrongly-scoped read.
  Not part of this exercise's hypothesis; queued for `EXPOSURES.md` if it turns out to matter.
- Whether Exchange Administrator's and Teams Administrator's activation windows should differ from
  each other, and from the shared PT8H/P365D/P180D defaults, given their different real-world blast
  radius.
- Which account can and should run the policy writes, given only Privileged Role Administrator or
  Global Administrator can write another role's management policy.

## Not started

- Authoring either role's activation policy.
- Choosing and provisioning the second approver.
- Any write to `roleManagementPolicies` or its rules.
