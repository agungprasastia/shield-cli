"""Subfinder — Passive subdomain enumeration"""

from typing import Dict, Any, List
from tools.base_tool import BaseTool


class SubfinderTool(BaseTool):
    def get_command(self, target: str, **kwargs) -> List[str]:
        cmd = ["subfinder", "-d", target, "-silent"]
        if kwargs.get("sources"):
            cmd.extend(["-sources", ",".join(kwargs["sources"])])
        return cmd

    def parse_output(self, output: str) -> Dict[str, Any]:
        subs = [l.strip() for l in output.strip().split("\n") if l.strip()]
        return {"subdomains": subs, "count": len(subs)}
