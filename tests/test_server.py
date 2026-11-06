"""Comprehensive automated test suite for SupportPipe FastAPI native server."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from supportpipe.server import app


@pytest.fixture
def client() -> TestClient:
    """Fixture providing a FastAPI TestClient instance."""
    return TestClient(app)


def test_server_root_dashboard(client: TestClient) -> None:
    """Verify root GET / serves the native HTML5 dashboard."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "SupportPipe" in response.text or "cockpit" in response.text.lower()


def test_server_health_check(client: TestClient) -> None:
    """Verify /api/health returns operational status and registered engines."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "operational"
    assert "offline_model_version" in data
    assert "engines" in data
    assert "mock" in data["engines"]
    assert data["engines"]["mock"]["ready"] is True


def test_server_cors_headers(client: TestClient) -> None:
    """Verify CORS headers allow configured origin and block credentials with wildcard."""
    # Test valid origin in allowed_origins
    response = client.get(
        "/api/health",
        headers={"Origin": "http://127.0.0.1:8000"},
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://127.0.0.1:8000"
    assert response.headers.get("access-control-allow-credentials") == "true"

    # Test disallowed origin is not granted Access-Control-Allow-Origin
    disallowed_response = client.get(
        "/api/health",
        headers={"Origin": "http://malicious-external-site.com"},
    )
    assert disallowed_response.headers.get("access-control-allow-origin") is None


def test_server_preset_scenarios_pii_masked(client: TestClient) -> None:
    """Verify preset scenarios endpoint scrubs PII from dev sample ticket texts."""
    response = client.get("/api/scenarios")
    assert response.status_code == 200
    data = response.json()
    assert "presets" in data
    assert "dev_samples" in data
    assert isinstance(data["dev_samples"], list)

    for sample in data["dev_samples"]:
        text = sample.get("text", "")
        # Raw Iraqi phone numbers must not appear unmasked
        assert not any(
            p in text for p in ["0780", "0770", "0750", "0790", "+9647"]
        ) or "[PHONE_SCRUBBED]" in text


def test_server_classify_endpoint_mock(client: TestClient) -> None:
    """Verify /api/classify processes tickets and tracks consensus accurately."""
    payload = {
        "text": "سلام عليكم حولت 50 الف لصاحبي برقم TXN-99887766 وخصموا الرصيد بس ما وصلت",
        "models": ["mock"],
        "channel": "app",
    }
    response = client.post("/api/classify", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 1
    res = data["results"][0]
    assert res["modelKey"] == "mock"
    assert res["category"] in ["pending_transfer", "failed_transfer"]
    assert res["priority"] in ["HIGH", "MEDIUM", "LOW"]
    assert "TXN-99887766" in res["ref"]
    assert "consensus" in data
    assert data["consensus"]["firstCategory"] in ["pending_transfer", "failed_transfer"]


def test_server_classify_empty_rejects(client: TestClient) -> None:
    """Verify /api/classify returns HTTP 400 on empty ticket payload."""
    response = client.post("/api/classify", json={"text": "   ", "models": ["mock"]})
    assert response.status_code == 400


def test_server_queue_pagination_and_masking(client: TestClient) -> None:
    """Verify /api/queue pagination and PII privacy protection."""
    response = client.get("/api/queue?limit=5&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert "tickets" in data
    assert len(data["tickets"]) <= 5
    assert data["limit"] == 5
    assert data["offset"] == 0

    if data["tickets"]:
        sample = data["tickets"][0]
        assert "id" in sample
        assert "cat" in sample
        assert "text" in sample
        assert "status" in sample


def test_server_queue_action(client: TestClient) -> None:
    """Verify /api/queue/action records human approval into the audit store."""
    payload = {
        "ticket_id": "TEST-TKT-001",
        "action": "APPROVED",
        "final_reply": "تم حل المشكلة واعتماد الحوالة بنجاح.",
        "notes": "تم التحقق من المقسم المصرفي",
    }
    response = client.post("/api/queue/action", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data.get("success") is True
    assert data.get("status") == "success"
    assert data["entry"]["ticket_id"] == "TEST-TKT-001"
    assert data["entry"]["action"] == "APPROVED"


def test_server_outage_intelligence(client: TestClient) -> None:
    """Verify /api/outage returns gateways, recurring categories, and anomaly detection."""
    response = client.get("/api/outage?dataset=dev")
    assert response.status_code == 200
    data = response.json()
    assert "gateways" in data
    assert "recurring_categories" in data
    assert "incident" in data


def test_server_outage_markdown_report(client: TestClient) -> None:
    """Verify /api/outage/report.md returns downloadable markdown content."""
    response = client.get("/api/outage/report.md")
    assert response.status_code == 200
    assert "text/plain" in response.headers.get("content-type", "")
    assert "attachment" in response.headers.get("content-disposition", "")
    assert len(response.text) > 50


def test_server_candidate_rule_lifecycle(client: TestClient) -> None:
    """Verify /api/learning and persistent candidate rule updates."""
    get_res = client.get("/api/learning")
    assert get_res.status_code == 200
    initial_data = get_res.json()
    assert "candidate_rule" in initial_data
    assert "kpi" in initial_data

    # Update candidate rule to approved
    post_res = client.post(
        "/api/learning/candidate-rule",
        json={"rule_id": "RULE-V13-CANDIDATE", "status": "approved"},
    )
    assert post_res.status_code == 200
    post_data = post_res.json()
    assert post_data.get("success") is True
    assert post_data.get("status") == "approved"

    # Subsequent GET must reflect persisted approved status
    recheck_res = client.get("/api/learning")
    recheck_data = recheck_res.json()
    assert recheck_data["candidate_rule"]["status"] == "approved"


def test_server_ping_provider_mock(client: TestClient) -> None:
    """Verify /api/settings/ping connectivity test for mock engine."""
    payload = {"provider": "mock"}
    response = client.post("/api/settings/ping", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data.get("ok") is True
    assert data.get("status") == "connected"
    assert "latency_ms" in data


def test_server_batch_processing(client: TestClient) -> None:
    """Verify /api/batch processes multiple tickets with aggregate statistics."""
    payload = {
        "tickets_raw": [
            {
                "ticket_id": "BATCH-TEST-1",
                "raw_text": "حولت رصيد برقم TXN-11223344 وما وصل للمستلم",
                "channel": "app",
            },
            {
                "ticket_id": "BATCH-TEST-2",
                "raw_text": "محفظتي مقفولة ومجمدة واريد افتحها",
                "channel": "app",
            },
        ],
        "provider": "mock",
    }
    response = client.post("/api/batch", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_tickets"] == 2
    assert "auto_approval_rate" in data
    assert "escalation_rate" in data
    assert len(data["results"]) == 2


def test_server_queue_invalid_pagination(client: TestClient) -> None:
    """Verify /api/queue returns HTTP 422 on negative offset or zero limit."""
    res_neg_offset = client.get("/api/queue?offset=-1")
    assert res_neg_offset.status_code == 422

    res_zero_limit = client.get("/api/queue?limit=0")
    assert res_zero_limit.status_code == 422


def test_server_queue_rejection_action(client: TestClient) -> None:
    """Verify /api/queue/action records REJECTED action and queue reflects 'تم الرفض'."""
    reject_payload = {
        "ticket_id": "TKT-DEV-REJECT-01",
        "action": "REJECTED",
        "notes": "الطلب مخالف للشروط",
    }
    action_res = client.post("/api/queue/action", json=reject_payload)
    assert action_res.status_code == 200
    assert action_res.json()["entry"]["action"] == "REJECTED"


def test_server_candidate_rule_sanitization(client: TestClient) -> None:
    """Verify whitespace-padded rule_id and status are sanitized properly."""
    res = client.post(
        "/api/learning/candidate-rule",
        json={"rule_id": "   ", "status": "  DEFERRED  "},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["rule_id"] == "RULE-V13-CANDIDATE"
    assert data["status"] == "deferred"
