"""LLM connector supporting OpenAI and Ollama."""
import logging, os
from typing import Any, Dict, List, Optional
logger = logging.getLogger(__name__)

class LLMConnector:
    def __init__(self, provider="openai", model=None, api_key=None, base_url=None,
                 temperature=0.7, max_tokens=2048):
        self.provider = provider.lower(); self.temperature = temperature; self.max_tokens = max_tokens
        if self.provider == "openai":
            self.model = model or "gpt-4o-mini"
            self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
            self.base_url = base_url or "https://api.openai.com/v1"
        elif self.provider == "ollama":
            self.model = model or "llama3"; self.api_key = "ollama"
            self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        else:
            raise ValueError(f"Unsupported provider: {provider!r}")
    async def chat(self, messages, system_prompt=None):
        if system_prompt: messages = [{"role": "system", "content": system_prompt}] + list(messages)
        return await self._openai_chat(messages) if self.provider == "openai" else await self._ollama_chat(messages)
    async def complete(self, prompt):
        return await self.chat([{"role": "user", "content": prompt}])
    async def _openai_chat(self, messages):
        try:
            import openai
            client = openai.AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
            r = await client.chat.completions.create(model=self.model, messages=messages,
                temperature=self.temperature, max_tokens=self.max_tokens)
            return r.choices[0].message.content or ""
        except ImportError: return "[OpenAI not installed]"
        except Exception as e: logger.error("OpenAI error: %s", e); raise
    async def _ollama_chat(self, messages):
        try:
            import httpx
            async with httpx.AsyncClient(timeout=120) as c:
                r = await c.post(f"{self.base_url}/api/chat",
                    json={"model": self.model, "messages": messages, "stream": False,
                          "options": {"temperature": self.temperature, "num_predict": self.max_tokens}})
                r.raise_for_status(); return r.json().get("message", {}).get("content", "")
        except ImportError: return "[httpx not installed]"
        except Exception as e: logger.error("Ollama error: %s", e); raise
    def get_info(self):
        return {"provider": self.provider, "model": self.model, "base_url": self.base_url,
                "temperature": self.temperature, "max_tokens": self.max_tokens}
