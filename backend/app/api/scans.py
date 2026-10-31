from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
from datetime import datetime
from backend.app.database.connection import get_connection
from backend.app.models.schemas import ApiResponse, ScanTriggerRequest, ScanSummary, IntegrityIssueModel
from backend.app.services.integrity_scanner import IntegrityScanner

router = APIRouter(prefix="/scans", tags=["Integrity Scans"])

scanner = IntegrityScanner()

@router.post("", response_model=ApiResponse[Dict[str, Any]])
def trigger_scan(payload: ScanTriggerRequest):
    """Triggers an integrity scan across specified or default database tables."""
    try:
        result = scanner.run_scan(
            scan_type=payload.scan_type,
            target_tables=payload.target_tables,
            rule_codes=payload.rule_codes,
            operator="ADMIN_USER"
        )
        return ApiResponse(
            success=True,
            message=f"Integrity scan completed. Discovered {result['issues_found']} issues.",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=ApiResponse[List[ScanSummary]])
def list_scans(limit: int = 20):
    """Retrieves execution history of past scans."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM scan_runs
                ORDER BY start_time DESC
                LIMIT %s
            """, (limit,))
            rows = cur.fetchall()

            summaries = []
            for r in rows:
                duration_ms = None
                if r["end_time"] and r["start_time"]:
                    duration_ms = round((r["end_time"] - r["start_time"]).total_seconds() * 1000, 2)
                
                target_tables_list = r["target_tables"].split(",") if r["target_tables"] else []

                summaries.append(ScanSummary(
                    scan_id=r["scan_id"],
                    scan_type=r["scan_type"],
                    target_tables=target_tables_list,
                    start_time=r["start_time"],
                    end_time=r["end_time"],
                    status=r["status"],
                    total_rows_inspected=r["total_rows_inspected"] or 0,
                    issues_found=r["issues_found"] or 0,
                    critical_count=r["critical_count"] or 0,
                    high_count=r["high_count"] or 0,
                    medium_count=r["medium_count"] or 0,
                    low_count=r["low_count"] or 0,
                    duration_ms=duration_ms,
                    error_message=r.get("error_message")
                ))

            return ApiResponse(
                success=True,
                message=f"Retrieved {len(summaries)} scan runs.",
                data=summaries
            )
    finally:
        conn.close()

@router.get("/{scan_id}", response_model=ApiResponse[Dict[str, Any]])
def get_scan(scan_id: str):
    """Retrieves details of a specific scan run."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM scan_runs WHERE scan_id = %s", (scan_id,))
            run = cur.fetchone()
            if not run:
                raise HTTPException(status_code=404, detail=f"Scan run '{scan_id}' not found.")

            cur.execute("SELECT * FROM integrity_issues WHERE scan_id = %s", (scan_id,))
            issues = cur.fetchall()

            return ApiResponse(
                success=True,
                message=f"Retrieved scan run {scan_id}.",
                data={
                    "run": run,
                    "issues_count": len(issues),
                    "issues": issues
                }
            )
    finally:
        conn.close()

@router.get("/{scan_id}/issues", response_model=ApiResponse[List[Dict[str, Any]]])
def get_scan_issues(scan_id: str):
    """Retrieves all issues detected by a specific scan."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS c FROM scan_runs WHERE scan_id = %s", (scan_id,))
            if cur.fetchone()["c"] == 0:
                raise HTTPException(status_code=404, detail=f"Scan run '{scan_id}' not found.")

            cur.execute("SELECT * FROM integrity_issues WHERE scan_id = %s ORDER BY severity ASC", (scan_id,))
            issues = cur.fetchall()
            return ApiResponse(
                success=True,
                message=f"Retrieved {len(issues)} issues for scan {scan_id}.",
                data=issues
            )
    finally:
        conn.close()
