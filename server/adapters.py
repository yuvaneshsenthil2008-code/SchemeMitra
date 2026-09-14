import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

# Ensure project root is in sys.path
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

M1_DATA_DIR = ROOT_DIR / "modules" / "M1_data"
M2_DATA_DIR = ROOT_DIR / "modules" / "M2_eligibility_graph" / "data"
M4_DATA_DIR = ROOT_DIR / "modules" / "M4_ranking_pathway" / "data"


# Public catalogue filter/search normalization. Raw M1 values remain unchanged.
SUPPORT_FAMILY_MAP = {
    "LOAN_CREDIT": {"CREDIT", "LOAN", "CREDIT_GUARANTEE"},
    "SUBSIDY_GRANT": {"SUBSIDY", "GRANT"},
    "TRAINING_SKILL": {"TRAINING", "SKILL_DEVELOPMENT"},
    "INFRASTRUCTURE_EQUIPMENT": {"INFRASTRUCTURE", "EQUIPMENT_SUPPORT"},
    "MARKET_EXPORT": {"MARKET_ACCESS", "EXPORT_SUPPORT"},
    "OTHER_SUPPORT": {"INCUBATION", "MENTORSHIP", "CERTIFICATION", "FELLOWSHIP", "OTHER_SUPPORT"},
}

CANONICAL_SECTORS = (
    "Agriculture & Allied",
    "Food Processing & Agri Value Addition",
    "MSME & Manufacturing",
    "Finance & Credit",
    "Startup & Innovation",
    "Skills & Employment",
    "Women & SHG Entrepreneurship",
    "Social Empowerment & Inclusive Entrepreneurship",
    "Handicrafts, Handloom & Artisan Economy",
    "Export, Market Access & Business Growth",
)

SECTOR_SEARCH_ALIASES = {
    "agriculture": "Agriculture & Allied", "farming": "Agriculture & Allied", "agri": "Agriculture & Allied",
    "food": "Food Processing & Agri Value Addition", "food processing": "Food Processing & Agri Value Addition", "bakery": "Food Processing & Agri Value Addition",
    "manufacturing": "MSME & Manufacturing", "factory": "MSME & Manufacturing", "msme": "MSME & Manufacturing",
    "finance": "Finance & Credit", "credit": "Finance & Credit", "business finance": "Finance & Credit",
    "startup": "Startup & Innovation", "innovation": "Startup & Innovation", "tech startup": "Startup & Innovation",
    "skills": "Skills & Employment", "training": "Skills & Employment", "employment": "Skills & Employment",
    "women": "Women & SHG Entrepreneurship", "shg": "Women & SHG Entrepreneurship", "self help group": "Women & SHG Entrepreneurship",
    "social empowerment": "Social Empowerment & Inclusive Entrepreneurship", "inclusive entrepreneurship": "Social Empowerment & Inclusive Entrepreneurship",
    "handicraft": "Handicrafts, Handloom & Artisan Economy", "handloom": "Handicrafts, Handloom & Artisan Economy", "artisan": "Handicrafts, Handloom & Artisan Economy", "weaving": "Handicrafts, Handloom & Artisan Economy",
    "export": "Export, Market Access & Business Growth", "market access": "Export, Market Access & Business Growth", "international market": "Export, Market Access & Business Growth",
}


