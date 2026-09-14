import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT.parent.parent
if str(PARENT) not in sys.path:
    sys.path.insert(0, str(PARENT))

import modules.M2_eligibility_graph as m2
sys.modules['OpportunityOS_v2_M2_eligibility_graph'] = m2
