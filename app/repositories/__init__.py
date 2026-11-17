"""Repositórios isolam as consultas ao banco de dados.

Antes, as consultas ficavam dentro das rotas, misturando HTTP, regra e SQL;
com os repositórios, serviço não sabe SQL e rota não sabe banco.
"""

from app.repositories.base import RepositorioBase
from app.repositories.tarefa import (
    FiltroDeTarefas,
    PaginaDeTarefas,
    TarefaRepositorio,
)
from app.repositories.usuario import UsuarioRepositorio

__all__ = [
    "FiltroDeTarefas",
    "PaginaDeTarefas",
    "RepositorioBase",
    "TarefaRepositorio",
    "UsuarioRepositorio",
]
