"""
Tool Selector Agent
Picks the right security tool and configures parameters for each objective.
"""

import shutil
from typing import Dict, Any, List
from core.agent import BaseAgent
from ai.prompt_templates import TOOL_SELECTOR_SYSTEM_PROMPT, TOOL_SELECTOR_PROMPT


# Map of all supported tools
ALL_TOOLS = {
    "nmap": "tools.nmap.NmapTool",
    "masscan": "tools.masscan.MasscanTool",
    "httpx": "tools.httpx_tool.HttpxTool",
    "subfinder": "tools.subfinder.SubfinderTool",
    "amass": "tools.amass.AmassTool",
    "nuclei": "tools.nuclei.NucleiTool",
    "nikto": "tools.nikto.NiktoTool",
    "sqlmap": "tools.sqlmap.SqlmapTool",
    "whatweb": "tools.whatweb.WhatwebTool",
    "wafw00f": "tools.wafw00f.Wafw00fTool",
    "wpscan": "tools.wpscan.WpscanTool",
    "testssl": "tools.testssl.TestsslTool",
    "sslyze": "tools.sslyze.SslyzeTool",
    "gobuster": "tools.gobuster.GobusterTool",
    "ffuf": "tools.ffuf.FfufTool",
    "arjun": "tools.arjun.ArjunTool",
    "xsstrike": "tools.xsstrike.XsstrikeTool",
    "gitleaks": "tools.gitleaks.GitleaksTool",
    "dnsrecon": "tools.dnsrecon.DnsreconTool",
}


class ToolAgent(BaseAgent):
    """Selects and executes security tools"""

    def __init__(self, config, ai_client, memory):
        super().__init__("ToolAgent", config, ai_client, memory)
        self._tool_cache: Dict[str, Any] = {}

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Select the best tool for an objective"""
        objective = kwargs.get("objective", "")
        target = kwargs.get("target", self.memory.target)

        available = self._get_available_tools()
        safe_mode = self.config.get("pentest", {}).get("safe_mode", True)

        prompt = TOOL_SELECTOR_PROMPT.format(
            objective=objective,
            target=target,
            available_tools=", ".join(available),
            safe_mode="enabled" if safe_mode else "disabled",
            context=self.memory.get_context_for_ai(),
        )

        result = await self.think(prompt, TOOL_SELECTOR_SYSTEM_PROMPT)
        selection = self._parse_tool_selection(result["response"])
        selection["reasoning"] = result["reasoning"]

        self.log_action("Tool Selected", selection.get("tool", "unknown"))
        return selection

    async def execute_tool(self, tool_name: str, target: str, **kwargs) -> Dict[str, Any]:
        """Execute a specific tool against a target"""
        try:
            tool = self._get_tool_instance(tool_name)
            if tool is None:
                return {
                    "success": False,
                    "error": f"Tool '{tool_name}' not available or not installed",
                }

            if not tool.is_available:
                return {
                    "success": False,
                    "error": f"Tool '{tool_name}' is not installed on this system",
                }

            # Check safe mode restrictions
            if self._is_unsafe_params(tool_name, kwargs):
                return {
                    "success": False,
                    "error": f"Safe mode blocked destructive parameters for {tool_name}",
                }

            # Execute
            self.log_action("Executing", f"{tool_name} on {target}")
            result = await tool.execute(target, **kwargs)

            # Log execution
            self.logger.log_tool_execution(
                tool=tool_name,
                command=result.get("command", ""),
                target=target,
                exit_code=result.get("exit_code", -1),
                duration=result.get("duration", 0),
            )

            result["success"] = True
            return result

        except Exception as e:
            self.logger.error(f"Tool {tool_name} execution failed: {e}")
            return {"success": False, "error": str(e)}

    def _get_tool_instance(self, name: str):
        """Get or create a tool instance"""
        if name in self._tool_cache:
            return self._tool_cache[name]

        if name not in ALL_TOOLS:
            return None

        try:
            module_path, class_name = ALL_TOOLS[name].rsplit(".", 1)
            import importlib
            module = importlib.import_module(module_path)
            tool_class = getattr(module, class_name)
            instance = tool_class(self.config)
            self._tool_cache[name] = instance
            return instance
        except Exception as e:
            self.logger.error(f"Failed to load tool {name}: {e}")
            return None

    def _get_available_tools(self) -> List[str]:
        """Return list of tools that are installed on this system"""
        available = []
        for name in ALL_TOOLS:
            binary = name
            # Some tools have different binary names
            if name == "httpx":
                binary = "httpx"
            if shutil.which(binary) is not None:
                available.append(name)
        return available if available else list(ALL_TOOLS.keys())

    def _is_unsafe_params(self, tool_name: str, params: Dict) -> bool:
        """Check if parameters are blocked by safe mode"""
        safe_mode = self.config.get("pentest", {}).get("safe_mode", True)
        if not safe_mode:
            return False

        # SQLMap destructive flags
        if tool_name == "sqlmap":
            if params.get("risk", 1) > 1 or params.get("level", 1) > 3:
                return True
            if params.get("os_shell") or params.get("os_pwn"):
                return True

        # Nmap aggressive scans
        if tool_name == "nmap":
            args = params.get("default_args", "")
            if any(flag in args for flag in ["-sU", "--script=exploit", "--script=vuln"]):
                return True

        return False

    def _parse_tool_selection(self, response: str) -> Dict[str, Any]:
        selection: Dict[str, Any] = {"tool": "nmap", "parameters": {}, "rationale": ""}

        if "TOOL:" in response:
            start = response.find("TOOL:") + len("TOOL:")
            end = response.find("PARAMETERS:", start) if "PARAMETERS:" in response else len(response)
            selection["tool"] = response[start:end].strip().lower()

        if "RATIONALE:" in response:
            start = response.find("RATIONALE:") + len("RATIONALE:")
            selection["rationale"] = response[start:].strip()

        return selection
