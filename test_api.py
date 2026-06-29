"""Tests for ECO-IA API."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    # Set test keys before importing the app
    os.environ["ECO_IA_API_KEY"] = "test-api-key"
    os.environ["ECO_IA_ADMIN_KEY"] = "test-admin-key"
    os.environ["DEBUG"] = "true"

    from api.main import create_app
    app = create_app()
    return TestClient(app)


# ──────────────────────────────────────────────────────────────────────────────
# Public endpoints
# ──────────────────────────────────────────────────────────────────────────────

class TestPublicEndpoints:
    def test_root(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["system"] == "ECO-IA"

    def test_health(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_openapi_docs(self, client):
        response = client.get("/docs")
        assert response.status_code == 200

    def test_openapi_json(self, client):
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert schema["info"]["title"] == "ECO-IA API"


# ──────────────────────────────────────────────────────────────────────────────
# Authentication
# ──────────────────────────────────────────────────────────────────────────────

class TestAuthentication:
    def test_service_endpoint_requires_api_key(self, client):
        response = client.get("/api/v1/services/hosting/plans")
        assert response.status_code == 401

    def test_service_endpoint_with_valid_key(self, client):
        response = client.get(
            "/api/v1/services/hosting/plans",
            headers={"X-API-Key": "test-api-key"},
        )
        assert response.status_code == 200

    def test_service_endpoint_with_invalid_key(self, client):
        response = client.get(
            "/api/v1/services/hosting/plans",
            headers={"X-API-Key": "wrong-key"},
        )
        assert response.status_code == 401

    def test_admin_endpoint_requires_admin_key(self, client):
        response = client.get("/api/v1/admin/health")
        assert response.status_code == 403

    def test_admin_endpoint_with_valid_key(self, client):
        response = client.get(
            "/api/v1/admin/health",
            headers={"X-Admin-Key": "test-admin-key"},
        )
        assert response.status_code == 200

    def test_admin_endpoint_api_key_not_sufficient(self, client):
        response = client.get(
            "/api/v1/admin/health",
            headers={"X-API-Key": "test-api-key"},
        )
        assert response.status_code == 403


# ──────────────────────────────────────────────────────────────────────────────
# Services endpoints
# ──────────────────────────────────────────────────────────────────────────────

class TestServiceEndpoints:
    API_HEADERS = {"X-API-Key": "test-api-key"}

    def test_hosting_plans(self, client):
        response = client.get("/api/v1/services/hosting/plans", headers=self.API_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "plans" in data
        assert len(data["plans"]) == 3

    def test_hosting_status(self, client):
        response = client.get("/api/v1/services/hosting/status", headers=self.API_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "operational"

    def test_data_process(self, client):
        response = client.post(
            "/api/v1/services/data/process",
            headers=self.API_HEADERS,
            json={"data": {"key": "value"}, "operation": "summarize"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "processed"
        assert data["operation"] == "summarize"


# ──────────────────────────────────────────────────────────────────────────────
# Admin endpoints
# ──────────────────────────────────────────────────────────────────────────────

class TestAdminEndpoints:
    ADMIN_HEADERS = {"X-Admin-Key": "test-admin-key"}

    def test_health(self, client):
        response = client.get("/api/v1/admin/health", headers=self.ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "agents" in data

    def test_metrics(self, client):
        response = client.get("/api/v1/admin/metrics", headers=self.ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "cpu_percent" in data
        assert "ram_percent" in data

    def test_list_agents(self, client):
        response = client.get("/api/v1/admin/agents", headers=self.ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data
        assert data["total"] == 6

    def test_scheduler_tasks(self, client):
        response = client.get("/api/v1/admin/scheduler/tasks", headers=self.ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert len(data["tasks"]) > 0


# ──────────────────────────────────────────────────────────────────────────────
# Webhook endpoints
# ──────────────────────────────────────────────────────────────────────────────

class TestWebhookEndpoints:
    def test_stripe_webhook_invalid_json(self, client):
        response = client.post(
            "/api/v1/webhooks/stripe",
            content=b"not-json",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 400

    def test_stripe_webhook_unknown_event(self, client):
        import json
        payload = json.dumps({"type": "some.unknown.event", "data": {}}).encode()
        response = client.post(
            "/api/v1/webhooks/stripe",
            content=payload,
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ignored"

    def test_stripe_webhook_payment_succeeded(self, client):
        import json
        payload = json.dumps({
            "type": "invoice.payment_succeeded",
            "data": {"object": {"id": "inv_test123"}},
        }).encode()
        response = client.post(
            "/api/v1/webhooks/stripe",
            content=payload,
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 200
        assert response.json()["action"] == "payment_recorded"
