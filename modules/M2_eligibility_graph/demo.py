from models.profile import EntrepreneurProfile
from engine.eligibility_engine import EligibilityEngine
from pathway.pathway_engine import PathwayEngine

p = EntrepreneurProfile(age=24, gender="Female", category="SC", state="Tamil Nadu", sector="Food Processing & Agri Value Addition", business_stage="Startup", business_goal="Start a food processing enterprise")
e = EligibilityEngine()
print("Evaluated:", len(e.evaluate_all(p)))
print(PathwayEngine().build(p, "OPP011"))
