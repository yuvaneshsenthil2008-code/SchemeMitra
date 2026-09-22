from __future__ import annotations
from dataclasses import dataclass, field, fields
from typing import Any, Optional

@dataclass
class EntrepreneurProfile:
    age: Optional[int] = None
    gender: Optional[str] = None
    category: Optional[str] = None
    disability_status: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    annual_income: Optional[float] = None
    project_cost: Optional[float] = None
    education: Optional[str] = None
    education_course: Optional[str] = None
    education_field: Optional[str] = None
    sector: Optional[str] = None
    business_stage: Optional[str] = None
    business_goal: Optional[str] = None
    selected_goal: Optional[str] = "GENERAL_READINESS"
    target_group: Optional[str] = None
    target_entity: Optional[str] = None
    entity_type: Optional[str] = None
    greenfield: Optional[bool] = None
    existing_business: Optional[bool] = None
    street_vendor: Optional[bool] = None
    available_capital: Optional[float] = None
    is_new_unit: Optional[bool] = None
    prior_gov_subsidy: Optional[bool] = None
    family_pmegp_availed: Optional[bool] = None
    preferred_support_types: list[str] = field(default_factory=list)
    support_needs: list[str] = field(default_factory=list)
    registrations: list[str] = field(default_factory=list)
    certifications: list[str] = field(default_factory=list)
    trainings: list[str] = field(default_factory=list)
    documents: list[str] = field(default_factory=list)
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EntrepreneurProfile":
        if not isinstance(data, dict):
            raise TypeError("Profile must be a dictionary")
        d = dict(data)
        aliases = {
            "income": "annual_income",
            "business_type": "business_stage",
            "estimated_project_cost": "project_cost"
        }
        for src, dst in aliases.items():
            if dst not in d and src in d:
                d[dst] = d[src]
        if not d.get("selected_goal"):
            d["selected_goal"] = d.get("business_goal") or "GENERAL_READINESS"
        if not d.get("business_goal") and d.get("selected_goal") not in (None, "", "GENERAL_READINESS"):
            d["business_goal"] = d.get("selected_goal")
        known = {f.name for f in fields(cls) if f.name != "extra"}
        kwargs = {k:v for k,v in d.items() if k in known}
        extra_combined = dict(d.get("extra") or {}) if isinstance(d.get("extra"), dict) else {}
        for k, v in d.items():
            if k not in known and k not in aliases and k != "extra":
                extra_combined[k] = v
        kwargs["extra"] = extra_combined
        return cls(**kwargs)

    def get(self, name: str, default=None):
        if name == "udyam_registered":
            val = getattr(self, "udyam_registered", None)
            if val is not None:
                return val
            if "udyam_registered" in self.extra:
                return self.extra["udyam_registered"]
            # Check registrations list for explicit positive evidence
            if self.registrations and any("udyam" in str(r).lower() for r in self.registrations):
                return True
            # Check missing_registrations for explicit negative evidence
            missing_regs = self.extra.get("missing_registrations") or getattr(self, "missing_registrations", [])
            if missing_regs and any("udyam" in str(r).lower() for r in missing_regs):
                return False
            # Check unregistered_business flag for explicit negative evidence
            if self.extra.get("unregistered_business") is True or getattr(self, "unregistered_business", False) is True:
                return False
            return default
        if hasattr(self, name):
            val = getattr(self, name)
            if val is not None:
                return val
        return self.extra.get(name, default)
