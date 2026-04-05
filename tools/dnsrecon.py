"""DNSRecon — DNS reconnaissance and enumeration"""
from typing import Dict, Any, List
from tools.base_tool import BaseTool

class DnsreconTool(BaseTool):
    def get_command(self, target: str, **kwargs) -> List[str]:
        cmd = ["dnsrecon", "-d", target]
        record_type = kwargs.get("type", "std")
        cmd.extend(["-t", record_type])
        return cmd

    def parse_output(self, output: str) -> Dict[str, Any]:
        results: Dict[str, Any] = {"records": [], "nameservers": []}
        for line in output.strip().split("\n"):
            l = line.strip()
            if l and ("[*]" in l or "[+]" in l):
                results["records"].append(l)
                if "NS" in l:
                    results["nameservers"].append(l)
        return results
