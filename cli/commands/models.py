"""List AI models and provider status"""

import yaml
from pathlib import Path
from rich.console import Console
from rich.table import Table

console = Console()


def list_models_command():
    """List AI providers and their configuration status"""
    console.print("\n[bold cyan]🤖 AI Provider Status[/bold cyan]\n")

    config = _load_config()

    from ai.client import AIClient

    status = AIClient.get_all_provider_status(config)
    active_provider = config.get("ai", {}).get("provider", "gemini")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Provider", style="cyan")
    table.add_column("Model")
    table.add_column("Status")
    table.add_column("Active", justify="center")

    for name, info in status.items():
        is_active = "⭐" if name == active_provider else ""
        table.add_row(
            name.title(),
            info["model"],
            info["status"],
            is_active,
        )

    console.print(table)
    console.print(f"\n  Active provider: [bold green]{active_provider}[/bold green]")
    console.print("  Switch provider: edit [bold]config/shield.yaml[/bold] or use [bold]--provider[/bold] flag")


def _load_config():
    config_path = Path("config/shield.yaml")
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}
