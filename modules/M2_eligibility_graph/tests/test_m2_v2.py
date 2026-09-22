from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parent))
from OpportunityOS_v2_M2_eligibility_graph.engine.eligibility_engine import EligibilityEngine
from OpportunityOS_v2_M2_eligibility_graph.engine.gap_analysis import GapAnalyzer
from OpportunityOS_v2_M2_eligibility_graph.graph.graph_engine import OpportunityGraph
from OpportunityOS_v2_M2_eligibility_graph.pathway.pathway_engine import PathwayEngine


def test_loads_100_opportunities():
    assert len(EligibilityEngine().opportunities) == 102

def test_graph_counts_and_integrity():
    v=OpportunityGraph().validate()
    assert v["opportunity_nodes"] == 102
    assert v["requirement_nodes"] == 379
    assert v["relationship_count"] == 534
    assert v["valid"] is True

def test_expired_or_closed_not_recommendable():
    e=EligibilityEngine()
    for oid in ["OPP035"]:
        r=e.evaluate_opportunity({},oid)
        assert r["status"] == "NEEDS_VERIFICATION"
        assert r["recommendable"] is False

def test_transgender_not_treated_as_female():
    e=EligibilityEngine()
    # OPP067 is female + SC.
    r=e.evaluate_opportunity({"gender":"Transgender","category":"SC","annual_income":300000},"OPP067")
    assert r["status"] == "NOT_ELIGIBLE"
    assert any(x["field"]=="gender" for x in r["failed"])

def test_transgender_specific_scheme_accepts_transgender():
    e=EligibilityEngine()
    r=e.evaluate_opportunity({"gender":"Transgender","state":"Tamil Nadu"},"OPP061")
    assert not any(x["field"]=="gender" for x in r["failed"])

def test_sc_income_ceiling_passes():
    e=EligibilityEngine()
    r=e.evaluate_opportunity({"category":"SC","annual_income":450000},"OPP073")
    assert not r["failed"]
    assert any(x["field"]=="annual_income" for x in r["passed"])

def test_sc_income_ceiling_fails():
    e=EligibilityEngine()
    r=e.evaluate_opportunity({"category":"SC","annual_income":550000},"OPP073")
    assert r["status"] == "NOT_ELIGIBLE"

def test_tamil_nadu_geography_hard_rule():
    e=EligibilityEngine()
    r=e.evaluate_opportunity({"state":"Kerala","gender":"Transgender"},"OPP061")
    assert r["status"] == "NOT_ELIGIBLE"
    assert any(x["field"]=="state" for x in r["failed"])

def test_partial_rules_do_not_become_eligible():
    e=EligibilityEngine()
    r=e.evaluate_opportunity({"state":"Tamil Nadu","age":30},"OPP001")
    assert r["status"] == "POTENTIALLY_ELIGIBLE"

def test_missing_hard_field_does_not_false_reject():
    e=EligibilityEngine()
    r=e.evaluate_opportunity({},"OPP073")
    assert r["status"] == "POTENTIALLY_ELIGIBLE"
    assert r["missing_profile_fields"]

def test_specific_fssai_gap_detection():
    g=GapAnalyzer()
    r=g.analyze({"registrations":[]},"OPP011")
    assert any(x["requirement_type"]=="FSSAI" for x in r["action_gaps"])

def test_specific_fssai_completion_detection():
    g=GapAnalyzer()
    r=g.analyze({"registrations":["FSSAI"]},"OPP011")
    assert any(x["requirement_type"]=="FSSAI" for x in r["completed_requirements"])

def test_generic_document_is_verify_not_false_complete():
    g=GapAnalyzer()
    r=g.analyze({"documents":["Aadhaar"]},"OPP011")
    assert any(x["requirement_type"]=="DOCUMENT" for x in r["unverified_or_generic_requirements"])

def test_pathway_has_requirements_and_supports():
    p=PathwayEngine().build({"registrations":["FSSAI"]},"OPP011")
    assert p["pathway"]["requirements"]
    assert p["pathway"]["supports_unlocked_if_approved"]

def test_pathway_does_not_invent_successors():
    p=PathwayEngine().build({},"OPP011")
    assert p["pathway"]["verified_next_opportunities"] == []

def test_all_results_have_safety_fields():
    results=EligibilityEngine().evaluate_all({})
    assert len(results)==102
    assert all("recommendable" in x and "official_source_url" in x and "rule_completeness" in x for x in results)
