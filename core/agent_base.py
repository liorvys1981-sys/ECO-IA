"""Base class for all ECO-IA agents."""

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from .communication import Message, MessageBus

logger = logging.getLogger(__name__)


class AgentBase(ABC):
    def __init__(
        self,
        name: str,
        description: str,
        message_bus: MessageBus | None = None,
        config: dict[str, Any] | None = None,
    ) -> None:
        self.name = name
        self.description = description
        self.message_bus = message_bus
        self.config = config or {}
        self.is_running = False
        self.last_heartbeat: datetime | None = None
        self.tasks_completed = 0
        self.tasks_failed = 0
        self._logger = logging.getLogger(f"eco_ia.agents.{name}")
        self._heartbeat_task: asyncio.Task[None] | None = None

    async def start(self) -> None:
        self.is_running = True
        if self.message_bus:
            await self.message_bus.subscribe(self.name, self._handle_message)
        await self.on_start()
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

    async def stop(self) -> None:
        self.is_running = False
        await self.on_stop()
        if self.message_bus:
            await self.message_bus.unsubscribe(self.name, self._handle_message)
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            await asyncio.gather(self._heartbeat_task, return_exceptions=True)

    @abstractmethod
    async def on_start(self) -> None:
        """Called when the agent starts."""

    @abstractmethod
    async def on_stop(self) -> None:
        """Called when the agent stops."""

    @abstractmethod
    async def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        """Execute a task."""

    async def _handle_message(self, message: Message) -> None:
        try:
            await self.on_message(message)
        except Exception as exc:  # noqa: BLE001
            self._logger.error("Message error: %s", exc)

    async def on_message(self, message: Message) -> None:
        if message.content.get("type") == "health_ping":
            await self.send_message(
                "orchestrator",
                {"type": "health_pong", "agent_name": self.name},
            )

    async def send_message(self, target: str, content: dict[str, Any]) -> None:
        if not self.message_bus:
            return
        await self.message_bus.publish(Message(sender=self.name, target=target, content=content))

    async def _heartbeat_loop(self) -> None:
        interval = int(self.config.get("heartbeat_interval", 30))
        while self.is_running:
            self.last_heartbeat = datetime.utcnow()
            await asyncio.sleep(interval)

    def health_status(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "is_running": self.is_running,
            "last_heartbeat": self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
        }

    def get_config(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)
