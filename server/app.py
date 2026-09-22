import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from server.ai.gemini_provider import load_local_dotenv
load_local_dotenv()

from server.adapters import (
    M2_DATA_DIR,
    M4_DATA_DIR,
    get_health_stats,
    get_m1_opportunity_master,
    get_m1_pathway_requirements,
    get_m1_relationships,
    get_m1_taxonomy,
    sanitize_profile,
    format_analyze_response,
    filter_candidate_set,
    matches_support_family,
    normalize_scope_group,
    search_opportunities,
    format_goal_pathway_response
)

from modules.M2_eligibility_graph.main import build_engines
from modules.M3_nlp_ai.ai.ai_assistant import AIAssistant
from modules.M4_ranking_pathway.main import build_recommendations

app = FastAPI(
    title="SchemeMitra API",
    description="SchemeMitra — AI-powered scheme matching for entrepreneurs",
    version="2.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_no_cache_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# Initialize M2 engines
m2_engines = build_engines(M2_DATA_DIR)

# Request Models
class ParseProfileRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    existing_profile: Optional[Dict[str, Any]] = None

class ProfilePayload(BaseModel):
    profile: Optional[Dict[str, Any]] = None

class RecommendPayload(BaseModel):
    profile: Optional[Dict[str, Any]] = None

class PathwayPayload(BaseModel):
    profile: Optional[Dict[str, Any]] = None
    opportunity_id: str
    business_goal: Optional[str] = None

class AnalyzePayload(BaseModel):
    profile: Optional[Dict[str, Any]] = None
    selected_opportunity_id: Optional[str] = None

class GoalPathwayPayload(BaseModel):
    profile: Optional[Dict[str, Any]] = None
    business_goal: Optional[str] = None
    user_progress_overlay: Optional[Dict[str, Any]] = None
    force_general: Optional[bool] = False
    client_id: Optional[str] = None

class GoalPathwayUpdatePayload(BaseModel):
    profile: Optional[Dict[str, Any]] = None
    business_goal: Optional[str] = None
    user_progress_overlay: Optional[Dict[str, Any]] = None
    completed_requirement_id: Optional[str] = None
    action: Optional[str] = "COMPLETE"
    client_id: Optional[str] = None

class CompleteRequirementRequest(BaseModel):
    client_id: str
    requirement_id: str

class ReopenRequirementRequest(BaseModel):
    client_id: str
    requirement_id: str




def build_under18_applicability_response(profile: Dict[str, Any]) -> Dict[str, Any]:
    """Product-level applicability gate for personalized entrepreneur matching.

    This does not change or reinterpret any scheme's official eligibility rules.
    Public catalogue browsing remains available for all ages.
    """
    return {
        "profile": profile,
        "recommendations": [],
        "best_matches": [],
        "more_information_needed": [],
        "needs_verification": [],
        "not_eligible": [],
        "pathway": None,
        "graph": None,
        "summary": {
            "recommendations": 0,
            "best_matches": 0,
            "more_information_needed": 0,
            "eligible": 0,
            "potentially_eligible": 0,
            "needs_verification": 0,
            "not_eligible": 0,
        },
        "applicability": {
            "personalized_matching_available": False,
            "reason": "UNDER_18_PRODUCT_SCOPE",
            "minimum_age": 18,
            "message": "Personalized entrepreneur matching is currently available for adults aged 18 and above. Public scheme browsing remains available."
        }
    }


def personalized_matching_available(profile: Dict[str, Any]) -> bool:
    age = profile.get("age")
    return age is None or not isinstance(age, (int, float)) or age >= 18

# Centralized Error Handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": str(exc),
            "path": request.url.path
        }
    )

# Endpoints
@app.get("/api/health")
async def health_check():
    """GET /api/health — returns readiness & catalogue count."""
    return get_health_stats()

