"""AI text completion service with usage tracking."""
import logging
import os
import time
from typing import Any, Dict, Optional
from core.llm_connector import LLMConnector

logger = logging.getLogger(__name__)

# Cost per 1000 tokens (USD)
COST_PER_1K_TOKENS = {
    "gpt-4o-mini": 0.00015,
    "gpt-4o": 0.005,
    "gpt-4-turbo": 0.01,
    "llama3": 0.0,
    "mistral": 0.0,
}


class AICompletionService:
    """Handles AI completions with cost tracking and caching."""

    def __init__(self):
        self._provider = os.getenv("LLM_PROVIDER", "openai")
        self._model = os.getenv("LLM_MODEL", "gpt-4o-mini")
        self._total_tokens = 0
        self._total_cost = 0.0
        self._request_count = 0

    async def complete(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 512,
        temperature: float = 0.7,
        client_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Run a completion and return result with usage stats."""
        model = model or self._model
        start = time.monotonic()

        llm = LLMConnector(
            provider=self._provider,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        result = await llm.complete(prompt)
        elapsed = round(time.monotonic() - start, 3)

        # Estimate tokens (rough: 1 token ≈ 4 chars)
        tokens_in = len(prompt) // 4
        tokens_out = len(result) // 4
        total_tokens = tokens_in + tokens_out
        cost = (total_tokens / 1000) * COST_PER_1K_TOKENS.get(model, 0.0)

        self._total_tokens += total_tokens
        self._total_cost += cost
        self._request_count += 1

        logger.info("Completion: model=%s tokens=%d cost=$%.5f elapsed=%ss",
                    model, total_tokens, cost, elapsed)

        return {
            "result": result,
            "model": model,
            "tokens_used": total_tokens,
            "cost_usd": round(cost, 6),
            "elapsed_seconds": elapsed,
            "client_id": client_id,
        }

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_requests": self._request_count,
            "total_tokens": self._total_tokens,
            "total_cost_usd": round(self._total_cost, 4),
        }

# Singleton
_service: Optional[AICompletionService] = None

def get_completion_service() -> AICompletionService:
    global _service
    if _service is None:
        _service = AICompletionService()
    return _service
