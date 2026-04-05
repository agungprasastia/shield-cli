"""
OpenRouter Provider — Access many models via a single API
"""

import os
from typing import Optional, Dict, Any
from ai.providers.base_provider import BaseProvider


class OpenRouterProvider(BaseProvider):
    """OpenRouter provider via LangChain OpenAI-compatible API"""

    def __init__(self, config: Dict[str, Any], logger):
        super().__init__(config, logger)
        self.provider_config = config.get("ai", {}).get("openrouter", {})
        self.model = self.provider_config.get("model", "anthropic/claude-3.5-sonnet")
        self.api_key = self.provider_config.get("api_key") or os.getenv("OPENROUTER_API_KEY")
        self.llm = None
        self._initialize()

    def _initialize(self):
        if not self.api_key:
            self.logger.warning("OpenRouter API key not configured")
            return
        try:
            from langchain_openai import ChatOpenAI

            self.llm = ChatOpenAI(
                model=self.model,
                api_key=self.api_key,
                base_url="https://openrouter.ai/api/v1",
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                default_headers={
                    "HTTP-Referer": "https://github.com/agungprasastia/shield-cli",
                    "X-Title": "Shield CLI",
                },
            )
            self.logger.info(f"OpenRouter provider initialized with model: {self.model}")
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenRouter: {e}")

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        context: Optional[list] = None,
    ) -> str:
        if not self.llm:
            raise RuntimeError("OpenRouter provider not initialized — check API key")

        await self._apply_rate_limit()

        messages = []
        if system_prompt:
            messages.append(("system", system_prompt))
        if context:
            messages.extend(context)
        messages.append(("human", prompt))

        response = await self.llm.ainvoke(messages)
        return response.content

    def generate_sync(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        context: Optional[list] = None,
    ) -> str:
        if not self.llm:
            raise RuntimeError("OpenRouter provider not initialized — check API key")

        self._apply_rate_limit_sync()

        messages = []
        if system_prompt:
            messages.append(("system", system_prompt))
        if context:
            messages.extend(context)
        messages.append(("human", prompt))

        response = self.llm.invoke(messages)
        return response.content

    def get_model_name(self) -> str:
        return self.model

    def is_configured(self) -> bool:
        return bool(self.api_key and self.llm)
