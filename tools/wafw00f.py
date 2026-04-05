"""Wafw00f — WAF detection"""
from typing import Dict, Any, List
from tools.base_tool import BaseTool

class Wafw00fTool(BaseTool):
    def __init__(self, config):
        super().__init__(config)
        self.tool_name = "wafw00f"

    def get_command(self, target: str, **kwargs) -> List[str]:
        return ["wafw00f", target]

    def parse_output(self, output: str) -> Dict[str, Any]:
        results: Dict[str, Any] = {"waf_detected": False, "waf_name": None}
        if "is behind" in output.lower():
            results["waf_detected"] = True
            for line in output.split("\n"):
                if "is behind" in line.lower():
                    results["waf_name"] = line.split("is behind")[-1].strip()
        return results
