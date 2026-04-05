"""Nikto — Web server vulnerability scanning"""
from typing import Dict, Any, List
from tools.base_tool import BaseTool

class NiktoTool(BaseTool):
    def get_command(self, target: str, **kwargs) -> List[str]:
        cmd = ["nikto", "-h", target, "-Format", "txt"]
        if kwargs.get("tuning"):
            cmd.extend(["-Tuning", kwargs["tuning"]])
        return cmd

    def parse_output(self, output: str) -> Dict[str, Any]:
        results: Dict[str, Any] = {"findings": [], "server": None}
        for line in output.split("\n"):
            if "+ " in line and "OSVDB" in line:
                results["findings"].append(line.strip())
            if "Server:" in line:
                results["server"] = line.split("Server:")[1].strip()
        return results
