# SchemeMitra — Marginalized Entrepreneur Personalization Update

Build date: 2026-09-15

## Scope

This build changes only the requested areas while preserving the existing Opportunity Graph, Goal Pathway semantics, M1/M2/M4 separation, progress persistence, profile schema behavior, URLs already corrected, and other unrelated features.

## UI changes

- Removed the visible **Total Pathway Steps** card from Goal Pathway. The backend `total_steps` field remains for compatibility/testing, but it is no longer shown to users.
- Goal Pathway **Where You Are Now** now also shows Gender and Social Category, in addition to Disability and Selected Goal.
- Opportunity Graph profile context now includes Social Category.
- Home/Explore scheme cards now show verified demographic eligibility metadata:
  - Gender
  - Social Category
  - Disability eligibility when the scheme is disability-specific
- Scheme Detail now shows Gender, Social Category and Disability eligibility for every opportunity.
- Scheme Detail can show a **Benefit for your profile** card only when a verified demographic benefit variant matches the saved profile. If no special benefit applies, the card is omitted.
- Home catalogue fallback statistics and hero copy now reflect the expanded verified dataset.

## Fresh sentence / voice extraction behavior

Each explicit **Extract Profile Fields** action is now a fresh interpretation of the new sentence:

- fields that were auto-detected by the previous extraction are cleared before the new extraction is applied;
- manually edited/confirmed fields are preserved unless the new sentence explicitly provides a replacement;
- `_detectedFields` is replaced by the current extraction rather than accumulated forever;
- a previously auto-derived Selected Goal falls back to **General Business Readiness** if the new sentence does not contain a goal;
- a manually selected goal is preserved.

## Demographic-aware verified data model

All 102 opportunities now carry:

- `Eligible_Genders`
- `Eligible_Social_Categories`
- `Disability_Eligibility`
- `Demographic_Targeting`
- `Demographic_Eligibility_Notes`
- `Demographic_Benefit_Variants`

The M2 engine evaluates verified gender, social-category and disability restrictions conservatively. M4 uses demographic fit only as a modest tie-breaker; it cannot override M2 eligibility truth or displace strong sector relevance by itself.

## Verified corrections / additions

### PMEGP (OPP021)

PMEGP remains open across the stored gender/social-category profile values, but its revised official guidelines contain special-category contribution/subsidy terms. A profile-specific benefit variant is stored for SC/ST/OBC/Minority, Female/Transgender, and persons with disabilities:

- 5% beneficiary contribution
- 25% margin-money subsidy for urban projects
- 35% margin-money subsidy for rural projects

Official evidence:
`https://www.kviconline.gov.in/pmegpeportal/dashboard/notification/Revised_PMEGP_Scheme_Guidelines_07122023_compressed.pdf`

### TWEES (OPP061)

Corrected deterministic gender applicability to **Female OR Transgender** based on the current Tamil Nadu MSME TWEES FAQ.

Official evidence:
`https://msmeonline.tn.gov.in/twees/pdf/twees_faqs.pdf`

### AABCS (OPP071)

Corrected social-category applicability to **SC OR ST** based on the Tamil Nadu MSME official AABCS page.

Official evidence:
`https://msmeonline.tn.gov.in/aabcs/aabcs_desc.php`

### New OPP101 — NMDFC Term Loan Scheme

Added to cover the verified minority-entrepreneur financing gap.

- Eligible social category: Minority
- Credit Line-2 annual family income ceiling encoded at ₹8 lakh
- Gender: not a general eligibility restriction
- Verified benefit variant: Credit Line-2 rate is 6% p.a. for women vs 8% p.a. for male beneficiaries

Official source:
`https://nmdfc.org/credit-2`

### New OPP102 — NDFDC Divyangjan Swavalamban Yojana

Added to cover the verified disability-focused entrepreneurship/credit gap.

- Specifically for eligible persons with disabilities
- 40%+ disability / UDID requirement represented in verified scheme data
- self-employment component supported
- verified benefit variant for the official 1% interest rebate described for qualifying women with disabilities on self-employment loans up to ₹50,000

Official source:
`https://www.ndfdc.nic.in/schemes/DIVYANGJAN%20SWAVALAMBAN%20YOJANA.pdf`

## Dataset totals

- Opportunities: **102**
- Canonical requirements: **379**
- Verified relationships: **534**
- Focus sectors: **10**

The two new opportunities reuse the existing sector taxonomy instead of inventing new sectors.

## Safety / provenance rules preserved

- AI/NLP does not determine scheme eligibility.
- M1 remains the verified scheme/requirement/source layer.
- M2 remains the deterministic eligibility and gap layer.
- M4 ranks only M2-safe opportunities.
- User progress does not mutate canonical M1/M2 data.
- No demographic benefit is displayed unless a verified variant explicitly matches the user's saved profile.
- No replacement scheme or special benefit was invented when an official source could not verify it.

## Verification

- Frontend JavaScript syntax check: PASS
- Full Python test suite: **415 passed**
- `/api/health`: 102 opportunities / 379 requirements / 534 relationships
- `/api/opportunities?limit=200`: all 102 opportunities available
- Demographic M2 regression coverage added for TWEES, AABCS, NMDFC and NDFDC
- Fresh re-extraction regression coverage added
- Scheme Detail demographic/personalized-benefit UI regression coverage added
