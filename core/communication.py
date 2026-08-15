"""Inter-agent communication via an in-process async message bus."""

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Coroutine, Dict, List, Optional


@dataclass
class Message:
    sender: str
    target: str
    content: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    message_id: Optional[str] = None

    def __post_init__(self) -> None:
        if self.message_id is None:
            self.message_id = str(uuid.uuid4())


Handler = Callable[[Message], Coroutine[Any, Any, None]]


class MessageBus:
    def __init__(self) -> None:
        self._subscribers: Dict[str, List[Handler]] = {}
        self._history: List[Message] = []
        self._max_history = 1000

    async def subscribe(self, agent_name: str, handler: Handler) -> None:
        self._subscribers.setdefault(agent_name, []).append(handler)

    async def unsubscribe(self, agent_name: str, handler: Handler) -> None:
        handlers = self._subscribers.get(agent_name, [])
        if handler in handlers:
            handlers.remove(handler)

    async def publish(self, message: Message) -> None:
        self._store(message)
        handlers: List[Handler] = []
        if message.target == "*":
            for subscriber_handlers in self._subscribers.values():
                for handler in subscriber_handlers:
                    if handler not in handlers:
                        handlers.append(handler)
        else:
            handlers.extend(self._subscribers.get(message.target, []))
            for handler in self._subscribers.get("*", []):
                if handler not in handlers:
                    handlers.append(handler)
        await asyncio.gather(*(handler(message) for handler in handlers), return_exceptions=True)

    def _store(self, message: Message) -> None:
        self._history.append(message)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history :]

    def get_history(self, limit: int = 50) -> List[Message]:
        return self._history[-limit:]

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_messages": len(self._history),
            "subscribers": {name: len(handlers) for name, handlers in self._subscribers.items()},
        }
