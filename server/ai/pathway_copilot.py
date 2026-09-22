"""
OpportunityOS — AI Pathway Copilot Core Service

Reconstructs backend trusted context from M1/M2, invokes GeminiProvider,
and enforces strict validation & grounding rules.
"""

import hashlib
import json
import logging
import re
from typing import Dict, Any, List, Optional
from server.ai.gemini_provider import GeminiProvider

logger = logging.getLogger("OpportunityOS.PathwayCopilot")

# Global in-memory cache for validated copilot output
_copilot_cache: Dict[str, Dict[str, Any]] = {}


def format_support_type_title(st_code: str) -> str:
    """Format support type code into human-readable label."""
    MAPPING = {
        "SUP_CREDIT": "Loan / Credit",
        "SUP_SUBSIDY": "Capital Subsidy",
        "SUP_TRAINING": "Skill Training & Handholding",
        "SUP_GRANT": "Grant Support",
        "SUP_GUARANTEE": "Credit Guarantee",
        "SUP_RESEARCH": "R&D / Technology Innovation",
        "SUP_INFRASTRUCTURE": "Infrastructure Support",
        "LOAN": "Loan / Credit",
        "CAPITAL_SUBSIDY": "Capital Subsidy",
        "INTEREST_SUBVENTION": "Interest Subvention",
        "CREDIT_GUARANTEE": "Credit Guarantee",
        "GRANT": "Grant Support",
        "SEED_CAPITAL": "Seed Capital",
        "MARGIN_MONEY": "Margin Money Subsidy",
        "TRAINING": "Skill Training",
        "INCUBATION": "Incubation Support"
    }
    return MAPPING.get(st_code, st_code.replace("_", " ").title())


