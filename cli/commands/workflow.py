"""Workflow management command"""

import typer
import asyncio
import yaml
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from typing import Optional

console = Console()


def workflow_command(
    action: str = typer.Argument("list", help="Action: list, run"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Workflow name"),
    target: Optional[str] = typer.Option(None, "--target", "-t", help="Target URL/IP"),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="AI provider"),
):
    """Manage and run pentest workflows"""
    if action == "list":
        _list_workflows()
    elif action == "run":
        if not name or not target:
            console.print("[red]❌ --name and --target are required for 'run'[/red]")
            console.print("   Example: python -m cli.main workflow run --name web_pentest --target example.com")
            raise typer.Exit(1)
        _run_workflow(name, target, provider)
    else:
        console.print(f"[red]❌ Unknown action: {action}. Use 'list' or 'run'[/red]")


def _list_workflows():
    """List all available workflows"""
    console.print("\n[bold cyan]📋 Available Workflows[/bold cyan]\n")

    workflows_dir = Path("workflows")
    if not workflows_dir.exists():
        console.print("[red]No workflows directory found[/red]")
        return

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Name", style="cyan")
    table.add_column("Description")
    table.add_column("Category", style="green")
    table.add_column("Steps", justify="right")

    for wf in sorted(workflows_dir.glob("*.yaml")):
        try:
            with open(wf, "r") as f:
                data = yaml.safe_load(f)
            table.add_row(
                data.get("name", wf.stem),
                data.get("description", "N/A"),
                data.get("category", "general"),
                str(len(data.get("steps", []))),
            )
        except Exception:
            table.add_row(wf.stem, "Error loading", "-", "-")

    console.print(table)
    console.print("\n  Run: [bold]python -m cli.main workflow run --name <name> --target <target>[/bold]")


def _run_workflow(name: str, target: str, provider: Optional[str]):
    """Run a specific workflow"""
    console.print(f"\n[bold cyan]🚀 Running Workflow: {name}[/bold cyan]")
    console.print(f"  Target: [yellow]{target}[/yellow]\n")

    config = _load_config()

    from core.workflow import WorkflowEngine

    engine = WorkflowEngine(config, target, provider_override=provider)

    console.print(f"  Provider: [green]{engine.ai_client.get_provider_name()}[/green]")
    console.print(f"  Model: [green]{engine.ai_client.get_model_name()}[/green]")
    console.print(f"  Safe mode: [yellow]{'enabled' if config.get('pentest', {}).get('safe_mode') else 'disabled'}[/yellow]")
    console.print()

    try:
        if name == "autonomous":
            result = asyncio.run(engine.run_autonomous())
        else:
            result = asyncio.run(engine.run_workflow(name))

        console.print(Panel(
            f"[green]Workflow completed![/green]\n\n"
            f"  Status: {result['status']}\n"
            f"  Findings: {result['findings']}\n"
            f"  Session: {result['session_id']}\n\n"
            f"  Report: ./reports/report_{result['session_id']}.md",
            title="✅ Workflow Results",
            border_style="green",
        ))
    except ValueError as e:
        console.print(f"[red]❌ {e}[/red]")
    except Exception as e:
        console.print(f"[red]❌ Workflow failed: {e}[/red]")


def _load_config():
    config_path = Path("config/shield.yaml")
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}
