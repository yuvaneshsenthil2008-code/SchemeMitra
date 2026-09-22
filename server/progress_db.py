"""
SchemeMitra — Server-Side Pathway Progress SQLite Database Module
Authoritative SQLite storage for user requirement progress (goal_requirement_progress).
"""

from __future__ import annotations
import sqlite3
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from modules.M2_eligibility_graph.pathway.requirement_presentation import format_requirement_presentation

# Root directory of project
ROOT_DIR = Path(__file__).resolve().parents[1]
DB_DIR = ROOT_DIR / "server" / "data"
DB_PATH = DB_DIR / "schememitra_progress.db"

_cached_req_map: Optional[Dict[str, Any]] = None
_cached_opp_map: Optional[Dict[str, Any]] = None


def _get_m1_maps():
    global _cached_req_map, _cached_opp_map
    if _cached_req_map is None or _cached_opp_map is None:
        from server.adapters import get_m1_pathway_requirements, get_m1_opportunity_master
        reqs = get_m1_pathway_requirements()
        opps = get_m1_opportunity_master()
        _cached_req_map = {r.get("requirement_node_id"): r for r in reqs if r.get("requirement_node_id")}
        _cached_opp_map = {o.get("opportunity_id"): o for o in opps if o.get("opportunity_id")}
    return _cached_req_map, _cached_opp_map


def get_db_path() -> Path:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    return DB_PATH


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    try:
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS goal_requirement_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id TEXT NOT NULL,
                    requirement_id TEXT NOT NULL,
                    source_opportunity_id TEXT,
                    status TEXT NOT NULL,
                    confirmed_by_user INTEGER NOT NULL DEFAULT 1,
                    completed_at TEXT,
                    updated_at TEXT,
                    UNIQUE(client_id, requirement_id)
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_artifacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id TEXT NOT NULL,
                    artifact_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    display_name TEXT,
                    notes TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    UNIQUE(client_id, artifact_type)
                )
            """)
    finally:
        conn.close()



def complete_requirement(client_id: str, requirement_id: str) -> Dict[str, Any]:
    if not client_id or not str(client_id).strip():
        raise ValueError("client_id is required for progress persistence.")
    
    req_id = str(requirement_id).strip()
    req_map, opp_map = _get_m1_maps()
    
    if req_id not in req_map:
        raise ValueError(f"Invalid requirement_id '{req_id}'. Must exist in canonical M1 pathway requirements.")
    
    req_info = req_map[req_id]
    source_opp_id = req_info.get("opportunity_id")
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    conn = get_connection()
    try:
        with conn:
            conn.execute("""
                INSERT INTO goal_requirement_progress (
                    client_id, requirement_id, source_opportunity_id, status, confirmed_by_user, completed_at, updated_at
                ) VALUES (?, ?, ?, 'COMPLETED', 1, ?, ?)
                ON CONFLICT(client_id, requirement_id) DO UPDATE SET
                    status = 'COMPLETED',
                    source_opportunity_id = excluded.source_opportunity_id,
                    confirmed_by_user = 1,
                    completed_at = excluded.completed_at,
                    updated_at = excluded.updated_at
            """, (client_id, req_id, source_opp_id, now_iso, now_iso))
    finally:
        conn.close()
        
    return {
        "client_id": client_id,
        "requirement_id": req_id,
        "source_opportunity_id": source_opp_id,
        "status": "COMPLETED",
        "confirmed_by_user": True,
        "completed_at": now_iso
    }


def reopen_requirement(client_id: str, requirement_id: str) -> Dict[str, Any]:
    if not client_id or not str(client_id).strip():
        raise ValueError("client_id is required for progress persistence.")
        
    req_id = str(requirement_id).strip()
    conn = get_connection()
    try:
        with conn:
            conn.execute("""
                DELETE FROM goal_requirement_progress
                WHERE client_id = ? AND requirement_id = ?
            """, (client_id, req_id))
    finally:
        conn.close()
        
    return {
        "client_id": client_id,
        "requirement_id": req_id,
        "status": "REOPENED"
    }


def get_completed_requirement_ids(client_id: str) -> List[str]:
    if not client_id or not str(client_id).strip():
        return []
        
    conn = get_connection()
    try:
        cursor = conn.execute("""
            SELECT requirement_id FROM goal_requirement_progress
            WHERE client_id = ? AND status = 'COMPLETED'
        """, (client_id,))
        return [row["requirement_id"] for row in cursor.fetchall()]
    finally:
        conn.close()


def get_completed_actions(client_id: str) -> Dict[str, Any]:
    if not client_id or not str(client_id).strip():
        return {"completed_actions": [], "count": 0}
        
    conn = get_connection()
    try:
        cursor = conn.execute("""
            SELECT requirement_id, source_opportunity_id, status, completed_at
            FROM goal_requirement_progress
            WHERE client_id = ? AND status = 'COMPLETED'
            ORDER BY completed_at DESC
        """, (client_id,))
        rows = cursor.fetchall()
    finally:
        conn.close()
        
    req_map, opp_map = _get_m1_maps()
    completed_actions = []
    
    for row in rows:
        rid = row["requirement_id"]
        req_node = req_map.get(rid) or {}
        opp_id = row["source_opportunity_id"] or req_node.get("opportunity_id") or ""
        opp_info = opp_map.get(opp_id) or {}
        
        opp_name = opp_info.get("Opportunity_Name") or opp_info.get("opportunity_name") or opp_id
        
        req_type_val = req_node.get("requirement_type", "DOCUMENT")
        pres = format_requirement_presentation(req_node)
        canonical_title = pres["canonical_title"]
        display_title = pres["display_title"]
        supporting_text = pres["supporting_text"]
        
        completed_actions.append({
            "requirement_id": rid,
            "canonical_title": canonical_title,
            "display_title": display_title,
            "title": display_title,
            "supporting_text": supporting_text,
            "requirement_type": req_type_val,
            "source_opportunity_id": opp_id,
            "source_opportunity_name": opp_name,
            "status": "COMPLETED",
            "basis": "CONFIRMED_USER_PROGRESS",
            "completed_at": row["completed_at"],
            "official_source_url": req_node.get("official_source_url") or opp_info.get("Official_Source_URL") or "https://myscheme.gov.in/"
        })
        
    return {
        "completed_actions": completed_actions,
        "count": len(completed_actions)
    }


def reset_user_data(client_id: str) -> Dict[str, Any]:
    if not client_id or not str(client_id).strip():
        raise ValueError("client_id is required for reset.")
        
    cid = str(client_id).strip()
    conn = get_connection()
    try:
        with conn:
            cur1 = conn.execute("DELETE FROM goal_requirement_progress WHERE client_id = ?", (cid,))
            c1 = cur1.rowcount
            cur2 = conn.execute("DELETE FROM user_artifacts WHERE client_id = ?", (cid,))
            c2 = cur2.rowcount
    finally:
        conn.close()
        
    return {
        "client_id": cid,
        "goal_requirement_progress_deleted": c1 if c1 >= 0 else 0,
        "user_artifacts_deleted": c2 if c2 >= 0 else 0,
        "status": "SUCCESS"
    }


# Automatically initialize table schema on module import
init_db()

