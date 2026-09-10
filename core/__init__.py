"""Core runtime package for ECO-IA."""

from .agent_base import AgentBase
from .communication import Message, MessageBus
from .llm_connector import LLMConnector
from .scheduler import ScheduledTask, TaskScheduler

__all__ = [
    "AgentBase",
    "AgentManager",
    "LLMConnector",
    "Message",
    "MessageBus",
    "ScheduledTask",
    "TaskScheduler",
]


def __getattr__(name: str):
    if name == "AgentManager":
        from .agent_manager import AgentManager

        return AgentManager
    raise AttributeError(name)
