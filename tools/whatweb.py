"""WhatWeb — Technology fingerprinting"""
from typing import Dict, Any, List
from tools.base_tool import BaseTool

class WhatwebTool(BaseTool):
    def get_command(self, target: str, **kwargs) -> List[str]:
        cmd = ["whatweb", target, "--color=never", "-v"]
        aggression = kwargs.get("aggression", "1")
        cmd.extend(["-a", str(aggression)])
        return cmd

    def parse_output(self, output: str) -> Dict[str, Any]:
        results: Dict[str, Any] = {"technologies": [], "headers": {}}
        for line in output.split("\n"):
            line = line.strip()
            if line and not line.startswith("http"):
                results["technologies"].append(line)
        return results
