"""Operações de negócio de tarefas."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

from app.core.exceptions import AcessoNaoAutorizado, TarefaNaoEncontrada
from app.models.enums import PrioridadeTarefa
from app.models.tarefa import Tarefa
from app.repositories.tarefa import TarefaRepositorio


# Marca campos que não foram enviados no PATCH, distinguindo-os de valores como None.
NAO_INFORMADO: Any = object()


@dataclass(frozen=True)
class AlteracoesDaTarefa:
    """Campos que um PATCH pediu para alterar."""

    titulo: Any = NAO_INFORMADO
    prioridade: Any = NAO_INFORMADO
    prazo: Any = NAO_INFORMADO

    def informado(self, campo: str) -> bool:
        """Informa se o cliente enviou este campo."""
        return getattr(self, campo) is not NAO_INFORMADO


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

    def buscar(self, tarefa_id: int, usuario_id: int) -> Tarefa:
        """Devolve uma tarefa do usuário autenticado.

        Raises:
            TarefaNaoEncontrada: quando a tarefa não existe.
            AcessoNaoAutorizado: quando a tarefa pertence a outro usuário.
        """
        tarefa = self._repositorio.buscar_por_id(tarefa_id)
        if tarefa is None:
            raise TarefaNaoEncontrada()
        if not tarefa.pertence_a(usuario_id):
            raise AcessoNaoAutorizado()
        return tarefa

    def atualizar(
        self, tarefa_id: int, usuario_id: int, alteracoes: AlteracoesDaTarefa
    ) -> Tarefa:
        """Aplica as alterações informadas e devolve a tarefa.

        Raises:
            TarefaNaoEncontrada: quando a tarefa não existe.
            AcessoNaoAutorizado: quando a tarefa pertence a outro usuário.
        """
        tarefa = self.buscar(tarefa_id, usuario_id)
        if alteracoes.informado("titulo"):
            tarefa.titulo = alteracoes.titulo
        if alteracoes.informado("prioridade"):
            tarefa.prioridade = alteracoes.prioridade
        if alteracoes.informado("prazo"):
            tarefa.prazo = alteracoes.prazo
        return self._repositorio.salvar(tarefa)

    def remover(self, tarefa_id: int, usuario_id: int) -> None:
        """Remove a tarefa do usuário autenticado.

        Raises:
            TarefaNaoEncontrada: quando a tarefa não existe.
            AcessoNaoAutorizado: quando a tarefa pertence a outro usuário.
        """
        self._repositorio.remover(self.buscar(tarefa_id, usuario_id))