def normalize_search_text(value: Any) -> str:
    """Normalize public search text without mutating source data."""
    import re
    text = str(value or "").lower().replace("&", " and ")
    text = re.sub(r"[\-_–—/\\'’\".,:;()\[\]{}]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def resolve_sector_intent(query: str) -> Optional[str]:
    q = normalize_search_text(query)
    if not q:
        return None
    for sector in CANONICAL_SECTORS:
        if q == normalize_search_text(sector):
            return sector
    return SECTOR_SEARCH_ALIASES.get(q)


def normalize_scope_group(raw_scope: Any) -> Optional[str]:
    """Map current M1 scope strings into simple public Central/State groups."""
    raw = str(raw_scope or "").strip()
    if not raw:
        return None
    low = raw.lower()
    if low.startswith("central"):
        return "CENTRAL"
    # Current state-specific catalogue entries use a state name (for example Tamil Nadu).
    if low in {
        "tamil nadu", "kerala", "karnataka", "andhra pradesh", "telangana", "maharashtra",
        "delhi", "uttar pradesh", "west bengal", "bihar", "rajasthan", "gujarat", "punjab",
        "haryana", "odisha", "assam", "madhya pradesh", "jharkhand", "chhattisgarh", "goa",
    } or low.startswith("state"):
        return "STATE"
    return None


def matches_support_family(support_types: List[str], family: str) -> bool:
    family_key = str(family or "").strip().upper()
    if not family_key:
        return True
    allowed = SUPPORT_FAMILY_MAP.get(family_key)
    if not allowed:
        return False
    actual = {str(x).strip().upper() for x in (support_types or []) if str(x).strip()}
    return bool(actual & allowed)


def _search_score(opportunity: Dict[str, Any], query: str) -> tuple:
    """Return (score, reason) for public catalogue search."""
    q = normalize_search_text(query)
    if not q:
        return (0, None)
    oid = normalize_search_text(opportunity.get("opportunity_id", ""))
    name = normalize_search_text(opportunity.get("opportunity_name", ""))
    sector = normalize_search_text(opportunity.get("primary_sector", ""))
    secondary = " ".join(normalize_search_text(x) for x in opportunity.get("secondary_sectors", []))
    ministry = normalize_search_text(opportunity.get("ministry_department", ""))
    support = " ".join(normalize_search_text(x) for x in opportunity.get("support_types", []))
    benefit = normalize_search_text(opportunity.get("benefit_summary", ""))
    eligibility = normalize_search_text(opportunity.get("eligibility_summary", ""))

    if q == oid:
        return (1000, "Matched opportunity ID")
    if q == name:
        return (950, "Matched scheme name")
    if name.startswith(q):
        return (900, "Matched scheme name")
    q_tokens = [x for x in q.split() if len(x) > 1]
    if q_tokens and all(tok in name.split() or tok in name for tok in q_tokens):
        return (850, "Matched scheme name")
    if q == sector:
        return (800, "Matched sector")
    if q in secondary or q in ministry or q in support:
        return (500, "Related match")
    if q in benefit or q in eligibility:
        return (300, "Related match")
    return (0, None)


def search_opportunities(opportunities: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
    """Sector-intent search or relevance-ranked catalogue search."""
    q = str(query or "").strip()
    if not q:
        return list(opportunities)
    sector_intent = resolve_sector_intent(q)
    if sector_intent:
        return [
            {**o, "match_reason": "Matched sector"}
            for o in opportunities
            if o.get("primary_sector") == sector_intent
        ]
    ranked = []
    for idx, o in enumerate(opportunities):
        score, reason = _search_score(o, q)
        if score > 0:
            ranked.append((score, idx, {**o, "match_reason": reason}))
    ranked.sort(key=lambda x: (-x[0], x[1]))
    return [item for _, _, item in ranked]

def load_json_file(file_path: Path) -> Any:
    if not file_path.exists():
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def normalize_m1_opportunity(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure consistent snake_case field access alongside original M1 fields."""
    secondary_raw = raw.get("Secondary_Sectors") or raw.get("secondary_sectors") or ""
    if isinstance(secondary_raw, str):
        secondary_sectors = [s.strip() for s in secondary_raw.split(";") if s.strip()]
    elif isinstance(secondary_raw, list):
        secondary_sectors = secondary_raw
    else:
        secondary_sectors = []

    support_raw = raw.get("Support_Types") or raw.get("support_types") or ""
    if isinstance(support_raw, str):
        support_types = [s.strip() for s in support_raw.split(";") if s.strip()]
    elif isinstance(support_raw, list):
        support_types = support_raw
    else:
        support_types = []

    rec_val = raw.get("Recommendable") or raw.get("recommendable")
    recommendable = str(rec_val).strip().upper() == "TRUE" if rec_val is not None else True

    normalized = {
        **raw,
        "opportunity_id": raw.get("Opportunity_ID") or raw.get("opportunity_id", ""),
        "opportunity_name": raw.get("Opportunity_Name") or raw.get("opportunity_name", ""),
        "name": raw.get("Opportunity_Name") or raw.get("opportunity_name") or raw.get("name", ""),
        "primary_sector": raw.get("Primary_Sector") or raw.get("primary_sector", ""),
        "secondary_sectors": secondary_sectors,
        "ministry_department": raw.get("Ministry_Department") or raw.get("ministry_department", ""),
        "scope": raw.get("Scope") or raw.get("scope", ""),
        "target_beneficiary": raw.get("Target_Beneficiary") or raw.get("target_beneficiary", ""),
        "benefit_summary": raw.get("Benefit_Summary") or raw.get("benefit_summary", ""),
        "eligibility_summary": raw.get("Eligibility_Summary") or raw.get("eligibility_summary", ""),
        "prerequisite_types": raw.get("Prerequisite_Types") or raw.get("prerequisite_types", ""),
        "required_documents_summary": raw.get("Required_Documents_Summary") or raw.get("required_documents_summary", ""),
        "application_route": raw.get("Application_Route") or raw.get("application_route", ""),
        "official_source_url": raw.get("Official_Source_URL") or raw.get("official_source_url", ""),
        "application_url": raw.get("Application_URL") or raw.get("application_url", ""),
        "lifecycle_status": raw.get("Lifecycle_Status") or raw.get("lifecycle_status", "ACTIVE"),
        "recommendable": recommendable,
        "last_verified": raw.get("Last_Verified") or raw.get("last_verified", ""),
        "verification_notes": raw.get("Verification_Notes") or raw.get("verification_notes", ""),
        "support_types": support_types,
        "rule_completeness": raw.get("Rule_Completeness") or raw.get("rule_completeness", ""),
    }
    return normalized

def get_m1_opportunity_master() -> List[Dict[str, Any]]:
    raw_list = load_json_file(M1_DATA_DIR / "opportunity_master.json")
    return [normalize_m1_opportunity(item) for item in raw_list]

def get_m1_pathway_requirements() -> List[Dict[str, Any]]:
    return load_json_file(M1_DATA_DIR / "pathway_requirements.json")

def get_m1_relationships() -> List[Dict[str, Any]]:
    return load_json_file(M1_DATA_DIR / "relationships.json")

def get_m1_taxonomy() -> Dict[str, Any]:
    return load_json_file(M1_DATA_DIR / "taxonomy.json")

def get_health_stats() -> Dict[str, Any]:
    opps = get_m1_opportunity_master()
    reqs = get_m1_pathway_requirements()
    rels = get_m1_relationships()
    tax = get_m1_taxonomy()
    
    sectors = tax.get("sectors", []) if isinstance(tax, dict) else []
    
    return {
        "status": "ok",
        "pipeline_version": "candidate-pipeline-v2",
        "catalogue_count": len(opps),
        "requirements_count": len(reqs),
        "relationships_count": len(rels),
        "sectors_count": len(sectors),
        "modules": {
            "m1": len(opps) > 0,
            "m2": True,
            "m3": True,
            "m4": True
        }
    }

def sanitize_profile(profile_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Ensure output matches CANONICAL_PROFILE_SCHEMA.json."""
    if not profile_data or not isinstance(profile_data, dict):
        profile_data = {}

    canonical_fields = {
        "age": None,
        "gender": None,
        "category": None,
        "state": None,
        "district": None,
        "annual_income": None,
        "available_capital": None,
        "project_cost": None,
        "education": None,
        "education_field": None,
        "sector": None,
        "business_stage": None,
        "business_goal": None,
        "is_new_unit": None,
        "prior_gov_subsidy": None,
        "family_pmegp_availed": None,
        "preferred_support_types": [],
        "support_needs": [],
        "artisan_trade": None,
        "new_business": None,
        "registrations": [],
        "certifications": [],
        "training_completed": [],
        "documents_available": [],
        "extra": {}
    }

    sanitized = {}
    for key, default in canonical_fields.items():
        val = profile_data.get(key)
        if key == "annual_income" and val is None:
            val = profile_data.get("income")
        if key == "available_capital" and val is None and isinstance(profile_data.get("extra"), dict):
            val = profile_data["extra"].get("available_capital")
        if val is None:
            sanitized[key] = default
        else:
            sanitized[key] = val

    # Validate enums & types
    if sanitized["gender"] not in ["Male", "Female", "Transgender", None]:
        sanitized["gender"] = None
    if sanitized["business_stage"] not in ["Idea", "Startup", "Existing", None]:
        sanitized["business_stage"] = None

    # Handle numeric types safely
    for num_field in ["age", "annual_income", "available_capital", "project_cost"]:
        if sanitized[num_field] is not None:
            try:
                sanitized[num_field] = float(sanitized[num_field]) if "." in str(sanitized[num_field]) else int(sanitized[num_field])
                if sanitized[num_field] < 0:
                    sanitized[num_field] = None
                if num_field == "age" and sanitized[num_field] is not None:
                    if isinstance(sanitized[num_field], bool) or float(sanitized[num_field]).is_integer() is False or not (1 <= sanitized[num_field] <= 120):
                        sanitized[num_field] = None
                    else:
                        sanitized[num_field] = int(sanitized[num_field])
            except (ValueError, TypeError):
                sanitized[num_field] = None

    # Ensure list types
    for list_field in ["preferred_support_types", "support_needs", "registrations", "certifications", "training_completed", "documents_available"]:
        if not isinstance(sanitized[list_field], list):
            sanitized[list_field] = []

    extra_dict = dict(profile_data.get("extra") or {})
    for k in ("missing_registrations", "unregistered_business", "available_capital", "is_new_unit", "prior_gov_subsidy", "family_pmegp_availed", "pms_events_availed_this_fy", "udyam_registered", "udyam_category"):
        if k in profile_data and profile_data[k] is not None:
            extra_dict[k] = profile_data[k]
        elif isinstance(profile_data.get("extra"), dict) and k in profile_data["extra"] and profile_data["extra"][k] is not None:
            extra_dict[k] = profile_data["extra"][k]

    for bool_field in ["is_new_unit", "prior_gov_subsidy", "family_pmegp_availed"]:
        val = profile_data.get(bool_field)
        if val is None:
            val = extra_dict.get(bool_field)
        sanitized[bool_field] = val

    sanitized["extra"] = extra_dict

    # Deterministic normalization of udyam_registered from explicit evidence
    registrations = sanitized.get("registrations") or []
    missing_regs = extra_dict.get("missing_registrations") or sanitized.get("missing_registrations") or []
    if sanitized.get("udyam_registered") is None:
        if any("udyam" in str(r).lower() for r in registrations):
            sanitized["udyam_registered"] = True
        elif any("udyam" in str(r).lower() for r in missing_regs) or extra_dict.get("unregistered_business") is True:
            sanitized["udyam_registered"] = False

    return sanitized

def filter_candidate_set(opportunities: List[Dict[str, Any]], profile: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Filters full catalogue into RELEVANT, RELEVANT_NEEDS_PROFILE_INFO, and FILTERED_OUT.
    Reuses M2 structured rules and M1 metadata evidence.
    """
    if not profile or not isinstance(profile, dict):
        profile = {}

    m2_rules_list = load_json_file(M2_DATA_DIR / "eligibility_rules.json")
    m2_rules_dict = {r["Opportunity_ID"]: r for r in m2_rules_list}

    user_sector = profile.get("sector")
    user_state = profile.get("state")
    user_gender = profile.get("gender")
    user_category = profile.get("category")

    relevant = []
    relevant_needs_info = []
    filtered_out = []
    candidate_set = []

    for opp in opportunities:
        oid = opp.get("opportunity_id", "")
        oname = opp.get("opportunity_name") or opp.get("name") or ""
        p_sec = opp.get("primary_sector", "")
        s_secs = opp.get("secondary_sectors", [])
        scope = str(opp.get("scope") or "").strip()
        beneficiary = opp.get("target_beneficiary") or ""
        benefit_sum = opp.get("benefit_summary") or ""
        elig_sum = opp.get("eligibility_summary") or ""
        text_content = f"{oname} {benefit_sum} {elig_sum} {beneficiary}".lower()

        m2_rule = m2_rules_dict.get(oid, {})

        # STAGE 1: GEOGRAPHY & DOMAIN RELEVANCE
        geo_ok = scope.lower().startswith("central") or scope == user_state
        
        is_direct_sector = (p_sec == user_sector or user_sector in s_secs)
        has_value_chain_link = any(kw in text_content for kw in [
            "food processing", "agro processing", "cold chain", "processed food", "agri value", "post-harvest"
        ])

        # Trade & Specialized Domain Restrictions
        is_trade_restricted = any(kw in text_content or kw in p_sec.lower() for kw in [
            "coir", "silk", "handloom", "weaver", "handicraft", "artisan", "leather", "rubber", "tea", "coffee", "cardamom", "beekeeping", "livestock"
        ]) and not has_value_chain_link and not is_direct_sector

        # Technology Domain Restrictions
        is_tech_domain_restricted = any(kw in text_content for kw in [
            "ict/emerging tech", "software/product startups", "biotechnology innovation", "biotech"
        ]) and not has_value_chain_link and not is_direct_sector

        # Specific Entity Restrictions
        is_entity_restricted = any(kw in text_content for kw in ["street vendor"]) and not is_direct_sector and not has_value_chain_link

        # Factual Universal Horizontal MSME / Credit / Startup Applicability (Scheme-level evidence)
        is_general_credit_or_startup = (
            (p_sec in ["Multi-Sector & General MSME", "Finance & Credit", "Startup & Innovation", "Social Empowerment & Inclusive Entrepreneurship", "Women & SHG Entrepreneurship", "MSME & Manufacturing"] or "Multi-Sector & General MSME" in s_secs) and
            not is_trade_restricted and
            not is_tech_domain_restricted and
            not is_entity_restricted and
            any(kw in text_content for kw in [
                "micro-enterprises", "micro and small enterprises", "startups", 
                "credit guarantee", "mudra", "greenfield", "incubation", "seed support", "nidhi", "genesis"
            ])
        )

        domain_relevant = (is_direct_sector or has_value_chain_link or is_general_credit_or_startup) and not is_trade_restricted and not is_tech_domain_restricted and not is_entity_restricted

        if not geo_ok or not domain_relevant:
            known_mismatches = []
            if not geo_ok: known_mismatches.append(f"Geography scope '{scope}' vs state '{user_state}'")
            if is_trade_restricted: known_mismatches.append("Specialized trade domain restriction (Coir/Handloom/Silk/Rubber/Tea) vs Food Processing")
            if is_tech_domain_restricted: known_mismatches.append("Specialized tech domain restriction (ICT, Software, Biotech) vs Food Processing")
            if is_entity_restricted: known_mismatches.append("Entity restriction (Street Vendor) vs general enterprise")
            if not (is_direct_sector or has_value_chain_link or is_general_credit_or_startup): known_mismatches.append(f"Sector mismatch ({p_sec}) without food processing link")

            filtered_out.append({
                "opportunity": opp,
                "domain_relevant": False,
                "relevance_state": "FILTERED_OUT",
                "reason": "; ".join(known_mismatches)
            })
            continue

        # STAGE 2: APPLICABILITY REQUIREMENTS & PROFILE COMPLETENESS
        required_profile_fields = []
        known_matches = []
        if is_direct_sector: known_matches.append(f"sector: {user_sector}")
        if geo_ok: known_matches.append(f"state: {user_state}")
        known_mismatches = []
        unknown_requirements = []

        # M2 Gender Rule
        gender_rule = m2_rule.get("Gender_Rule", "")
        if "Transgender" in gender_rule or "transgender" in text_content:
            required_profile_fields.append("gender: Transgender")
            if user_gender != "Transgender":
                known_mismatches.append(f"gender: Transgender (user is {user_gender})")
        elif "Female" in gender_rule or "women" in text_content or "female" in text_content:
            required_profile_fields.append("gender: Female")
            if user_gender == "Female":
                known_matches.append("gender: Female")

        # M2 Social Category Rule
        category_rule = m2_rule.get("Social_Category_Rule", "")
        cat_req = None
        if category_rule in ["Scheduled Caste", "Scheduled Tribe", "Notified Backward Classes"]:
            cat_req = category_rule
        elif "scheduled caste" in text_content or "sc certificate" in text_content or "nsfdc" in text_content:
            cat_req = "Scheduled Caste"
        elif "backward class" in text_content or "nbcfdc" in text_content:
            cat_req = "Notified Backward Classes"
        elif "scheduled tribe" in text_content or "nstfdc" in text_content:
            cat_req = "Scheduled Tribe"

        if cat_req:
            required_profile_fields.append(f"category: {cat_req}")
            if user_category is None:
                unknown_requirements.append(f"category: {cat_req}")
            elif user_category == cat_req:
                known_matches.append(f"category: {cat_req}")
            else:
                known_mismatches.append(f"category: {cat_req} (user is {user_category})")

        # Entity Requirements (SHG, FPO, Cooperative)
        if any(k in text_content for k in ["shg member", "shg seed"]):
            required_profile_fields.append("shg_membership")
            shg_val = profile.get("shg_membership") if "shg_membership" in profile else profile.get("extra", {}).get("shg_membership")
            if shg_val is None:
                unknown_requirements.append("shg_membership")
            elif shg_val is True or str(shg_val).lower() == "true":
                known_matches.append("shg_membership: True")
            else:
                known_mismatches.append(f"shg_membership: {shg_val}")

        if any(k in text_content for k in ["fpo", "producer cooperative", "collective entity"]):
            required_profile_fields.append("entity_type: FPO/SHG/Cooperative")
            ent_val = profile.get("entity_type") if "entity_type" in profile else profile.get("extra", {}).get("entity_type")
            if ent_val is None:
                unknown_requirements.append("entity_type: FPO/SHG/Cooperative")
            elif str(ent_val).upper() in ["FPO", "SHG", "COOPERATIVE", "PRODUCER COOPERATIVE"]:
                known_matches.append(f"entity_type: {ent_val}")
            else:
                known_mismatches.append(f"entity_type: {ent_val}")

        # DPIIT Recognition
        prereq_types = opp.get("prerequisite_types") or opp.get("Prerequisite_Types") or ""
        if "DPIIT_RECOGNITION" in prereq_types or "dpiit-recognised" in text_content or "dpiit recognised" in text_content or "dpiit recognition" in text_content:
            required_profile_fields.append("dpiit_recognition")
            dpiit_val = profile.get("dpiit_recognition") if "dpiit_recognition" in profile else profile.get("extra", {}).get("dpiit_recognition")
            if dpiit_val is None:
                unknown_requirements.append("DPIIT recognition")
            elif dpiit_val is True or str(dpiit_val).lower() == "true":
                known_matches.append("DPIIT recognition: True")
            else:
                known_mismatches.append(f"DPIIT recognition: {dpiit_val}")

        # Incubator Linkage / TBI / PRAYAS Centre
        if "INCUBATOR_LINKAGE" in prereq_types or "INCUBATOR_APPLICATION" in prereq_types or any(k in text_content for k in ["incubator linkage", "tbi incubation", "prayas centre", "designated tbi"]):
            required_profile_fields.append("incubator_linkage")
            inc_val = profile.get("incubator_linkage") if "incubator_linkage" in profile else profile.get("extra", {}).get("incubator_linkage")
            if inc_val is None:
                unknown_requirements.append("Incubator linkage")
            elif inc_val is True or str(inc_val).lower() == "true":
                known_matches.append("Incubator linkage: True")
            else:
                known_mismatches.append(f"Incubator linkage: {inc_val}")

        # Strict Existing Unit Requirement
        if any(k in text_content for k in ["existing micro-enterprise", "existing unit in operation", "commercial operation for 3 years"]):
            required_profile_fields.append("business_stage: Existing")
            stage_val = profile.get("business_stage")
            if stage_val is None:
                unknown_requirements.append("Business stage (existing enterprise required)")
            elif stage_val == "Existing":
                known_matches.append("business_stage: Existing")
            elif stage_val == "Idea":
                known_mismatches.append("Existing operating enterprise required (user is in Idea stage)")

        # Decision Rules
        if known_mismatches:
            relevance_state = "FILTERED_OUT"
            reason = f"Known profile mismatch: {'; '.join(known_mismatches)}"
            filtered_out.append({
                "opportunity": opp,
                "domain_relevant": True,
                "relevance_state": relevance_state,
                "reason": reason
            })
        elif unknown_requirements:
            relevance_state = "RELEVANT_NEEDS_PROFILE_INFO"
            reason = f"Scheme is domain-relevant, but requires: {', '.join(unknown_requirements)}"
            item = {
                "opportunity": opp,
                "domain_relevant": True,
                "relevance_state": relevance_state,
                "reason": reason,
                "unknown_requirements": unknown_requirements
            }
            relevant_needs_info.append(item)
            candidate_set.append(opp)
        else:
            relevance_state = "RELEVANT"
            reason = "Geographically & domain relevant; profile satisfies or matches scheme criteria"
            item = {
                "opportunity": opp,
                "domain_relevant": True,
                "relevance_state": relevance_state,
                "reason": reason
            }
            relevant.append(item)
            candidate_set.append(opp)

    return {
        "candidate_set": candidate_set,
        "relevant": relevant,
        "relevant_needs_info": relevant_needs_info,
        "filtered_out": filtered_out,
        "summary": {
            "catalogue_count": len(opportunities),
            "relevant_count": len(relevant),
            "relevant_needs_info_count": len(relevant_needs_info),
            "filtered_out_count": len(filtered_out),
            "candidate_set_count": len(candidate_set)
        }
    }

def format_analyze_response(
    profile: Dict[str, Any],
    m4_output: Dict[str, Any],
    pathway_output: Optional[Dict[str, Any]] = None,
    graph_output: Optional[Dict[str, Any]] = None,
    relevance_summary: Optional[Dict[str, Any]] = None,
    relevance_res: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Format M4 outputs to strictly conform to CANONICAL_ANALYZE_RESPONSE_SCHEMA.json."""
    needs_info_map = {}
    if relevance_res and "relevant_needs_info" in relevance_res:
        for r_item in relevance_res["relevant_needs_info"]:
            oid = r_item.get("opportunity", {}).get("opportunity_id") or r_item.get("opportunity_id", "")
            if oid:
                needs_info_map[oid] = r_item.get("unknown_requirements", [])

    from modules.M2_eligibility_graph.engine.gap_analysis import GapAnalyzer
    gap_analyzer = GapAnalyzer(M2_DATA_DIR)

    raw_recs = m4_output.get("recommendations", [])
    best_matches = []
    more_info_needed = []
    
    for item in raw_recs:
        opp_name = item.get("opportunity_name") or item.get("name") or "Unknown Opportunity"
        oid = item.get("opportunity_id", "")
        missing_info = needs_info_map.get(oid, [])
        rel_state = "RELEVANT_NEEDS_PROFILE_INFO" if missing_info else "RELEVANT"

        # Compute scheme-specific requirement gaps
        g_res = gap_analyzer.analyze(profile, oid)
        action_labels = [g.get("action_label") for g in g_res.get("action_gaps", []) if g.get("action_label")]
        unverified_labels = [g.get("action_label") for g in g_res.get("unverified_or_generic_requirements", []) if g.get("action_label")]
        scheme_gaps = action_labels + unverified_labels

        formatted_item = {
            "opportunity_id": oid,
            "name": opp_name,
            "opportunity_name": opp_name,
            "eligibility_status": item.get("eligibility_status", "POTENTIALLY_ELIGIBLE"),
            "relevance_state": rel_state,
            "missing_profile_info": missing_info,
            "scheme_gaps": scheme_gaps,
            "recommendable": True,
            "rank": item.get("rank"),
            "score": item.get("score"),
            "why_match": item.get("why_match", []),
            "missing_requirements": item.get("missing_requirements", []),
            "support_types": item.get("support_types", []),
            "official_source_url": item.get("official_source_url"),
            "opportunity_pathway": item.get("opportunity_pathway"),
            "application_guide": item.get("application_guide"),
            "primary_sector": item.get("primary_sector"),
            "secondary_sectors": item.get("secondary_sectors", []),
            "benefit_summary": item.get("benefit_summary"),
            "target_beneficiary": item.get("target_beneficiary"),
            "scope": item.get("scope"),
            "rule_completeness": item.get("rule_completeness"),
            "last_verified": item.get("last_verified"),
        }

        rule_comp = item.get("rule_completeness", "SUMMARY_ONLY")
        m2_status = item.get("eligibility_status", "POTENTIALLY_ELIGIBLE")
        m2_missing = item.get("missing_profile_fields", [])

        # FULL_STRUCTURED scheme with missing hard fields (POTENTIALLY_ELIGIBLE status or non-empty m2_missing)
        is_full_structured_unknown = (rule_comp == "FULL_STRUCTURED" and (m2_status == "POTENTIALLY_ELIGIBLE" or len(m2_missing) > 0))

        if rel_state == "RELEVANT_NEEDS_PROFILE_INFO" or len(missing_info) > 0 or is_full_structured_unknown:
            if m2_missing:
                m2_field_names = [m.get("field") for m in m2_missing if isinstance(m, dict) and m.get("field")]
                all_missing = list(dict.fromkeys(missing_info + m2_field_names))
                formatted_item["missing_profile_info"] = all_missing
                formatted_item["relevance_state"] = "RELEVANT_NEEDS_PROFILE_INFO"
            more_info_needed.append(formatted_item)
        else:
            best_matches.append(formatted_item)

    raw_needs = m4_output.get("needs_verification", [])
    formatted_needs = []
    for item in raw_needs:
        opp_name = item.get("opportunity_name") or item.get("name") or "Unknown Opportunity"
        formatted_needs.append({
            "opportunity_id": item.get("opportunity_id", ""),
            "name": opp_name,
            "opportunity_name": opp_name,
            "eligibility_status": "NEEDS_VERIFICATION",
            "recommendable": False,
            "lifecycle_status": item.get("lifecycle_status", "NEEDS_VERIFICATION"),
            "lifecycle_warning": item.get("lifecycle_warning"),
            "official_source_url": item.get("official_source_url"),
            "last_verified": item.get("last_verified"),
        })

    raw_not_eligible = m4_output.get("not_eligible", [])
    formatted_not_eligible = []
    for item in raw_not_eligible:
        opp_name = item.get("opportunity_name") or item.get("name") or "Unknown Opportunity"
        formatted_not_eligible.append({
            "opportunity_id": item.get("opportunity_id", ""),
            "name": opp_name,
            "opportunity_name": opp_name,
            "eligibility_status": "NOT_ELIGIBLE",
            "recommendable": False,
            "failed_rules": item.get("failed_rules", [])
        })

    summary = {
        "recommendations": len(best_matches),
        "best_matches": len(best_matches),
        "more_information_needed": len(more_info_needed),
        "eligible": len([x for x in best_matches if x["eligibility_status"] == "ELIGIBLE"]),
        "potentially_eligible": len([x for x in best_matches if x["eligibility_status"] == "POTENTIALLY_ELIGIBLE"]),
        "needs_verification": len(formatted_needs),
        "not_eligible": len(formatted_not_eligible)
    }

    if relevance_summary:
        summary["relevance"] = relevance_summary

    return {
        "profile": sanitize_profile(profile),
        "recommendations": best_matches,
        "best_matches": best_matches,
        "more_information_needed": more_info_needed,
        "needs_verification": formatted_needs,
        "not_eligible": formatted_not_eligible,
        "pathway": pathway_output,
        "graph": graph_output,
        "summary": summary
    }


def format_goal_pathway_response(goal_pathway_data: Dict[str, Any]) -> Dict[str, Any]:
    """Helper to ensure clean formatting of Goal Pathway responses."""
    if not isinstance(goal_pathway_data, dict):
        return {}
    return goal_pathway_data


