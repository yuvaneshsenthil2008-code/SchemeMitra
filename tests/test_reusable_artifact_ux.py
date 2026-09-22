"""Static/runtime checks that reusable-artifact UX was removed cleanly."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_prepared_documents_not_in_active_frontend():
    js = (ROOT / "frontend" / "my_opportunities.js").read_text(encoding="utf-8")
    forbidden = [
        "Prepared Documents",
        "openPreparedDocumentsModal",
        "markArtifactAvailable",
        "removeArtifact",
        "confirmSchemeRequirementWithArtifact",
        "SHARED_ARTIFACT_TYPES",
        "I Have a DPR",
        "I Have Identity / KYC Proof",
    ]
    for token in forbidden:
        assert token not in js
    assert "Completed Actions" in js
    assert "toggleGoalRequirement" in js


def test_no_artifact_fetches_in_active_frontend():
    js = (ROOT / "frontend" / "my_opportunities.js").read_text(encoding="utf-8")
    assert "/api/pathway/artifacts" not in js
    assert "userArtifactsList" not in js
    assert "userArtifactsCount" not in js
