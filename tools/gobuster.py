"""Gobuster — Directory brute forcing"""
import sys
from pathlib import Path
from typing import Dict, Any, List
from tools.base_tool import BaseTool


def _default_wordlist() -> str:
    """Find a wordlist path that works on this OS"""
    candidates = [
        Path("/usr/share/wordlists/dirb/common.txt"),       # Kali Linux
        Path("/usr/share/seclists/Discovery/Web-Content/common.txt"),  # SecLists
        Path.home() / "wordlists" / "common.txt",           # User home
        Path("wordlists/common.txt"),                        # Project local
    ]
    if sys.platform == "win32":
        candidates.insert(0, Path("C:/Tools/wordlists/common.txt"))
        candidates.insert(0, Path("C:/SecLists/Discovery/Web-Content/common.txt"))

    for p in candidates:
        if p.exists():
            return str(p)
    return "common.txt"  # Fallback — gobuster will error if missing


class GobusterTool(BaseTool):
    def get_command(self, target: str, **kwargs) -> List[str]:
        cfg = self.config.get("tools", {}).get("gobuster", {})
        wordlist = kwargs.get("wordlist", cfg.get("wordlist", _default_wordlist()))
        threads = kwargs.get("threads", cfg.get("threads", 30))
        cmd = ["gobuster", "dir", "-u", target, "-w", wordlist, "-t", str(threads), "-q"]
        return cmd

    def parse_output(self, output: str) -> Dict[str, Any]:
        results: Dict[str, Any] = {"directories": [], "files": []}
        for line in output.strip().split("\n"):
            l = line.strip()
            if l and "Status:" in l:
                results["directories"].append(l)
            elif l:
                results["files"].append(l)
        return results
