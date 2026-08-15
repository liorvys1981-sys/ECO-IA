"""LLM connector supporting OpenAI and Ollama."""

import logging
import os
from typing import Any, Dict, List, Optional


logger = logging.getLogger(__name__)


class LLMConnector:
    def __init__(
        self,
        provider: str = "openai",
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> None:
        self.provider = provider.lower()
        self.temperature = temperature
        self.max_tokens = max_tokens

        if self.provider == "openai":
            self.model = model or "gpt-4o-mini"
            self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
            self.base_url = base_url or "https://api.openai.com/v1"
        elif self.provider == "ollama":
            self.model = model or "llama3"
            self.api_key = "ollama"
            self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        else:
            raise ValueError(f"Unsupported LLM provider: {provider!r}")

    async def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
    ) -> str:
        payload = list(messages)
        if system_prompt:
            payload = [{"role": "system", "content": system_prompt}, *payload]
        if self.provider == "openai":
            return await self._openai_chat(payload)
        return await self._ollama_chat(payload)

    async def complete(self, prompt: str) -> str:
        return await self.chat([{"role": "user", "content": prompt}])

    async def _openai_chat(self, messages: List[Dict[str, str]]) -> str:
        try:
            import openai

            client = openai.AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
            response = await client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            return response.choices[0].message.content or ""
        except ImportError:
            return "[OpenAI not installed]"
        except Exception as exc:  # noqa: BLE001
            logger.error("OpenAI error: %s", exc)
            raise

    async def _ollama_chat(self, messages: List[Dict[str, str]]) -> str:
        try:
            import httpx

            async with httpx.AsyncClient(timeout=120) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "stream": False,
                        "options": {
                            "temperature": self.temperature,
                            "num_predict": self.max_tokens,
                        },
                    },
                )
                response.raise_for_status()
                return response.json().get("message", {}).get("content", "")
        except ImportError:
            return "[httpx not installed]"
        except Exception as exc:  # noqa: BLE001
            logger.error("Ollama error: %s", exc)
            raise

    def get_info(self) -> Dict[str, Any]:
        return {
            "provider": self.provider,
            "model": self.model,
            "base_url": self.base_url,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
