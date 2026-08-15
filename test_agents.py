"""Tests for ECO-IA agents."""

import asyncio
import os
import sys
from unittest.mock import AsyncMock, patch

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from agents.analytics import AnalyticsAgent
from agents.analytics.dashboard import DashboardData
from agents.analytics.predictor import Predictor
from agents.analytics.reporter import Reporter
from agents.devops import DevOpsAgent
from agents.devops.backup import BackupManager
from agents.monetization import MonetizationAgent
from agents.monetization.billing import BillingManager
from agents.monetization.clients import ClientManager
from agents.monetization.pricing import PricingEngine
from agents.resources import ResourcesAgent
from agents.resources.optimizer import ResourceOptimizer
from agents.security import SecurityAgent
from agents.security.firewall import FirewallManager
from agents.security.intrusion_detector import IntrusionDetector
from core.agent_manager import AgentManager
from core.communication import Message, MessageBus
from core.llm_connector import LLMConnector
from core.scheduler import TaskScheduler
from orchestrator import (
    MasterOrchestrator,
    OrchestratorAgent,
    bytes_to_human,
    iso_now,
    safe_json,
)


@pytest.fixture
def resources_agent():
    return ResourcesAgent()


@pytest.fixture
def security_agent():
    return SecurityAgent()


@pytest.fixture
def analytics_agent():
    return AnalyticsAgent()


@pytest.fixture
def monetization_agent():
    return MonetizationAgent()


@pytest.fixture
def devops_agent():
    return DevOpsAgent()

# ──────────────────────────────────────────────────────────────────────────────
# Core – MessageBus
# ──────────────────────────────────────────────────────────────────────────────

class TestMessageBus:
    def setup_method(self):
        self.bus = MessageBus()

    @pytest.mark.asyncio
    async def test_publish_and_subscribe(self):
        received = []

        async def handler(msg: Message):
            received.append(msg)

        await self.bus.subscribe("agent_a", handler)
        msg = Message(sender="agent_b", target="agent_a", content={"type": "ping"})
        await self.bus.publish(msg)

        assert len(received) == 1
        assert received[0].content["type"] == "ping"

    @pytest.mark.asyncio
    async def test_broadcast(self):
        received = []

        async def handler(msg: Message):
            received.append(msg)

        await self.bus.subscribe("agent_a", handler)
        msg = Message(sender="orchestrator", target="*", content={"type": "broadcast"})
        await self.bus.publish(msg)

        assert len(received) == 1

    def test_get_stats(self):
        stats = self.bus.get_stats()
        assert "total_messages" in stats
        assert "subscribers" in stats

    def test_get_history(self):
        history = self.bus.get_history()
        assert isinstance(history, list)


# ──────────────────────────────────────────────────────────────────────────────
# Core – TaskScheduler
# ──────────────────────────────────────────────────────────────────────────────

class TestTaskScheduler:
    def setup_method(self):
        self.scheduler = TaskScheduler()

    def test_register_and_list(self):
        async def dummy():
            pass

        self.scheduler.register("task1", dummy, 60, "Test task")
        tasks = self.scheduler.list_tasks()
        assert len(tasks) == 1
        assert tasks[0]["task_id"] == "task1"

    def test_unregister(self):
        async def dummy():
            pass

        self.scheduler.register("task2", dummy, 30)
        removed = self.scheduler.unregister("task2")
        assert removed is True
        assert not self.scheduler.list_tasks()

    def test_unregister_nonexistent(self):
        assert self.scheduler.unregister("nonexistent") is False


# ──────────────────────────────────────────────────────────────────────────────
# Core – LLMConnector
# ──────────────────────────────────────────────────────────────────────────────

class TestLLMConnector:
    def test_openai_init(self):
        llm = LLMConnector(provider="openai", model="gpt-4o-mini")
        assert llm.provider == "openai"
        assert llm.model == "gpt-4o-mini"

    def test_ollama_init(self):
        llm = LLMConnector(provider="ollama", model="llama3")
        assert llm.provider == "ollama"
        assert llm.model == "llama3"

    def test_invalid_provider(self):
        with pytest.raises(ValueError, match="Unsupported LLM provider"):
            LLMConnector(provider="unknown")

    def test_get_info(self):
        llm = LLMConnector(provider="openai")
        info = llm.get_info()
        assert info["provider"] == "openai"
        assert "model" in info