@app.get("/api/opportunities")
async def list_opportunities(
    sector: Optional[str] = None,
    search: Optional[str] = None,
    support_type: Optional[str] = None,
    scope: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=200)
):
    """GET /api/opportunities — Public catalogue discovery (no profile required)."""
    master = get_m1_opportunity_master()
    filtered = master

    if sector and sector.strip():
        sec_lower = sector.strip().lower()
        filtered = [
            o for o in filtered
            if sec_lower in o.get("primary_sector", "").lower()
            or any(sec_lower in s.lower() for s in o.get("secondary_sectors", []))
        ]

    if search and search.strip():
        filtered = search_opportunities(filtered, search)

    if support_type and support_type.strip():
        filtered = [
            o for o in filtered
            if matches_support_family(o.get("support_types", []), support_type)
        ]

    if scope and scope.strip():
        scope_group = scope.strip().upper()
        filtered = [
            o for o in filtered
            if normalize_scope_group(o.get("scope")) == scope_group
        ]

    total = len(filtered)
    start = (page - 1) * limit
    end = start + limit
    paginated = filtered[start:end]

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "items": paginated
    }

@app.get("/api/opportunities/{opportunity_id}")
@app.get("/api/opportunity/{opportunity_id}")
async def get_opportunity_detail(opportunity_id: str):
    """GET /api/opportunities/{opportunity_id} — Public scheme detail from M1."""
    master = get_m1_opportunity_master()
    opp = next((o for o in master if o.get("opportunity_id") == opportunity_id or o.get("Opportunity_ID") == opportunity_id), None)
    if not opp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Opportunity with ID '{opportunity_id}' not found."
        )

    # Attach requirements & relationships from M1
    all_reqs = get_m1_pathway_requirements()
    opp_reqs = [r for r in all_reqs if r.get("opportunity_id") == opportunity_id]

    all_rels = get_m1_relationships()
    opp_rels = [
        r for r in all_rels
        if r.get("source_opportunity_id") == opportunity_id
        or r.get("target_opportunity_id") == opportunity_id
    ]

    return {
        **opp,
        "requirements": opp_reqs,
        "relationships": opp_rels
    }

@app.post("/api/profile/parse")
async def parse_profile(payload: ParseProfileRequest):
    """POST /api/profile/parse — Multilingual profile extraction via M3. No eligibility decisions."""
    assistant = AIAssistant()
    
    # If existing profile was provided, populate assistant state
    if payload.existing_profile:
        for k, v in payload.existing_profile.items():
            if v is not None:
                assistant.profile[k] = v

    resp = assistant.process_message(payload.message)
    # /api/profile/parse returns the canonical user profile, not the reduced M2 adapter payload.
    # This preserves presentation fields such as education_course while eligibility adapters remain unchanged.
    canonical_profile = sanitize_profile(assistant.profile)

    missing = assistant._get_missing_fields() if hasattr(assistant, "_get_missing_fields") else []
    lang = getattr(assistant, "conversation_language", "English")
    conflicts = getattr(assistant, "last_conflicts", [])

    return {
        "profile": canonical_profile,
        "missing_fields": missing,
        "language": lang,
        "confidence": {},
        "conflicts": conflicts,
        "assistant_response": resp
    }

@app.post("/api/eligibility/check")
async def check_eligibility(payload: ProfilePayload):
    """POST /api/eligibility/check — Deterministic M2 evaluation. No M4 ranking."""
    profile = sanitize_profile(payload.profile or {})
    eligibility_engine = m2_engines["eligibility"]
    gap_analyzer = m2_engines["gaps"]

    evaluations = eligibility_engine.evaluate_all(profile)
    gaps = [gap_analyzer.analyze(profile, ev["opportunity_id"]) for ev in evaluations]

    return {
        "profile": profile,
        "evaluations": evaluations,
        "gaps": gaps
    }

@app.post("/api/opportunities/recommend")
async def recommend_opportunities(payload: RecommendPayload):
    """POST /api/opportunities/recommend — Stage 1 & 2 relevance, Stage 3 M2 eligibility then Stage 4 M4 ranking."""
    profile = sanitize_profile(payload.profile or {})
    if not personalized_matching_available(profile):
        return build_under18_applicability_response(profile)
    master = get_m1_opportunity_master()
    relevance_res = filter_candidate_set(master, profile)
    candidate_ids = {o["opportunity_id"] for o in relevance_res["candidate_set"]}

    evaluations = m2_engines["eligibility"].evaluate_all(profile)
    candidate_evaluations = [e for e in evaluations if e["opportunity_id"] in candidate_ids]

    m4_output = build_recommendations(profile, candidate_evaluations, data_dir=M4_DATA_DIR)
    
    return format_analyze_response(profile, m4_output, relevance_summary=relevance_res["summary"])

