# Implementation Plan — SchemeMitra Full Antigravity Package (Revised)

Build SchemeMitra as a public-first, desktop-first government-opportunity portal with deterministic eligibility, gap analysis, verified Opportunity Pathway, Opportunity Graph, and M3 conversational profile extraction, backed by robust runtime crash protection and strict module ownership boundaries.

## User Review Required

> [!IMPORTANT]
> **Strict Core Logic & Module Ownership Boundaries**:
> - **M1 Data**: Factual source of truth (100 official schemes). No fabricated scheme data or false lifecycle statuses.
> - **M2 Engine**: Owns deterministic eligibility classification (`ELIGIBLE`, `POTENTIALLY_ELIGIBLE`, `NEEDS_VERIFICATION`, `NOT_ELIGIBLE`), gap analysis, Opportunity Graph edge validation, and Opportunity Pathway generation.
> - **M3 NLP/AI**: Multilingual conversational profile extraction ONLY. M3 MUST NOT decide scheme eligibility or rank schemes.
> - **M4 Ranking**: Safe ranking/recommendation of M2-recommendable schemes. M4 MUST NOT invent eligibility rules, missing requirements, graph edges, or pathway steps.
> - **Canonical Schemas**: Strict adherence to `CANONICAL_PROFILE_SCHEMA.json`, `CANONICAL_ANALYZE_RESPONSE_SCHEMA.json`, `API_CONTRACT.md`, and `FINAL_INTEGRATION_SPEC.md`.

> [!WARNING]
> **Runtime Crash Protection Architecture**:
> - **Global Error Boundary**: Catch-all UI fallback preventing full-page "red screen" or blank screen crashes.
> - **Centralized API Error Handler**: Graceful handling of network, 4xx, 5xx, or malformed API responses with retry/recovery controls.
> - **Schema Validation at Boundary**: Validate API responses against canonical contracts prior to UI rendering.
> - **Dynamic Statistics**: All dataset counts (schemes, sectors, requirements, relationships) fetched dynamically from backend `/api/health` and catalogue data — ZERO hardcoded statistics.
> - **Real Voice Recognition**: Standard browser Web Speech API (`SpeechRecognition`) ONLY when supported; clear fallback message & text input when unsupported or denied. NO fake/simulated speech recognition.

---

## 9-Phase Incremental Implementation Plan

To ensure quality and prevent regressions, development will proceed strictly in 9 sequential phases. Tests will be executed after each phase before advancing.

---

### Phase 1 — Backend Adapters, Canonical Schemas & Health Endpoint

#### Objective
Establish a clean FastAPI backend layer wrapping M1, M2, M3, and M4 with canonical schema validation, dynamic statistics reporting, and `/api/health`.

#### [NEW] [app.py](file:///d:/SCHOOL/Yuvan%20studies/OppoOS/SchemeMitra_v2_FULL_ANTIGRAVITY_PACKAGE/server/app.py)
- Create FastAPI application with CORS middleware, centralized exception handlers (500, 422, 404), and JSON schema validation.
- Implement `/api/health` returning dynamic counts:
  ```json
  {
    "status": "ok",
    "catalogue_count": 100,
    "requirements_count": 371,
    "relationships_count": 522,
    "sectors_count": 10,
    "modules": {"m1": true, "m2": true, "m3": true, "m4": true}
  }
  ```

#### [NEW] [adapters.py](file:///d:/SCHOOL/Yuvan%20studies/OppoOS/SchemeMitra_v2_FULL_ANTIGRAVITY_PACKAGE/server/adapters.py)
- Create data adapters mapping M1/M2/M3/M4 outputs to exact JSON schema specifications:
  - Canonical Profile Adapter: sanitize and validate input against `CANONICAL_PROFILE_SCHEMA.json`.
  - Canonical Analyze Adapter: structure outputs into `recommendations`, `needs_verification`, `not_eligible`, `pathway`, and `graph` adhering strictly to `CANONICAL_ANALYZE_RESPONSE_SCHEMA.json`. Ensure every recommendation has `recommendable = true`, while `needs_verification` has `recommendable = false` and `eligibility_status = "NEEDS_VERIFICATION"`.

#### Verification for Phase 1
- Run `python -m pytest modules/M2_eligibility_graph modules/M3_nlp_ai modules/M4_ranking_pathway`.
- Test `/api/health` endpoint for dynamic statistics.

---

### Phase 2 — Public Home, Sector, Explore & Detail Experience

