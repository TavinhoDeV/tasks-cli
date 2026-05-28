#  Task CLI — Gerenciador de Tarefas por Linha de Comando

Ferramenta CLI desenvolvida em **Python + Typer + Rich** para gerenciar tarefas diretamente pelo terminal. Suporta prioridades, prazos, categorias, busca e estatísticas, com persistência em **SQLite**.

---

##  Funcionalidades

-  Adicionar tarefas com título, categoria, prioridade e prazo
-  Listar tarefas com filtros por categoria e prioridade
-  Marcar tarefas como concluídas
-  Editar qualquer campo de uma tarefa existente
-  Buscar tarefas por palavra-chave
-  Deletar tarefas com confirmação
-  Ver estatísticas: pendentes, concluídas, atrasadas e por categoria
-  Interface colorida e tabelas formatadas com Rich

---

##  Tecnologias

| Tecnologia | Uso |
|---|---|
| [Typer](https://typer.tiangolo.com/) | Framework para CLIs modernas em Python |
| [Rich](https://rich.readthedocs.io/) | Interface colorida e tabelas no terminal |
| [SQLite](https://www.sqlite.org/) | Banco de dados local para persistência |
| [Pytest](https://pytest.org/) | Testes automatizados |

---

##  Instalação

```bash
git clone https://github.com/seu-usuario/task-cli.git
cd task-cli

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
pip install -e .
```

Após instalar, o comando `task` fica disponível globalmente no terminal.

---

##  Uso

```bash
# Ver tarefas pendentes
task

# Adicionar tarefa
task add "Estudar FastAPI" --cat estudo --pri alta --due 2024-12-31

# Listar com filtros
task list --cat trabalho --pri alta
task list --all   # inclui concluídas

# Marcar como feita
task done 1

# Editar tarefa
task edit 1 --title "Novo título" --pri baixa

# Buscar
task search "Python"

# Deletar
task delete 2

# Estatísticas
task stats
```

---

##  Prioridades e Categorias

**Prioridades:** `alta` `media` `baixa`

**Categorias:** `geral` `trabalho` `estudo` `pessoal` `saude`

---

##  Testes

```bash
pytest tests/ -v
```

---

##  Estrutura do Projeto

```
task-cli/
├── task_cli/
│   ├── cli.py         # Comandos da CLI (Typer)
│   ├── database.py    # Operações SQLite
│   ├── display.py     # Formatação com Rich
│   └── __init__.py
├── tests/
│   └── test_task_cli.py  # 20+ testes automatizados
├── setup.py
├── requirements.txt
└── README.md
```

---

##  Licença

MIT License
