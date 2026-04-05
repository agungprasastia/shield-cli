"""
Analyst Agent
Interprets tool outputs into structured findings, filters false positives.
"""

import time
from typing import Dict, Any, List
from core.agent import BaseAgent
from core.memory import Finding
from ai.prompt_templates import (
    ANALYST_SYSTEM_PROMPT,
    ANALYST_INTERPRET_PROMPT,
    ANALYST_CORRELATE_PROMPT,
)


class AnalystAgent(BaseAgent):
    """Analyzes tool output and produces structured findings"""

    def __init__(self, config, ai_client, memory):
        super().__init__("Analyst", config, ai_client, memory)

    async def execute(self, **kwargs) -> Dict[str, Any]:
        return await self.correlate_findings()

    async def interpret_output(
        self,
        tool: str,
        target: str,
        command: str,
        output: str,
        execution_id: str | None = None,
        exit_code: int = 0,
    ) -> Dict[str, Any]:
        """Interpret raw tool output into structured findings"""
        # Truncate output for AI consumption
        truncated = output[:3000] if output else "No output"

        prompt = ANALYST_INTERPRET_PROMPT.format(
            tool=tool,
            target=target,
            command=command,
            exit_code=exit_code,
            output=truncated,
        )

        result = await self.think(prompt, ANALYST_SYSTEM_PROMPT)

        # Parse findings from AI response
        findings = self._parse_findings(
            result["response"], tool, target, execution_id, output
        )

        # Add to memory
        for finding in findings:
            self.memory.add_finding(finding)
            self.logger.log_finding(finding.severity, finding.title, finding.tool)

        self.log_action(
            "Analysis Complete",
            f"{len(findings)} findings from {tool}",
        )

        return {"findings": findings, "reasoning": result["reasoning"]}

    async def correlate_findings(self) -> Dict[str, Any]:
        """Cross-correlate findings from multiple tools"""
        if not self.memory.findings:
            return {"analysis": "No findings to correlate", "patterns": []}

        findings_text = "\n".join(
            f"- [{f.severity.upper()}] {f.title} (from {f.tool}): {f.description[:100]}"
            for f in self.memory.findings
            if not f.false_positive
        )

        tools_text = "\n".join(
            f"- {t.tool} on {t.target} ({t.duration:.1f}s)"
            for t in self.memory.tool_executions
        )

        prompt = ANALYST_CORRELATE_PROMPT.format(
            findings=findings_text,
            tool_executions=tools_text,
            target=self.memory.target,
        )

        result = await self.think(prompt, ANALYST_SYSTEM_PROMPT)

        return {"analysis": result["response"], "reasoning": result["reasoning"]}

    def _parse_findings(
        self,
        response: str,
        tool: str,
        target: str,
        execution_id: str | None,
        raw_output: str,
    ) -> List[Finding]:
        """Parse AI response into Finding objects"""
        findings: List[Finding] = []

        # Split by FINDING: markers
        sections = response.split("FINDING:")
        for i, section in enumerate(sections[1:], 1):  # Skip preamble
            finding = self._parse_single_finding(
                section, tool, target, execution_id, raw_output, i
            )
            if finding:
                findings.append(finding)

        # If no structured findings found but response has content,
        # try direct severity pattern
        if not findings and any(kw in response.upper() for kw in ["CRITICAL", "HIGH", "MEDIUM"]):
            finding = self._fallback_parse(response, tool, target, execution_id, raw_output)
            if finding:
                findings.append(finding)

        return findings

    def _parse_single_finding(
        self, text: str, tool: str, target: str,
        execution_id: str | None, raw_output: str, idx: int,
    ) -> Finding | None:
        """Parse a single finding section"""
        severity = "info"
        title = f"Finding from {tool}"
        description = ""
        evidence = ""
        remediation = ""
        false_positive = False

        for line in text.strip().split("\n"):
            line = line.strip()
            upper = line.upper()
            if upper.startswith("SEVERITY:"):
                sev = line.split(":", 1)[1].strip().lower()
                if sev in ("critical", "high", "medium", "low", "info"):
                    severity = sev
            elif upper.startswith("TITLE:"):
                title = line.split(":", 1)[1].strip()
            elif upper.startswith("DESCRIPTION:"):
                description = line.split(":", 1)[1].strip()
            elif upper.startswith("EVIDENCE:"):
                evidence = line.split(":", 1)[1].strip()
            elif upper.startswith("REMEDIATION:"):
                remediation = line.split(":", 1)[1].strip()
            elif upper.startswith("FALSE_POSITIVE:"):
                val = line.split(":", 1)[1].strip().lower()
                false_positive = val in ("true", "yes", "1")

        if not title or title == f"Finding from {tool}":
            return None

        ts = int(time.time() * 1000)
        return Finding(
            id=f"{tool}_{ts}_{idx}",
            severity=severity,
            title=title,
            description=description or title,
            evidence=evidence,
            tool=tool,
            target=target,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S"),
            remediation=remediation,
            false_positive=false_positive,
            execution_id=execution_id,
            raw_evidence=raw_output[:2000] if raw_output else None,
        )

    def _fallback_parse(
        self, response: str, tool: str, target: str,
        execution_id: str | None, raw_output: str,
    ) -> Finding | None:
        """Fallback parsing when structured format isn't found"""
        ts = int(time.time() * 1000)
        
        # Try to determine severity from response
        upper = response.upper()
        if "CRITICAL" in upper:
            severity = "critical"
        elif "HIGH" in upper:
            severity = "high"
        elif "MEDIUM" in upper:
            severity = "medium"
        else:
            severity = "low"

        return Finding(
            id=f"{tool}_{ts}_fallback",
            severity=severity,
            title=f"Finding from {tool} analysis",
            description=response[:500],
            evidence=response[:300],
            tool=tool,
            target=target,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S"),
            remediation="Review the raw output for detailed remediation steps.",
            execution_id=execution_id,
            raw_evidence=raw_output[:2000] if raw_output else None,
        )
