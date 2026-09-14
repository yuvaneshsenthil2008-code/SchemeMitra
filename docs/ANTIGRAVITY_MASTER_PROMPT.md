# Antigravity Master Prompt — OpportunityOS v2

Build OpportunityOS v2 from this package.

## Critical instruction
Do **not** reuse the old frontend architecture or old 720px portrait web layout. Build a new responsive, desktop-first public government-opportunity portal according to `docs/WEBSITE_BUILD_SPEC.md`.

Do not redesign the backend logic. Preserve the ownership boundaries and safety rules in `docs/FINAL_INTEGRATION_SPEC.md`.

## Read before coding
1. `README.md`
2. `docs/FINAL_INTEGRATION_SPEC.md`
3. `schemas/CANONICAL_PROFILE_SCHEMA.json`
4. `docs/API_CONTRACT.md`
5. `schemas/CANONICAL_ANALYZE_RESPONSE_SCHEMA.json`
6. `docs/WEBSITE_BUILD_SPEC.md`
7. each module README/test suite

## Module ownership
- M1 = factual opportunity data and official-source metadata.
- M2 = deterministic eligibility, gap analysis, graph, pathway.
- M3 = multilingual profile extraction/normalization only.
- M4 = ranking/recommendation presentation only.

Never let an LLM decide deterministic eligibility or fabricate scheme facts.

## Backend
Create a clean FastAPI integration layer exposing the endpoints in `docs/API_CONTRACT.md`.
Use adapters rather than editing module logic unnecessarily.
Use `opportunity_id` consistently.
No silent mock-data fallback.

## Frontend
Build the public flow first:
Home -> sector discovery -> listing/filter -> opportunity detail -> Set Your Profile.

Then profile/personalization:
profile -> Show My Schemes -> My Opportunities -> Why You Match -> Missing Requirements -> Needs Verification.

Then innovation views:
Opportunity Pathway + Opportunity Graph + separate Application Guide.

## Data and lifecycle rules
- Only `recommendable=true` can enter normal recommendation ranking.
- `NEEDS_VERIFICATION` stays in its own section.
- `NOT_ELIGIBLE` is never recommended.
- Missing/unknown rules are not automatic failures.
- Do not create fake cross-opportunity graph relationships.
- Preserve official source URLs and lifecycle metadata.

## UI requirements
- Desktop inner content approx. 1200–1440px with full-width page sections.
- English/Tamil/Hindi frontend localization.
- Profile saved locally; Reset Profile asks confirmation.
- Before profile: no personalized eligibility/ranking percentages.
- After profile: show `My Opportunities` in header.
- AI profile builder CTA text: `Speak to build your profile` and also allow typing.

## Verification before declaring completion
Run all existing M2/M3/M4 tests, add integration/API tests, validate all M1 opportunity IDs, verify no `recommendable=false` item appears in normal recommendations, verify `NOT_ELIGIBLE` never appears in recommendations, verify Needs Verification separation, verify public browsing works with no profile, and perform at least one full end-to-end profile -> analysis -> recommendations -> pathway flow.

Do not report completion while tests are failing. Produce a final integration report listing test counts, known limitations, and any changes made to module boundaries.
