# M4 Upgrade Report

## Upgrade goal
Align Member 4 with OpportunityOS v2 rather than the previous scheme-application-checklist architecture.

## Changes
- Migrated identifiers from `scheme_id` to `opportunity_id`.
- Consumes the 100-record M1 Opportunity Master.
- Consumes M2's v2 conservative eligibility contract.
- Enforces `recommendable=false` and lifecycle safety.
- Separates `NEEDS_VERIFICATION` from normal recommendations.
- Excludes `NOT_ELIGIBLE` from recommendation output.
- Ranks with explicit support preference first, inferred support need second, then other safe opportunities.
- Generates Why You Match only from M2 deterministic passed-rule evidence plus transparent ranking metadata.
- Removed the old M4-generated application-checklist pathway.
- M4 now attaches only M2-produced Opportunity Pathways.
- Added a distinct Application Guide built from M1 application/document metadata.

## No fabricated graph/pathway facts
M4 cannot generate `UNLOCKS`, `ENABLES`, `FOLLOWED_BY`, registration, certification, training, or document dependency edges. Those remain M1/M2 responsibilities.
