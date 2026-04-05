"""
Base class for all pentest tool wrappers.
Provides async execution, timeout, and evidence capture.
"""

import asyncio
import subprocess
import shutil
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
from abc import ABC, abstractmethod

from utils.logger import get_logger


class BaseTool(ABC):
    """Base class for external penetration testing tools"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_logger(config)
        self.tool_name = self.__class__.__name__.replace("Tool", "").lower()
        self.is_available = self._check_installation()

        if not self.is_available:
            self.logger.warning(f"Tool {self.tool_name} is not installed or not in PATH")

    @abstractmethod
    def get_command(self, target: str, **kwargs) -> List[str]:
        """Build command line for the tool"""
        pass

    @abstractmethod
    def parse_output(self, output: str) -> Dict[str, Any]:
        """Parse tool output into structured data"""
        pass

    async def execute(self, target: str, **kwargs) -> Dict[str, Any]:
        """Execute the tool against a target"""
        if not self.is_available:
            raise RuntimeError(f"Tool {self.tool_name} is not available")

        command = self.get_command(target, **kwargs)
        self.logger.info(f"Executing: {' '.join(command)}")

        timeout = self.config.get("pentest", {}).get("tool_timeout", 300)
        start_time = datetime.now()

        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=timeout
            )

            duration = (datetime.now() - start_time).total_seconds()
            output = stdout.decode("utf-8", errors="replace")
            error = stderr.decode("utf-8", errors="replace")

            parsed = self.parse_output(output)

            result = {
                "tool": self.tool_name,
                "target": target,
                "command": " ".join(command),
                "exit_code": process.returncode,
                "duration": duration,
                "raw_output": output,
                "error": error if error else None,
                "parsed": parsed,
            }

            self.logger.info(f"Tool {self.tool_name} completed in {duration:.2f}s")
            return result

        except asyncio.TimeoutError:
            self.logger.error(f"Tool {self.tool_name} timed out after {timeout}s")
            raise
        except Exception as e:
            self.logger.error(f"Tool {self.tool_name} failed: {e}")
            raise

    def _check_installation(self) -> bool:
        return shutil.which(self.tool_name) is not None

    def get_version(self) -> Optional[str]:
        try:
            result = subprocess.run(
                [self.tool_name, "--version"],
                capture_output=True, text=True, timeout=5,
            )
            return result.stdout.strip() or result.stderr.strip()
        except Exception:
            return None