def build_trusted_context(
    profile: Dict[str, Any],
    opportunity_id: str,
    master_opps: List[Dict[str, Any]],
    m2_engines: Dict[str, Any]
) -> Dict[str, Any]:
    """Reconstructs trusted backend context using M1/M2 data and sanitized profile.

    Frontend facts are NOT trusted. All facts come from M1/M2 engines.
    """
    opp_master_map = {x["Opportunity_ID"]: x for x in master_opps}
    opp_info = opp_master_map.get(opportunity_id) or {}
    opp_name = opp_info.get("Opportunity_Name") or opportunity_id

    # 1. Profile Summary (omit missing/null fields)
    prof_sum = {}
    if profile.get("state"): prof_sum["state"] = profile["state"]
    if profile.get("sector"): prof_sum["sector"] = profile["sector"]
    if profile.get("business_stage"): prof_sum["business_stage"] = profile["business_stage"]
    if profile.get("gender"): prof_sum["gender"] = profile["gender"]
    if profile.get("age"): prof_sum["age"] = profile["age"]
    if profile.get("annual_income") is not None and profile.get("annual_income") > 0:
        prof_sum["annual_income"] = profile["annual_income"]
    if profile.get("available_capital") is not None and profile.get("available_capital") > 0:
        prof_sum["available_capital"] = profile["available_capital"]
    if profile.get("project_cost") is not None and profile.get("project_cost") > 0:
        prof_sum["project_cost"] = profile["project_cost"]

    raw_goal = str(profile.get("selected_goal") or profile.get("business_goal") or "GENERAL_READINESS").strip()
    if raw_goal: prof_sum["goal"] = raw_goal

    # 2. M2 Eligibility Evaluation
    eligibility_engine = m2_engines.get("eligibility")
    eval_result = None
    if eligibility_engine:
        try:
            all_evals = eligibility_engine.evaluate_all(profile)
            eval_result = next((e for e in all_evals if e.get("opportunity_id") == opportunity_id), None)
        except Exception:
            eval_result = None

    status = (eval_result.get("eligibility_status") or eval_result.get("status")) if eval_result else "POTENTIALLY_ELIGIBLE"
    rule_comp = eval_result.get("rule_completeness") if eval_result else "SUMMARY_ONLY"
    passed_rules = eval_result.get("passed_rules") or [] if eval_result else []
    failed_rules = eval_result.get("failed_rules") or [] if eval_result else []
    missing_fields = eval_result.get("missing_profile_fields") or [] if eval_result else []

    eligibility_data = {
        "status": status,
        "rule_completeness": rule_comp,
        "passed_rules": passed_rules,
        "failed_rules": failed_rules,
        "unknown_rules": missing_fields
    }

    # 3. M2 Pathway Requirements
    pathway_engine = m2_engines.get("pathway")
    pathway_data = None
    if pathway_engine:
        try:
            pathway_data = pathway_engine.build(profile=profile, opportunity_id=opportunity_id)
        except Exception:
            pathway_data = None

    ordering_confidence = pathway_data.get("ordering_confidence", "NO_OFFICIAL_SEQUENCE") if pathway_data else "NO_OFFICIAL_SEQUENCE"

    official_url = opp_info.get("Official_Source_URL") or opp_info.get("Application_URL")
    official_sources = [url for url in [opp_info.get("Official_Source_URL"), opp_info.get("Application_URL")] if url and isinstance(url, str) and url.strip()]
    # Deduplicate sources
    official_sources = list(dict.fromkeys(official_sources))

    requirements = []
    if pathway_data and "steps" in pathway_data:
        req_idx = 1
        for step in pathway_data["steps"]:
            if step.get("step_type") == "REQUIREMENT":
                rid = f"req_{opportunity_id}_{req_idx}"
                label = step.get("title") or step.get("action_label") or f"Requirement {req_idx}"
                st = step.get("state") or "NEED_TO_CONFIRM"
                requirements.append({
                    "requirement_id": rid,
                    "label": label,
                    "state": st,
                    "category": step.get("category") or "APPLICATION_PREPARATION",
                    "source_url": step.get("official_source_url") or official_url
                })
                req_idx += 1

    # If pathway yielded no requirements, supply baseline M1 requirement nodes if present
    if not requirements:
        requirements = [
            {
                "requirement_id": f"req_{opportunity_id}_1",
                "label": "Enterprise Registration / Eligibility Facts",
                "state": "ACTION_NEEDED" if status == "POTENTIALLY_ELIGIBLE" else ("COMPLETED" if status == "ELIGIBLE" else "NEED_TO_CONFIRM"),
                "category": "ELIGIBILITY",
                "source_url": official_url
            }
        ]

    # 4. Supports / Benefits List
    supports = []
    raw_sups = opp_info.get("Support_Types") or []
    if isinstance(raw_sups, str):
        raw_sups = [raw_sups]

    for idx, s in enumerate(raw_sups):
        sid = f"sup_{opportunity_id}_{idx+1}"
        supports.append({
            "support_id": sid,
            "type": s,
            "label": format_support_type_title(s),
            "source_url": official_url
        })

    if not supports:
        supports = [
            {
                "support_id": f"sup_{opportunity_id}_1",
                "type": "SUP_CREDIT",
                "label": "Government Supported Financial / Credit Scheme",
                "source_url": official_url
            }
        ]

    return {
        "profile_summary": prof_sum,
        "opportunity": {
            "opportunity_id": opportunity_id,
            "name": opp_name,
            "primary_sector": opp_info.get("Primary_Sector"),
            "benefit_summary": opp_info.get("Benefit_Summary")
        },
        "eligibility": eligibility_data,
        "requirements": requirements,
        "supports": supports,
        "official_process": [],
        "ordering_confidence": ordering_confidence,
        "goal": raw_goal or "START_BUSINESS",
        "official_sources": official_sources
    }


def extract_allowed_tokens(trusted_context: Dict[str, Any]) -> set:
    """Extracts all legitimate numbers, amounts, percentages, and URLs from trusted context."""
    allowed = set()
    raw_str = json.dumps(trusted_context)
    
    # Numbers (integers, floats)
    nums = re.findall(r'\b\d+(?:\.\d+)?\b', raw_str)
    for n in nums:
        allowed.add(n)
        try:
            val = float(n)
            if val >= 100000 and val % 100000 == 0:
                allowed.add(f"{int(val//100000)} lakh")
                allowed.add(f"{int(val//100000)}lakh")
            if val >= 10000000 and val % 10000000 == 0:
                allowed.add(f"{int(val//10000000)} crore")
                allowed.add(f"{int(val//10000000)}crore")
        except ValueError:
            pass

    for url in trusted_context.get("official_sources", []):
        if isinstance(url, str):
            allowed.add(url.strip())

    return allowed


