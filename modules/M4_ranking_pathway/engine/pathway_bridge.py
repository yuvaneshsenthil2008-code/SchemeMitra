from __future__ import annotations


def attach_verified_pathway(opportunity_id: str, pathway_results: dict | None) -> dict | None:
    """Consume M2 pathway output; M4 never invents prerequisite or cross-opportunity steps."""
    if not pathway_results:
        return None
    if opportunity_id in pathway_results:
        return pathway_results[opportunity_id]
    # Accept a single M2 pathway object as convenience.
    if pathway_results.get("opportunity_id") == opportunity_id:
        return pathway_results
    return None
