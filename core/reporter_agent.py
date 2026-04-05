"""
Reporter Agent
Generates professional penetration test reports.
"""

from typing import Dict, Any
from datetime import datetime

from core.agent import BaseAgent
from ai.prompt_templates import (
    REPORTER_SYSTEM_PROMPT,
    REPORTER_EXECUTIVE_SUMMARY_PROMPT,
    REPORTER_REMEDIATION_PROMPT,
)
from reports.generator import ReportGenerator


class ReporterAgent(BaseAgent):
    """Generates professional pentest reports"""

    def __init__(self, config, ai_client, memory):
        super().__init__("Reporter", config, ai_client, memory)
        self.generator = ReportGenerator()

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Generate a full report"""
        report_format = kwargs.get(
            "format",
            self.config.get("output", {}).get("format", "markdown"),
        )

        # Generate executive summary via AI
        exec_summary = await self._generate_executive_summary()

        # Generate remediation plan via AI
        remediation = await self._generate_remediation_plan()

        # Calculate duration
        duration = self._calculate_duration()

        # Build report data
        report_data = {
            "target": self.memory.target,
            "session_id": self.memory.session_id,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "duration": duration,
            "executive_summary": exec_summary,
            "findings_summary": self.memory.get_findings_summary(),
            "findings": self.memory.findings,
            "tool_executions": self.memory.tool_executions,
            "ai_decisions": self.memory.ai_decisions if self.config.get("output", {}).get("include_reasoning", True) else [],
            "remediation_plan": remediation,
        }

        # Render template
        content = self.generator.render(report_format, report_data)

        self.log_action("Report Generated", f"{report_format} format, {len(self.memory.findings)} findings")

        return {"content": content, "format": report_format}

    async def _generate_executive_summary(self) -> str:
        """Use AI to write an executive summary"""
        summary = self.memory.get_findings_summary()

        key_findings = "\n".join(
            f"- [{f.severity.upper()}] {f.title}"
            for f in self.memory.findings
            if f.severity in ("critical", "high") and not f.false_positive
        ) or "No critical or high severity findings."

        prompt = REPORTER_EXECUTIVE_SUMMARY_PROMPT.format(
            target=self.memory.target,
            duration=self._calculate_duration(),
            session_id=self.memory.session_id,
            critical_count=summary["critical"],
            high_count=summary["high"],
            medium_count=summary["medium"],
            low_count=summary["low"],
            info_count=summary["info"],
            key_findings=key_findings,
        )

        try:
            result = await self.think(prompt, REPORTER_SYSTEM_PROMPT)
            return result["response"]
        except Exception:
            return (
                f"A penetration test was conducted against {self.memory.target}. "
                f"The assessment identified {sum(summary.values())} findings "
                f"including {summary['critical']} critical and {summary['high']} high severity issues."
            )

    async def _generate_remediation_plan(self) -> str:
        """Use AI to create a remediation plan"""
        if not self.memory.findings:
            return "No findings requiring remediation."

        findings_text = "\n".join(
            f"- [{f.severity.upper()}] {f.title}: {f.description[:100]}"
            for f in self.memory.findings
            if not f.false_positive
        )

        prompt = REPORTER_REMEDIATION_PROMPT.format(findings=findings_text)

        try:
            result = await self.think(prompt, REPORTER_SYSTEM_PROMPT)
            return result["response"]
        except Exception:
            return "Review each finding and apply the individual remediation steps provided."

    def _calculate_duration(self) -> str:
        """Calculate test duration"""
        try:
            start = datetime.fromisoformat(self.memory.start_time)
            elapsed = datetime.now() - start
            minutes = int(elapsed.total_seconds() // 60)
            seconds = int(elapsed.total_seconds() % 60)
            return f"{minutes}m {seconds}s"
        except Exception:
            return "N/A"
