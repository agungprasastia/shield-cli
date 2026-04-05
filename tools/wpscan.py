"""WPScan — WordPress security scanner"""
from typing import Dict, Any, List
from tools.base_tool import BaseTool

class WpscanTool(BaseTool):
    def get_command(self, target: str, **kwargs) -> List[str]:
        cmd = ["wpscan", "--url", target, "--no-banner", "--format", "cli"]
        if kwargs.get("enumerate"):
            cmd.extend(["--enumerate", kwargs["enumerate"]])
        return cmd

    def parse_output(self, output: str) -> Dict[str, Any]:
        results: Dict[str, Any] = {"vulnerabilities": [], "plugins": [], "themes": [], "version": None}
        for line in output.split("\n"):
            if "WordPress version" in line:
                results["version"] = line.split("WordPress version")[1].strip()
            if "[!]" in line:
                results["vulnerabilities"].append(line.strip())
        return results