#### Objective
Build the public-first frontend portal allowing visitors to discover opportunities without a profile.

#### [NEW] [index.html](file:///d:/SCHOOL/Yuvan%20studies/OppoOS/SchemeMitra_v2_FULL_ANTIGRAVITY_PACKAGE/frontend/index.html)
- Desktop-first layout container (1200–1440px inner max-width, full-width section backgrounds).
- **Header**: Logo, Home, Explore Schemes, How It Works, Language Switcher (EN/TA/HI), "Set Your Profile" CTA.
- **Home View**:
  - Government portal hero banner with live search input.
  - Sector Discovery Grid: dynamically populated 10 M1 sectors with real scheme counts.
  - Live Dataset Stats bar (dynamic counts from `/api/health`).
  - How SchemeMitra Works (Explainable eligibility + verified pathways).
  - Clear "Set Your Profile" CTA.
- **Explore / Sector Listing View**:
  - Desktop left filter sidebar (Sector, Support Type, Business Stage, Scope).
  - Top search input + sort options + result count badge.
  - Scheme cards grid with tags, scope, support types, and detail drawer trigger.
  - Zero personalized match percentages or fake eligibility scores before profile creation.
- **Opportunity Detail Drawer / Page**:
  - Comprehensive view displaying M1 scheme facts, benefits summary, eligibility summary, required documents, application route, official source URL, and lifecycle/verification badge.

#### [NEW] [styles.css](file:///d:/SCHOOL/Yuvan%20studies/OppoOS/SchemeMitra_v2_FULL_ANTIGRAVITY_PACKAGE/frontend/styles.css)
- Professional government tech aesthetic (navy/blue slate palette, crisp typography, clean status badges, subtle hover micro-interactions, responsive CSS grid/flexbox for desktop and mobile).

#### Verification for Phase 2
- Test public browsing flow: Home -> Sector -> Explore -> Scheme Detail without creating a profile.
- Verify no match percentages or personalized recommendations are displayed before profile creation.

---

### Phase 3 — Manual Profile Creation & Local Persistence

#### Objective
Provide structured manual profile entry conforming to `CANONICAL_PROFILE_SCHEMA.json` with local storage persistence.

#### [NEW] [profile_form.js](file:///d:/SCHOOL/Yuvan%20studies/OppoOS/SchemeMitra_v2_FULL_ANTIGRAVITY_PACKAGE/frontend/profile_form.js)
- Multi-section manual form:
  - Basic Info: Age, Gender (Male/Female/Transgender), Category, State, District.
  - Financial Info: Annual Income, Available Capital, Project Cost.
  - Business Info: Education, Sector, Business Stage (Idea/Startup/Existing), Business Goal, Artisan Trade, New Business flag.
  - Support & Requirements: Preferred Support Types (Loan, Subsidy, Grant, etc.), Registrations, Certifications, Training, Documents Available.
- **Local Persistence**: Save confirmed profile and selected UI language in `localStorage`.
- **Reset Profile**: Confirmation modal before clearing local profile state.
- **Header update**: Upon profile persistence, header updates CTA to `My Opportunities` and displays `Reset Profile`.

#### Verification for Phase 3
- Create profile manually, refresh browser, verify profile persists in `localStorage`.
- Verify Reset Profile triggers modal prompt and requires confirmation before clearing.

---

### Phase 4 — M3 Conversational Profile Builder + Real Voice & Text Input

#### Objective
Integrate M3 `AIAssistant` for conversational profile extraction with real browser Web Speech API voice input.

#### Backend Endpoints in [app.py](file:///d:/SCHOOL/Yuvan%20studies/OppoOS/SchemeMitra_v2_FULL_ANTIGRAVITY_PACKAGE/server/app.py)
- `POST /api/profile/parse`: calls M3 `AIAssistant.process_message()` to extract canonical profile fields, identify missing profile fields, language, and confidence. Exposes extracted fields for user review — NO eligibility decisions.

#### Frontend Component in [profile_builder.js](file:///d:/SCHOOL/Yuvan%20studies/OppoOS/SchemeMitra_v2_FULL_ANTIGRAVITY_PACKAGE/frontend/profile_builder.js)
- **Primary Voice CTA Wording**: `Speak to build your profile`.
- **Real Web Speech API**: Uses browser `SpeechRecognition` / `webkitSpeechRecognition` ONLY when supported. If unsupported, denied, or failing, displays a clear notification banner and enables typed text input. NO fake speech simulation.
- **Review / Edit / Confirm Flow**:
  1. Speech → Text transcript.
  2. Transcript sent to `POST /api/profile/parse`.
  3. Extracted profile fields rendered in interactive Structured Review card.
  4. User reviews, edits any field manually, and clicks **Confirm Profile**.
  5. Confirmed profile saved to `localStorage`. `Show My Schemes` button activated.
  6. Conversational chat raw history is NOT persisted by default.

