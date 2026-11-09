"""Operações de negócio de tarefas."""

from __future__ import annotations

from datetime import date

from app.models.enums import PrioridadeTarefa
from app.models.tarefa import Tarefa
from app.repositories.tarefa import TarefaRepositorio


class TarefaServico:
    def __init__(self, repositorio: TarefaRepositorio) -> None:
        self._repositorio = repositorio

    def criar(
        self, titulo: str, prioridade: PrioridadeTarefa, prazo: date, usuario_id: int
    ) -> Tarefa:
        tarefa = Tarefa(
            titulo=titulo,
            prioridade=prioridade,
            prazo=prazo,
            usuario_id=usuario_id,
        )
        return self._repositorio.salvar(tarefa)

    def listar(self, usuario_id: int) -> list[Tarefa]:
        """Lista as tarefas do usuário autenticado via repositório."""
        return self._repositorio.listar(usuario_id)
