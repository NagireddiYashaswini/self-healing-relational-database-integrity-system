from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
from backend.app.models.schemas import ApiResponse, TransactionDemoResponse, TransactionDemoType
from backend.app.services.transaction_manager import TransactionManager

router = APIRouter(prefix="/transactions", tags=["DBMS Transaction Simulator"])

@router.post("/demo", response_model=ApiResponse[TransactionDemoResponse])
def run_transaction_demo(scenario: TransactionDemoType = TransactionDemoType.SIMULATED_FAILURE_ROLLBACK):
    """
    Executes an interactive demonstration of MySQL InnoDB ACID transaction mechanics.
    Supports COMMIT_SUCCESS, SIMULATED_FAILURE_ROLLBACK, and SAVEPOINT_PARTIAL_ROLLBACK.
    """
    try:
        result = TransactionManager.run_demonstration(scenario.value)
        return ApiResponse(
            success=True,
            message=result["explanation"],
            data=TransactionDemoResponse(**result)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=ApiResponse[List[Dict[str, Any]]])
def get_transactions(limit: int = 50):
    """Retrieves transaction history logs recorded by the system."""
    try:
        history = TransactionManager.get_transaction_history(limit)
        return ApiResponse(
            success=True,
            message=f"Retrieved {len(history)} transaction records.",
            data=history
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
