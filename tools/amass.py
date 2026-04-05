"""Amass — Active/passive subdomain discovery"""

from typing import Dict, Any, List
from tools.base_tool import BaseTool


class AmassTool(BaseTool):
    def get_command(self, target: str, **kwargs) -> List[str]:
        mode = kwargs.get("mode", "enum")
        cmd = ["amass", mode, "-d", target, "-passive"]
        return cmd

    def parse_output(self, output: str) -> Dict[str, Any]:
        subs = [l.strip() for l in output.strip().split("\n") if l.strip()]
        return {"subdomains": subs, "count": len(subs)}