#### Verification for Phase 4
- Test speech-to-text / typed input -> M3 profile extraction -> review/edit UI -> confirm profile.
- Verify M3 output contains zero eligibility claims.

---

### Phase 5 — M2 Eligibility & Gap Integration

#### Objective
Connect M2 deterministic eligibility engine (`EligibilityEngine`, `GapAnalyzer`) to evaluate profiles strictly according to deterministic rules.

#### Backend Endpoints in [app.py](file:///d:/SCHOOL/Yuvan%20studies/OppoOS/SchemeMitra_v2_FULL_ANTIGRAVITY_PACKAGE/server/app.py)
- `POST /api/eligibility/check`: input canonical profile, returns M2 deterministic status for all 100 schemes (`ELIGIBLE`, `POTENTIALLY_ELIGIBLE`, `NEEDS_VERIFICATION`, `NOT_ELIGIBLE`) along with passed rules, failed rules, and missing requirement gaps.

#### Safety & Data Rules
- `NOT_ELIGIBLE` returned ONLY from a definitive failed M2 rule.
- `POTENTIALLY_ELIGIBLE` returned when rules are partial or profile data is missing.
- `NEEDS_VERIFICATION` returned when lifecycle status or recommendability is flagged.

#### Verification for Phase 5
- Run M2 test suite: `pytest modules/M2_eligibility_graph/tests`.
- Verify POST `/api/eligibility/check` against test profiles.

---

### Phase 6 — M4 Recommendations & My Opportunities View

#### Objective
Integrate M4 ranking engine to display the personalized `My Opportunities` dashboard.

#### Backend Endpoints in [app.py](file:///d:/SCHOOL/Yuvan%20studies/OppoOS/SchemeMitra_v2_FULL_ANTIGRAVITY_PACKAGE/server/app.py)
- `POST /api/opportunities/recommend`: runs M2 then M4 `RecommendationEngine`.
- `POST /api/analyze`: primary unified personalized endpoint conforming to `schemas/CANONICAL_ANALYZE_RESPONSE_SCHEMA.json`.

#### Safety & Filtering Rules
- `ELIGIBLE` + `recommendable=true`: normal recommendation list.
- `POTENTIALLY_ELIGIBLE` + `recommendable=true`: recommended with missing requirements section.
- `NEEDS_VERIFICATION` or `recommendable=false`: isolated in Needs Verification section ONLY.
- `NOT_ELIGIBLE`: NEVER appears in normal recommendations (placed in diagnostic diagnostic list).

#### Frontend Dashboard in [my_opportunities.js](file:///d:/SCHOOL/Yuvan%20studies/OppoOS/SchemeMitra_v2_FULL_ANTIGRAVITY_PACKAGE/frontend/my_opportunities.js)
- Profile Summary bar with "Edit My Profile" button.
- Tabbed/Sectional structure:
  1. Recommended Opportunities (Ranked list with score, Why You Match tags, support types).
  2. Potentially Eligible / Missing Requirements (Cards showing required actions to become eligible).
  3. Needs Verification (Isolated list for ended schemes like Stand-Up India, SISFS, etc.).

#### Verification for Phase 6
- Run M4 test suite: `pytest modules/M4_ranking_pathway/tests`.
- Verify `NOT_ELIGIBLE` and `recommendable=false` schemes never enter normal recommendations.

---

### Phase 7 — Opportunity Pathway, Opportunity Graph & Application Guide

#### Objective
Render Opportunity Pathway, Opportunity Graph, and Application Guide as distinct, verified features.

#### Opportunity Pathway (M2 Driven)
- Visual node timeline: `Current State` -> `Gap / Missing Requirement` -> `Required Action` -> `Requirement Completed` -> `Opportunity Unlocked` -> `Support Provided` -> `Business Goal`.
- **Strict Rule**: Built strictly from M2 `PathwayEngine`. Non-mandated requirement order clearly labeled as display hint. NOT presented as an application checklist.

