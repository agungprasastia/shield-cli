"""Report generation command"""

import typer
import asyncio
import yaml
import json
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from typing import Optional

console = Console()


def report_command(
    session: str = typer.Option(..., "--session", "-s", help="Session ID to generate report from"),
    format: str = typer.Option("markdown", "--format", "-f", help="Report format: markdown, html, json"),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="AI provider"),
):
    """Generate a report from a previous session"""
    console.print(f"\n[bold cyan]📊 Generating Report[/bold cyan]")
    console.print(f"  Session: {session}")
    console.print(f"  Format: {format}\n")

    # Load session
    reports_dir = Path("reports")
    session_file = reports_dir / f"session_{session}.json"

    if not session_file.exists():
        console.print(f"[red]❌ Session file not found: {session_file}[/red]")
        console.print("   Available sessions:")
        for sf in reports_dir.glob("session_*.json"):
            sid = sf.stem.replace("session_", "")
            console.print(f"     • {sid}")
        raise typer.Exit(1)

    config = _load_config()

    # Load session state and generate report
    from core.memory import PentestMemory
    from core.workflow import WorkflowEngine

    memory = PentestMemory("unknown")
    memory.load_state(session_file)

    engine = WorkflowEngine(config, memory.target, provider_override=provider)
    engine.memory = memory

    try:
        result = asyncio.run(engine.reporter.execute(format=format))

        # Save report
        ext_map = {"markdown": "md", "html": "html", "json": "json"}
        ext = ext_map.get(format, "md")
        report_file = reports_dir / f"report_{session}.{ext}"

        with open(report_file, "w", encoding="utf-8") as f:
            f.write(result["content"])

        console.print(Panel(
            f"[green]Report generated![/green]\n\n"
            f"  File: {report_file}\n"
            f"  Format: {format}\n"
            f"  Findings: {len(memory.findings)}",
            title="✅ Report Ready",
            border_style="green",
        ))
    except Exception as e:
        console.print(f"[red]❌ Report generation failed: {e}[/red]")


def _load_config():
    config_path = Path("config/shield.yaml")
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}
