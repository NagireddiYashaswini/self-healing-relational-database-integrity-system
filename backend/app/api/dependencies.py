from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
from backend.app.models.schemas import ApiResponse, DependencyGraphResponse
from backend.app.services.dependency_analyzer import DependencyAnalyzer
from backend.app.database.connection import validate_identifier

router = APIRouter(prefix="/dependencies", tags=["Relational Dependency Graph"])

analyzer = DependencyAnalyzer()

@router.get("/graph", response_model=ApiResponse[DependencyGraphResponse])
def get_dependency_graph():
    """Generates the full directed relational dependency graph of the database."""
    try:
        graph_data = analyzer.build_graph()
        return ApiResponse(
            success=True,
            message="Relational dependency graph built successfully.",
            data=DependencyGraphResponse(**graph_data)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/table/{table_name}", response_model=ApiResponse[Dict[str, Any]])
def get_table_dependency(table_name: str):
    """Retrieves direct parents, direct children, ancestors, and descendants for a specific table."""
    try:
        table_name = validate_identifier(table_name)
        data = analyzer.get_table_neighborhood(table_name)
        if data is None:
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' does not exist.")
        return ApiResponse(
            success=True,
            message=f"Dependency neighborhood retrieved for table '{table_name}'.",
            data=data
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/impact", response_model=ApiResponse[Dict[str, Any]])
def assess_impact(table_name: str, record_id: str, action: str = "DELETE_RECORD"):
    """Calculates foreign key cascading impact and blast radius before modifying a record."""
    try:
        table_name = validate_identifier(table_name)
        impact = analyzer.assess_repair_impact(table_name, record_id, action)
        return ApiResponse(
            success=True,
            message="Repair impact assessment completed.",
            data=impact
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
