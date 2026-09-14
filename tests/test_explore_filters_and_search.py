from pathlib import Path

from fastapi.testclient import TestClient

from server.app import app
from server.adapters import (
    SUPPORT_FAMILY_MAP,
    get_m1_opportunity_master,
    matches_support_family,
    normalize_scope_group,
    resolve_sector_intent,
    search_opportunities,
)

client = TestClient(app)

CANONICAL_SECTORS = [
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
]


def test_catalogue_and_primary_sector_integrity():
    master = get_m1_opportunity_master()
    assert len(master) == 100
    counts = {sector: sum(o["primary_sector"] == sector for o in master) for sector in CANONICAL_SECTORS}
    assert counts == {sector: 10 for sector in CANONICAL_SECTORS}


def test_support_family_mapping_covers_all_current_support_types_and_allows_overlap():
    master = get_m1_opportunity_master()
    raw_types = {x for o in master for x in o.get("support_types", [])}
    mapped_types = set().union(*SUPPORT_FAMILY_MAP.values())
    assert raw_types <= mapped_types

    # A multi-support record should legitimately match more than one family.
    multi = next(o for o in master if len(o.get("support_types", [])) >= 2)
    matching_families = [
        family for family in SUPPORT_FAMILY_MAP
        if matches_support_family(multi["support_types"], family)
    ]
    assert len(matching_families) >= 2


def test_support_family_api_filters_are_data_driven():
    for family in SUPPORT_FAMILY_MAP:
        response = client.get("/api/opportunities", params={"support_type": family, "limit": 100})
        assert response.status_code == 200
        payload = response.json()
        assert payload["total"] == len(payload["items"])
        assert all(matches_support_family(o["support_types"], family) for o in payload["items"])


def test_scope_normalization_counts_cover_catalogue():
    master = get_m1_opportunity_master()
    groups = [normalize_scope_group(o.get("scope")) for o in master]
    assert None not in groups
    assert groups.count("CENTRAL") == 97
    assert groups.count("STATE") == 3
    assert len(groups) == 100

    central = client.get("/api/opportunities", params={"scope": "CENTRAL", "limit": 100}).json()
    state = client.get("/api/opportunities", params={"scope": "STATE", "limit": 100}).json()
    assert central["total"] == 97
    assert state["total"] == 3
    assert central["total"] + state["total"] == 100


def test_sector_intent_aliases_resolve_to_canonical_sectors():
    cases = {
        "agriculture": "Agriculture & Allied",
        "food": "Food Processing & Agri Value Addition",
        "manufacturing": "MSME & Manufacturing",
        "finance": "Finance & Credit",
        "startup": "Startup & Innovation",
        "skills": "Skills & Employment",
        "women": "Women & SHG Entrepreneurship",
        "social empowerment": "Social Empowerment & Inclusive Entrepreneurship",
        "handicraft": "Handicrafts, Handloom & Artisan Economy",
        "export": "Export, Market Access & Business Growth",
    }
    for query, expected in cases.items():
        assert resolve_sector_intent(query) == expected
        response = client.get("/api/opportunities", params={"search": query, "limit": 100})
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 10
        assert {o["primary_sector"] for o in data["items"]} == {expected}


def test_canonical_sector_text_search_works_with_and_or_ampersand():
    response = client.get(
        "/api/opportunities",
        params={"search": "Food Processing and Agri Value Addition", "limit": 100},
    )
    data = response.json()
    assert data["total"] == 10
    assert all(o["primary_sector"] == "Food Processing & Agri Value Addition" for o in data["items"])


def test_exact_scheme_name_ranks_above_related_text_match():
    master = get_m1_opportunity_master()
    results = search_opportunities(master, "Common Infrastructure")
    assert results
    assert results[0]["opportunity_name"].startswith("PMFME")
    assert "Common Infrastructure" in results[0]["opportunity_name"]
    assert results[0]["match_reason"] == "Matched scheme name"

    exact = search_opportunities(master, "PMKSY Agro Processing Cluster")
    assert exact
    assert "Agro Processing Cluster" in exact[0]["opportunity_name"]
    assert exact[0]["match_reason"] == "Matched scheme name"


def test_frontend_home_search_and_sector_card_clear_stale_filters():
    js = (Path(__file__).resolve().parents[1] / "frontend" / "app.js").read_text(encoding="utf-8")
    assert "this.clearFilters(false);" in js
    assert 'if (filterSup) filterSup.value = "";' in js
    assert 'if (filterScope) filterScope.value = "";' in js
    assert 'if (searchInput) searchInput.value = "";' in js
