from __future__ import annotations
import json, re
from pathlib import Path
from ..models.profile import EntrepreneurProfile

SPECIFIC_LIST_REQUIREMENTS = {
    "UDYAM_REGISTRATION": ("registrations", {"udyam", "udyam registration", "msme registration"}),
    "FSSAI": ("registrations", {"fssai", "fssai registration", "fssai licence", "fssai license"}),
    "DPIIT_RECOGNITION": ("registrations", {"dpiit", "dpiit recognition", "startup india recognition"}),
    "GEM_REGISTRATION": ("registrations", {"gem", "gem registration", "government e-marketplace"}),
    "IEC": ("registrations", {"iec", "import export code", "importer exporter code"}),
    "APEDA_REGISTRATION": ("registrations", {"apeda", "apeda registration"}),
    "MPEDA_REGISTRATION": ("registrations", {"mpeda", "mpeda registration"}),
    "SPICES_BOARD_REGISTRATION": ("registrations", {"spices board", "spices board registration"}),
    "TEA_BOARD_REGISTRATION": ("registrations", {"tea board", "tea board registration"}),
    "ARTISAN_REGISTRATION": ("registrations", {"artisan registration", "artisan card"}),
    "WEAVER_REGISTRATION": ("registrations", {"weaver registration", "weaver card"}),
    "SHG_MEMBERSHIP": ("registrations", {"shg", "self help group", "shg membership"}),
    "TRAINING": ("trainings", set()),
    "CERTIFICATION": ("certifications", set()),
}
BOOL_EXTRA = {
    "DPR": "has_dpr", "BUSINESS_PLAN": "has_business_plan", "LAND": "has_land_or_lease",
    "ELIGIBLE_LENDER": "has_eligible_lender", "INCUBATOR_LINKAGE": "has_incubator_linkage",
    "BANK_LINKAGE": "has_bank_linkage", "IDENTITY_PROOF": "has_identity_proof",
    "INCOME_PROOF": "has_income_proof", "CATEGORY_PROOF": "has_category_proof",
    "CASTE_CERTIFICATE": "has_caste_certificate", "TRIBE_CERTIFICATE": "has_tribe_certificate",
    "VENDING_CERTIFICATE_OR_RECOMMENDATION": "has_vending_certificate_or_recommendation",
    "TRANSGENDER_CERTIFICATE_OR_ID": "has_transgender_certificate_or_id",
    "LAND_OR_FARM_PROOF": "has_land_or_farm_proof", "LAND_OR_ACTIVITY_PROOF": "has_land_or_activity_proof",
    "EDUCATION_PROOF": "has_education_proof", "BUSINESS_PROOF": "has_business_proof",
}

class GapAnalyzer:
    def __init__(self, data_dir: str | Path | None = None):
        self.data_dir = Path(data_dir or Path(__file__).resolve().parents[1] / "data")
        self.requirements = json.loads((self.data_dir / "pathway_requirements.json").read_text(encoding="utf-8"))
        self.by_opportunity = {}
        for r in self.requirements:
            self.by_opportunity.setdefault(r["opportunity_id"], []).append(r)

    @staticmethod
    def _norm(v):
        return re.sub(r"\s+", " ", str(v or "").strip().lower())

    def analyze(self, profile: EntrepreneurProfile | dict, opportunity_id: str) -> dict:
        if isinstance(profile, dict): profile = EntrepreneurProfile.from_dict(profile)
        completed, missing, unknown = [], [], []
        for req in self.by_opportunity.get(opportunity_id, []):
            state, evidence = self._check(profile, req["requirement_type"])
            item = dict(req)
            item["profile_evidence"] = evidence
            if state == "COMPLETED": completed.append(item)
            elif state == "MISSING": missing.append(item)
            else: unknown.append(item)
        return {
            "opportunity_id": opportunity_id,
            "completed_requirements": completed,
            "action_gaps": missing,
            "unverified_or_generic_requirements": unknown,
            "gap_count": len(missing),
            "unknown_count": len(unknown),
        }

    def _check(self, p: EntrepreneurProfile, typ: str):
        typ = typ.upper()
        if typ == "NONE": return "COMPLETED", "No prerequisite encoded"
        if typ in SPECIFIC_LIST_REQUIREMENTS:
            attr, aliases = SPECIFIC_LIST_REQUIREMENTS[typ]
            vals = [self._norm(x) for x in getattr(p, attr, [])]
            if aliases:
                if any(v in aliases for v in vals): return "COMPLETED", f"Found in {attr}"
                return "MISSING", f"No matching {typ} found in {attr}"
            if vals: return "COMPLETED", f"At least one {attr} record supplied"
            return "MISSING", f"No {attr} evidence supplied"
        extra_dict = getattr(p, "extra", {}) or {}
        if typ in BOOL_EXTRA:
            key = BOOL_EXTRA[typ]
            val = extra_dict.get(key)
            if val is True: return "COMPLETED", key
            if val is False: return "MISSING", key
            return "UNKNOWN", f"Profile does not say whether {key} is complete"
        if typ == "DOCUMENT":
            if extra_dict.get("documents_complete") is True: return "COMPLETED", "documents_complete"
            return "UNKNOWN", "Generic DOCUMENT cannot be proven complete from a partial document list"
        if typ == "REGISTRATION":
            if extra_dict.get("registrations_complete") is True: return "COMPLETED", "registrations_complete"
            return "UNKNOWN", "Generic REGISTRATION needs scheme-specific verification"
        if typ in {"ENTITY_REGISTRATION","STARTUP_REGISTRATION","EXPORT_REGISTRATION","PROGRAMME_REGISTRATION","COURSE_REGISTRATION","COOPERATIVE_REGISTRATION","GROWER_OR_ENTITY_REGISTRATION"}:
            if p.registrations: return "UNKNOWN", "Some registrations supplied, exact required registration not encoded"
            return "UNKNOWN", "Exact required registration is not parameterized in M1"
        # Generic proposal/proof/linkage/compliance requirements are actions, but M1
        # does not always encode a matching profile field safely.
        return "UNKNOWN", "Requirement type is verified at type level but completion evidence is not parameterized"
