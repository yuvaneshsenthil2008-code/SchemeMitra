from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


def _split(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    return [x.strip() for x in str(value).split(';') if x.strip()]


@dataclass
class Opportunity:
    opportunity_id: str
    opportunity_name: str
    primary_sector: str | None = None
    secondary_sectors: list[str] = field(default_factory=list)
    support_types: list[str] = field(default_factory=list)
    benefit_summary: str = ""
    eligibility_summary: str = ""
    application_route: str = ""
    required_documents_summary: str = ""
    official_source_url: str | None = None
    lifecycle_status: str = "UNKNOWN"
    source_recommendable: bool = False
    rule_completeness: str = "SUMMARY_ONLY"
    target_beneficiary: str = ""
    scope: str = ""
    ministry_department: str = ""
    eligibility_status: str = "NEEDS_VERIFICATION"
    m2_recommendable: bool = False
    passed: list[dict] = field(default_factory=list)
    failed: list[dict] = field(default_factory=list)
    missing_profile_fields: list[dict] = field(default_factory=list)
    uncertain_rules: list[dict] = field(default_factory=list)
    lifecycle_warning: str | None = None
    last_verified: str | None = None

    @classmethod
    def from_m1_m2(cls, m1: dict, m2: dict) -> "Opportunity":
        return cls(
            opportunity_id=m1.get("Opportunity_ID") or m2.get("opportunity_id"),
            opportunity_name=m1.get("Opportunity_Name") or m2.get("opportunity_name", ""),
            primary_sector=m1.get("Primary_Sector"),
            secondary_sectors=_split(m1.get("Secondary_Sectors")),
            support_types=[x.upper() for x in _split(m1.get("Support_Types"))],
            benefit_summary=str(m1.get("Benefit_Summary") or ""),
            eligibility_summary=str(m1.get("Eligibility_Summary") or ""),
            application_route=str(m1.get("Application_Route") or ""),
            required_documents_summary=str(m1.get("Required_Documents_Summary") or ""),
            official_source_url=m2.get("official_source_url") or m1.get("Official_Source_URL"),
            lifecycle_status=str(m1.get("Lifecycle_Status") or "UNKNOWN"),
            source_recommendable=str(m1.get("Recommendable", "FALSE")).upper() == "TRUE",
            rule_completeness=str(m2.get("rule_completeness") or m1.get("Rule_Completeness") or "SUMMARY_ONLY"),
            target_beneficiary=str(m1.get("Target_Beneficiary") or ""),
            scope=str(m1.get("Scope") or ""),
            ministry_department=str(m1.get("Ministry_Department") or ""),
            eligibility_status=str(m2.get("status") or "NEEDS_VERIFICATION"),
            m2_recommendable=bool(m2.get("recommendable", False)),
            passed=list(m2.get("passed") or []),
            failed=list(m2.get("failed") or []),
            missing_profile_fields=list(m2.get("missing_profile_fields") or []),
            uncertain_rules=list(m2.get("uncertain_rules") or []),
            lifecycle_warning=m2.get("lifecycle_warning"),
            last_verified=m2.get("last_verified") or m1.get("Last_Verified"),
        )

    def is_safe_to_recommend(self) -> bool:
        return (
            self.source_recommendable
            and self.m2_recommendable
            and self.lifecycle_status == "ACTIVE"
            and self.eligibility_status in {"ELIGIBLE", "POTENTIALLY_ELIGIBLE"}
        )
