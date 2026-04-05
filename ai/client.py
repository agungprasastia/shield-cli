"""
Shield — Unified AI Client
Routes requests to the active AI provider.
"""

from typing import Dict, Any, Optional
from utils.logger import get_logger


class AIClient:
    """Unified AI client that routes to the configured provider"""

    PROVIDERS = {
        "openai": "ai.providers.openai_provider.OpenAIProvider",
        "claude": "ai.providers.claude_provider.ClaudeProvider",
        "gemini": "ai.providers.gemini_provider.GeminiProvider",
        "openrouter": "ai.providers.openrouter_provider.OpenRouterProvider",
    }

    def __init__(self, config: Dict[str, Any], provider_override: Optional[str] = None):
        self.config = config
        self.logger = get_logger(config)

        # Load .env if present
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass

        # Determine active provider
        self.provider_name = provider_override or config.get("ai", {}).get("provider", "gemini")
        self.provider = self._create_provider(self.provider_name)

    def _create_provider(self, name: str):
        """Create a provider instance by name"""
        if name not in self.PROVIDERS:
            raise ValueError(f"Unknown AI provider: {name}. Available: {list(self.PROVIDERS.keys())}")

        module_path, class_name = self.PROVIDERS[name].rsplit(".", 1)

        import importlib
        module = importlib.import_module(module_path)
        provider_class = getattr(module, class_name)

        return provider_class(self.config, self.logger)

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        context: Optional[list] = None,
    ) -> str:
        """Generate a response using the active provider"""
        return await self.provider.generate(prompt, system_prompt, context)

    def generate_sync(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        context: Optional[list] = None,
    ) -> str:
        """Generate a response synchronously"""
        return self.provider.generate_sync(prompt, system_prompt, context)

    async def generate_with_reasoning(
        self,
        prompt: str,
        system_prompt: str,
        task_context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate response with reasoning trace"""
        return await self.provider.generate_with_reasoning(
            prompt, system_prompt, task_context
        )

    def get_model_name(self) -> str:
        return self.provider.get_model_name()

    def get_provider_name(self) -> str:
        return self.provider_name

    def is_configured(self) -> bool:
        return hasattr(self.provider, "is_configured") and self.provider.is_configured()

    @classmethod
    def get_all_provider_status(cls, config: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Check configuration status of all providers"""
        # Load .env so API keys are visible
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass

        logger = get_logger(config)
        status = {}

        for name in cls.PROVIDERS:
            try:
                module_path, class_name = cls.PROVIDERS[name].rsplit(".", 1)
                import importlib
                module = importlib.import_module(module_path)
                provider_class = getattr(module, class_name)
                provider = provider_class(config, logger)

                status[name] = {
                    "model": provider.get_model_name(),
                    "configured": provider.is_configured(),
                    "status": "✅ Ready" if provider.is_configured() else "❌ Not configured",
                }
            except Exception as e:
                status[name] = {
                    "model": "N/A",
                    "configured": False,
                    "status": f"❌ Error: {e}",
                }

        return status
