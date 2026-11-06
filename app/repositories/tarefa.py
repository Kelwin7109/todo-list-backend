"""Acesso a dados de tarefas."""

from app.models.tarefa import Tarefa
from app.repositories.base import RepositorioBase


class TarefaRepositorio(RepositorioBase[Tarefa]):
    @property
    def modelo(self) -> type[Tarefa]:
        return Tarefa
