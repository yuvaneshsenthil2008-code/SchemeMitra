# OpportunityOS v2 — M3 Upgrade Report

M3 is aligned to the M2 v2.1 EntrepreneurProfile contract.

## Guarantees
- M3 extracts/normalizes user facts only; M2 remains eligibility source of truth.
- Exports annual_income, business_stage, target/entity fields, greenfield/existing/street-vendor evidence, registrations, certifications, trainings, documents, and explicit gap evidence.
- Unknown prerequisite evidence remains unknown; it is never invented as completed.
- Transgender is canonical and is not normalized to Female.
- Existing English/Tamil/Hindi/multilingual hybrid pipeline and optional speech-to-text interface are preserved.
- Voice transcript must still be reviewed/confirmed by the frontend before persistent profile save.

## Boundary
UI localization is not performed by M3. Flutter/web localization must translate interface labels separately.
