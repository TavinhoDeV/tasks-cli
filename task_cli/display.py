from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich import box

console = Console()

PRIORITY_STYLE = {
    "alta":  ("🔴", "bold red"),
    "media": ("🟡", "yellow"),
    "baixa": ("🟢", "green"),
}

VALID_PRIORITIES = ["alta", "media", "baixa"]
VALID_CATEGORIES = ["geral", "trabalho", "estudo", "pessoal", "saude"]


def format_due_date(due_date: str | None) -> Text:
    if not due_date:
        return Text("—", style="dim")
    try:
        d = datetime.strptime(due_date, "%Y-%m-%d")
        today = datetime.today()
        diff = (d - today).days
        label = d.strftime("%d/%m/%Y")
        if diff < 0:
            return Text(f"{label} ⚠ atrasada", style="bold red")
        elif diff == 0:
            return Text(f"{label} (hoje)", style="bold yellow")
        elif diff <= 2:
            return Text(f"{label} ({diff}d)", style="yellow")
        return Text(label, style="cyan")
    except ValueError:
        return Text(due_date, style="dim")


def print_tasks(tasks: list[dict], title: str = "Tarefas"):
    if not tasks:
        console.print(f"\n[dim]Nenhuma tarefa encontrada.[/dim]\n")
        return

    table = Table(
        title=f"\n📋 {title}",
        box=box.ROUNDED,
        show_lines=True,
        header_style="bold cyan",
    )
    table.add_column("ID", style="dim", width=4, justify="right")
    table.add_column("Título", min_width=25)
    table.add_column("Categoria", width=12)
    table.add_column("Prioridade", width=12)
    table.add_column("Prazo", width=18)
    table.add_column("Status", width=10)

    for t in tasks:
        icon, pstyle = PRIORITY_STYLE.get(t["priority"], ("⚪", "white"))
        status = Text("✅ Feita", style="dim green") if t["done"] else Text("⏳ Pendente", style="blue")
        title_text = Text(t["title"], style="dim strike" if t["done"] else "white")

        table.add_row(
            str(t["id"]),
            title_text,
            f"[bold]{t['category']}[/bold]",
            Text(f"{icon} {t['priority']}", style=pstyle),
            format_due_date(t["due_date"]),
            status,
        )

    console.print(table)


def print_stats(stats: dict):
    console.print("\n[bold cyan]📊 Estatísticas[/bold cyan]\n")
    console.print(f"  Total de tarefas : [bold]{stats['total']}[/bold]")
    console.print(f"  Pendentes        : [bold yellow]{stats['pending']}[/bold yellow]")
    console.print(f"  Concluídas       : [bold green]{stats['done']}[/bold green]")
    console.print(f"  Atrasadas        : [bold red]{stats['overdue']}[/bold red]")

    if stats["by_category"]:
        console.print("\n  [bold]Por categoria:[/bold]")
        for cat, count in stats["by_category"].items():
            console.print(f"    • {cat}: {count}")
    console.print()


def print_success(msg: str):
    console.print(f"\n[bold green]✅ {msg}[/bold green]\n")


def print_error(msg: str):
    console.print(f"\n[bold red]❌ {msg}[/bold red]\n")


def print_warning(msg: str):
    console.print(f"\n[bold yellow]⚠ {msg}[/bold yellow]\n")