def sanitize_free_text_claims(text: str, trusted_context: Dict[str, Any]) -> str:
    """Sanitizes ungrounded monetary amounts, percentages, deadlines/dates, URLs, and approval claims."""
    if not text or not isinstance(text, str):
        return ""

    allowed_tokens = extract_allowed_tokens(trusted_context)
    official_urls = trusted_context.get("official_sources", [])

    # 1. Strip unverified URLs
    def url_sub(match):
        u = match.group(0)
        if any(u.startswith(off_u) for off_u in official_urls):
            return u
        return ""
    text = re.sub(r'https?://[^\s<>"]+', url_sub, text)

    # 2. Sanitize unverified monetary amounts (e.g. ₹10 lakh, INR 5,00,000, 25 lakh)
    money_pattern = re.compile(r'(?:₹|INR|\bRs\.?)\s*(?P<num>[\d,]+(?:\.\d+)?)\s*(?:lakh|crore|thousand|k)?\b|\b(?P<num2>[\d,]+)\s*(?:lakh|crore)\b', re.IGNORECASE)
    def money_replacer(m):
        raw = m.group(0)
        num = m.group('num') or m.group('num2') or ""
        clean_num = num.replace(",", "")
        if clean_num in allowed_tokens or raw.lower() in allowed_tokens:
            return raw
        return "the eligible amount under scheme guidelines"
    text = money_pattern.sub(money_replacer, text)

    # 3. Sanitize unverified percentages (e.g. 50%, 75%)
    pct_pattern = re.compile(r'\b(?P<num>\d+(?:\.\d+)?)\s*%', re.IGNORECASE)
    def pct_replacer(m):
        raw = m.group(0)
        num = m.group('num')
        if num in allowed_tokens or raw in allowed_tokens:
            return raw
        return "the percentage specified under scheme rules"
    text = pct_pattern.sub(pct_replacer, text)

    # 4. Sanitize unverified deadlines / dates (e.g. 31st March 2026, deadline)
    date_pattern = re.compile(r'\b\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s*\d{0,4}\b|\b(?:deadline|due date|expiry date)\b', re.IGNORECASE)
    def date_replacer(m):
        raw = m.group(0)
        if raw in allowed_tokens:
            return raw
        return "the timeline specified in official scheme notices"
    text = date_pattern.sub(date_replacer, text)

    # 5. Sanitize ungrounded approval / fee claims
    text = re.sub(r'\bofficially (?:approved|sanctioned|selected)\b', 'evaluated for eligibility', text, flags=re.IGNORECASE)
    text = re.sub(r'\bguarantee[s]?\s+\d+%\s+success\b', 'supports enterprise setup', text, flags=re.IGNORECASE)
    text = re.sub(r'\bpay\s+(?:₹|INR|Rs\.?)\s*[\d,]+\s+(?:processing|upfront)\s+fee\b', 'follow official fee guidelines if any', text, flags=re.IGNORECASE)

    return text.strip()


