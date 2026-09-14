# OpportunityOS — M3 NLP / AI

This folder is the completed M3 conversation/NLP layer for OpportunityOS. It is designed to sit between the user/frontend and M2 eligibility.

## Core rule

M3 **extracts and structures user information**. It does not decide scheme eligibility and it does not rank schemes. M2 owns eligibility truth. M4 owns support preference ranking, loan-first display, pathway generation, and alternative opportunities.

## Architecture

```text
nlp_ai/
├── nlp/
│   ├── __init__.py
│   ├── language_detector.py
│   ├── entity_extractor.py
│   ├── rule_extractor.py
│   ├── llm_extractor.py
│   ├── profile_extractor.py
│   ├── intent_detector.py
│   ├── normalizer.py
│   ├── validator.py
│   ├── missing_info.py
│   ├── confidence.py
│   ├── money_parser.py
│   ├── support_inference.py
│   └── m2_adapter.py
├── ai/
│   ├── __init__.py
│   ├── ai_assistant.py
│   └── explanation_generator.py
├── multilingual/
│   ├── __init__.py
│   ├── translator.py
│   └── language_config.py
├── voice/
│   ├── __init__.py
│   └── speech_interface.py
├── tests/
│   ├── conftest.py
│   ├── test_ai_assistant.py
│   ├── test_nlp_pipeline.py
│   ├── test_stress_conversations.py
│   ├── test_stress_edge_cases.py
│   ├── test_stress_semantic_cases.py
│   ├── test_extended_multilingual.py
│   ├── test_hybrid_llm.py
│   ├── test_m2_contract.py
│   ├── test_error_recovery.py
│   ├── test_extraction.py
│   ├── test_intent.py
│   └── test_profiles.json
├── requirements.txt
├── .env.example
└── README.md
```

## What it handles

- Stateful one-by-one conversation and profile memory.
- Contextual short answers based on the previously asked field.
- Follow-up questions only for missing core eligibility information.
- Profile merging across messages.
- Conflict detection without silently overwriting previous data.
- Conflict resolution on a later user turn.
- Conservative implicit facts such as `planning to start` → `Startup`.
- Age, gender, state, education, category, sector, business stage, income, project cost, available capital, artisan trade.
- Indian money forms such as `₹25,000`, `25k`, `2 lakh`, `2.5L`, `1cr`, commas and decimals.
- Monthly/yearly income period tracking. Monthly income is annualized only at the M2 export boundary.
- Safe typo handling for closed/contextual answers such as `tamilnaduu`, `dgree`, `genral`, `femle`.
- Tamil/Tanglish and Hindi/Hinglish rules and conversation prompts.
- Native-script support and LLM fallback design for Telugu, Kannada, Malayalam, Bengali, Marathi, Gujarati, Punjabi and Odia.
- Mixed-script/language detection.
- Opportunity/general/unclear intent detection.
- Rule-first + optional LLM hybrid extraction.
- Per-field confidence/provenance.
- Safe failure when the LLM, translator, voice device, or optional packages are unavailable.
- Canonical M2/M4 output contract.

## Hybrid NLU flow

```text
User message
   ↓
Intent detection
   ↓
Language / script detection
   ↓
Deterministic rule + contextual extraction
   ↓
Optional LLM fallback only when configured/useful
   ↓
Rule-vs-LLM conflict detection
   ↓
Normalization
   ↓
Confidence/provenance
   ↓
Validation + missing fields
   ↓
Stateful AIAssistant
   ↓
M2 canonical profile
```

Rules have priority when both rules and the LLM extract the same field differently. A conflict record is exposed instead of letting the model silently replace deterministic evidence.

## LLM connection

The core works with **no API key**. To enable an LLM, use either an injected Python callable or an OpenAI-compatible chat-completions endpoint.

Environment variables:

```text
LLM_BASE_URL=<full chat-completions endpoint>
LLM_API_KEY=<your key>
LLM_MODEL=<model id>
```

The LLM prompt explicitly forbids guessing unsupported profile data, deciding eligibility, ranking schemes, or creating `preferred_support_types`.

