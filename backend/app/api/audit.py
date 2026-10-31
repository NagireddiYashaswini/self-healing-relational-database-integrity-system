from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
from backend.app.models.schemas import ApiResponse
from backend.app.services.audit_service import AuditService

router = APIRouter(prefix="/audit-logs", tags=["Audit & Traceability"])

@router.get("", response_model=ApiResponse[Dict[str, Any]])
def get_audit_logs(
    event_type: Optional[str] = None,
    target_table: Optional[str] = None,
    result: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """Retrieves paginated audit log events with filtering."""
    try:
        logs_data = AuditService.get_logs(
            event_type=event_type,
            target_table=target_table,
            result=result,
            search=search,
            limit=limit,
            offset=offset
        )
        return ApiResponse(
            success=True,
            message=f"Retrieved {len(logs_data['items'])} audit events.",
            data=logs_data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