def validate_copilot_response(
    raw_output: Dict[str, Any],
    trusted_context: Dict[str, Any]
) -> Dict[str, Any]:
    """Strictly validates Gemini output against backend trusted context.

    Enforces grounding:
    - Strips hallucinated requirement_id or support_id entries.
    - Enforces ordering_basis matching trusted ordering_confidence.
    - Preserves M2 eligibility status without allowing override or claims of official approval.
    - Rejects unknown URLs not in official_sources.
    - Sanitizes ungrounded monetary amounts, percentages, deadlines, and fee claims from free-text.
    """
    if not isinstance(raw_output, dict):
        raise ValueError("Raw output is not a dict")

    summary = sanitize_free_text_claims(str(raw_output.get("summary") or "").strip(), trusted_context)
    current_position = sanitize_free_text_claims(str(raw_output.get("current_position") or "").strip(), trusted_context)
    why_fits = sanitize_free_text_claims(str(raw_output.get("why_this_opportunity_fits") or "").strip(), trusted_context)
    goal_conn = sanitize_free_text_claims(str(raw_output.get("goal_connection") or "").strip(), trusted_context)
    imp_note = sanitize_free_text_claims(str(raw_output.get("important_note") or "").strip(), trusted_context)

    # 1. Validate Priority Actions
    valid_req_map = {r["requirement_id"]: r for r in trusted_context.get("requirements", [])}
    raw_actions = raw_output.get("priority_actions") or []
    validated_actions = []

    is_official_seq = trusted_context.get("ordering_confidence") == "OFFICIAL_SEQUENCE"
    forced_basis = "OFFICIAL_SEQUENCE" if is_official_seq else "PLANNING_GUIDANCE"

    if isinstance(raw_actions, list):
        for act in raw_actions:
            if not isinstance(act, dict): continue
            rid = act.get("requirement_id")
            if rid not in valid_req_map:
                logger.warning("Rejecting unknown requirement_id '%s' from Gemini output", rid)
                continue

            matched_req = valid_req_map[rid]
            title = sanitize_free_text_claims(str(act.get("title") or matched_req["label"]).strip(), trusted_context)
            exp = sanitize_free_text_claims(str(act.get("explanation") or "").strip(), trusted_context)
            prio = str(act.get("priority") or "MEDIUM").upper()
            if prio not in ["HIGH", "MEDIUM", "LOW"]:
                prio = "MEDIUM"

            validated_actions.append({
                "requirement_id": rid,
                "title": title,
                "explanation": exp,
                "priority": prio,
                "ordering_basis": forced_basis
            })

    # If Gemini failed to match actions, build validated fallback actions from trusted requirements
    if not validated_actions:
        for r in trusted_context.get("requirements", []):
            validated_actions.append({
                "requirement_id": r["requirement_id"],
                "title": r["label"],
                "explanation": f"Fulfill requirement: {r['label']} (Status: {r['state']})",
                "priority": "HIGH" if r["state"] == "ACTION_NEEDED" else "MEDIUM",
                "ordering_basis": forced_basis
            })

    # 2. Validate Support Explanations
    valid_sup_map = {s["support_id"]: s for s in trusted_context.get("supports", [])}
    raw_sups = raw_output.get("support_explanation") or []
    validated_sups = []

    if isinstance(raw_sups, list):
        for s_item in raw_sups:
            if not isinstance(s_item, dict): continue
            sid = s_item.get("support_id")
            if sid not in valid_sup_map:
                logger.warning("Rejecting unknown support_id '%s' from Gemini output", sid)
                continue

            matched_sup = valid_sup_map[sid]
            st_label = sanitize_free_text_claims(str(s_item.get("support_type") or matched_sup["label"]).strip(), trusted_context)
            exp = sanitize_free_text_claims(str(s_item.get("explanation") or "").strip(), trusted_context)

            validated_sups.append({
                "support_id": sid,
                "support_type": st_label,
                "explanation": exp
            })

    if not validated_sups:
        for s in trusted_context.get("supports", []):
            validated_sups.append({
                "support_id": s["support_id"],
                "support_type": s["label"],
                "explanation": f"Verified support offered under this opportunity ({s['label']})."
            })

    # 3. Grounding & Wording Safety Checks
    m2_status = trusted_context.get("eligibility", {}).get("status", "POTENTIALLY_ELIGIBLE")

    # Sanitize current position wording according to M2 status contract
    if m2_status == "ELIGIBLE":
        if not current_position or any(w in current_position.lower() for w in ["officially approved", "sanctioned", "guaranteed", "officially selected"]):
            current_position = "Based on the information you provided, SchemeMitra currently finds that you meet the structured eligibility conditions assessed for this opportunity."
    elif m2_status == "POTENTIALLY_ELIGIBLE":
        current_position = "You may be eligible for this opportunity, but some information still needs to be confirmed."
    elif m2_status == "NEEDS_VERIFICATION":
        current_position = "Current official information for this opportunity needs verification before a reliable assessment can be made."
    elif m2_status == "NOT_ELIGIBLE":
        current_position = "Based on the current evaluation, you do not meet one or more required eligibility conditions."

    # Remove any unverified URLs from text
    official_urls = trusted_context.get("official_sources") or []
    url_pattern = re.compile(r'https?://[^\s<>"]+')

    def sanitize_text_urls(text: str) -> str:
        def replace_url(match):
            found_url = match.group(0)
            if any(found_url.startswith(off_u) for off_u in official_urls):
                return found_url
            return "" # Strip unverified URL
        return url_pattern.sub(replace_url, text).strip()

    summary = sanitize_text_urls(summary)
    why_fits = sanitize_text_urls(why_fits)
    goal_conn = sanitize_text_urls(goal_conn)
    imp_note = sanitize_text_urls(imp_note)

    if not summary:
        summary = f"Pathway guidance for {trusted_context.get('opportunity', {}).get('name')} based on your profile."

    return {
        "summary": summary,
        "current_position": current_position,
        "why_this_opportunity_fits": why_fits or "This opportunity aligns with your selected sector and location.",
        "priority_actions": validated_actions,
        "support_explanation": validated_sups,
        "goal_connection": goal_conn or "Fulfilling these steps directly supports establishing your enterprise.",
        "important_note": imp_note or ("This order is planning guidance and is not an official government sequence." if not is_official_seq else "Follow official scheme guidelines during final application submission.")
    }


