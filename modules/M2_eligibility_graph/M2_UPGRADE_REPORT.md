# OpportunityOS v2 — Member 2 Upgrade Report

## Scope
Member 2 has been rebuilt against the 100-record M1 v2 foundation to restore the original OpportunityOS concept:

`profile -> deterministic eligibility -> missing requirements -> opportunity -> support -> verified next opportunities`

The previous simplified application-checklist interpretation is not used as the Opportunity Pathway.

## Data consumed
- 100 opportunities
- 371 verified requirement-type nodes
- 522 M1 relationships
- 10 sectors

## Safety rules
1. Hard `NOT_ELIGIBLE` is used only when a parameterized deterministic condition definitively fails.
2. `PARTIAL_STRUCTURED` and `SUMMARY_ONLY` records remain `POTENTIALLY_ELIGIBLE` unless a hard rule fails.
3. Lifecycle/recommendability restrictions return `NEEDS_VERIFICATION` and `recommendable=false`.
4. Transgender is never treated as Female unless a future official rule explicitly encodes that inclusion.
5. Generic requirement labels do not become falsely "completed" from weak profile evidence.
6. Cross-opportunity `UNLOCKS / ENABLES / FOLLOWED_BY` relationships are never invented.

## Implemented deterministic rules from current M1
- Tamil Nadu geography where explicitly encoded
- Female and Transgender gender requirements
- Scheduled Caste / Scheduled Tribe / Notified Backward Classes
- encoded annual-family-income ceilings (₹5 lakh / ₹3 lakh rows)
- exact `Above 35 years` rule
- lifecycle/recommendability policy

Ambiguous wording such as `Typically 15–45; relaxations...` stays uncertain and cannot hard-reject a user.

## Gap analysis
Profile evidence can currently verify specific items such as:
- FSSAI
- Udyam registration
- DPIIT recognition
- GeM registration
- IEC and selected export registrations
- training/certification presence
- DPR/business-plan/land/lender/incubator evidence when explicitly supplied in profile `extra`

Generic `DOCUMENT`, `REGISTRATION`, or component-specific requirements remain `VERIFY` unless M1 provides exact requirement details.

## Opportunity Graph
Validation result:
- Opportunity nodes: 100
- Requirement nodes: 371
- Relationships: 522
- Dangling relationships: 0
- Graph valid: YES

## Pathway engine
Produces:
- current user state
- eligibility state
- completed requirements
- action-needed gaps
- verification-needed requirements
- target opportunity
- supports provided by the opportunity
- verified next-opportunity relationships if M1 later provides them

Requirement ordering is explicitly labelled a UI display suggestion, not an official government application sequence.

## Test results
`16 passed`

Tests cover dataset size, graph integrity, lifecycle safety, Female/Transgender separation, social-category/income rules, Tamil Nadu geography, no false ELIGIBLE on partial data, requirement-gap detection, pathway support nodes, and no invented successors.

## Current limitation inherited from M1
Most of the 100 records are intentionally `PARTIAL_STRUCTURED` or `SUMMARY_ONLY`. Therefore M2 cannot safely produce many final `ELIGIBLE` decisions yet. This is expected and preferable to fabricated certainty. More official rules can be parameterized later without changing the engine's safety contract.
