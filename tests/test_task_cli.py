import pytest
import os
import tempfile
import sqlite3
from task_cli.database import (
    init_db, add_task, list_tasks, search_tasks,
    complete_task, delete_task, edit_task, get_stats
)

TEST_DB = os.path.join(tempfile.gettempdir(), "test_task_cli.db")


@pytest.fixture(autouse=True)
def use_test_db(monkeypatch):
    """Usa um banco de dados temporário para testes."""
    monkeypatch.setattr("task_cli.database.DB_PATH", TEST_DB)
    init_db()
    yield
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

# ── Testes de criação ─────────────────────────────────────────────

def test_add_task_returns_id():
    task_id = add_task("Estudar Python", "estudo", "alta", "2025-12-31")
    assert isinstance(task_id, int)
    assert task_id > 0


def test_add_multiple_tasks():
    add_task("Tarefa 1", "geral", "baixa", None)
    add_task("Tarefa 2", "trabalho", "alta", "2025-06-01")
    tasks = list_tasks()
    assert len(tasks) == 2


# ── Testes de listagem ────────────────────────────────────────────

def test_list_tasks_default_excludes_done():
    add_task("Pendente", "geral", "media", None)
    tid = add_task("Feita", "geral", "media", None)
    complete_task(tid)
    tasks = list_tasks()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Pendente"


def test_list_tasks_show_done():
    add_task("Pendente", "geral", "media", None)
    tid = add_task("Feita", "geral", "media", None)
    complete_task(tid)
    tasks = list_tasks(show_done=True)
    assert len(tasks) == 2


def test_list_tasks_filter_category():
    add_task("Estudar", "estudo", "alta", None)
    add_task("Reunião", "trabalho", "media", None)
    tasks = list_tasks(category="estudo")
    assert len(tasks) == 1
    assert tasks[0]["category"] == "estudo"


def test_list_tasks_filter_priority():
    add_task("Urgente", "geral", "alta", None)
    add_task("Normal", "geral", "media", None)
    tasks = list_tasks(priority="alta")
    assert len(tasks) == 1
    assert tasks[0]["priority"] == "alta"


def test_list_tasks_ordered_by_priority():
    add_task("Baixa", "geral", "baixa", None)
    add_task("Alta", "geral", "alta", None)
    add_task("Media", "geral", "media", None)
    tasks = list_tasks()
    assert tasks[0]["priority"] == "alta"
    assert tasks[1]["priority"] == "media"
    assert tasks[2]["priority"] == "baixa"


# ── Testes de busca ───────────────────────────────────────────────

def test_search_tasks_found():
    add_task("Estudar FastAPI", "estudo", "alta", None)
    add_task("Fazer academia", "saude", "media", None)
    results = search_tasks("FastAPI")
    assert len(results) == 1
    assert "FastAPI" in results[0]["title"]


def test_search_tasks_not_found():
    add_task("Tarefa qualquer", "geral", "baixa", None)
    results = search_tasks("xyzabc")
    assert len(results) == 0


def test_search_tasks_case_insensitive():
    add_task("Estudar Python", "estudo", "alta", None)
    results = search_tasks("python")
    assert len(results) == 1


# ── Testes de conclusão ───────────────────────────────────────────

def test_complete_task():
    tid = add_task("Tarefa", "geral", "media", None)
    result = complete_task(tid)
    assert result is True
    tasks = list_tasks(show_done=True)
    done = [t for t in tasks if t["id"] == tid]
    assert done[0]["done"] is True


def test_complete_task_not_found():
    result = complete_task(9999)
    assert result is False


def test_complete_task_already_done():
    tid = add_task("Tarefa", "geral", "media", None)
    complete_task(tid)
    result = complete_task(tid)
    assert result is False


# ── Testes de exclusão ────────────────────────────────────────────

def test_delete_task():
    tid = add_task("Deletar isso", "geral", "baixa", None)
    result = delete_task(tid)
    assert result is True
    tasks = list_tasks(show_done=True)
    assert all(t["id"] != tid for t in tasks)


def test_delete_task_not_found():
    result = delete_task(9999)
    assert result is False


# ── Testes de edição ──────────────────────────────────────────────

def test_edit_task_title():
    tid = add_task("Título antigo", "geral", "media", None)
    result = edit_task(tid, title="Título novo", category=None, priority=None, due_date=None)
    assert result is True
    tasks = list_tasks()
    assert tasks[0]["title"] == "Título novo"


def test_edit_task_priority():
    tid = add_task("Tarefa", "geral", "baixa", None)
    edit_task(tid, title=None, category=None, priority="alta", due_date=None)
    tasks = list_tasks()
    assert tasks[0]["priority"] == "alta"


def test_edit_task_not_found():
    result = edit_task(9999, title="X", category=None, priority=None, due_date=None)
    assert result is False


def test_edit_task_no_fields():
    tid = add_task("Tarefa", "geral", "media", None)
    result = edit_task(tid, title=None, category=None, priority=None, due_date=None)
    assert result is False


# ── Testes de estatísticas ────────────────────────────────────────

def test_stats_empty():
    stats = get_stats()
    assert stats["total"] == 0
    assert stats["done"] == 0
    assert stats["pending"] == 0


def test_stats_with_tasks():
    add_task("T1", "trabalho", "alta", None)
    add_task("T2", "estudo", "media", None)
    tid = add_task("T3", "trabalho", "baixa", None)
    complete_task(tid)
    stats = get_stats()
    assert stats["total"] == 3
    assert stats["done"] == 1
    assert stats["pending"] == 2
    assert stats["by_category"]["trabalho"] == 1
    assert stats["by_category"]["estudo"] == 1
