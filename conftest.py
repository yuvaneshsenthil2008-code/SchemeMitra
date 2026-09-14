import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Register module aliases for backward compatibility with module test imports
import modules.M2_eligibility_graph as m2
import modules.M4_ranking_pathway as m4

sys.modules['OpportunityOS_v2_M2_eligibility_graph'] = m2
sys.modules['OpportunityOS_v2_M4_ranking_pathway'] = m4
