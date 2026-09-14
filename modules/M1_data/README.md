# OpportunityOS v2 — M1 Official-Source Foundation

Verification date: 2026-09-12

## What this package contains

- `OpportunityOS_v2_M1_100_official_source_foundation.xlsx`
  - Summary
  - Opportunity_Master (100 records; 10 sectors × 10)
  - Eligibility_Rules
  - Pathway_Requirements
  - Relationships
  - Source_Verification
  - Taxonomy
  - Legacy_Mapping
- `opportunity_master.json`
- `pathway_requirements.json`
- `relationships.json`
- `taxonomy.json`

## OpportunityOS design rules

1. M1 is the factual source of truth. AI must not invent scheme requirements.
2. M2 should use deterministic rules for eligibility.
3. A missing/unknown eligibility field is not the same as NOT_ELIGIBLE.
4. Only `Recommendable=true` records may enter normal ranking.
5. Lifecycle-flagged records belong in Needs Verification / historical context, not normal recommendations.
6. Opportunity Pathway means:
   current user state → missing requirement → action → opportunity unlocked/available → support → business goal.
7. `Pathway_Requirements` contains requirement/action nodes, but `Ordering=DISPLAY_HINT_ONLY`; the engine must compute order from actual dependencies.
8. `Relationships` intentionally contains only conservative `REQUIRED_FOR` and `PROVIDES` edges. Do not fabricate cross-scheme `UNLOCKS` or `FOLLOWED_BY` edges.

## Critical lifecycle corrections

- Stand-Up India is retained only for history/migration. The Department of Financial Services states the scheme was up to 31 March 2025.
- Startup India Seed Fund Scheme (SISFS) closed new startup applications on 31 May 2026.
- Raw Material Supply Scheme (Handloom), TIES, and Tea Development & Promotion are flagged for continuation confirmation because the published programme/guideline period reached FY2025-26.

## Data-quality note

The 100 records are an official-source research foundation, not a claim that every sub-component already has every machine-readable eligibility rule. `Rule_Completeness` is deliberately included. Before M2 makes a hard eligibility rejection from a `PARTIAL_STRUCTURED` rule, the relevant official component guideline should be fully parameterized.

## Migration from the old 32-record dataset

The workbook includes `Legacy_Mapping`. Sector-specific duplicates such as separate MUDRA tranches or PMEGP sector variants are normalized to one real scheme record and should be represented through tags/rules rather than duplicated schemes.
