"""httpx — HTTP probing and technology detection"""

import json as _json
from typing import Dict, Any, List
from tools.base_tool import BaseTool


class HttpxTool(BaseTool):
    def __init__(self, config):
        super().__init__(config)
        self.tool_name = "httpx"

    def _check_installation(self) -> bool:
        """Check for ProjectDiscovery httpx binary (not Python httpx library)"""
        import subprocess
        try:
            r = subprocess.run(
                ["httpx", "-version"], capture_output=True, text=True, timeout=5
            )
            # ProjectDiscovery httpx prints version like "projectdiscovery/httpx vX.X.X"
            output = r.stdout + r.stderr
            return "projectdiscovery" in output.lower() or "httpx" in output.lower() and "-u" not in output
        except Exception:
            return False

    def get_command(self, target: str, **kwargs) -> List[str]:
        cfg = self.config.get("tools", {}).get("httpx", {})
        cmd = ["httpx", "-u", target, "-json"]
        threads = kwargs.get("threads", cfg.get("threads", 50))
        timeout = kwargs.get("timeout", cfg.get("timeout", 10))
        cmd.extend(["-threads", str(threads), "-timeout", str(timeout)])
        if kwargs.get("tech_detect", cfg.get("tech_detect", True)):
            cmd.append("-tech-detect")
        cmd.extend(["-status-code", "-title", "-web-server", "-content-length"])
        return cmd

    def parse_output(self, output: str) -> Dict[str, Any]:
        results: Dict[str, Any] = {"urls": [], "technologies": [], "servers": []}
        for line in output.strip().split("\n"):
            if not line.strip():
                continue
            try:
                data = _json.loads(line)
                results["urls"].append(data.get("url", ""))
                if "tech" in data:
                    results["technologies"].extend(data["tech"])
                if "webserver" in data:
                    results["servers"].append(data["webserver"])
            except _json.JSONDecodeError:
                continue
        return results
