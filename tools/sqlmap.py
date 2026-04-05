"""SQLMap — SQL injection detection"""
from typing import Dict, Any, List
from tools.base_tool import BaseTool

class SqlmapTool(BaseTool):
    def get_command(self, target: str, **kwargs) -> List[str]:
        cfg = self.config.get("tools", {}).get("sqlmap", {})
        cmd = ["sqlmap", "-u", target, "--batch", "--output-dir=/tmp/sqlmap"]
        risk = kwargs.get("risk", cfg.get("risk", 1))
        level = kwargs.get("level", cfg.get("level", 1))
        cmd.extend(["--risk", str(risk), "--level", str(level)])
        return cmd

    def parse_output(self, output: str) -> Dict[str, Any]:
        results: Dict[str, Any] = {"injectable": False, "parameters": [], "dbms": None}
        if "is vulnerable" in output.lower() or "sqlmap identified" in output.lower():
            results["injectable"] = True
        if "back-end DBMS:" in output:
            idx = output.find("back-end DBMS:") + len("back-end DBMS:")
            results["dbms"] = output[idx:].split("\n")[0].strip()
        return results
