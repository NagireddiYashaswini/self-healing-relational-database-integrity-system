import pytest
from backend.app.services.audit_service import AuditService, sanitize_json

def test_sanitize_json_redaction():
    payload = {
        "username": "admin",
        "password": "supersecretpassword123",
        "api_token": "xyz987token",
        "email": "test@univ.edu"
    }
    sanitized_str = sanitize_json(payload)
    assert "[REDACTED]" in sanitized_str
    assert "supersecretpassword123" not in sanitized_str
    assert "test@univ.edu" in sanitized_str

def test_audit_log_persisted(mysql_available):
    if not mysql_available:
        pytest.skip("Local MySQL server not reachable")
    
    event_id = AuditService.log_event(
        event_type="TEST_EVENT",
        action_description="Automated unit test audit log entry.",
        actor="PYTEST",
        result="SUCCESS"
    )
    assert event_id > 0

    logs = AuditService.get_logs(event_type="TEST_EVENT", limit=1)
    assert logs["total"] >= 1
    assert logs["items"][0]["event_type"] == "TEST_EVENT"
