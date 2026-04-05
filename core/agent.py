"""
Base Agent class — all Shield AI agents inherit from this.
"""

from typing import Dict, Any
from abc import ABC, abstractmethod

from ai.client import AIClient
from core.memory import PentestMemory
from utils.logger import get_logger


class BaseAgent(ABC):
    """Base class for all AI agents in Shield"""

    def __init__(
        self,
        name: str,
        config: Dict[str, Any],
        ai_client: AIClient,
        memory: PentestMemory,
    ):
        self.name = name
        self.config = config
        self.ai = ai_client
        self.memory = memory
        self.logger = get_logger(config)

    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the agent's primary function"""
        pass

    async def think(self, prompt: str, system_prompt: str) -> Dict[str, str]:
        """
        Use AI to think through a problem with reasoning.

        Returns:
            Dict with 'reasoning' and 'response' keys
        """
        try:
            result = await self.ai.generate_with_reasoning(
                prompt=prompt,
                system_prompt=system_prompt,
            )

            # Log AI decision
            self.logger.log_ai_decision(
                agent=self.name,
                decision=result["response"],
                reasoning=result["reasoning"],
                context={"prompt": prompt[:200]},
            )

            # Store in memory
            self.memory.add_ai_decision(
                agent=self.name,
                decision=result["response"],
                reasoning=result["reasoning"],
            )

            return result

        except Exception as e:
            self.logger.error(f"Agent {self.name} thinking error: {e}")
            raise

    def log_action(self, action: str, details: str):
        self.logger.info(f"[{self.name}] {action}: {details}")
