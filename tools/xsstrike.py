"""XSStrike — Advanced XSS detection"""
from typing import Dict, Any, List
from tools.base_tool import BaseTool

class XsstrikeTool(BaseTool):
    def __init__(self, config):
        super().__init__(config)
        self.tool_name = "xsstrike"

    def get_command(self, target: str, **kwargs) -> List[str]:
        return ["python3", "XSStrike/xsstrike.py", "-u", target, "--skip"]

    def parse_output(self, output: str) -> Dict[str, Any]:
        results: Dict[str, Any] = {"xss_found": [], "reflections": []}
        for line in output.strip().split("\n"):
            if "Payload:" in line or "XSS" in line.upper():
                results["xss_found"].append(line.strip())
            if "Reflection" in line:
                results["reflections"].append(line.strip())
        return results
