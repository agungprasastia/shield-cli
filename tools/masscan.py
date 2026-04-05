"""Masscan — Ultra-fast port scanner"""

import re
from typing import Dict, Any, List
from tools.base_tool import BaseTool


class MasscanTool(BaseTool):
    def get_command(self, target: str, **kwargs) -> List[str]:
        cmd = ["masscan"]
        ports = kwargs.get("ports", "1-65535")
        rate = kwargs.get("rate", "1000")
        cmd.extend(["-p", ports, "--rate", str(rate), target])
        return cmd

    def parse_output(self, output: str) -> Dict[str, Any]:
        results: Dict[str, Any] = {"open_ports": []}
        for m in re.finditer(r"Discovered open port (\d+)/(\w+) on ([\d.]+)", output):
            results["open_ports"].append({"port": int(m.group(1)), "proto": m.group(2), "ip": m.group(3)})
        return results