def compute_profile_fingerprint(profile: Dict[str, Any]) -> str:
    """Computes deterministic MD5 hash of sanitized user profile."""
    clean_dict = {k: v for k, v in profile.items() if v is not None}
    dumped = json.dumps(clean_dict, sort_keys=True)
    return hashlib.md5(dumped.encode("utf-8")).hexdigest()


def build_fallback_response(
    trusted_context: Dict[str, Any],
    fallback_message: str = "Personalized AI explanation is temporarily unavailable. Your verified pathway is still available above."
) -> Dict[str, Any]:
    """Generates structured fallback output when AI provider is unavailable or fails."""
    m2_status = trusted_context.get("eligibility", {}).get("status", "POTENTIALLY_ELIGIBLE")
    is_official_seq = trusted_context.get("ordering_confidence") == "OFFICIAL_SEQUENCE"
    forced_basis = "OFFICIAL_SEQUENCE" if is_official_seq else "PLANNING_GUIDANCE"

    pos_msg = "You may be eligible, but some information still needs to be confirmed."
    if m2_status == "ELIGIBLE":
        pos_msg = "Based on the information you provided, SchemeMitra currently finds that you meet the structured eligibility conditions assessed for this opportunity."
    elif m2_status == "NEEDS_VERIFICATION":
        pos_msg = "Current official information for this opportunity needs verification before a reliable assessment can be made."

    actions = []
    for r in trusted_context.get("requirements", []):
        actions.append({
            "requirement_id": r["requirement_id"],
            "title": r["label"],
            "explanation": f"Verify and complete requirement: {r['label']}",
            "priority": "HIGH" if r["state"] == "ACTION_NEEDED" else "MEDIUM",
            "ordering_basis": forced_basis
        })

    sups = []
    for s in trusted_context.get("supports", []):
        sups.append({
            "support_id": s["support_id"],
            "support_type": s["label"],
            "explanation": f"Verified support offered under this opportunity ({s['label']})."
        })

    return {
        "summary": f"Verified pathway details for {trusted_context.get('opportunity', {}).get('name')}.",
        "current_position": pos_msg,
        "why_this_opportunity_fits": "Opportunity aligns with your confirmed profile sector and location.",
        "priority_actions": actions,
        "support_explanation": sups,
        "goal_connection": "Fulfilling these requirements helps establish your planned business.",
        "important_note": "This order is planning guidance and is not an official government sequence." if not is_official_seq else "Follow official scheme sequence."
    }


def get_pathway_copilot_guidance(
    profile: Dict[str, Any],
    opportunity_id: str,
    language: str,
    master_opps: List[Dict[str, Any]],
    m2_engines: Dict[str, Any],
    provider: Optional[GeminiProvider] = None
) -> Dict[str, Any]:
    """Primary orchestration entry point for Gemini Pathway Copilot."""
    lang = language or "English"
    trusted_context = build_trusted_context(profile, opportunity_id, master_opps, m2_engines)

    prof_hash = compute_profile_fingerprint(profile)
    cache_key = f"{opportunity_id}:{prof_hash}:{trusted_context.get('ordering_confidence')}:{lang}"

    if cache_key in _copilot_cache:
        logger.info("Returning cached copilot guidance for %s (%s)", opportunity_id, lang)
        return _copilot_cache[cache_key]

    active_provider = provider or GeminiProvider()

    ai_data = None
    if active_provider.is_available():
        raw_output = active_provider.generate_copilot_explanation(trusted_context, language=lang)
        if raw_output and isinstance(raw_output, dict):
            try:
                ai_data = validate_copilot_response(raw_output, trusted_context)
            except Exception as val_err:
                logger.warning("Copilot validation failed: %s", val_err)
                ai_data = None

    if ai_data is not None:
        result = {
            "opportunity_id": opportunity_id,
            "language": lang,
            "ai_available": True,
            "copilot_data": ai_data,
            "official_sources": trusted_context.get("official_sources", [])
        }
        _copilot_cache[cache_key] = result
        return result

    # Fallback when AI is unavailable or failed validation
    fallback_data = build_fallback_response(trusted_context)
    return {
        "opportunity_id": opportunity_id,
        "language": lang,
        "ai_available": False,
        "fallback_message": "Personalized AI explanation is temporarily unavailable. Your verified pathway is still available above.",
        "copilot_data": fallback_data,
        "official_sources": trusted_context.get("official_sources", [])
    }
