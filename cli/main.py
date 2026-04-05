"""
Shield CLI — Main Entry Point
"""

import os
import sys

# Fix Windows encoding — prevent 'charmap' codec errors
if sys.platform == "win32":
    os.environ["PYTHONUTF8"] = "1"
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Load .env file early — API keys must be available to all commands
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import typer
from rich.console import Console

from cli.commands import init_cmd, scan, recon, workflow, report, models, analyze

banner = """
[bold blue]      ███████████████████████[/bold blue]
[bold blue]      ██[/bold blue][bold cyan]▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓[/bold cyan][bold blue]██[/bold blue]      [bold cyan]███████╗██╗  ██╗██╗███████╗██╗     ██████╗[/bold cyan]
[bold blue]      ██[/bold blue][bold cyan]▓▓▓▓▓▓▓▓[/bold cyan][bold white]███[/bold white][bold cyan]▓▓▓▓▓▓▓▓[/bold cyan][bold blue]██[/bold blue]      [bold cyan]██╔════╝██║  ██║██║██╔════╝██║     ██╔══██╗[/bold cyan]
[bold blue]      ██[/bold blue][bold cyan]▓▓▓▓▓▓▓[/bold cyan][bold white]█████[/bold white][bold cyan]▓▓▓▓▓▓▓[/bold cyan][bold blue]██[/bold blue]      [bold cyan]███████╗███████║██║█████╗  ██║     ██║  ██║[/bold cyan]
[bold blue]      ██[/bold blue][bold cyan]▓▓▓[/bold cyan][bold white]█████████████[/bold white][bold cyan]▓▓▓[/bold cyan][bold blue]██[/bold blue]      [bold cyan]╚════██║██╔══██║██║██╔══╝  ██║     ██║  ██║[/bold cyan]
[bold blue]      ██[/bold blue][bold cyan]▓▓▓▓▓▓▓[/bold cyan][bold white]█████[/bold white][bold cyan]▓▓▓▓▓▓▓[/bold cyan][bold blue]██[/bold blue]      [bold cyan]███████║██║  ██║██║███████╗███████╗██████╔╝[/bold cyan]
[bold blue]      ██[/bold blue][bold cyan]▓▓▓▓▓▓▓▓[/bold cyan][bold white]███[/bold white][bold cyan]▓▓▓▓▓▓▓▓[/bold cyan][bold blue]██[/bold blue]      [bold cyan]╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚═════╝[/bold cyan]
[bold blue]       ██[/bold blue][bold cyan]▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓[/bold cyan][bold blue]██[/bold blue]
[bold blue]        ██[/bold blue][bold cyan]▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓[/bold cyan][bold blue]██[/bold blue]        [bold green]v0.1.0[/bold green] [dim]— AI-Powered Pentest Framework[/dim]
[bold blue]         ███[/bold blue][bold cyan]▓▓▓▓▓▓▓▓▓▓▓[/bold cyan][bold blue]███[/bold blue]
[bold blue]           ███[/bold blue][bold cyan]▓▓▓▓▓▓▓[/bold cyan][bold blue]███[/bold blue]          [dim]Providers:[/dim]  Gemini • GPT-4 • Claude • OpenRouter
[bold blue]             ███[/bold blue][bold cyan]▓▓▓[/bold cyan][bold blue]███[/bold blue]            [dim]Features:[/dim]   19 Tools • Smart Workflows • Multi-Agent
[bold blue]               █████[/bold blue]
                                    [italic dim]Shield — Your Digital Armor 🛡️[/italic dim]
"""

# Initialize Typer app
app = typer.Typer(
    name="Shield",
    help="🔐 Shield — AI-Powered Penetration Testing CLI Tool",
    add_completion=False,
    rich_markup_mode="rich",
)

console = Console()

# Register commands
app.command(name="init")(init_cmd.init_command)
app.command(name="scan")(scan.scan_command)
app.command(name="recon")(recon.recon_command)
app.command(name="workflow")(workflow.workflow_command)
app.command(name="report")(report.report_command)
app.command(name="models")(models.list_models_command)
app.command(name="analyze")(analyze.analyze_command)


@app.callback()
def callback():
    """
    Shield — AI-Powered Penetration Testing CLI Tool

    Leverage AI to orchestrate intelligent penetration testing workflows.
    """
    console.print(banner)
    console.print()


def version_callback(value: bool):
    if value:
        console.print("[bold green]Shield CLI v0.1.0.0[/bold green]")
        raise typer.Exit()


@app.command()
def version(
    show: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show version and exit",
        callback=version_callback,
        is_eager=True,
    ),
):
    """Show Shield version"""
    pass


def main():
    """Main entry point"""
    try:
        app()
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
