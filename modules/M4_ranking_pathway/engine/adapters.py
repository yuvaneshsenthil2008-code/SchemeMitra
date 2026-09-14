from __future__ import annotations
from ..models.opportunity import Opportunity


def combine_m1_m2(opportunity_master: list[dict], eligibility_results: list[dict]) -> list[Opportunity]:
    """Join M1 source-of-truth metadata to M2 deterministic results by Opportunity_ID."""
    m1 = {row["Opportunity_ID"]: row for row in opportunity_master}
    out: list[Opportunity] = []
    for result in eligibility_results:
        oid = result.get("opportunity_id")
        if not oid or oid not in m1:
            # Unknown results are ignored rather than fabricating scheme metadata.
            continue
        out.append(Opportunity.from_m1_m2(m1[oid], result))
    return out
