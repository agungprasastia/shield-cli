"""
Workflow Orchestration Engine
Coordinates agents and manages pentest execution flow.
"""

import time
import yaml
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime

from core.memory import PentestMemory, ToolExecution
from ai.client import AIClient
from utils.logger import get_logger
from utils.scope_validator import ScopeValidator


class WorkflowEngine:
    """Orchestrates the penetration testing workflow"""

    def __init__(
        self,
        config: Dict[str, Any],
        target: str,
        provider_override: Optional[str] = None,
    ):
        self.config = config
        self.target = target
        self.logger = get_logger(config)

        # Initialize components
        self.memory = PentestMemory(target)
        self.scope_validator = ScopeValidator(config)
        self.ai_client = AIClient(config, provider_override)

        # Initialize agents (lazy — avoids circular imports)
        self._planner = None
        self._tool_agent = None
        self._analyst = None
        self._reporter = None

        # Workflow state
        self.is_running = False
        self.current_step = 0
        self.max_steps = config.get("workflows", {}).get("max_steps", 20)

    @property
    def planner(self):
        if self._planner is None:
            from core.planner import PlannerAgent
            self._planner = PlannerAgent(self.config, self.ai_client, self.memory)
        return self._planner

    @property
    def tool_agent(self):
        if self._tool_agent is None:
            from core.tool_agent import ToolAgent
            self._tool_agent = ToolAgent(self.config, self.ai_client, self.memory)
        return self._tool_agent

    @property
    def analyst(self):
        if self._analyst is None:
            from core.analyst_agent import AnalystAgent
            self._analyst = AnalystAgent(self.config, self.ai_client, self.memory)
        return self._analyst

    @property
    def reporter(self):
        if self._reporter is None:
            from core.reporter_agent import ReporterAgent
            self._reporter = ReporterAgent(self.config, self.ai_client, self.memory)
        return self._reporter

    async def run_workflow(self, workflow_name: str) -> Dict[str, Any]:
        """Run a predefined workflow"""
        self.logger.info(f"Starting workflow: {workflow_name} for target: {self.target}")

        # Validate target
        is_valid, reason = self.scope_validator.validate_target(self.target)
        if not is_valid:
            self.logger.error(f"Target validation failed: {reason}")
            raise ValueError(f"Invalid target: {reason}")

        self.is_running = True
        self.memory.update_phase(f"{workflow_name}_workflow")

        try:
            steps = self._load_workflow(workflow_name)

            from rich.console import Console
            c = Console()

            for i, step in enumerate(steps, 1):
                if not self.is_running:
                    break

                step_name = step.get('name', 'unknown')
                step_type = step.get('type', 'tool')
                c.print(f"\n[bold cyan]  [{i}/{len(steps)}] {step_name}[/bold cyan] [dim]({step_type})[/dim]")

                try:
                    await self._execute_step(step)
                    c.print("       [green]✅ Done[/green]")
                except Exception as e:
                    c.print(f"       [yellow]⚠️  Skipped: {e}[/yellow]")
                    self.logger.warning(f"Step {step_name} failed: {e}")

                self.current_step += 1

            # Final analysis
            analysis = await self.planner.analyze_results()
            self._save_session()

            return {
                "status": "completed",
                "findings": len(self.memory.findings),
                "analysis": analysis,
                "session_id": self.memory.session_id,
            }

        except Exception as e:
            self.logger.error(f"Workflow failed: {e}")
            self._save_session()
            raise
        finally:
            self.is_running = False

    async def run_autonomous(self) -> Dict[str, Any]:
        """Run autonomous pentest where AI decides each step"""
        self.logger.info(f"Starting autonomous pentest for target: {self.target}")

        is_valid, reason = self.scope_validator.validate_target(self.target)
        if not is_valid:
            raise ValueError(f"Invalid target: {reason}")

        self.is_running = True
        self.memory.update_phase("reconnaissance")

        try:
            while self.is_running and self.current_step < self.max_steps:
                decision = await self.planner.decide_next_action()

                self.logger.info(f"AI Decision: {decision.get('next_action')}")

                action = decision.get("next_action", "").lower()
                if action in ("done", "complete", "finish", "generate_report"):
                    self.logger.info("Planner decided workflow is complete")
                    break

                await self._execute_ai_decision(decision)
                self.current_step += 1
                self._maybe_advance_phase()

            analysis = await self.planner.analyze_results()
            self._save_session()

            return {
                "status": "completed",
                "findings": len(self.memory.findings),
                "analysis": analysis,
                "session_id": self.memory.session_id,
            }

        except Exception as e:
            self.logger.error(f"Autonomous workflow failed: {e}")
            self._save_session()
            raise
        finally:
            self.is_running = False

    def stop(self):
        self.logger.info("Stopping workflow")
        self.is_running = False

    # ── Internal Methods ────────────────────────────────────────

    async def _execute_step(self, step: Dict[str, Any]):
        """Execute a workflow step"""
        step_type = step.get("type", "tool")

        if step_type == "tool":
            tool_name = step["tool"]
            params = step.get("parameters", {})

            result = await self.tool_agent.execute_tool(
                tool_name=tool_name,
                target=self.target,
                **params,
            )

            if result.get("success"):
                execution_id = f"{tool_name}_{int(time.time() * 1000)}"

                execution = ToolExecution(
                    id=execution_id,
                    tool=tool_name,
                    command=result.get("command", ""),
                    target=self.target,
                    timestamp=datetime.now().isoformat(),
                    exit_code=result.get("exit_code", 0),
                    output=result.get("raw_output", ""),
                    duration=result.get("duration", 0),
                )
                self.memory.add_tool_execution(execution)

                self.logger.info("Analyst Agent analyzing results...")
                await self.analyst.interpret_output(
                    tool=tool_name,
                    target=self.target,
                    command=result.get("command", ""),
                    output=result.get("raw_output", ""),
                    execution_id=execution_id,
                    exit_code=result.get("exit_code", 0),
                )
            else:
                raise RuntimeError(f"Tool '{tool_name}': {result.get('error', 'unknown error')}")

        elif step_type == "analysis":
            self.logger.info("Running correlation analysis...")
            await self.analyst.correlate_findings()

        elif step_type == "report":
            config_format = self.config.get("output", {}).get("format", "markdown")
            report_format = step.get("format", config_format)

            self.logger.info(f"Generating {report_format} report...")
            report = await self.reporter.execute(format=report_format)

            output_dir = Path(self.config.get("output", {}).get("save_path", "./reports"))
            output_dir.mkdir(parents=True, exist_ok=True)

            ext_map = {"markdown": "md", "html": "html", "json": "json"}
            ext = ext_map.get(report_format, "md")
            report_file = output_dir / f"report_{self.memory.session_id}.{ext}"

            with open(report_file, "w", encoding="utf-8") as f:
                f.write(report["content"])

            self.logger.info(f"Report saved to: {report_file}")

        self.memory.mark_action_complete(step["name"])

    async def _execute_ai_decision(self, decision: Dict[str, Any]):
        """Execute an AI-decided action"""
        action = decision.get("next_action", "")
        self.logger.info(f"Executing AI decision: {action}")

        try:
            tool_selection = await self.tool_agent.execute(
                objective=action,
                target=self.target,
            )

            result = await self.tool_agent.execute_tool(
                tool_name=tool_selection["tool"],
                target=self.target,
            )

            if result.get("success"):
                await self.analyst.interpret_output(
                    tool=tool_selection["tool"],
                    target=self.target,
                    command=result.get("command", ""),
                    output=result.get("raw_output", ""),
                )

        except Exception as e:
            self.logger.error(f"Failed to execute AI decision: {e}")

        self.memory.mark_action_complete(action)

    def _load_workflow(self, workflow_name: str) -> List[Dict[str, Any]]:
        """Load workflow definition from YAML file"""
        project_root = Path(__file__).parent.parent
        workflows_dir = project_root / "workflows"

        self.logger.info(f"Looking for workflow: {workflow_name}")

        # Exact match
        exact = workflows_dir / f"{workflow_name}.yaml"
        workflow_file = None
        if exact.exists():
            workflow_file = exact
        else:
            # Fuzzy match
            for yf in workflows_dir.glob("*.yaml"):
                stem = yf.stem.lower()
                wl = workflow_name.lower()
                if stem in wl or wl in stem:
                    workflow_file = yf
                    break

        if not workflow_file:
            self.logger.warning(f"Workflow not found: {workflow_name}. Using fallback.")
            return [
                {"name": "port_scanning", "type": "tool", "tool": "nmap"},
                {"name": "analysis", "type": "analysis"},
            ]

        try:
            with open(workflow_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            steps = data.get("steps", [])
            self.logger.info(f"Loaded {len(steps)} steps from {workflow_file.name}")
            return steps

        except Exception as e:
            self.logger.error(f"Failed to load workflow: {e}")
            return [
                {"name": "basic_scan", "type": "tool", "tool": "nmap"},
                {"name": "analysis", "type": "analysis"},
            ]

    def _maybe_advance_phase(self):
        phases = ["reconnaissance", "scanning", "analysis", "reporting"]
        try:
            idx = phases.index(self.memory.current_phase)
        except ValueError:
            idx = 0

        if self.current_step % 5 == 0 and idx < len(phases) - 1:
            new_phase = phases[idx + 1]
            self.logger.info(f"Advancing to phase: {new_phase}")
            self.memory.update_phase(new_phase)

    def _save_session(self):
        output_dir = Path(self.config.get("output", {}).get("save_path", "./reports"))
        output_dir.mkdir(parents=True, exist_ok=True)
        state_file = output_dir / f"session_{self.memory.session_id}.json"
        self.memory.save_state(state_file)
        self.logger.info(f"Session saved to: {state_file}")
