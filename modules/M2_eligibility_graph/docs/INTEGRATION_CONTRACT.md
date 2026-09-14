# OpportunityOS v2 — M1 → M2 contract

M2 consumes the M1 v2 files in `data/`.

## Safety contract
- `NOT_ELIGIBLE` only when a machine-parameterized rule definitively fails.
- `POTENTIALLY_ELIGIBLE` when M1 is partial/summary-only, profile data is missing, or a rule cannot safely be parameterized.
- `NEEDS_VERIFICATION` when lifecycle/recommendability says the opportunity must not be recommended.
- `recommendable=false` is never overridden by profile matching.
- `Female` and `Transgender` are distinct deterministic values.

## Pathway contract
The pathway is not an application checklist. It models:
`current profile -> requirements/gaps -> opportunity -> verified support`.
Cross-opportunity edges (`UNLOCKS`, `ENABLES`, `FOLLOWED_BY`, etc.) are shown only if M1 later supplies verified relationships.

## Application Guide
A future frontend may build a separate scheme application guide from M1's application route and document summary. It must not be confused with Opportunity Pathway.
