"""Quick scan command"""

import typer
import asyncio
import yaml
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from typing import Optional

console = Console()


def scan_command(
    target: str = typer.Argument(..., help="Target URL or IP to scan"),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="AI provider to use"),
):
    """Run a quick security scan against a target"""
    from utils.input_validator import validate_target as validate_input

    # Validate target input
    valid, error = validate_input(target)
    if not valid:
        console.print(f"[red]❌ Invalid target: {error}[/red]")
        raise typer.Exit(1)

    console.print(f"\n[bold cyan]🎯 Quick Scan: {target}[/bold cyan]\n")

    # Load config
    config = _load_config()

    from core.workflow import WorkflowEngine

    engine = WorkflowEngine(config, target, provider_override=provider)

    console.print(f"  Provider: [green]{engine.ai_client.get_provider_name()}[/green]")
    console.print(f"  Model: [green]{engine.ai_client.get_model_name()}[/green]")
    console.print(f"  Safe mode: [yellow]{'enabled' if config.get('pentest', {}).get('safe_mode') else 'disabled'}[/yellow]")
    console.print()

    try:
        result = asyncio.run(engine.run_workflow("quick_scan"))
        console.print(Panel(
            f"[green]Scan completed![/green]\n"
            f"Findings: {result['findings']}\n"
            f"Session: {result['session_id']}",
            title="✅ Results",
            border_style="green",
        ))
    except ValueError as e:
        console.print(f"[red]❌ {e}[/red]")
    except Exception as e:
        console.print(f"[red]❌ Scan failed: {e}[/red]")


def _load_config():
    config_path = Path("config/shield.yaml")
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}
