"""GitLeaks — Secret scanning in code repositories"""
from typing import Dict, Any, List
from tools.base_tool import BaseTool

class GitleaksTool(BaseTool):
    def get_command(self, target: str, **kwargs) -> List[str]:
        cmd = ["gitleaks", "detect", "--source", target, "--no-git", "-v"]
        return cmd

    def parse_output(self, output: str) -> Dict[str, Any]:
        results: Dict[str, Any] = {"secrets": [], "count": 0}
        for line in output.strip().split("\n"):
            if "Secret:" in line or "RuleID:" in line:
                results["secrets"].append(line.strip())
                results["count"] += 1
        return results
