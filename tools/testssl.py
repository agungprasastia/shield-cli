"""TestSSL — SSL/TLS configuration testing"""
from typing import Dict, Any, List
from tools.base_tool import BaseTool

class TestsslTool(BaseTool):
    def get_command(self, target: str, **kwargs) -> List[str]:
        return ["testssl", "--quiet", "--color", "0", target]

    def parse_output(self, output: str) -> Dict[str, Any]:
        results: Dict[str, Any] = {"issues": [], "protocols": [], "ciphers": []}
        for line in output.split("\n"):
            if "VULNERABLE" in line.upper():
                results["issues"].append(line.strip())
            if "TLS" in line or "SSL" in line:
                results["protocols"].append(line.strip())
        return results
