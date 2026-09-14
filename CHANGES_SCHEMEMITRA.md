# SchemeMitra Refinement Pass

## Product identity
- Renamed public-facing product to **SchemeMitra**
- Tagline: **AI-powered scheme matching for entrepreneurs**
- Updated FastAPI metadata and public UI branding

## Age applicability
- Ages 1–120 remain valid profile data
- Personalized entrepreneur matching is gated to age 18+
- Under-18 profiles are saved but receive no personalized entrepreneurship recommendations
- Public Explore catalogue remains available

## Support filter simplification
Public support filters are now:
- Loan / Credit
- Subsidy / Grant
- Training & Skill Support
- Infrastructure & Equipment
- Market & Export Support
- Other Support

Detailed verified support taxonomy remains unchanged internally.

## Voice input
- Continuous/interim speech recognition retained
- Auto-stops after 3 seconds of no speech
- Uses up to 3 recognition alternatives
- Preserves transcript across pauses
- Manual Stop remains available

## Natural-language profile extraction
- Expanded Indian city/district -> state mapping
- Expanded education field recognition
- Does not infer a degree from field name alone
- Explicit qualifications such as B.Tech CSE / M.Tech AI are extracted correctly
- E-shop/e-commerce is treated as retail/MSME activity unless startup/innovation is explicitly stated
- Planning to build/open/launch/create a business is recognized as Idea stage

## Navigation
- Desktop top navbar auto-hides
- Slides down when pointer reaches the top edge
- Slides back up when pointer moves away
- Mobile navbar remains visible/sticky for usability

## Verification
- Python test suite: 313 passed
- JavaScript syntax checks: passed for app.js, profile_builder.js, my_opportunities.js and i18n.js
- Manual browser testing is still recommended for microphone timing and navbar pointer behavior
