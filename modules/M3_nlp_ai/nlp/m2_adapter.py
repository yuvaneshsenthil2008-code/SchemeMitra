"""Canonical OpportunityOS v2 M3 -> M2 profile adapter.

M3 only structures user-supplied facts. It never decides eligibility,
recommendability, ranking, or invents requirements.
"""

M2_FIELDS = (
    "age","gender","category","state","district","annual_income","project_cost",
    "education","education_field","sector","business_stage","business_goal",
    "target_group","target_entity","entity_type","greenfield","existing_business",
    "street_vendor","artisan_trade","preferred_support_types","support_needs",
    "registrations","certifications","trainings","documents","extra",
)

def _list(v):
    if v is None: return []
    if isinstance(v, (list, tuple, set)): return [str(x).strip() for x in v if str(x).strip()]
    return [str(v).strip()] if str(v).strip() else []

def build_m2_profile(profile: dict) -> dict:
    if not isinstance(profile, dict):
        raise TypeError("profile must be a dictionary")
    income = profile.get("annual_income", profile.get("income"))
    if income is not None and profile.get("income_period") == "monthly":
        income = float(income) * 12
    stage = profile.get("business_stage", profile.get("business_type"))
    existing = profile.get("existing_business")
    if existing is None and stage is not None:
        existing = str(stage).lower() == "existing"
    out = {
        "age": profile.get("age"), "gender": profile.get("gender"),
        "category": profile.get("category"), "state": profile.get("state"),
        "district": profile.get("district"), "annual_income": income,
        "project_cost": profile.get("project_cost"), "education": profile.get("education"),
        "education_field": profile.get("education_field"), "sector": profile.get("sector"),
        "business_stage": stage, "business_goal": profile.get("business_goal"),
        "target_group": profile.get("target_group"), "target_entity": profile.get("target_entity"),
        "entity_type": profile.get("entity_type"), "greenfield": profile.get("greenfield"),
        "existing_business": existing, "street_vendor": profile.get("street_vendor"),
        "artisan_trade": profile.get("artisan_trade"),
        "available_capital": profile.get("available_capital"),
        "is_new_unit": profile.get("is_new_unit"),
        "prior_gov_subsidy": profile.get("prior_gov_subsidy"),
        "family_pmegp_availed": profile.get("family_pmegp_availed"),
        "preferred_support_types": _list(profile.get("preferred_support_types")),
        "support_needs": _list(profile.get("support_needs")),
        "registrations": _list(profile.get("registrations")),
        "certifications": _list(profile.get("certifications")),
        "trainings": _list(profile.get("trainings")), "documents": _list(profile.get("documents")),
    }
    # Evidence used by M2 gap analysis is passed explicitly, never inferred as completed.
    extra = dict(profile.get("extra") or {})
    for k in ("has_dpr","has_business_plan","has_land","has_eligible_lender","has_incubator_linkage","available_capital","missing_registrations","unregistered_business","is_new_unit","prior_gov_subsidy","family_pmegp_availed"):
        if k in profile and profile[k] is not None: extra[k] = profile[k]
    out["extra"] = extra
    return out

def build_m2_payload(profile: dict) -> dict:
    return {"profile": build_m2_profile(profile)}
