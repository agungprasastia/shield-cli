"""Initialize Shield configuration"""

import shutil
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

console = Console()


def init_command():
    """Initialize Shield configuration and check dependencies"""
    console.print("[bold cyan]🔧 Initializing Shield...[/bold cyan]\n")

    # Check config
    config_path = Path("config/shield.yaml")
    if config_path.exists():
        console.print(f"  ✅ Configuration found: {config_path}")
    else:
        console.print(f"  ❌ Configuration not found: {config_path}")
        console.print("     Run from the shield-cli root directory")

    # Check .env
    env_path = Path(".env")
    if env_path.exists():
        console.print(f"  ✅ Environment file found: {env_path}")
    else:
        example = Path(".env.example")
        if example.exists():
            shutil.copy(example, env_path)
            console.print("  📋 Created .env from .env.example — edit with your API keys")
        else:
            console.print("  ⚠️  No .env file — set API keys via environment variables")

    # Check tools
    console.print("\n[bold cyan]🛠️  Checking installed tools...[/bold cyan]\n")
    tools = [
        "nmap", "masscan", "httpx", "subfinder", "amass", "nuclei",
        "nikto", "sqlmap", "whatweb", "wafw00f", "wpscan", "testssl",
        "sslyze", "gobuster", "ffuf", "arjun", "gitleaks", "dnsrecon",
    ]

    available = 0
    for tool in tools:
        if shutil.which(tool):
            console.print(f"  ✅ {tool}")
            available += 1
        else:
            console.print(f"  ❌ {tool} [dim](not installed)[/dim]")

    console.print(
        f"\n  {available}/{len(tools)} tools available. "
        f"Shield works with any subset — AI adapts accordingly."
    )

    console.print(Panel(
        "[green]Shield initialized successfully![/green]\n\n"
        "Next steps:\n"
        "  1. Edit [bold].env[/bold] with your AI provider API key\n"
        "  2. Run [bold]python -m cli.main models[/bold] to verify\n"
        "  3. Run [bold]python -m cli.main workflow list[/bold] to see workflows",
        title="🔐 Shield Ready",
        border_style="green",
    ))
