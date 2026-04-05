"""Nmap — Port scanning and service detection"""

import re
from typing import Dict, Any, List
from tools.base_tool import BaseTool


class NmapTool(BaseTool):
    def get_command(self, target: str, **kwargs) -> List[str]:
        cfg = self.config.get("tools", {}).get("nmap", {})
        cmd = ["nmap"]
        args = kwargs.get("default_args", cfg.get("default_args", "-sV -sC"))
        if args:
            cmd.extend(args.split())
        timing = kwargs.get("timing", cfg.get("timing", "T4"))
        cmd.append(f"-{timing}")
        cmd.extend(["-oX", "-"])
        if "ports" in kwargs:
            cmd.extend(["-p", kwargs["ports"]])
        elif "ports" in cfg:
            cmd.extend(["-p", cfg["ports"]])
        cmd.append(target)
        return cmd

    def parse_output(self, output: str) -> Dict[str, Any]:
        results: Dict[str, Any] = {"open_ports": [], "services": [], "os_detection": None}
        pattern = r'portid="(\d+)".*?service name="([^"]*)".*?product="([^"]*)"'
        for m in re.finditer(pattern, output, re.DOTALL):
            port, service, product = int(m.group(1)), m.group(2), m.group(3) or "unknown"
            results["open_ports"].append(port)
            results["services"].append({"port": port, "service": service, "product": product})
        os_match = re.search(r'osclass type="([^"]*)".*?osfamily="([^"]*)"', output)
        if os_match:
            results["os_detection"] = {"type": os_match.group(1), "family": os_match.group(2)}
        return results
