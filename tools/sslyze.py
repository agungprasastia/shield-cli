"""SSLyze — Advanced SSL/TLS analysis"""
from typing import Dict, Any, List
from tools.base_tool import BaseTool

class SslyzeTool(BaseTool):
    def get_command(self, target: str, **kwargs) -> List[str]:
        return ["sslyze", "--regular", target]

    def parse_output(self, output: str) -> Dict[str, Any]:
        results: Dict[str, Any] = {"certificate": {}, "issues": [], "protocols": []}
        for line in output.split("\n"):
            l = line.strip()
            if "VULNERABLE" in l.upper() or "WEAK" in l.upper():
                results["issues"].append(l)
            if "Certificate" in l:
                results["certificate"]["info"] = l
        return results
