from .engine.recommendation_engine import RecommendationEngine


def build_recommendations(profile: dict, eligibility_results: list[dict], pathway_results: dict | None = None, data_dir=None) -> dict:
    return RecommendationEngine(data_dir).build(profile, eligibility_results, pathway_results)
