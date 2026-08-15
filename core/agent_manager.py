"""Agent manager for the ECO-IA multi-agent runtime."""

from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from agents.analytics import AnalyticsAgent
from agents.devops import DevOpsAgent
from agents.monetization import MonetizationAgent
from agents.orchestrator import OrchestratorAgent
from agents.resources import ResourcesAgent
from agents.security import SecurityAgent
from .communication import MessageBus
from .llm_connector import LLMConnector


class AgentManager:
    def __init__(
        self,
        message_bus: Optional[MessageBus] = None,
        llm: Optional[LLMConnector] = None,
        config_path: Optional[str] = None,
    ) -> None:
        self.message_bus = message_bus or MessageBus()
        self.config_path = Path(config_path or Path(__file__).resolve().parent.parent / "agents.yaml")
        self.config = self._load_config()
        self.llm = llm or LLMConnector(
            provider=self.config.get("orchestrator", {}).get("llm", {}).get("provider", "openai"),
            model=self.config.get("orchestrator", {}).get("llm", {}).get("model", "gpt-4o-mini"),
            temperature=self.config.get("orchestrator", {}).get("llm", {}).get("temperature", 0.7),
            max_tokens=self.config.get("orchestrator", {}).get("llm", {}).get("max_tokens", 2048),
        )
        self.agents: Dict[str, Any] = {}

    def _load_config(self) -> Dict[str, Any]:
        if not self.config_path.exists():
            return {}
        with self.config_path.open(encoding="utf-8") as config_file:
            return yaml.safe_load(config_file) or {}

    async def initialize_all(self) -> Dict[str, Any]:
        self.agents = {
            "orchestrator": OrchestratorAgent(
                message_bus=self.message_bus,
                llm=self.llm,
                config=self.config.get("orchestrator", {}),
            ),
            "monetization": MonetizationAgent(
                message_bus=self.message_bus,
                config=self.config.get("monetization", {}),
            ),
            "devops": DevOpsAgent(
                message_bus=self.message_bus,
                config=self.config.get("devops", {}),
            ),
            "resources": ResourcesAgent(
                message_bus=self.message_bus,
                config=self.config.get("resources", {}),
            ),
            "security": SecurityAgent(
                message_bus=self.message_bus,
                config=self.config.get("security", {}),
            ),
            "analytics": AnalyticsAgent(
                message_bus=self.message_bus,
                config=self.config.get("analytics", {}),
            ),
        }

        for agent in self.agents.values():
            await agent.start()

        orchestrator = self.agents["orchestrator"]
        for name, agent in self.agents.items():
            if name == "orchestrator":
                continue
            orchestrator._register_agent(  # noqa: SLF001
                {"agent_name": agent.name, "description": agent.description}
            )
        return self.status()

    async def stop_all(self) -> None:
        for agent in reversed(list(self.agents.values())):
            await agent.stop()

    def list_agents(self) -> Dict[str, Any]:
        return {
            "total": len(self.agents),
            "agents": [agent.health_status() for agent in self.agents.values()],
        }

    def status(self) -> Dict[str, Any]:
        return {"started": bool(self.agents), **self.list_agents()}
