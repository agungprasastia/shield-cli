"""Analyze existing session findings"""

import typer
import asyncio
import yaml
from pathlib import Path
from rich.console import Console
from typing import Optional

console = Console()


def analyze_command(
    session: str = typer.Option(..., "--session", "-s", help="Session ID to re-analyze"),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="AI provider"),
):
    """Re-analyze findings from a previous session"""
    console.print(f"\n[bold cyan]🔬 Re-analyzing Session: {session}[/bold cyan]\n")

    session_file = Path("reports") / f"session_{session}.json"
    if not session_file.exists():
        console.print(f"[red]❌ Session not found: {session_file}[/red]")
        raise typer.Exit(1)

    config = _load_config()

    from core.memory import PentestMemory
    from core.workflow import WorkflowEngine

    memory = PentestMemory("unknown")
    memory.load_state(session_file)

    engine = WorkflowEngine(config, memory.target, provider_override=provider)
    engine.memory = memory

    try:
        result = asyncio.run(engine.analyst.correlate_findings())
        console.print("\n[bold green]Analysis Complete:[/bold green]\n")
        console.print(result.get("analysis", "No analysis available"))
    except Exception as e:
        console.print(f"[red]❌ Analysis failed: {e}[/red]")


def _load_config():
    config_path = Path("config/shield.yaml")
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}