class TestAgentManager:
    @pytest.mark.asyncio
    async def test_initialize_all_registers_specialists(self):
        manager = AgentManager()
        status = await manager.initialize_all()
        assert status["total"] == 6
        orchestrator = manager.agents["orchestrator"]
        registered = orchestrator.execute  # keep reference for type narrowing
        assert callable(registered)
        assert "monetization" in orchestrator._agent_registry  # noqa: SLF001
        await manager.stop_all()


class TestOrchestratorRouting:
    @pytest.mark.asyncio
    async def test_routes_task_to_registered_agent(self):
        orchestrator = OrchestratorAgent()

        async def fake_execute(task):
            return {"handled": task["type"]}

        orchestrator._register_agent(  # noqa: SLF001
            {
                "agent_name": "monetization",
                "description": "test agent",
                "executor": fake_execute,
                "task_types": ["list_plans"],
            }
        )

        result = await orchestrator.execute({"type": "list_plans"})
        assert result["status"] == "routed"
        assert result["agent"] == "monetization"
        assert result["result"]["handled"] == "list_plans"


# ──────────────────────────────────────────────────────────────────────────────
# Monetization – ClientManager
# ──────────────────────────────────────────────────────────────────────────────

class TestClientManager:
    def setup_method(self):
        self.manager = ClientManager()

    def test_create_client(self):
        client = self.manager.create_client("Alice", "alice@example.com", plan="pro")
        assert client.name == "Alice"
        assert client.plan == "pro"
        assert client.is_active

    def test_list_clients(self):
        self.manager.create_client("Bob", "bob@example.com")
        clients = self.manager.list_clients()
        assert len(clients) >= 1

    def test_deactivate_client(self):
        client = self.manager.create_client("Carol", "carol@example.com")
        result = self.manager.deactivate_client(client.client_id)
        assert result is True
        active = self.manager.list_clients(active_only=True)
        assert all(c.client_id != client.client_id for c in active)

    def test_upgrade_plan(self):
        client = self.manager.create_client("Dave", "dave@example.com", plan="basic")
        self.manager.upgrade_plan(client.client_id, "enterprise")
        updated = self.manager.get_client(client.client_id)
        assert updated.plan == "enterprise"

    def test_upsell_opportunities(self):
        client = self.manager.create_client("Eve", "eve@example.com", plan="basic")
        client.monthly_spend = 100.0
        opportunities = self.manager.detect_upsell_opportunities()
        assert any(o["client_id"] == client.client_id for o in opportunities)

    def test_summary(self):
        summary = self.manager.get_summary()
        assert "total_clients" in summary
        assert "active_clients" in summary


# ──────────────────────────────────────────────────────────────────────────────
# Monetization – PricingEngine
# ──────────────────────────────────────────────────────────────────────────────

class TestPricingEngine:
    def setup_method(self):
        self.engine = PricingEngine()

    def test_get_price_basic(self):
        price = self.engine.get_price("basic")
        assert price == 9.99

    def test_get_price_unknown_plan(self):
        with pytest.raises(ValueError, match="Unknown plan"):
            self.engine.get_price("unknown")

    def test_surge_pricing(self):
        normal = self.engine.get_price("pro", usage_pct=40)
        surge = self.engine.get_price("pro", usage_pct=95)
        assert surge > normal

    def test_list_plans(self):
        plans = self.engine.list_plans()
        assert len(plans) == 3
        plan_keys = {p["plan_key"] for p in plans}
        assert {"basic", "pro", "enterprise"}.issubset(plan_keys)

    def test_recommend_plan(self):
        plan = self.engine.recommend_plan(monthly_api_calls=5_000, storage_gb=5)
        assert plan == "basic"

        plan = self.engine.recommend_plan(monthly_api_calls=500_000, storage_gb=500)
        assert plan == "enterprise"

    def test_demand_multiplier(self):
        self.engine.set_demand_multiplier(2.0)
        price = self.engine.get_price("basic")
        assert abs(price - 9.99 * 2.0) < 0.01

    def test_invalid_multiplier(self):
        with pytest.raises(ValueError, match="positive"):
            self.engine.set_demand_multiplier(-1)


# ──────────────────────────────────────────────────────────────────────────────
# Monetization – BillingManager (simulation mode)
# ──────────────────────────────────────────────────────────────────────────────

