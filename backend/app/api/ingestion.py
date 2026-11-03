from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from backend.app.models.schemas import ApiResponse, IngestionRecordRequest, IngestionResponse
from backend.app.services.ingestion_service import IngestionService, CORE_BUSINESS_TABLES

router = APIRouter(prefix="/ingestion", tags=["Data Ingestion & Staging"])

@router.get("/tables", response_model=ApiResponse[List[str]])
def list_ingestion_tables():
    """Returns the list of the 6 core business tables eligible for record ingestion."""
    return ApiResponse(
        success=True,
        message="Eligible ingestion tables retrieved.",
        data=CORE_BUSINESS_TABLES
    )

@router.get("/schema/{table_name}", response_model=ApiResponse[Dict[str, Any]])
def get_table_schema(table_name: str):
    """Retrieves column metadata, nullability, data types, and FK reference options for dynamic form generation."""
    try:
        schema = IngestionService.get_table_schema(table_name)
        return ApiResponse(
            success=True,
            message=f"Schema retrieved for table '{table_name}'.",
            data=schema
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/insert", response_model=ApiResponse[IngestionResponse])
def insert_record(payload: IngestionRecordRequest):
    """
    Ingests a record via the staging pipeline:
    1. Stages incoming record in staging_[table_name].
    2. Runs integrity validations (required fields, FK parent existence, domains, uniqueness).
    3. If valid: Transactionally commits to production business table, marks staging as VALID.
    4. If invalid: Marks staging as REJECTED and archives record into quarantine_records.
    """
    try:
        result = IngestionService.ingest_record(
            table_name=payload.table_name,
            record_data=payload.record_data,
            external_ref=payload.external_ref,
            operator="ADMIN_USER"
        )
        return ApiResponse(
            success=result["success"],
            message=result["message"],
            data=IngestionResponse(**result)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

