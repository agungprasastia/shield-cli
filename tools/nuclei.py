"""Nuclei — Template-based vulnerability scanning"""

import json as _json
from typing import Dict, Any, List
from tools.base_tool import BaseTool


class NucleiTool(BaseTool):
    def get_command(self, target: str, **kwargs) -> List[str]:
        cfg = self.config.get("tools", {}).get("nuclei", {})
        cmd = ["nuclei", "-u", target, "-jsonl"]
        severity = kwargs.get("severity", cfg.get("severity", ["critical", "high", "medium"]))
        if severity:
            cmd.extend(["-severity", ",".join(severity)])
        tpl = kwargs.get("templates_path", cfg.get("templates_path"))
        if tpl:
            cmd.extend(["-t", str(tpl)])
        return cmd

    def parse_output(self, output: str) -> Dict[str, Any]:
        results: Dict[str, Any] = {"vulnerabilities": [], "templates_matched": []}
        for line in output.strip().split("\n"):
            if not line.strip():
                continue
            try:
                data = _json.loads(line)
                results["vulnerabilities"].append({
                    "template_id": data.get("template-id", ""),
                    "name": data.get("info", {}).get("name", ""),
                    "severity": data.get("info", {}).get("severity", ""),
                    "matched_at": data.get("matched-at", ""),
                })
                results["templates_matched"].append(data.get("template-id", ""))
            except _json.JSONDecodeError:
                continue
        return results
