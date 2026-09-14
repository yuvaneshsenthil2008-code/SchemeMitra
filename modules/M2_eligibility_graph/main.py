from .engine.eligibility_engine import EligibilityEngine
from .engine.gap_analysis import GapAnalyzer
from .graph.graph_engine import OpportunityGraph
from .pathway.pathway_engine import PathwayEngine
from .pathway.goal_pathway_builder import GoalPathwayBuilder
from .models.profile import EntrepreneurProfile

def build_engines(data_dir=None):
    return {
        "eligibility": EligibilityEngine(data_dir),
        "gaps": GapAnalyzer(data_dir),
        "graph": OpportunityGraph(data_dir),
        "pathway": PathwayEngine(data_dir),
        "goal_pathway": GoalPathwayBuilder(data_dir),
    }

