"""
Shield — Memory & State Management
Maintains state across the penetration testing workflow.
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict


@dataclass
class Finding:
    """Represents a security finding"""
    id: str
    severity: str          # critical, high, medium, low, info
    title: str
    description: str
    evidence: str
    tool: str
    target: str
    timestamp: str
    remediation: Optional[str] = None
    cvss_score: Optional[float] = None
    false_positive: bool = False
    execution_id: Optional[str] = None   # Link to ToolExecution
    raw_evidence: Optional[str] = None   # Full command output snippet


@dataclass
class ToolExecution:
    """Represents a tool execution record"""
    tool: str
    command: str
    target: str
    timestamp: str
    exit_code: int
    output: str
    duration: float
    findings_count: int = 0
    id: Optional[str] = None


class PentestMemory:
    """Manages penetration test state and context for all agents"""

    def __init__(self, target: str, session_id: Optional[str] = None):
        self.target = target
        self.session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.start_time = datetime.now().isoformat()

        # State tracking
        self.current_phase = "initialization"
        self.completed_actions: List[str] = []
        self.findings: List[Finding] = []
        self.tool_executions: List[ToolExecution] = []
        self.ai_decisions: List[Dict[str, str]] = []

        # Context for AI agents
        self.context: Dict[str, Any] = {
            "target": target,
            "scope": [],
            "discovered_assets": [],
            "open_ports": [],
            "services": [],
            "technologies": [],
        }

    def add_finding(self, finding: Finding):
        self.findings.append(finding)

    def add_tool_execution(self, execution: ToolExecution):
        self.tool_executions.append(execution)

    def add_ai_decision(self, agent: str, decision: str, reasoning: str):
        self.ai_decisions.append({
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "decision": decision,
            "reasoning": reasoning,
        })

    def update_phase(self, phase: str):
        self.current_phase = phase

    def mark_action_complete(self, action: str):
        if action not in self.completed_actions:
            self.completed_actions.append(action)

    def update_context(self, key: str, value: Any):
        if key in self.context and isinstance(self.context[key], list):
            if isinstance(value, list):
                self.context[key].extend(value)
            else:
                self.context[key].append(value)
        else:
            self.context[key] = value

    def get_findings_by_severity(self, severity: str) -> List[Finding]:
        return [f for f in self.findings if f.severity.lower() == severity.lower()]

    def get_findings_summary(self) -> Dict[str, int]:
        summary: Dict[str, int] = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
        for finding in self.findings:
            if not finding.false_positive:
                sev = finding.severity.lower()
                if sev in summary:
                    summary[sev] += 1
        return summary

    def get_context_for_ai(self) -> str:
        assets = self.context.get("discovered_assets", [])
        ports = self.context.get("open_ports", [])
        techs = self.context.get("technologies", [])

        return f"""Target: {self.target}
Current Phase: {self.current_phase}
Session: {self.session_id}

Completed Actions:
{chr(10).join(f'- {a}' for a in self.completed_actions) if self.completed_actions else 'None'}

Findings Summary:
- Critical: {len(self.get_findings_by_severity('critical'))}
- High: {len(self.get_findings_by_severity('high'))}
- Medium: {len(self.get_findings_by_severity('medium'))}
- Low: {len(self.get_findings_by_severity('low'))}

Discovered Assets:
{chr(10).join(f'- {a}' for a in assets) if assets else 'None'}

Open Ports: {', '.join(map(str, ports)) if ports else 'None'}
Technologies: {', '.join(techs) if techs else 'None'}"""

    def save_state(self, filepath: Path):
        state = {
            "target": self.target,
            "session_id": self.session_id,
            "start_time": self.start_time,
            "current_phase": self.current_phase,
            "completed_actions": self.completed_actions,
            "findings": [asdict(f) for f in self.findings],
            "tool_executions": [asdict(t) for t in self.tool_executions],
            "ai_decisions": self.ai_decisions,
            "context": self.context,
        }
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)

    def load_state(self, filepath: Path) -> bool:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                state = json.load(f)
            self.target = state["target"]
            self.session_id = state["session_id"]
            self.start_time = state["start_time"]
            self.current_phase = state["current_phase"]
            self.completed_actions = state["completed_actions"]
            self.findings = [Finding(**f) for f in state["findings"]]
            self.tool_executions = [ToolExecution(**t) for t in state["tool_executions"]]
            self.ai_decisions = state["ai_decisions"]
            self.context = state["context"]
            return True
        except Exception:
            return False