from server.ai.pathway_copilot import get_pathway_copilot_guidance

@app.post("/api/pathway/generate")
async def generate_pathway(payload: PathwayPayload):
    """POST /api/pathway/generate — Returns M2 Opportunity Pathway for specific scheme."""
    profile = sanitize_profile(payload.profile or {})
    pathway_engine = m2_engines["pathway"]
    pathway = pathway_engine.build(
        profile=profile,
        opportunity_id=payload.opportunity_id
    )
    return pathway

@app.post("/api/pathway/goal/generate")
async def generate_goal_pathway(payload: GoalPathwayPayload):
    """POST /api/pathway/goal/generate — Generates deterministic Goal Pathway across matched opportunities."""
    profile = sanitize_profile(payload.profile or {})
    master = get_m1_opportunity_master()
    relevance_res = filter_candidate_set(master, profile)
    candidate_ids = {o["opportunity_id"] for o in relevance_res["candidate_set"]}

    evaluations = m2_engines["eligibility"].evaluate_all(profile)
    candidate_evaluations = [e for e in evaluations if e["opportunity_id"] in candidate_ids]
    m4_output = build_recommendations(profile, candidate_evaluations, data_dir=M4_DATA_DIR)
    m4_recs = m4_output.get("recommendations", [])

    overlay = payload.user_progress_overlay or {"completed_requirements": []}
    if payload.client_id:
        from server import progress_db
        db_completed_ids = progress_db.get_completed_requirement_ids(payload.client_id)
        comp_list = list(overlay.get("completed_requirements", []))
        existing_ids = {c.get("requirement_id") for c in comp_list if isinstance(c, dict)}
        for cid in db_completed_ids:
            if cid not in existing_ids:
                comp_list.append({
                    "requirement_id": cid,
                    "status": "COMPLETED",
                    "confirmed_by_user": True
                })
        overlay["completed_requirements"] = comp_list

    builder = m2_engines["goal_pathway"]
    raw_pathway = builder.build(
        profile=profile,
        candidate_evaluations=m4_recs,
        business_goal=payload.business_goal,
        user_progress_overlay=overlay,
        force_general=payload.force_general or False,
        m4_data_dir=M4_DATA_DIR
    )
    res = format_goal_pathway_response(raw_pathway)
    return res

@app.post("/api/pathway/goal/update")
async def update_goal_pathway(payload: GoalPathwayUpdatePayload):
    """POST /api/pathway/goal/update — Recomputes Goal Pathway with updated progress overlay."""
    profile = sanitize_profile(payload.profile or {})
    master = get_m1_opportunity_master()
    relevance_res = filter_candidate_set(master, profile)
    candidate_ids = {o["opportunity_id"] for o in relevance_res["candidate_set"]}

    evaluations = m2_engines["eligibility"].evaluate_all(profile)
    candidate_evaluations = [e for e in evaluations if e["opportunity_id"] in candidate_ids]
    m4_output = build_recommendations(profile, candidate_evaluations, data_dir=M4_DATA_DIR)
    m4_recs = m4_output.get("recommendations", [])

    overlay = payload.user_progress_overlay or {}
    completed_list = list(overlay.get("completed_requirements", []))

    if payload.completed_requirement_id:
        req_id = payload.completed_requirement_id
        if payload.client_id:
            from server import progress_db
            try:
                if payload.action == "COMPLETE":
                    progress_db.complete_requirement(payload.client_id, req_id)
                elif payload.action == "REOPEN":
                    progress_db.reopen_requirement(payload.client_id, req_id)
            except ValueError as ve:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(ve)
                )
        else:
            all_reqs = get_m1_pathway_requirements()
            valid_ids = {r.get("requirement_node_id") for r in all_reqs if r.get("requirement_node_id")}
            if req_id not in valid_ids:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid requirement_id '{req_id}'. Must exist in canonical M1 pathway requirements."
                )

        if payload.action == "COMPLETE":
            if not any(c.get("requirement_id") == req_id for c in completed_list):
                from datetime import datetime, timezone
                completed_list.append({
                    "requirement_id": req_id,
                    "status": "COMPLETED",
                    "confirmed_by_user": True,
                    "confirmed_at": datetime.now(timezone.utc).isoformat()
                })
        elif payload.action == "REOPEN":
            completed_list = [c for c in completed_list if c.get("requirement_id") != req_id]

    if payload.client_id:
        from server import progress_db
        db_completed_ids = progress_db.get_completed_requirement_ids(payload.client_id)
        existing_ids = {c.get("requirement_id") for c in completed_list if isinstance(c, dict)}
        for cid in db_completed_ids:
            if cid not in existing_ids:
                completed_list.append({
                    "requirement_id": cid,
                    "status": "COMPLETED",
                    "confirmed_by_user": True
                })

    overlay["completed_requirements"] = completed_list

    builder = m2_engines["goal_pathway"]
    raw_pathway = builder.build(
        profile=profile,
        candidate_evaluations=m4_recs,
        business_goal=payload.business_goal,
        user_progress_overlay=overlay,
        m4_data_dir=M4_DATA_DIR
    )
    res = format_goal_pathway_response(raw_pathway)
    res["user_progress_overlay"] = overlay
    return res


