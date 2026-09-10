"""Smoke tests for the requested project structure."""

from pathlib import Path

from src.agents import (
    AnalyticsAgent,
    BaseAgent,
    DevOpsAgent,
    MonetizationAgent,
    ResourcesAgent,
    SecurityAgent,
)
from src.orchestrator import MasterAgent

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_requested_structure_exists():
    expected_paths = [
        REPO_ROOT / "config" / "settings.py",
        REPO_ROOT / "config" / "agents_config.yaml",
        REPO_ROOT / "src" / "main.py",
        REPO_ROOT / "src" / "orchestrator" / "master_agent.py",
        REPO_ROOT / "src" / "agents" / "base_agent.py",
        REPO_ROOT / "src" / "services" / "api" / "routes.py",
        REPO_ROOT / "src" / "services" / "payments" / "stripe_service.py",
        REPO_ROOT / "src" / "services" / "database" / "models.py",
        REPO_ROOT / "src" / "tools" / "server_tools.py",
        REPO_ROOT / "src" / "tools" / "monitoring_tools.py",
        REPO_ROOT / "src" / "tools" / "notification_tools.py",
        REPO_ROOT / "src" / "utils" / "logger.py",
        REPO_ROOT / "src" / "utils" / "helpers.py",
        REPO_ROOT / "scripts" / "setup.sh",
        REPO_ROOT / "scripts" / "start.sh",
        REPO_ROOT / "scripts" / "backup.sh",
        REPO_ROOT / "monitoring" / "prometheus.yml",
        REPO_ROOT / "monitoring" / "grafana" / "dashboards" / "overview.json",
    ]
    for path in expected_paths:
        assert path.exists(), f"Missing required path: {path}"


def test_src_exports_resolve_to_existing_agents():
    assert issubclass(MasterAgent, BaseAgent)
    assert issubclass(MonetizationAgent, BaseAgent)
    assert issubclass(DevOpsAgent, BaseAgent)
    assert issubclass(ResourcesAgent, BaseAgent)
    assert issubclass(SecurityAgent, BaseAgent)
    assert issubclass(AnalyticsAgent, BaseAgent)
