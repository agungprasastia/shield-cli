"""Quick reconnaissance command"""

import typer
import asyncio
import yaml
from pathlib import Path
from rich.console import Console
from typing import Optional

console = Console()


def recon_command(
    target: str = typer.Argument(..., help="Target domain to recon"),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="AI provider to use"),
):
    """Run quick reconnaissance on a target"""
    from utils.input_validator import validate_target as validate_input

    valid, error = validate_input(target)
    if not valid:
        console.print(f"[red]❌ Invalid target: {error}[/red]")
        raise typer.Exit(1)

    console.print(f"\n[bold cyan]🔍 Reconnaissance: {target}[/bold cyan]\n")

    config = _load_config()

    from core.workflow import WorkflowEngine

    engine = WorkflowEngine(config, target, provider_override=provider)

    console.print(f"  Provider: [green]{engine.ai_client.get_provider_name()}[/green]")
    console.print(f"  Model: [green]{engine.ai_client.get_model_name()}[/green]")
    console.print()

    try:
        result = asyncio.run(engine.run_workflow("recon"))
        console.print(f"\n[green]✅ Recon complete! {result['findings']} findings. Session: {result['session_id']}[/green]")
    except ValueError as e:
        console.print(f"[red]❌ {e}[/red]")
    except Exception as e:
        console.print(f"[red]❌ Recon failed: {e}[/red]")


def _load_config():
    config_path = Path("config/shield.yaml")
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}
