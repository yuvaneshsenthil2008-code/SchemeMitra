from __future__ import annotations
import json, re
from pathlib import Path
from typing import Any
from ..models.profile import EntrepreneurProfile

ELIGIBLE = "ELIGIBLE"
NOT_ELIGIBLE = "NOT_ELIGIBLE"
POTENTIALLY_ELIGIBLE = "POTENTIALLY_ELIGIBLE"
NEEDS_VERIFICATION = "NEEDS_VERIFICATION"

CATEGORY_ALIASES = {
    "scheduled caste": {"sc", "scheduled caste", "scheduled_caste"},
    "scheduled tribe": {"st", "scheduled tribe", "scheduled_tribe"},
    "notified backward classes": {"obc", "backward class", "backward classes", "notified backward classes", "nbc"},
}
GENDER_ALIASES = {
    "female": {"female", "woman", "women"},
    "male": {"male", "man", "men"},
    "transgender": {"transgender", "trans", "third gender", "thirunangai", "thirunambi", "hijra", "kinnar", "aravani"},
}

class EligibilityEngine:
    """Conservative deterministic evaluator for M1 v2.

    Hard NOT_ELIGIBLE is emitted only for a parameterized condition that can be
    evaluated from the profile. Partial/summary-only M1 rows never become
    ELIGIBLE merely because no contradiction was found.
    """
    def __init__(self, data_dir: str | Path | None = None):
        self.data_dir = Path(data_dir or Path(__file__).resolve().parents[1] / "data")
        self.opportunities = self._load("opportunity_master.json")
        self.rules = {r["Opportunity_ID"]: r for r in self._load("eligibility_rules.json")}
        self.by_id = {o["Opportunity_ID"]: o for o in self.opportunities}

    def _load(self, name):
        return json.loads((self.data_dir / name).read_text(encoding="utf-8"))

    @staticmethod
    def _norm(v: Any) -> str:
        return re.sub(r"\s+", " ", str(v or "").strip().lower())

    def _same_gender(self, actual, expected):
        a, e = self._norm(actual), self._norm(expected)
        vals = GENDER_ALIASES.get(e, {e})
        return a in vals

    def _same_category(self, actual, expected):
        a, e = self._norm(actual), self._norm(expected)
        vals = CATEGORY_ALIASES.get(e, {e})
        return a in vals

    def evaluate_opportunity(self, profile: EntrepreneurProfile | dict, opportunity_id: str) -> dict:
        if isinstance(profile, dict):
            profile = EntrepreneurProfile.from_dict(profile)
        opp = self.by_id[opportunity_id]
        row = self.rules[opportunity_id]
        passed, failed, missing, uncertain = [], [], [], []

        recommendable = str(opp.get("Recommendable", "FALSE")).upper() == "TRUE"
        lifecycle = opp.get("Lifecycle_Status", "UNKNOWN")
        if not recommendable or lifecycle != "ACTIVE":
            return self._result(opp, NEEDS_VERIFICATION, passed, failed, missing, uncertain,
                lifecycle_warning=f"Lifecycle={lifecycle}; Recommendable={recommendable}")

        # Geography: only explicit state rows are hard evaluated.
        geo = self._norm(row.get("Geography_Rule"))
        if geo == "tamil nadu":
            if not profile.state:
                missing.append(self._detail("state", "Tamil Nadu", "State is required for this state-level opportunity."))
            elif self._norm(profile.state) in {"tamil nadu", "tn"}:
                passed.append(self._detail("state", "Tamil Nadu", "State requirement matched.", profile.state))
            else:
                failed.append(self._detail("state", "Tamil Nadu", "Opportunity is restricted to Tamil Nadu.", profile.state))

        # Gender: exact Female or Transgender only. 'Female' never includes Transgender.
        gender_rule = str(row.get("Gender_Rule") or "")
        if gender_rule == "Transgender":
            self._eval_exact(profile.gender, "Transgender", "gender", self._same_gender, passed, failed, missing)
        elif gender_rule.startswith("Female"):
            self._eval_exact(profile.gender, "Female", "gender", self._same_gender, passed, failed, missing)

        # Social category: only well-defined categories are hard evaluated.
        category_rule = str(row.get("Social_Category_Rule") or "")
        if category_rule in {"Scheduled Caste", "Scheduled Tribe", "Notified Backward Classes"}:
            self._eval_exact(profile.category, category_rule, "category", self._same_category, passed, failed, missing)
        elif category_rule == "NSKFDC target group":
            # M1 does not encode a safe deterministic mapping for this phrase.
            uncertain.append(self._detail("target_group", category_rule, "Target-group definition is not fully parameterized in M1."))

        # Explicit income ceilings currently present in M1.
        income_rule = str(row.get("Income_Rule") or "")
        m = re.search(r"up to\s*₹?\s*([0-9.]+)\s*lakh", income_rule, re.I)
        if m:
            ceiling = float(m.group(1)) * 100000
            if profile.annual_income is None:
                missing.append(self._detail("annual_income", ceiling, "Annual family income is required for this rule."))
            elif float(profile.annual_income) <= ceiling:
                passed.append(self._detail("annual_income", ceiling, "Income ceiling matched.", profile.annual_income))
            else:
                failed.append(self._detail("annual_income", ceiling, "Income exceeds the encoded ceiling.", profile.annual_income))

        # Age rule: Handle "Above 18 years" or "Above 18" or "Above 35 years"
        age_rule = str(row.get("Age_Rule") or "")
        if "above 18" in age_rule.lower():
            if profile.age is None:
                missing.append(self._detail("age", ">18", "Age is required for this rule."))
            elif profile.age > 18:
                passed.append(self._detail("age", ">18", "Age rule matched (>18 years).", profile.age))
            else:
                failed.append(self._detail("age", ">18", "Age must be strictly above 18 years.", profile.age))
        elif age_rule == "Above 35 years":
            if profile.age is None:
                missing.append(self._detail("age", ">35", "Age is required for this rule."))
            elif profile.age > 35:
                passed.append(self._detail("age", ">35", "Age rule matched.", profile.age))
            else:
                failed.append(self._detail("age", ">35", "Age does not meet the encoded requirement.", profile.age))
        elif "Typically 15–45" in age_rule:
            uncertain.append(self._detail("age", age_rule, "Rule contains relaxations/priority wording, so M2 will not hard-fail it."))

        # Business or Entity Rules (Declarative/Generic check for PMEGP & PMS)
        biz_rule = str(row.get("Business_or_Entity_Rule") or "")
        qual_rule = str(row.get("Qualification_Rule") or "")

        # PMEGP Rule Evaluation (OPP021)
        if "is_new_unit" in biz_rule or "pmegp guidelines" in biz_rule.lower():
            # 1. New Unit Requirement (is_new_unit)
            is_new = profile.get("is_new_unit")
            if is_new is None:
                is_new = profile.get("new_business")
            if is_new is None and profile.greenfield is not None:
                is_new = profile.greenfield
            
            if is_new is None:
                missing.append(self._detail("is_new_unit", True, "New unit status (is_new_unit) is required for PMEGP eligibility."))
            elif bool(is_new) is True:
                passed.append(self._detail("is_new_unit", True, "New unit requirement matched.", is_new))
            else:
                failed.append(self._detail("is_new_unit", True, "PMEGP assistance is available exclusively for establishing new micro-enterprises.", is_new))

            # 2. Prior Government Subsidy Exclusion (prior_gov_subsidy)
            prior_sub = profile.get("prior_gov_subsidy")
            if prior_sub is None:
                prior_sub = profile.get("prior_subsidy_availed")

            if prior_sub is None:
                missing.append(self._detail("prior_gov_subsidy", False, "Information on prior government subsidy is required."))
            elif bool(prior_sub) is False:
                passed.append(self._detail("prior_gov_subsidy", False, "No prior government subsidy requirement matched.", prior_sub))
            else:
                failed.append(self._detail("prior_gov_subsidy", False, "Units that have received prior central/state government subsidy are ineligible.", prior_sub))

            # 3. Family Restriction (family_pmegp_availed)
            fam = profile.get("family_pmegp_availed")
            if fam is None:
                missing.append(self._detail("family_pmegp_availed", False, "Family PMEGP beneficiary status is required."))
            elif bool(fam) is False:
                passed.append(self._detail("family_pmegp_availed", False, "Family restriction matched (no prior family beneficiary).", fam))
            else:
                failed.append(self._detail("family_pmegp_availed", False, "Only one person per family (self and spouse) can receive PMEGP assistance.", fam))

            # 4. Educational Qualification Threshold & Subsidy Capping
            sec = self._norm(profile.sector)
            cost = profile.project_cost
            edu = profile.education

            is_mfg = "manufacturing" in sec or "food" in sec or "msme" in sec or sec == ""
            is_service = "service" in sec or "business" in sec or "trading" in sec
            threshold = 1000000 if is_mfg else 500000

            has_8th = self._is_8th_pass(edu) if edu is not None else None

            if cost is None:
                missing.append(self._detail("project_cost", "Amount in ₹", "Project cost is required for PMEGP evaluation."))
                if has_8th is True:
                    passed.append(self._detail("education", "8th Pass", f"Project cost is unknown, but 8th Pass qualification satisfies education requirement regardless of project cost.", edu))
                elif has_8th is False:
                    missing.append(self._detail("education", "8th Pass", f"Project cost is unknown and education is below 8th Pass ({edu}). Education requirement depends on whether project cost exceeds ₹{threshold//100000} Lakh."))
                else:
                    missing.append(self._detail("education", "8th Pass", f"Educational qualification and project cost are both unknown. Minimum 8th Pass is required if project cost exceeds ₹{threshold//100000} Lakh."))
            else:
                if cost <= threshold:
                    passed.append(self._detail("education", "Not Required", f"Project cost (₹{cost:,.0f}) is within ₹{threshold//100000} Lakh threshold; 8th Pass qualification is not mandatory.", edu or "N/A"))
                else:
                    if edu is None:
                        missing.append(self._detail("education", "8th Pass", f"Educational qualification (minimum 8th Pass) is required when project cost (₹{cost:,.0f}) exceeds ₹{threshold//100000} Lakh."))
                    elif has_8th is True:
                        passed.append(self._detail("education", "8th Pass", f"Minimum 8th Pass qualification matched for project cost (₹{cost:,.0f}) exceeding ₹{threshold//100000} Lakh.", edu))
                    else:
                        failed.append(self._detail("education", "8th Pass", f"Minimum 8th Standard pass required for projects exceeding ₹{threshold//100000} Lakh.", edu))

                # Subsidy Cap Notice (BENEFIT_CALCULATION, NOT HARD_ELIGIBILITY)
                cap = 5000000 if is_mfg else 2000000
                if cost > cap:
                    uncertain.append(self._detail("subsidy_cap_pmegp", f"₹{cap:,}", f"Project cost exceeds the amount covered by PMEGP margin-money subsidy (₹{cap//100000} Lakh). The excess amount may require separate financing.", cost))

        # PMS Rule Evaluation (OPP029)
        if "component 5(i)a" in biz_rule.lower() or "udyam_category in ['micro', 'small']" in biz_rule.lower():
            # 1. Udyam Registration & Category
            udyam_reg = profile.get("udyam_registered")
            if udyam_reg is None and (profile.registrations and any("udyam" in str(r).lower() for r in profile.registrations)):
                udyam_reg = True
            
            udyam_cat = profile.get("udyam_category")

            if udyam_reg is None:
                missing.append(self._detail("udyam_registered", True, "Udyam registration status (udyam_registered) is required for PMS Component 5(I)A."))
            elif bool(udyam_reg) is False:
                failed.append(self._detail("udyam_registered", True, "Valid Udyam Registration as a Micro or Small Enterprise is required for PMS Component 5(I)A.", actual=False))
            else:
                if udyam_cat is None:
                    missing.append(self._detail("udyam_category", "MICRO or SMALL", "Udyam enterprise category (udyam_category) is required for PMS Component 5(I)A."))
                elif str(udyam_cat).strip().upper() in ["MICRO", "SMALL"]:
                    passed.append(self._detail("udyam_category", "MICRO or SMALL", "Valid Micro/Small Udyam category matched for PMS Component 5(I)A.", actual=udyam_cat))
                else:
                    failed.append(self._detail("udyam_category", "MICRO or SMALL", "PMS Component 5(I)A assistance is restricted to Micro and Small Enterprises.", actual=udyam_cat))

            # 2. Assistance Frequency Limit (ASSISTANCE_LIMIT_REACHED)
            events = profile.get("pms_events_availed_this_fy")
            if events is not None and int(events) > 2:
                uncertain.append(self._detail("pms_events_availed_this_fy", "<=2", "Financial assistance limit of 2 events per financial year has been reached for Component 5(I)A. The enterprise remains scheme-eligible but cannot claim additional reimbursement in the current financial year.", actual=events))

        # M1 completeness controls confidence. It is unsafe to label a row ELIGIBLE
        # while unparameterized official conditions still exist.
        completeness = row.get("Rule_Completeness", "SUMMARY_ONLY")
        if failed:
            status = NOT_ELIGIBLE
        elif completeness in {"PARTIAL_STRUCTURED", "SUMMARY_ONLY"}:
            status = POTENTIALLY_ELIGIBLE
        elif missing or uncertain:
            status = POTENTIALLY_ELIGIBLE
        else:
            status = ELIGIBLE

        return self._result(opp, status, passed, failed, missing, uncertain)

    @staticmethod
    def _is_8th_pass(edu: Any) -> bool:
        if not edu:
            return False
        e = str(edu).strip().lower()
        if any(k in e for k in ["illiterate", "below 8th", "primary", "below 8", "uneducated", "5th pass", "none"]):
            return False
        return True

    def evaluate_all(self, profile: EntrepreneurProfile | dict) -> list[dict]:
        return [self.evaluate_opportunity(profile, o["Opportunity_ID"]) for o in self.opportunities]

    def _eval_exact(self, actual, expected, field, comparator, passed, failed, missing):
        if actual is None or str(actual).strip() == "":
            missing.append(self._detail(field, expected, f"{field.replace('_',' ').title()} is required for this rule."))
        elif comparator(actual, expected):
            passed.append(self._detail(field, expected, "Requirement matched.", actual))
        else:
            failed.append(self._detail(field, expected, "Profile does not match the encoded requirement.", actual))

    @staticmethod
    def _detail(field, expected, reason, actual=None):
        d = {"field": field, "expected": expected, "reason": reason}
        if actual is not None: d["actual"] = actual
        return d

    @staticmethod
    def _result(opp, status, passed, failed, missing, uncertain, lifecycle_warning=None):
        recommendable = str(opp.get("Recommendable", "FALSE")).upper() == "TRUE" and opp.get("Lifecycle_Status") == "ACTIVE"
        if status == NEEDS_VERIFICATION:
            recommendable = False
        return {
            "opportunity_id": opp["Opportunity_ID"],
            "opportunity_name": opp["Opportunity_Name"],
            "status": status,
            "recommendable": recommendable,
            "rule_completeness": opp.get("Rule_Completeness"),
            "passed": passed,
            "failed": failed,
            "missing_profile_fields": missing,
            "uncertain_rules": uncertain,
            "lifecycle_warning": lifecycle_warning,
            "official_source_url": opp.get("Official_Source_URL"),
            "last_verified": opp.get("Last_Verified"),
        }
