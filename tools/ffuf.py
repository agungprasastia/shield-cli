"""FFuf — Web fuzzing"""
from typing import Dict, Any, List
from tools.base_tool import BaseTool

class FfufTool(BaseTool):
    def get_command(self, target: str, **kwargs) -> List[str]:
        cfg = self.config.get("tools", {}).get("ffuf", {})
        wordlist = kwargs.get("wordlist", "/usr/share/wordlists/dirb/common.txt")
        threads = kwargs.get("threads", cfg.get("threads", 40))
        url = target if "FUZZ" in target else f"{target}/FUZZ"
        cmd = ["ffuf", "-u", url, "-w", wordlist, "-t", str(threads), "-mc", "200,301,302,403"]
        return cmd

    def parse_output(self, output: str) -> Dict[str, Any]:
        results: Dict[str, Any] = {"found": []}
        for line in output.strip().split("\n"):
            l = line.strip()
            if l and "[Status:" in l:
                results["found"].append(l)
        return results