class TestBillingManager:
    def setup_method(self):
        self.billing = BillingManager(stripe_api_key="")

    @pytest.mark.asyncio
    async def test_create_customer_simulated(self):
        result = await self.billing.create_customer("test@example.com", "Test User")
        assert "id" in result

    @pytest.mark.asyncio
    async def test_create_invoice_simulated(self):
        result = await self.billing.create_invoice("cus_sim", 999, "Test invoice")
        assert "id" in result

    def test_revenue_summary(self):
        summary = self.billing.get_revenue_summary()
        assert "total_invoices" in summary


# ──────────────────────────────────────────────────────────────────────────────
# DevOps – BackupManager
# ──────────────────────────────────────────────────────────────────────────────

class TestBackupManager:
    def setup_method(self):
        self.backup = BackupManager()  # no storage box configured → simulation

    def test_run_backup_simulated(self):
        result = self.backup.run_backup(label="test")
        assert result["status"] in ("simulated", "success", "partial")
        assert "backup_name" in result

    def test_list_backups(self):
        self.backup.run_backup()
        backups = self.backup.list_backups()
        assert len(backups) >= 1

    def test_get_latest_backup(self):
        self.backup.run_backup()
        latest = self.backup.get_latest_backup()
        assert latest is not None


# ──────────────────────────────────────────────────────────────────────────────
# Resources – ResourceOptimizer
# ──────────────────────────────────────────────────────────────────────────────

class TestResourceOptimizer:
    def setup_method(self):
        self.optimizer = ResourceOptimizer()

    def test_get_metrics_returns_dict(self):
        metrics = self.optimizer.get_metrics()
        assert isinstance(metrics, dict)
        assert "cpu_percent" in metrics
        assert "ram_percent" in metrics

    def test_analyse(self):
        result = self.optimizer.analyse()
        assert "metrics" in result
        assert "status" in result
        assert "recommendations" in result

    def test_is_under_pressure_returns_bool(self):
        assert isinstance(self.optimizer.is_under_pressure(), bool)


# ──────────────────────────────────────────────────────────────────────────────
# Security – FirewallManager
# ──────────────────────────────────────────────────────────────────────────────

class TestFirewallManager:
    def setup_method(self):
        self.fw = FirewallManager()

    def test_block_invalid_ip_raises(self):
        with pytest.raises(ValueError, match="Invalid IP"):
            self.fw.block_ip("not-an-ip")

    def test_unblock_invalid_ip_raises(self):
        with pytest.raises(ValueError, match="Invalid IP"):
            self.fw.unblock_ip("not-an-ip-address")

    def test_allow_port_invalid(self):
        with pytest.raises(ValueError, match="Invalid port"):
            self.fw.allow_port(0)

    def test_allow_port_invalid_protocol(self):
        with pytest.raises(ValueError, match="Invalid protocol"):
            self.fw.allow_port(80, protocol="ftp")

    def test_valid_ip_format(self):
        # UFW will fail but the method should accept the IP format
        result = self.fw.block_ip("192.168.1.100", reason="test")
        assert result["ip"] == "192.168.1.100"


# ──────────────────────────────────────────────────────────────────────────────
# Security – IntrusionDetector
# ──────────────────────────────────────────────────────────────────────────────

class TestIntrusionDetector:
    def setup_method(self):
        self.detector = IntrusionDetector(auth_log_path="/nonexistent/auth.log")

    def test_analyse_missing_log(self):
        threats = self.detector.analyse_auth_log()
        assert threats == []

    def test_get_summary(self):
        summary = self.detector.get_summary()
        assert "total_alerts" in summary
        assert "suspicious_ips" in summary

    def test_get_alerts_empty(self):
        alerts = self.detector.get_alerts()
        assert isinstance(alerts, list)


# ──────────────────────────────────────────────────────────────────────────────
# Analytics – Predictor
# ──────────────────────────────────────────────────────────────────────────────

class TestPredictor:
    def setup_method(self):
        self.predictor = Predictor(window_size=10, z_score_threshold=2.0)

    def test_record_and_predict(self):
        for v in [1.0, 1.1, 1.0, 0.9, 1.0, 1.1, 1.0, 0.9]:
            self.predictor.record("cpu", v)
        prediction = self.predictor.predict_next("cpu")
        assert prediction is not None

    def test_no_anomaly_normal_values(self):
        for v in [50.0, 51.0, 50.5, 49.5, 50.0, 51.0]:
            self.predictor.record("ram", v)
        anomaly, _ = self.predictor.is_anomaly("ram", 50.5)
        assert anomaly is False

    def test_anomaly_detected(self):
        for v in [10.0, 11.0, 9.5, 10.5, 10.0, 11.0, 9.5, 10.5]:
            self.predictor.record("metric", v)
        anomaly, z_score = self.predictor.is_anomaly("metric", 100.0)
        assert anomaly is True
        assert z_score is not None and z_score > 2.0

    def test_check_and_alert(self):
        for v in [5.0] * 8:
            self.predictor.record("disk", v)
        alert = self.predictor.check_and_alert("disk", 999.0)
        assert alert is not None
        assert alert["metric"] == "disk"

    def test_get_series_stats(self):
        self.predictor.record("temp", 42.0)
        stats = self.predictor.get_series_stats("temp")
        assert stats["count"] == 1


