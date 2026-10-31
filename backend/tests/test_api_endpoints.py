import pytest

def test_api_health(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "database" in data["data"]

def test_api_database_status(client):
    res = client.get("/api/database/status")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "tables" in data["data"]

def test_api_database_tables(client):
    res = client.get("/api/database/tables")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert len(data["data"]) >= 10

def test_api_list_rules(client):
    res = client.get("/api/rules")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert len(data["data"]) >= 5

def test_api_dependency_graph(client):
    res = client.get("/api/dependencies/graph")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "nodes" in data["data"]
    assert "edges" in data["data"]

def test_api_audit_logs(client):
    res = client.get("/api/audit-logs")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "items" in data["data"]

def test_api_cannot_manually_mark_repaired(client):
    res = client.patch("/api/issues/TEST-123/status", json={"status": "REPAIRED"})
    assert res.status_code == 400
    assert "Cannot manually mark issue as REPAIRED" in res.json()["error"]


# --- Focused Tests for Audit Findings ---

def test_cors_trusted_origin_allowed(client):
    """Finding 1: Verify explicitly trusted origin is allowed with credentials."""
    res = client.get("/api/health", headers={"Origin": "http://localhost:5173"})
    assert res.status_code == 200
    assert res.headers.get("access-control-allow-origin") == "http://localhost:5173"
    assert res.headers.get("access-control-allow-credentials") == "true"

def test_cors_untrusted_origin_rejected(client):
    """Finding 1: Verify untrusted origin is NOT reflected when credentials are enabled."""
    res = client.get("/api/health", headers={"Origin": "http://evil.com"})
    assert res.status_code == 200
    assert res.headers.get("access-control-allow-origin") is None

def test_invalid_sql_identifier_returns_400(client):
    """Finding 2: Verify invalid SQL identifiers produce HTTP 400 instead of HTTP 500."""
    res_table = client.get("/api/database/tables/invalid;table")
    assert res_table.status_code == 400
    assert "Invalid SQL identifier" in (res_table.json().get("error") or res_table.json().get("message"))

    res_impact = client.get("/api/dependencies/impact?table_name=invalid;name&record_id=1")
    assert res_impact.status_code == 400
    assert "Invalid SQL identifier" in (res_impact.json().get("error") or res_impact.json().get("message"))

    res_dep = client.get("/api/dependencies/table/invalid;name")
    assert res_dep.status_code == 400
    assert "Invalid SQL identifier" in (res_dep.json().get("error") or res_dep.json().get("message"))

def test_nonexistent_scan_issues_returns_404(client):
    """Finding 3: Verify nonexistent scan ID returns HTTP 404 instead of 200."""
    res = client.get("/api/scans/NONEXISTENT-SCAN-ID/issues")
    assert res.status_code == 404
    data = res.json()
    assert data["success"] is False
    assert "not found" in data["message"].lower()

def test_valid_scan_issues_regression(client):
    """Finding 3 Regression: Verify existing scan ID returns HTTP 200 with issues."""
    scans_res = client.get("/api/scans?limit=1")
    assert scans_res.status_code == 200
    scans = scans_res.json().get("data", [])
    if scans:
        scan_id = scans[0]["scan_id"]
        res = client.get(f"/api/scans/{scan_id}/issues")
        assert res.status_code == 200
        assert res.json()["success"] is True

def test_nonexistent_table_neighborhood_returns_404(client):
    """Finding 4: Verify nonexistent table returns HTTP 404 instead of 200."""
    res = client.get("/api/dependencies/table/nonexistent_table_xyz")
    assert res.status_code == 404
    data = res.json()
    assert data["success"] is False
    assert "does not exist" in data["message"]

def test_valid_table_neighborhood_regression(client):
    """Finding 4 Regression: Verify valid table returns HTTP 200 with neighborhood data."""
    res = client.get("/api/dependencies/table/students")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["data"]["table_name"] == "students"
    assert "direct_parents" in data["data"]
    assert "direct_children" in data["data"]