@app.post("/api/pathway/goal/progress/complete")
async def progress_complete_requirement(payload: CompleteRequirementRequest):
    """POST /api/pathway/goal/progress/complete — Persists requirement completion to SQLite DB."""
    from server import progress_db
    try:
        res = progress_db.complete_requirement(payload.client_id, payload.requirement_id)
        return res
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@app.post("/api/pathway/goal/progress/reopen")
async def progress_reopen_requirement(payload: ReopenRequirementRequest):
    """POST /api/pathway/goal/progress/reopen — Reopens requirement in SQLite DB."""
    from server import progress_db
    try:
        res = progress_db.reopen_requirement(payload.client_id, payload.requirement_id)
        return res
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@app.get("/api/pathway/goal/completed-actions")
async def list_completed_actions(client_id: str = Query(..., description="Client or user UUID")):
    """GET /api/pathway/goal/completed-actions — Returns all server-persisted completed requirement actions enriched with M1 metadata."""
    from server import progress_db
    return progress_db.get_completed_actions(client_id)


class UserResetPayload(BaseModel):
    client_id: Optional[str] = None

@app.post("/api/user/reset")
@app.post("/api/reset")
async def reset_user_data(payload: UserResetPayload):
    """POST /api/user/reset — Idempotently resets all server progress & artifacts for client_id."""
    from server import progress_db
    if not payload.client_id or not str(payload.client_id).strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="client_id is required for reset."
        )
    try:
        return progress_db.reset_user_data(payload.client_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

class CopilotPayload(BaseModel):
    opportunity_id: str
    language: Optional[str] = "English"
    profile: Optional[Dict[str, Any]] = None

@app.post("/api/pathway/copilot")
async def get_pathway_copilot(payload: CopilotPayload):
    """POST /api/pathway/copilot — Personalized AI Pathway Copilot explanation."""
    profile = sanitize_profile(payload.profile or {})
    master = get_m1_opportunity_master()
    result = get_pathway_copilot_guidance(
        profile=profile,
        opportunity_id=payload.opportunity_id,
        language=payload.language or "English",
        master_opps=master,
        m2_engines=m2_engines
    )
    return result

@app.post("/api/analyze")
async def analyze_profile(payload: AnalyzePayload):
    """POST /api/analyze — Primary personalized endpoint conforming to CANONICAL_ANALYZE_RESPONSE_SCHEMA."""
    profile = sanitize_profile(payload.profile or {})
    if not personalized_matching_available(profile):
        return build_under18_applicability_response(profile)
    
    master = get_m1_opportunity_master()
    relevance_res = filter_candidate_set(master, profile)
    candidate_ids = {o["opportunity_id"] for o in relevance_res["candidate_set"]}

    evaluations = m2_engines["eligibility"].evaluate_all(profile)
    candidate_evaluations = [e for e in evaluations if e["opportunity_id"] in candidate_ids]
    
    selected_opp_id = payload.selected_opportunity_id
    if not selected_opp_id and candidate_evaluations:
        selected_opp_id = candidate_evaluations[0]["opportunity_id"]

    pathway_output = None
    if selected_opp_id:
        try:
            pathway_output = m2_engines["pathway"].build(
                profile=profile,
                opportunity_id=selected_opp_id
            )
        except Exception:
            pathway_output = None

    graph_output = None
    try:
        graph_output = m2_engines["graph"].build_personalized_graph(
            profile=profile,
            candidate_evaluations=candidate_evaluations,
            selection_mode="TOP_3",
            limit=3
        )
    except Exception as e:
        print("Graph generation error in analyze:", e)
        graph_output = None

    m4_output = build_recommendations(profile, candidate_evaluations, pathway_results=pathway_output, data_dir=M4_DATA_DIR)
    
    best_matches = m4_output.get("best_matches", [])
    bm_order = {bm["opportunity_id"]: i for i, bm in enumerate(best_matches)}
    candidate_evaluations_sorted = sorted(candidate_evaluations, key=lambda ev: bm_order.get(ev["opportunity_id"], 999))

    graph_output = None
    try:
        graph_output = m2_engines["graph"].build_personalized_graph(
            profile=profile,
            candidate_evaluations=candidate_evaluations_sorted,
            selection_mode="TOP_3",
            limit=3
        )
    except Exception as e:
        print("Graph generation error in analyze:", e)
        graph_output = None
    
    return format_analyze_response(
        profile=profile,
        m4_output=m4_output,
        pathway_output=pathway_output,
        graph_output=graph_output,
        relevance_summary=relevance_res["summary"],
        relevance_res=relevance_res
    )


class GraphPayload(BaseModel):
    profile: Optional[Dict[str, Any]] = None
    selection_mode: Optional[str] = "TOP_3"
    limit: Optional[int] = 3

@app.api_route("/api/graph/generate", methods=["GET", "POST", "OPTIONS"])
async def generate_graph(
    request: Request,
    payload: Optional[GraphPayload] = None,
    selection_mode: Optional[str] = "TOP_3",
    limit: int = 3
):
    """POST/GET/OPTIONS /api/graph/generate — Generates personalized Opportunity Graph for profile & mode."""
    if request.method == "OPTIONS":
        return JSONResponse(content={"status": "ok"}, status_code=200)

    prof_dict = {}
    mode = selection_mode or "TOP_3"
    lim = limit or 3

    if payload and payload.profile:
        prof_dict = payload.profile
        if payload.selection_mode: mode = payload.selection_mode
        if payload.limit: lim = payload.limit
    elif request.method == "POST":
        try:
            body = await request.json()
            if isinstance(body, dict):
                prof_dict = body.get("profile") or {}
                mode = body.get("selection_mode") or mode
                lim = body.get("limit") or lim
        except Exception:
            pass

    profile = sanitize_profile(prof_dict)
    master = get_m1_opportunity_master()
    relevance_res = filter_candidate_set(master, profile)
    candidate_ids = {o["opportunity_id"] for o in relevance_res["candidate_set"]}

    evaluations = m2_engines["eligibility"].evaluate_all(profile)
    candidate_evaluations = [e for e in evaluations if e["opportunity_id"] in candidate_ids]

    selected_opp_id = candidate_evaluations[0]["opportunity_id"] if candidate_evaluations else None
    pathway_output = None
    if selected_opp_id:
        try:
            pathway_output = m2_engines["pathway"].build(profile=profile, opportunity_id=selected_opp_id)
        except Exception:
            pathway_output = None

    m4_output = build_recommendations(profile, candidate_evaluations, pathway_results=pathway_output, data_dir=M4_DATA_DIR)
    best_matches = m4_output.get("best_matches", [])
    bm_order = {bm["opportunity_id"]: i for i, bm in enumerate(best_matches)}
    candidate_evaluations.sort(key=lambda ev: bm_order.get(ev["opportunity_id"], 999))

    return m2_engines["graph"].build_personalized_graph(
        profile=profile,
        candidate_evaluations=candidate_evaluations,
        selection_mode=mode,
        limit=lim
    )


# Static file serving
FRONTEND_DIR = ROOT_DIR / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