#### Opportunity Graph (M1/M2 Data Driven)
- SVG / Canvas network graph visualizing verified scheme relationships from M1 `relationships.json` (`REQUIRED_FOR`, `PROVIDES`).
- **Strict Rule**: Render ONLY verified relationships present in M1/M2 data. DO NOT fabricate cross-scheme edges or dependencies. Unknown edges remain unconnected.

#### Application Guide (Separate Feature)
- Rendered in a separate section/card from the Pathway.
- Details application channels (online portal, bank branch, district industry centre), required physical/digital documents, submission process, verification steps, and status tracking.

#### Verification for Phase 7
- Validate pathway and graph JSON outputs against M1/M2 data source files to confirm no edges are fabricated.

---

### Phase 8 — Localization, Responsive Refinement & Error Handling Verification

#### Objective
Ensure full trilingual localization, mobile responsiveness, and end-to-end runtime crash resilience.

#### Localization in [i18n.js](file:///d:/SCHOOL/Yuvan%20studies/OppoOS/SchemeMitra_v2_FULL_ANTIGRAVITY_PACKAGE/frontend/i18n.js)
- Complete dictionary for English (EN), Tamil (TA), and Hindi (HI) covering all UI headings, navigation items, buttons, form labels, sector titles, and status badges.
- Dynamic language switcher with local storage persistence.

#### Runtime Crash Protection Components
- `GlobalErrorBoundary.js`: Global window error and unhandled rejection catchers displaying a friendly recovery UI with "Try Again" and "Reload Portal" buttons instead of a crash screen.
- `APIClient.js`: Centralized fetch wrapper with timeout, HTTP status checking, canonical response schema validation, and structured error reporting.
- Loading skeletons, empty state illustrations, and backend-offline banner with retry action.

#### Verification for Phase 8
- Test language switching across EN, TA, HI on all views.
- Simulate backend failure (shut down server) and verify UI displays offline banner with retry button without crashing.

---

### Phase 9 — Complete Automated & Manual End-to-End Testing

#### Objective
Execute full verification suite prior to declaring completion.

#### Automated Integration Test Suite in [test_api_integration.py](file:///d:/SCHOOL/Yuvan%20studies/OppoOS/SchemeMitra_v2_FULL_ANTIGRAVITY_PACKAGE/tests/test_api_integration.py)
- Unit & Integration tests covering all FastAPI endpoints (`/api/health`, `/api/opportunities`, `/api/profile/parse`, `/api/eligibility/check`, `/api/opportunities/recommend`, `/api/pathway/generate`, `/api/analyze`).
- Validation against `CANONICAL_ANALYZE_RESPONSE_SCHEMA.json` and `CANONICAL_PROFILE_SCHEMA.json`.
- Enforcement of safety invariants (`NOT_ELIGIBLE` exclusion, `NEEDS_VERIFICATION` isolation).

---

## Final Verification Checklist

Before declaring the project complete, the following verification checks must pass:

- [ ] All existing M2 unit tests pass (`pytest modules/M2_eligibility_graph/tests`).
- [ ] All existing M3 unit tests pass (`pytest modules/M3_nlp_ai/tests`).
- [ ] All existing M4 unit tests pass (`pytest modules/M4_ranking_pathway/tests`).
- [ ] New API integration tests pass (`pytest tests/test_api_integration.py`).
- [ ] Canonical JSON schemas validate successfully for all API responses.
- [ ] Public browsing works fully (Home -> Sector Discovery -> Explore -> Detail) without profile.
- [ ] Dataset statistics (catalogue count, sector count, requirements, relationships) are fetched dynamically from backend.
- [ ] Profile creation via manual form and conversational builder works; extracted fields require review/edit/confirmation.
- [ ] Web Speech API voice input works when supported; clean fallback & notification when unsupported or denied.
- [ ] Confirmed profile persists across browser refreshes in `localStorage`.
- [ ] Reset Profile requires confirmation modal before clearing data.
- [ ] Trilingual UI switching (English, Tamil, Hindi) works across all pages and components.
- [ ] Backend offline state or API errors show friendly retry UI — zero full-page white/red screen crashes.
- [ ] `NOT_ELIGIBLE` schemes never appear in normal recommendation list.
- [ ] `NEEDS_VERIFICATION` and `recommendable=false` schemes are strictly isolated in Needs Verification view.
- [ ] Opportunity Pathway uses verified M2 steps and is kept separate from Application Guide.
- [ ] Opportunity Graph contains zero fabricated edges or false dependencies.
- [ ] Final integration report generated with test counts, limitation notes, and module boundary verifications.
