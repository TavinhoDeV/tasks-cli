import typer
from typing import Optional
from datetime import datetime
from task_cli.database import (
    init_db, add_task, list_tasks, search_tasks,
    complete_task, delete_task, edit_task, get_stats
)
from task_cli.display import (
    console, print_tasks, print_stats,
    print_success, print_error, print_warning,
    VALID_PRIORITIES, VALID_CATEGORIES
)

app = typer.Typer(
    name="task",
    help="📝 Gerenciador de tarefas por linha de comando.",
    add_completion=False,
)


def _validate_priority(priority: str) -> str:
    p = priority.lower()
    if p not in VALID_PRIORITIES:
        print_error(f"Prioridade inválida. Use: {', '.join(VALID_PRIORITIES)}")
        raise typer.Exit(1)
    return p


def _validate_date(date_str: str | None) -> str | None:
    if not date_str:
        return None
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError:
        print_error("Formato de data inválido. Use AAAA-MM-DD (ex: 2024-12-31)")
        raise typer.Exit(1)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    init_db()
    if ctx.invoked_subcommand is None:
        tasks = list_tasks()
        print_tasks(tasks, "Tarefas Pendentes")


@app.command("add", help="➕ Adicionar uma nova tarefa.")
def cmd_add(
    title: str = typer.Argument(..., help="Título da tarefa"),
    category: str = typer.Option("geral", "--cat", "-c", help=f"Categoria: {', '.join(VALID_CATEGORIES)}"),
    priority: str = typer.Option("media", "--pri", "-p", help="Prioridade: alta, media, baixa"),
    due_date: Optional[str] = typer.Option(None, "--due", "-d", help="Prazo (AAAA-MM-DD)"),
):
    init_db()
    priority = _validate_priority(priority)
    due_date = _validate_date(due_date)
    task_id = add_task(title, category.lower(), priority, due_date)
    print_success(f"Tarefa #{task_id} adicionada: \"{title}\"")


@app.command("list", help="📋 Listar tarefas.")
def cmd_list(
    category: Optional[str] = typer.Option(None, "--cat", "-c", help="Filtrar por categoria"),
    priority: Optional[str] = typer.Option(None, "--pri", "-p", help="Filtrar por prioridade"),
    all_tasks: bool = typer.Option(False, "--all", "-a", help="Incluir tarefas concluídas"),
):
    init_db()
    tasks = list_tasks(category=category, priority=priority, show_done=all_tasks)
    title = "Todas as Tarefas" if all_tasks else "Tarefas Pendentes"
    if category:
        title += f" — {category}"
    if priority:
        title += f" [{priority}]"
    print_tasks(tasks, title)


@app.command("done", help="✅ Marcar tarefa como concluída.")
def cmd_done(
    task_id: int = typer.Argument(..., help="ID da tarefa"),
):
    init_db()
    if complete_task(task_id):
        print_success(f"Tarefa #{task_id} marcada como concluída!")
    else:
        print_error(f"Tarefa #{task_id} não encontrada ou já concluída.")


@app.command("delete", help="🗑️  Deletar uma tarefa.")
def cmd_delete(
    task_id: int = typer.Argument(..., help="ID da tarefa"),
    force: bool = typer.Option(False, "--force", "-f", help="Deletar sem confirmação"),
):
    init_db()
    if not force:
        confirm = typer.confirm(f"Tem certeza que deseja deletar a tarefa #{task_id}?")
        if not confirm:
            print_warning("Operação cancelada.")
            raise typer.Exit()
    if delete_task(task_id):
        print_success(f"Tarefa #{task_id} deletada.")
    else:
        print_error(f"Tarefa #{task_id} não encontrada.")


@app.command("edit", help="✏️  Editar uma tarefa existente.")
def cmd_edit(
    task_id: int = typer.Argument(..., help="ID da tarefa"),
    title: Optional[str] = typer.Option(None, "--title", "-t", help="Novo título"),
    category: Optional[str] = typer.Option(None, "--cat", "-c", help="Nova categoria"),
    priority: Optional[str] = typer.Option(None, "--pri", "-p", help="Nova prioridade"),
    due_date: Optional[str] = typer.Option(None, "--due", "-d", help="Novo prazo (AAAA-MM-DD)"),
):
    init_db()
    if priority:
        priority = _validate_priority(priority)
    if due_date:
        due_date = _validate_date(due_date)
    if edit_task(task_id, title, category, priority, due_date):
        print_success(f"Tarefa #{task_id} atualizada.")
    else:
        print_error(f"Tarefa #{task_id} não encontrada ou nenhum campo informado.")


@app.command("search", help="🔍 Buscar tarefas por palavra-chave.")
def cmd_search(
    term: str = typer.Argument(..., help="Termo de busca"),
):
    init_db()
    tasks = search_tasks(term)
    print_tasks(tasks, f"Resultados para \"{term}\"")


@app.command("stats", help="📊 Ver estatísticas das tarefas.")
def cmd_stats():
    init_db()
    stats = get_stats()
    print_stats(stats)


if __name__ == "__main__":
    app()
