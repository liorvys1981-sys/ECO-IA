"""Tests for ECO-IA agents."""

import asyncio
import sys
import os

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from core.communication import Message, MessageBus
from core.scheduler import TaskScheduler
from core.llm_connector import LLMConnector

from agents.monetization.billing import BillingManager
from agents.monetization.clients import ClientManager
from agents.monetization.pricing import PricingEngine

from agents.devops.backup import BackupManager
from agents.devops.auto_heal import AutoHealer

from agents.resources.optimizer import ResourceOptimizer
from agents.resources.scaler import AutoScaler

from agents.security.firewall import FirewallManager
from agents.security.intrusion_detector import IntrusionDetector

from agents.analytics.predictor import Predictor
from agents.analytics.dashboard import DashboardData
from agents.analytics.reporter import Reporter


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
