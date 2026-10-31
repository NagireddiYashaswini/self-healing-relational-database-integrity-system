from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
from backend.app.database.connection import get_connection
from backend.app.models.schemas import (
    ApiResponse, RepairPreviewRequest, RepairPreviewResponse, 
    RepairExecuteRequest, RepairExecutionModel
)
from backend.app.services.repair_engine import RepairEngine

router = APIRouter(prefix="/repairs", tags=["Self-Healing & Repair Center"])

engine = RepairEngine()

@router.get("/recommendations", response_model=ApiResponse[List[Dict[str, Any]]])
def list_recommendations(approval_status: Optional[str] = None):
    """Retrieves all pending or approved self-healing recommendations."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            sql = """
                SELECT 
                    r.*,
                    i.table_name,
                    i.record_id,
                    i.category,
                    i.column_name,
                    i.invalid_value,
                    i.status AS issue_status
                FROM repair_recommendations r
                JOIN integrity_issues i ON r.issue_id = i.issue_id
            """
            params = []
            if approval_status:
                sql += " WHERE r.approval_status = %s"
                params.append(approval_status)
            sql += " ORDER BY r.created_at DESC"

            cur.execute(sql, tuple(params))
            recs = cur.fetchall()

            return ApiResponse(
                success=True,
                message=f"Retrieved {len(recs)} repair recommendations.",
                data=recs
            )
    finally:
        conn.close()

@router.get("/recommendations/{recommendation_id}", response_model=ApiResponse[Dict[str, Any]])
def get_recommendation(recommendation_id: int):
    """Retrieves a single repair recommendation by ID."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    r.*,
                    i.table_name,
                    i.record_id,
                    i.category,
                    i.column_name,
                    i.invalid_value
                FROM repair_recommendations r
                JOIN integrity_issues i ON r.issue_id = i.issue_id
                WHERE r.recommendation_id = %s
            """, (recommendation_id,))
            rec = cur.fetchone()
            if not rec:
                raise HTTPException(status_code=404, detail="Recommendation not found.")
            return ApiResponse(success=True, message="Recommendation retrieved.", data=rec)
    finally:
        conn.close()

@router.post("/preview", response_model=ApiResponse[RepairPreviewResponse])
def preview_repair(payload: RepairPreviewRequest):
    """Generates an impact analysis, state diff, and SQL preview for an issue before execution."""
    try:
        preview = engine.get_repair_preview(
            issue_id=payload.issue_id,
            strategy_override=payload.strategy.value if payload.strategy else None,
            repair_parameters=payload.repair_parameters
        )
        return ApiResponse(
            success=True,
            message="Repair preview generated successfully.",
            data=RepairPreviewResponse(**preview)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/approve", response_model=ApiResponse[Dict[str, Any]])
def approve_repair(recommendation_id: int):
    """Authorizes a repair recommendation for execution."""
    try:
        result = engine.approve_recommendation(recommendation_id, operator="ADMIN_USER")
        return ApiResponse(success=True, message=result["message"], data=result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/execute", response_model=ApiResponse[Dict[str, Any]])
def execute_repair(payload: RepairExecuteRequest):
    """
    Executes a self-healing repair within an atomic transaction.
    Requires confirmed=True for destructive strategies (DELETE_RECORD, QUARANTINE).
    """
    try:
        # Destructive safety check
        if payload.strategy in ["DELETE_RECORD", "QUARANTINE"] and not payload.confirmed:
            raise HTTPException(
                status_code=400,
                detail="Destructive repair strategy requires explicit user confirmation (confirmed=True)."
            )

        result = engine.execute_repair(
            issue_id=payload.issue_id,
            strategy=payload.strategy.value,
            repair_parameters=payload.repair_parameters,
            confirmed=payload.confirmed,
            operator=payload.operator
        )
        return ApiResponse(success=True, message=result["message"], data=result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/executions", response_model=ApiResponse[List[Dict[str, Any]]])
def list_executions(limit: int = 50):
    """Retrieves history of past repair executions."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT e.*, i.table_name, i.record_id, i.category
                FROM repair_executions e
                JOIN integrity_issues i ON e.issue_id = i.issue_id
                ORDER BY e.executed_at DESC
                LIMIT %s
            """, (limit,))
            rows = cur.fetchall()
            return ApiResponse(
                success=True,
                message=f"Retrieved {len(rows)} repair execution logs.",
                data=rows
            )
    finally:
        conn.close()

@router.get("/executions/{execution_id}", response_model=ApiResponse[Dict[str, Any]])
def get_execution(execution_id: str):
    """Retrieves deep details of a specific repair execution including before/after state diffs."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM repair_executions WHERE execution_id = %s", (execution_id,))
            exec_row = cur.fetchone()
            if not exec_row:
                raise HTTPException(status_code=404, detail="Execution log not found.")
            return ApiResponse(success=True, message="Execution retrieved.", data=exec_row)
    finally:
        conn.close()
