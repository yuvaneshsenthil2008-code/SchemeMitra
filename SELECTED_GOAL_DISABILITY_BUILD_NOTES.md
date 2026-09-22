# SchemeMitra — Selected Goal + Disability Profile Upgrade

## Added profile fields

- `disability_status`
  - `NONE`
  - `PERSON_WITH_DISABILITY`
  - `PREFER_NOT_TO_SAY`
- `selected_goal`
  - defaults to `GENERAL_READINESS`
  - preset dropdown supports Start Business, Establish Enterprise, Expand Business, Working Capital, Upgrade Unit, Technology Innovation, and Export Development.
  - legacy/custom `business_goal` values remain supported.

## Set Your Profile

- Added Disability dropdown under Personal Details.
- Added Selected Goal dropdown under Business Details.
- Existing saved profiles are migrated in the browser:
  - existing `business_goal` becomes the initial `selected_goal`
  - otherwise `selected_goal = GENERAL_READINESS`
- Natural-language extraction can promote an explicitly extracted `business_goal` into `selected_goal` while the goal is still at the default.

## My Opportunities propagation

The two fields are now carried through the canonical profile and surfaced in:

- My Opportunities profile summary
- Goal Pathway generation
- Goal Pathway “Where You Are Now” context
- Opportunity Graph user-profile metadata
- Opportunity Graph goal node
- Custom Opportunity Graph profile card text
- Scheme Detail / pathway goal display
- Pathway Copilot goal context

## Evidence-safe disability behavior

`disability_status` is currently profile context only. It does **not** change eligibility or ranking unless a verified M1/M2 rule explicitly supports a disability-specific criterion. No scheme facts were invented or altered.

## Backward compatibility

- `business_goal` remains supported for NLP and older code/tests.
- `selected_goal` is the preferred user-selected planning goal.
- Specific selected goals are mirrored to the legacy `business_goal` where required.
- Custom legacy business goals remain valid.

## Verification

- Frontend JS syntax: PASS
- Full pytest suite: **402 passed**
- `/api/analyze` preserves `disability_status` + defaults `selected_goal`
- `/api/pathway/goal/generate` defaults to General Business Readiness
- Changing selected goal changes Goal Pathway goal
- Opportunity Graph carries disability context and the selected goal