# ──────────────────────────────────────────────────────────────────────────────
# Analytics – DashboardData
# ──────────────────────────────────────────────────────────────────────────────

class TestDashboardData:
    def setup_method(self):
        self.dashboard = DashboardData()

    def test_snapshot_and_latest(self):
        self.dashboard.snapshot(resources={"cpu_percent": 40})
        latest = self.dashboard.get_latest()
        assert latest is not None
        assert latest["resources"]["cpu_percent"] == 40

    def test_get_history(self):
        for i in range(5):
            self.dashboard.snapshot(resources={"cpu_percent": i * 10})
        history = self.dashboard.get_history(limit=3)
        assert len(history) == 3

    def test_get_kpis_no_data(self):
        kpis = self.dashboard.get_kpis()
        assert kpis["status"] == "no_data"

    def test_get_kpis_with_data(self):
        self.dashboard.snapshot(
            resources={"cpu_percent": 30, "ram_percent": 50, "disk_percent": 20},
            monetization={"active_clients": 5, "monthly_revenue_usd": 249.95},
            security={"total_alerts": 0},
        )
        kpis = self.dashboard.get_kpis()
        assert kpis["active_clients"] == 5
        assert kpis["system_health"] == "healthy"


# ──────────────────────────────────────────────────────────────────────────────
# Analytics – Reporter
# ──────────────────────────────────────────────────────────────────────────────

class TestReporter:
    def setup_method(self):
        self.reporter = Reporter()

    def test_generate_daily_report(self):
        report = self.reporter.generate_daily_report({"active_clients": 10, "revenue": 500})
        assert report["type"] == "daily"
        assert "summary" in report

    def test_generate_alert_report(self):
        report = self.reporter.generate_alert_report({"message": "High CPU", "severity": "high"})
        assert report["type"] == "alert"

    def test_send_email_no_config(self):
        # No SMTP configured → should return False without raising
        result = self.reporter.send_email("Test", "Body", to=["admin@example.com"])
        assert result is False

    def test_get_reports(self):
        self.reporter.generate_daily_report({})
        reports = self.reporter.get_reports()
        assert len(reports) >= 1


class TestResourcesAgent:
    @pytest.mark.asyncio
    async def test_health_check(self, resources_agent):
        assert await resources_agent.health_check() is True

    @pytest.mark.asyncio
    async def test_execute_returns_dict(self, resources_agent):
        result = await resources_agent.execute({})
        assert "metrics" in result
        assert "alerts" in result
        assert "cleanup" in result


class TestSecurityAgent:
    @pytest.mark.asyncio
    async def test_health_check(self, security_agent):
        assert await security_agent.health_check() is True

    @pytest.mark.asyncio
    async def test_scan_no_auth_log(self, security_agent, tmp_path):
        security_agent.detector.auth_log_path = str(tmp_path / "auth.log")
        with patch.object(security_agent, "_scan_journalctl", new_callable=AsyncMock) as mock_scan:
            mock_scan.return_value = {"suspicious_lines": 0, "source": "journalctl"}
            result = await security_agent._scan_auth_logs()
        assert isinstance(result, dict)

    def test_initial_state(self, security_agent):
        assert len(security_agent._blocked_ips) == 0
        assert len(security_agent._failed_attempts) == 0

    @pytest.mark.asyncio
    async def test_execute_returns_dict(self, security_agent):
        with patch.object(security_agent, "_scan_auth_logs", new_callable=AsyncMock) as scan_logs:
            scan_logs.return_value = {"suspicious_ips": 0, "newly_blocked": []}
            with patch.object(security_agent, "_run_audit", new_callable=AsyncMock) as run_audit:
                run_audit.return_value = {"open_ports": 3}
                result = await security_agent.execute({})
        assert "log_scan" in result
        assert "blocked" in result
        assert "audit" in result


