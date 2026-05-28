from setuptools import setup, find_packages

setup(
    name="task-cli",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "typer==0.12.3",
        "rich==13.7.1",
    ],
    entry_points={
        "console_scripts": [
            "task=task_cli.cli:app",
        ],
    },
    python_requires=">=3.10",
    author="Seu Nome",
    description="Gerenciador de tarefas por linha de comando com prioridade, prazo e categorias.",
)
