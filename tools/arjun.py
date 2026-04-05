"""Arjun — HTTP parameter discovery"""
from typing import Dict, Any, List
from tools.base_tool import BaseTool

class ArjunTool(BaseTool):
    def get_command(self, target: str, **kwargs) -> List[str]:
        cmd = ["arjun", "-u", target]
        if kwargs.get("method"):
            cmd.extend(["-m", kwargs["method"]])
        return cmd

    def parse_output(self, output: str) -> Dict[str, Any]:
        results: Dict[str, Any] = {"parameters": []}
        for line in output.strip().split("\n"):
            if line.strip() and "parameter" in line.lower():
                results["parameters"].append(line.strip())
        return results
