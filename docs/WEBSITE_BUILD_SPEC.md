# OpportunityOS v2 — Website Build Specification

## Design direction
Desktop-first/full-width government-service portal inspired by the information density and discoverability of myScheme, but visually original. Do not reuse the old 720px portrait/mobile web shell.

Use full-width header/hero/section backgrounds with an inner content width around 1200–1440px on desktop. Keep responsive mobile support.

## Global header — no profile
OpportunityOS | Home | Explore Schemes | How It Works | Language | Set Your Profile

Languages for v1 UI: English, Tamil, Hindi.

## Global header — profile exists
OpportunityOS | Home | Explore Schemes | How It Works | Language | My Opportunities | Reset Profile

Reset must require confirmation.

## Public screens
1. Home
   - government-service style hero
   - search/discovery entry
   - 10 sector cards from actual M1 taxonomy
   - real dataset statistics only
   - explanation of OpportunityOS
   - clear Set Your Profile CTA
2. Explore / sector results
   - left filter sidebar on desktop
   - search + sort + result count
   - opportunity cards/list on right
   - no personalized ranking before profile
3. Opportunity detail
   - overview
   - benefits/support
   - eligibility summary
   - documents/requirements where known
   - application route
   - official source
   - lifecycle/verification status where relevant

## Profile screen
- Manual editable sections using canonical profile schema.
- Primary AI CTA wording: `Speak to build your profile`.
- Also support typed conversational input.
- Extracted fields require user review/edit/confirm.
- Persist structured profile + selected language locally across refresh/reopen.
- Do not persist AI chat history by default.
- `Show My Schemes` when enough useful profile data exists.

## My Opportunities
Include:
- profile summary + Edit My Profile
- Recommended
- Potentially Eligible / Missing Information
- Opportunity Pathway
- Opportunity Graph
- Needs Verification
- Application Guide

`NOT_ELIGIBLE` must never appear as a normal recommendation.

## Opportunity Pathway UI
Visualize: Current State -> Gap -> Action -> Opportunity -> Support -> Goal.
Do not label the pathway as an application checklist.

## Opportunity Graph UI
Render only relationships returned by M2/M1. Do not create decorative fake edges in the frontend.

## Application Guide UI
Separate card/section/tab from pathway. Use application route and document metadata from M1.

## Localization
UI localization is a frontend responsibility. M3 multilingual NLP is separate. Do not assume NLP translation automatically localizes UI labels.
