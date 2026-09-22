import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
PARENT=ROOT.parent
if str(PARENT) not in sys.path: sys.path.insert(0,str(PARENT))

from OpportunityOS_v2_M4_ranking_pathway.engine.recommendation_engine import RecommendationEngine
from OpportunityOS_v2_M4_ranking_pathway.engine.ranking_engine import RankingEngine
from OpportunityOS_v2_M4_ranking_pathway.models.opportunity import Opportunity


def result(oid,status="POTENTIALLY_ELIGIBLE",recommendable=True,passed=None,failed=None):
    master={x["Opportunity_ID"]:x for x in json.loads((ROOT/'data/opportunity_master.json').read_text())}
    o=master[oid]
    return {"opportunity_id":oid,"opportunity_name":o["Opportunity_Name"],"status":status,"recommendable":recommendable,
            "rule_completeness":o.get("Rule_Completeness"),"passed":passed or [],"failed":failed or [],
            "missing_profile_fields":[],"uncertain_rules":[],"lifecycle_warning":None,
            "official_source_url":o["Official_Source_URL"],"last_verified":o["Last_Verified"]}


def find_active_support(support):
    rows=json.loads((ROOT/'data/opportunity_master.json').read_text())
    for r in rows:
        if r["Lifecycle_Status"]=="ACTIVE" and r["Recommendable"]=="TRUE" and support in r.get("Support_Types","").split(';'):
            return r["Opportunity_ID"]
    raise AssertionError(support)


def find_nonrecommendable():
    rows=json.loads((ROOT/'data/opportunity_master.json').read_text())
    return next(r["Opportunity_ID"] for r in rows if r["Recommendable"]!="TRUE" or r["Lifecycle_Status"]!="ACTIVE")


def test_master_has_100():
    assert len(json.loads((ROOT/'data/opportunity_master.json').read_text()))==102


def test_not_eligible_never_recommended():
    oid=find_active_support("LOAN")
    out=RecommendationEngine().build({},[result(oid,"NOT_ELIGIBLE",True,failed=[{"field":"age"}])])
    assert out["recommendations"]==[]
    assert out["not_eligible"][0]["opportunity_id"]==oid


def test_needs_verification_isolated():
    oid=find_nonrecommendable()
    out=RecommendationEngine().build({},[result(oid,"NEEDS_VERIFICATION",False)])
    assert not out["recommendations"]
    assert out["needs_verification"][0]["opportunity_id"]==oid


def test_m2_recommendable_false_cannot_be_overridden():
    oid=find_active_support("LOAN")
    out=RecommendationEngine().build({"preferred_support_types":["LOAN"]},[result(oid,"ELIGIBLE",False)])
    assert out["recommendations"]==[]
    assert out["needs_verification"]


def test_support_preference_boosts_matching_item():
    loan=find_active_support("LOAN")
    market=find_active_support("MARKET_ACCESS")
    if loan==market:
        rows=json.loads((ROOT/'data/opportunity_master.json').read_text())
        market=next(r["Opportunity_ID"] for r in rows if r["Opportunity_ID"]!=loan and r["Lifecycle_Status"]=="ACTIVE" and r["Recommendable"]=="TRUE" and "MARKET_ACCESS" in r.get("Support_Types","").split(';'))
    out=RecommendationEngine().build({"preferred_support_types":["LOAN"]},[result(market),result(loan)])
    assert out["recommendations"][0]["opportunity_id"]==loan
    assert out["recommendations"][0]["match"]["tier"]=="PREFERRED_SUPPORT_MATCH"


def test_finance_need_maps_to_finance_support():
    oid=find_active_support("CREDIT")
    out=RecommendationEngine().build({"support_needs":["FINANCE"]},[result(oid)])
    assert out["recommendations"][0]["match"]["tier"]=="INFERRED_NEED_MATCH"


def test_eligible_base_above_potential_when_other_factors_equal():
    oid=find_active_support("LOAN")
    m=json.loads((ROOT/'data/opportunity_master.json').read_text())
    oid2=next(r["Opportunity_ID"] for r in m if r["Opportunity_ID"]!=oid and r["Lifecycle_Status"]=="ACTIVE" and r["Recommendable"]=="TRUE")
    out=RecommendationEngine().build({},[result(oid,"ELIGIBLE"),result(oid2,"POTENTIALLY_ELIGIBLE")])
    assert out["recommendations"][0]["eligibility_status"]=="ELIGIBLE"


def test_pathway_is_only_attached_when_supplied():
    oid=find_active_support("LOAN")
    out=RecommendationEngine().build({},[result(oid)])
    assert out["recommendations"][0]["opportunity_pathway"] is None
    p={oid:{"opportunity_id":oid,"pathway":{"requirements":[]}}}
    out=RecommendationEngine().build({},[result(oid)],p)
    assert out["recommendations"][0]["opportunity_pathway"]["opportunity_id"]==oid


def test_application_guide_is_separate():
    oid=find_active_support("LOAN")
    out=RecommendationEngine().build({},[result(oid)])
    rec=out["recommendations"][0]
    assert "application_guide" in rec
    assert "opportunity_pathway" in rec
    assert rec["application_guide"]["note"].startswith("Application Guide")


def test_why_match_uses_m2_passed_evidence():
    oid=find_active_support("LOAN")
    passed=[{"field":"state","expected":"Tamil Nadu","actual":"Tamil Nadu","reason":"State requirement matched."}]
    out=RecommendationEngine().build({},[result(oid,passed=passed)])
    reasons=out["recommendations"][0]["why_match"]["reasons"]
    assert any(x.get("field")=="state" for x in reasons)


def test_unknown_m2_ids_are_ignored():
    out=RecommendationEngine().build({},[{"opportunity_id":"DOES_NOT_EXIST","status":"ELIGIBLE","recommendable":True}])
    assert out["summary"]["recommendations"]==0


def test_summary_counts_consistent():
    a=find_active_support("LOAN")
    b=find_active_support("MARKET_ACCESS")
    out=RecommendationEngine().build({},[result(a,"ELIGIBLE"),result(b,"POTENTIALLY_ELIGIBLE")])
    assert out["summary"]["recommendations"]==len(out["recommendations"])
    assert out["summary"]["eligible"]==len(out["eligible"])
    assert out["summary"]["potentially_eligible"]==len(out["potentially_eligible"])
