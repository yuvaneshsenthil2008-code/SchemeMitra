# OpportunityOS v2 — API Contract

Use `/api` as the versionless MVP prefix. Keep internal module APIs behind the FastAPI layer.

## GET /api/health
Returns backend/module readiness and catalogue count.

Example response:
```json
{
  "status": "ok",
  "catalogue_count": 100,
  "modules": {"m1": true, "m2": true, "m3": true, "m4": true}
}
```

## GET /api/opportunities
Public catalogue discovery. Supports sector/search/filter parameters. Must not require a profile.

## GET /api/opportunities/{opportunity_id}
Public full opportunity detail from M1. Include official source and lifecycle/verification metadata when available.

## POST /api/profile/parse
Input:
```json
{"message":"I am 24 and want to start a food business in Tamil Nadu","session_id":"optional"}
```
Output includes extracted/merged canonical profile, missing profile fields, language/confidence/provenance, and conflicts requiring review. It does not include eligibility decisions.

## POST /api/eligibility/check
Input:
```json
{"profile": {}}
```
Uses canonical profile. Returns M2 eligibility/gap results. No M4 ranking.

## POST /api/opportunities/recommend
Input:
```json
{"profile": {}}
```
Runs M2 then M4. Returns normal recommendations, potentially eligible items, Needs Verification, and not-eligible diagnostics where appropriate.

## POST /api/pathway/generate
Input:
```json
{"profile": {}, "opportunity_id":"OPP...", "business_goal":"optional"}
```
Returns M2 Opportunity Pathway. M4/frontend may present it, but may not manufacture missing edges.

## POST /api/analyze
Primary personalized endpoint.

Input:
```json
{
  "profile": {},
  "selected_opportunity_id": null
}
```

Output must conform to `schemas/CANONICAL_ANALYZE_RESPONSE_SCHEMA.json`.

## Contract notes
- New code uses `opportunity_id`, not `scheme_id`.
- HTTP 200 with explicit eligibility status is preferred for a valid request even when the user is not eligible.
- Validation errors use 422; server/integration failures use appropriate 5xx.
- No silent mock fallback in production/demo mode.
