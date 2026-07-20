"""Core compatibility package for ECO-IA."""

from .agent_base import AgentBase
from .communication import Message, MessageBus
from .llm_connector import LLMConnector
from .scheduler import TaskScheduler

__all__ = ["AgentBase", "LLMConnector", "Message", "MessageBus", "TaskScheduler"]