You can also inject a provider directly:

```python
from nlp.llm_extractor import LLMExtractor
from nlp.profile_extractor import ProfileExtractor


def my_llm(**kwargs):
    # Call your chosen provider and return a Python dict/JSON object.
    return {"age": 24, "state": "Tamil Nadu"}

extractor = ProfileExtractor(
    llm_extractor=LLMExtractor(client=my_llm)
)
```

## NLU + NLG

NLU is handled by the `nlp/` pipeline. NLG is handled by:

- localized follow-up templates in `multilingual/language_config.py`,
- conflict/error messages in `AIAssistant`,
- `ai/explanation_generator.py` for safe profile/conversation summaries.

M2 eligibility explanations should remain with M2 because M3 must not manufacture reasons for scheme eligibility.

## Preferred support vs inferred support

These are intentionally different:

```text
preferred_support_types
= explicit user/frontend selection

support_needs
= needs inferred from what the user says
```

Example:

```python
assistant.set_preferred_support_types(["LOAN"])
assistant.process_message(
    "I need a loan and I also need help marketing my products"
)
```

M3 can produce:

```json
{
  "preferred_support_types": ["LOAN"],
  "support_needs": ["LOAN", "MARKET_SUPPORT"]
}
```

M3 does **not** filter schemes using this choice. M4 should use it as a ranking/display preference:

```text
1. Preferred Support Matches
2. Inferred Need Matches
3. Other Eligible Opportunities
```

This means choosing `LOAN` does not hide an eligible subsidy, grant, training program, or market-support opportunity.

`FINANCE` may be emitted in `support_needs` when the user vaguely says `funding` or `financial help`. M4 should map that broad need across appropriate financing mechanisms rather than M3 guessing loan vs grant vs subsidy.

## M2 integration contract

Use:

```python
payload = assistant.to_m2_payload()
```

Example output:

```json
{
  "profile": {
    "age": 24,
    "gender": "Female",
    "category": "SC",
    "state": "Tamil Nadu",
    "district": null,
    "annual_income": 300000,
    "available_capital": null,
    "project_cost": 500000,
    "education": "Degree",
    "sector": "Food",
    "business_stage": "Startup",
    "business_goal": "START_BUSINESS",
    "preferred_support_types": ["LOAN"],
    "support_needs": ["LOAN", "MARKET_SUPPORT"],
    "artisan_trade": null,
    "new_business": true
  }
}
```

Internal backward-compatible M3 names remain:

```text
income         → annual_income at export
business_type  → business_stage at export
```

This prevents the existing NLP conversation implementation from being broken just to satisfy the cross-module contract.

## Quick usage

```python
from ai.ai_assistant import AIAssistant

assistant = AIAssistant()

print(assistant.process_message("I want to start a food business"))
print(assistant.process_message("24"))
print(assistant.process_message("Female"))

assistant.set_preferred_support_types(["LOAN", "MARKET_SUPPORT"])
print(assistant.to_m2_payload())
```

## Tests

From inside `nlp_ai`:

```powershell
python -m pytest -v
```

The completed package contains the original v3.6 regression/stress/edge/semantic tests plus added hybrid, multilingual, error-recovery, and M2-contract tests.

It can also be run from the repository parent:

```powershell
python -m pytest nlp_ai/tests -v
```

`tests/conftest.py` makes the existing `from ai...` / `from nlp...` imports work from either location.

## Voice

`voice/speech_interface.py` is optional. The core NLP does not depend on microphone libraries. For local voice support, install the optional packages listed as comments in `requirements.txt` and ensure the OS microphone/TTS dependencies are available.

## Safety / data-quality policy

- Missing data stays missing.
- A bare number is not assigned to age/income/project cost unless context justifies it.
- Facts clearly referring to another person are not assigned to the user.
- LLM output cannot override a conflicting deterministic rule silently.
- Preferred support is user-selected, not guessed.
- M3 never decides scheme eligibility.
- M4, not M3, controls loan-first/other-scheme ranking and display.
