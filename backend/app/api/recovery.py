from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
from backend.app.models.schemas import ApiResponse, CreateCheckpointRequest, RollbackCheckpointRequest
from backend.app.services.recovery_manager import RecoveryManager
from backend.app.database.connection import get_connection

router = APIRouter(prefix="/recovery", tags=["Recovery Center"])

@router.get("/checkpoints", response_model=ApiResponse[List[Dict[str, Any]]])
def list_checkpoints(limit: int = 50):
    """Retrieves all application-level recovery checkpoints."""
    try:
        checkpoints = RecoveryManager.list_checkpoints(limit)
        return ApiResponse(
            success=True,
            message=f"Retrieved {len(checkpoints)} recovery checkpoints.",
            data=checkpoints
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/checkpoints", response_model=ApiResponse[Dict[str, Any]])
def create_checkpoint(payload: CreateCheckpointRequest):
    """Creates a manual recovery checkpoint of a table before maintenance."""
    try:
        result = RecoveryManager.create_checkpoint(
            target_table=payload.target_table,
            checkpoint_name=payload.checkpoint_name,
            checkpoint_type="MANUAL"
        )
        return ApiResponse(
            success=True,
            message=f"Created recovery checkpoint '{payload.checkpoint_name}'.",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/rollback", response_model=ApiResponse[Dict[str, Any]])
def rollback_to_checkpoint(payload: RollbackCheckpointRequest):
    """Restores database table state from a previously captured recovery checkpoint."""
    if not payload.confirmed:
        raise HTTPException(
            status_code=400,
            detail="Restoring from a checkpoint overwrites current table rows. Confirmation required (confirmed=True)."
        )
    try:
        result = RecoveryManager.restore_from_checkpoint(payload.checkpoint_id, operator="ADMIN_USER")
        return ApiResponse(
            success=True,
            message=result["message"],
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history", response_model=ApiResponse[List[Dict[str, Any]]])
def get_recovery_history():
    """Retrieves history of rollback and recovery actions from the audit log."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM audit_logs
                WHERE event_type IN ('CHECKPOINT_CREATED', 'CHECKPOINT_RESTORED', 'REPAIR_FAILED', 'TRANSACTION_DEMO_ROLLBACK')
                ORDER BY timestamp DESC
                LIMIT 50
            """)
            rows = cur.fetchall()
            return ApiResponse(
                success=True,
                message=f"Retrieved {len(rows)} recovery events.",
                data=rows
            )
    finally:
        conn.close()
