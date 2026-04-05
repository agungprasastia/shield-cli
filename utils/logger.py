"""
Shield — Audit Logger
Provides structured logging for all AI decisions, tool executions, and system events.
"""

import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional


class ShieldLogger:
    """Structured logger with audit trail for AI decisions and tool executions"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        log_config = config.get("logging", {})

        self.enabled = log_config.get("enabled", True)
        self.log_level = getattr(logging, log_config.get("level", "INFO").upper(), logging.INFO)
        self.log_ai = log_config.get("log_ai_decisions", True)

        # Setup file logger
        log_path = Path(log_config.get("path", "./logs/Shield.log"))
        log_path.parent.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger("Shield")
        self.logger.setLevel(self.log_level)

        # Prevent duplicate handlers
        if not self.logger.handlers:
            # File handler
            fh = logging.FileHandler(str(log_path), encoding="utf-8")
            fh.setLevel(self.log_level)
            fh.setFormatter(logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            ))
            self.logger.addHandler(fh)

            # Console handler (only warnings+)
            ch = logging.StreamHandler()
            ch.setLevel(logging.WARNING)
            ch.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
            self.logger.addHandler(ch)

    def info(self, message: str):
        if self.enabled:
            self.logger.info(message)

    def warning(self, message: str):
        if self.enabled:
            self.logger.warning(message)

    def error(self, message: str):
        if self.enabled:
            self.logger.error(message)

    def debug(self, message: str):
        if self.enabled:
            self.logger.debug(message)

    def log_ai_decision(
        self,
        agent: str,
        decision: str,
        reasoning: str,
        context: Optional[Dict[str, Any]] = None,
    ):
        """Log an AI agent decision with full reasoning trace"""
        if not self.log_ai:
            return

        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "ai_decision",
            "agent": agent,
            "decision": decision[:500],
            "reasoning": reasoning[:1000],
            "context": context or {},
        }
        self.logger.info(f"AI_DECISION | {agent} | {decision[:200]}")
        self.logger.debug(f"AI_REASONING | {json.dumps(entry, default=str)}")

    def log_tool_execution(
        self,
        tool: str,
        command: str,
        target: str,
        exit_code: int,
        duration: float,
    ):
        """Log a security tool execution"""
        self.logger.info(
            f"TOOL_EXEC | {tool} | target={target} | "
            f"exit={exit_code} | duration={duration:.2f}s | cmd={command[:200]}"
        )

    def log_finding(self, severity: str, title: str, tool: str):
        """Log a security finding"""
        self.logger.info(f"FINDING | [{severity.upper()}] {title} | source={tool}")


# Module-level cache
_logger_instance: Optional[ShieldLogger] = None


def get_logger(config: Optional[Dict[str, Any]] = None) -> ShieldLogger:
    """Get or create the singleton logger instance"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = ShieldLogger(config or {})
    return _logger_instance
