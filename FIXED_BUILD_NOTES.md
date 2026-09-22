# SchemeMitra Fixed Build Notes

This build was prepared from the supplied SchemeMitra project with regression-safe fixes. Existing M1/M2/M4 ground-truth semantics and the working Opportunity Graph were intentionally preserved.

## Fixes applied

- Fixed the post-extraction JavaScript runtime error `noticeText is not defined` and separated network/extraction errors from UI-render errors.
- Preserved `education_course` (for example `B.Tech`) through `/api/profile/parse` instead of dropping it during profile sanitization.
- Added a visible Degree / Course field while preserving the existing qualification and field-of-study model.
- Strengthened Tamil/Hindi native and code-switched extraction for Chennai, degree/course terms, Computer Science/CSE, business-start intent, and common agriculture/retail expressions.
- Preserved third-party safeguards so a friend's education/location is not assigned to the user.
- Removed the active Prepared Documents / reusable-artifact feature while keeping canonical DOCUMENT, DPR, IDENTITY_PROOF and other scheme requirements.
- Kept `Completed Actions`, `Mark Completed`, server-side persistence, and Reopen as the single requirement-progress model.
- Simplified Goal Pathway completion refresh to use the authoritative server response.
- Kept the old `user_artifacts` SQLite table only as harmless legacy/reset cleanup; no active artifact APIs remain.
- Corrected profile localization keys for qualification/course placeholders and messages.

## Verification performed

- `python scratch/check_js_syntax.py` — PASS for all frontend JS files.
- `python -m pytest -q` — **391 passed**.
- `/api/profile/parse` directly verified for English, Tamil and Hindi.
- `/api/analyze` directly verified with HTTP 200.
- Goal Pathway Mark Completed → persisted → Completed Actions → Reopen directly verified using a temporary client ID.
- Confirmed no active `/api/pathway/artifacts*` routes remain.

## Runtime note

Run only one SchemeMitra server on `127.0.0.1:8000`. If Windows reports `WinError 10048`, another process is already using port 8000. Verify/stop the old server before starting this build; otherwise the browser may be connected to an older SchemeMitra copy and show stale behavior such as `Failed to fetch` or missing fixes.
