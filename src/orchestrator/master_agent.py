"""Compatibility exports for the orchestrator in the requested layout."""

from orchestrator import MasterOrchestrator, OrchestratorAgent

MasterAgent = OrchestratorAgent

__all__ = ["MasterAgent", "MasterOrchestrator", "OrchestratorAgent"]
