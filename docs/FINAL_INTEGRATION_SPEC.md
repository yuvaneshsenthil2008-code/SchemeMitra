# OpportunityOS v2 — Final Integration Specification

## 1. Purpose
Build a public-first government-opportunity discovery portal that becomes personalized only after a user chooses to create a profile. Preserve the original OpportunityOS concept: explainable eligibility, gap detection, verified opportunity relationships, and goal-oriented pathways.

## 2. Source-of-truth ownership
### M1 — Facts
Owns opportunity metadata, official sources, lifecycle/recommendability, benefits, eligibility summaries/rules, requirements, application metadata, taxonomy, and verified relationships.

### M2 — Deterministic decision layer
Owns eligibility classification, missing-data/gap analysis, requirement satisfaction, Opportunity Graph validation, and Opportunity Pathway generation. It must never hard-reject a user from ambiguous or unparameterized text.

### M3 — Profile understanding
Owns typed/spoken profile extraction, multilingual input interpretation, normalization, confidence/provenance, conflict handling, missing-profile-field prompts, and conversion to the canonical profile contract. It does not decide eligibility or rank opportunities.

### M4 — Ranking/presentation
Owns ranking safe M2-recommendable opportunities, support-preference ordering, Why You Match presentation, Needs Verification grouping, and Application Guide assembly from M1 metadata. It must not invent eligibility evidence, requirements, graph edges, or pathway steps.

## 3. Mandatory safety/status rules
- `NOT_ELIGIBLE`: only from a definitive failed deterministic M2 rule.
- `POTENTIALLY_ELIGIBLE`: missing profile data, partial M1 structure, or safely unparameterized rule.
- `NEEDS_VERIFICATION`: lifecycle or recommendability blocks normal recommendation.
- `recommendable=false`: never overridden by ranking or AI.
- Transgender is a distinct canonical gender and is not automatically treated as Female.
- Unknown requirements remain unknown/verify; never mark them completed from weak evidence.
- No fabricated `UNLOCKS`, `ENABLES`, `FOLLOWED_BY`, training, certification, registration, document, or application dependencies.

## 4. End-to-end flow
### Public flow
Home -> Sector discovery -> Opportunity listing + filters -> Opportunity detail -> Set Your Profile

No personalized eligibility percentage/ranking is shown before a profile exists.

### Profile flow
Set Your Profile -> manual form or "Speak to build your profile" -> review/edit extracted fields -> confirm -> Show My Schemes

Voice is speech-to-text input only. The transcript/extracted profile must be reviewed before persistence.

### Personalized flow
Profile -> M2 analysis -> M4 ranking -> My Opportunities

My Opportunities contains:
- Recommended
- Potentially Eligible
- Missing Requirements / Gaps
- Opportunity Pathway
- Opportunity Graph
- Needs Verification
- Application Guide (separate from pathway)

## 5. Opportunity Pathway semantics
The pathway answers: "What do I need to do, in what verified dependency order, to become ready for an opportunity and move toward my business goal?"

It may show:
current state -> missing registration/training/certification/document/business-plan/etc -> target opportunity -> support provided -> verified next opportunity -> goal

Requirement ordering that is not officially encoded must be labeled as a display suggestion, not a government-mandated sequence.

## 6. Application Guide semantics
The Application Guide is a practical scheme application view built from M1 application/document metadata. It may show documents, portal/channel, verification, and tracking. It must not be presented as the Opportunity Pathway.

## 7. Data rules
- Use the M1 100-opportunity foundation as the catalogue.
- Use `opportunity_id` consistently; do not return to `scheme_id` in new code.
- Do not duplicate one real scheme into fake sector/tranche schemes merely for UI density.
- Primary sector + secondary tags may surface one opportunity in multiple discovery contexts.
- Official source/lifecycle metadata must remain visible in scheme detail where available.

## 8. Integration rule
Do not rewrite module responsibilities during integration. Adapters may be added at module boundaries, but deterministic rules and source-of-truth data must not be silently changed.