class TestAnalyticsAgent:
    @pytest.mark.asyncio
    async def test_health_check(self, analytics_agent):
        assert await analytics_agent.health_check() is True

    def test_record_metrics(self, analytics_agent):
        analytics_agent.record_metrics(50.0, 60.0)
        assert len(analytics_agent._cpu_history) == 1
        assert len(analytics_agent._ram_history) == 1

    def test_no_anomaly_with_short_history(self, analytics_agent):
        for _ in range(5):
            analytics_agent.record_metrics(50.0, 60.0)
        result = asyncio.get_event_loop().run_until_complete(analytics_agent._detect_anomalies())
        assert result == []

    def test_anomaly_detection(self, analytics_agent):
        for _ in range(20):
            analytics_agent.record_metrics(50.0, 60.0)
        analytics_agent.record_metrics(200.0, 60.0)

        result = asyncio.get_event_loop().run_until_complete(analytics_agent._detect_anomalies())
        assert any(anomaly["resource"] == "cpu" for anomaly in result)

    @pytest.mark.asyncio
    async def test_execute_returns_dict(self, analytics_agent):
        result = await analytics_agent.execute({})
        assert "business_metrics" in result
        assert "anomalies" in result
        assert "report_generated" in result


class TestMonetizationAgent:
    @pytest.mark.asyncio
    async def test_health_check(self, monetization_agent):
        assert await monetization_agent.health_check() is True

    @pytest.mark.asyncio
    async def test_dynamic_pricing_returns_multiplier(self, monetization_agent):
        result = await monetization_agent._update_dynamic_pricing()
        assert "multiplier" in result
        assert isinstance(result["multiplier"], float)

    @pytest.mark.asyncio
    async def test_create_invoice(self, monetization_agent):
        result = await monetization_agent.create_invoice("cust_123", 99.0, "Test service")
        assert result["status"] == "created"
        assert result["customer_id"] == "cust_123"

    @pytest.mark.asyncio
    async def test_execute_returns_dict(self, monetization_agent):
        result = await monetization_agent.execute({})
        assert "overdue_invoices" in result
        assert "dynamic_pricing" in result
        assert "revenue_summary" in result


class TestDevOpsAgent:
    @pytest.mark.asyncio
    async def test_execute_returns_dict(self, devops_agent):
        with patch.object(devops_agent, "_check_services_health", new_callable=AsyncMock) as check_health:
            check_health.return_value = {"services": {}, "total": 0}
            with patch.object(devops_agent, "_auto_heal_failed_services", new_callable=AsyncMock) as auto_heal:
                auto_heal.return_value = {"restarted": []}
                with patch.object(devops_agent, "_run_backup_if_due", new_callable=AsyncMock) as backup:
                    backup.return_value = {"status": "script_not_found"}
                    with patch.object(devops_agent, "_cleanup_docker", new_callable=AsyncMock) as cleanup:
                        cleanup.return_value = {"status": "ok"}
                        result = await devops_agent.execute({})
        assert "health" in result
        assert "auto_heal" in result
        assert "backup" in result


class TestMasterOrchestrator:
    def test_orchestrator_has_all_agents(self):
        orch = MasterOrchestrator()
        assert hasattr(orch, "security")
        assert hasattr(orch, "resources")
        assert hasattr(orch, "devops")
        assert hasattr(orch, "monetization")
        assert hasattr(orch, "analytics")

    def test_status_structure(self):
        orch = MasterOrchestrator()
        status = orch.status()
        assert "orchestrator_running" in status
        assert "agents" in status
        assert len(status["agents"]) == 5

    @pytest.mark.asyncio
    async def test_start_and_stop(self):
        orch = MasterOrchestrator(cycle_seconds=999)
        await orch.start()
        assert orch.is_running is True
        await orch.stop()
        assert orch.is_running is False


class TestHelpers:
    def test_bytes_to_human(self):
        assert "1.0 KiB" in bytes_to_human(1024)
        assert "1.0 MiB" in bytes_to_human(1024 ** 2)
        assert "1.0 GiB" in bytes_to_human(1024 ** 3)

    def test_iso_now_is_string(self):
        ts = iso_now()
        assert isinstance(ts, str)
        assert "T" in ts

    def test_safe_json_dict(self):
        import json

        result = safe_json({"key": "value"})
        parsed = json.loads(result)
        assert parsed["key"] == "value"

    def test_safe_json_non_serializable(self):
        import datetime

        result = safe_json({"date": datetime.datetime.utcnow()})
        assert isinstance(result, str)
