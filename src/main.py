"""
Main application entry point.
"""

import os
import sys
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from dotenv import load_dotenv

from .identity_collector import IdentityCollector
from .identity_analyzer import IdentityAnalyzer

# Load environment variables
load_dotenv()

app = typer.Typer(help="NHI Agent - Identity Management and Analysis Tool")
console = Console()


@app.command()
def collect(
    aws_profile: Optional[str] = typer.Option(None, "--aws-profile", help="AWS profile name"),
    aws_region: Optional[str] = typer.Option(None, "--aws-region", help="AWS region"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file for identities JSON"),
):
    """Collect identities from AWS MCP servers."""
    console.print("[bold blue]Collecting identities...[/bold blue]")

    # Use environment variables if not provided
    aws_profile = aws_profile or os.getenv("AWS_PROFILE")
    aws_region = aws_region or os.getenv("AWS_REGION")

    collector = IdentityCollector(
        aws_profile=aws_profile,
        aws_region=aws_region
    )
    
    try:
        identities = collector.collect_all_identities()
        
        # Display summary
        table = Table(title="Identity Collection Summary")
        table.add_column("Source", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("Count", style="green")
        
        aws = identities.get("aws", {})
        if aws.get("users"):
            table.add_row("AWS", "Users", str(len(aws["users"])))
        if aws.get("roles"):
            table.add_row("AWS", "Roles", str(len(aws["roles"])))
        if aws.get("groups"):
            table.add_row("AWS", "Groups", str(len(aws["groups"])))
        
        table.add_row("", "Total", str(identities.get("total_count", 0)), style="bold")
        console.print(table)
        
        # Save to file if requested
        if output:
            import json
            with open(output, "w") as f:
                json.dump(identities, f, indent=2)
            console.print(f"[green]Identities saved to {output}[/green]")
        else:
            # Save to default location
            default_output = "identities.json"
            import json
            with open(default_output, "w") as f:
                json.dump(identities, f, indent=2)
            console.print(f"[green]Identities saved to {default_output}[/green]")
        
    finally:
        collector.close()


@app.command()
def ask(
    question: str = typer.Argument(..., help="Question to ask about identities"),
    identities_file: str = typer.Option("identities.json", "--file", "-f", help="Identities JSON file"),
    model: str = typer.Option("gpt-4o-mini", "--model", help="OpenAI model to use"),
):
    """Ask a question about collected identities."""
    import json
    
    console.print(f"[bold blue]Loading identities from {identities_file}...[/bold blue]")
    
    try:
        with open(identities_file, "r") as f:
            identities = json.load(f)
    except FileNotFoundError:
        console.print(f"[red]Error: File {identities_file} not found. Please collect identities first.[/red]")
        raise typer.Exit(1)
    except json.JSONDecodeError:
        console.print(f"[red]Error: Invalid JSON in {identities_file}[/red]")
        raise typer.Exit(1)
    
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        console.print("[red]Error: OPENAI_API_KEY environment variable not set[/red]")
        raise typer.Exit(1)
    
    analyzer = IdentityAnalyzer(openai_api_key=openai_api_key)
    analyzer.load_identities(identities)
    
    console.print(f"[bold blue]Analyzing question: {question}[/bold blue]")
    answer = analyzer.ask_question(question, model=model)
    
    console.print(Panel(answer, title="Answer", border_style="green"))


@app.command()
def analyze(
    identities_file: str = typer.Option("identities.json", "--file", "-f", help="Identities JSON file"),
    model: str = typer.Option("gpt-4o-mini", "--model", help="OpenAI model to use"),
):
    """Run comprehensive analysis on collected identities."""
    import json
    
    console.print(f"[bold blue]Loading identities from {identities_file}...[/bold blue]")
    
    try:
        with open(identities_file, "r") as f:
            identities = json.load(f)
    except FileNotFoundError:
        console.print(f"[red]Error: File {identities_file} not found. Please collect identities first.[/red]")
        raise typer.Exit(1)
    
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        console.print("[red]Error: OPENAI_API_KEY environment variable not set[/red]")
        raise typer.Exit(1)
    
    analyzer = IdentityAnalyzer(openai_api_key=openai_api_key)
    analyzer.load_identities(identities)
    
    # Generate summary
    console.print("[bold blue]Generating summary...[/bold blue]")
    summary = analyzer.summarize_identities()
    console.print(Panel(summary, title="Identity Summary", border_style="blue"))
    
    # Analyze security concerns
    console.print("\n[bold blue]Analyzing security concerns...[/bold blue]")
    security = analyzer.analyze_security_concerns()
    console.print(Panel(security, title="Security Analysis", border_style="yellow"))


@app.command()
def interactive(
    identities_file: str = typer.Option("identities.json", "--file", "-f", help="Identities JSON file"),
    model: str = typer.Option("gpt-4o-mini", "--model", help="OpenAI model to use"),
):
    """Interactive Q&A session about identities."""
    import json
    
    console.print(f"[bold blue]Loading identities from {identities_file}...[/bold blue]")
    
    try:
        with open(identities_file, "r") as f:
            identities = json.load(f)
    except FileNotFoundError:
        console.print(f"[red]Error: File {identities_file} not found. Please collect identities first.[/red]")
        raise typer.Exit(1)
    
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        console.print("[red]Error: OPENAI_API_KEY environment variable not set[/red]")
        raise typer.Exit(1)
    
    analyzer = IdentityAnalyzer(openai_api_key=openai_api_key)
    analyzer.load_identities(identities)
    
    console.print("[bold green]Interactive Q&A Mode[/bold green]")
    console.print("Enter questions about the identities. Type 'exit' or 'quit' to exit.\n")
    
    while True:
        question = Prompt.ask("[bold cyan]Question[/bold cyan]")
        
        if question.lower() in ["exit", "quit", "q"]:
            console.print("[yellow]Goodbye![/yellow]")
            break
        
        if not question.strip():
            continue
        
        console.print("[dim]Analyzing...[/dim]")
        answer = analyzer.ask_question(question, model=model)
        console.print(Panel(answer, title="Answer", border_style="green"))
        console.print()  # Blank line


if __name__ == "__main__":
    app()





