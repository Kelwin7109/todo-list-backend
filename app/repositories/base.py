"""Operações comuns de persistência."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from sqlalchemy.orm import Session

Entidade = TypeVar("Entidade")


class RepositorioBase(ABC, Generic[Entidade]):
    def __init__(self, sessao: Session) -> None:
        self.sessao = sessao

    @property
    @abstractmethod
    def modelo(self) -> type[Entidade]:
        """Modelo administrado pelo repositório."""

    def buscar_por_id(self, entidade_id: int) -> Entidade | None:
        return self.sessao.get(self.modelo, entidade_id)

    def salvar(self, entidade: Entidade) -> Entidade:
        self.sessao.add(entidade)
        self.sessao.commit()
        self.sessao.refresh(entidade)
        return entidade

    def remover(self, entidade: Entidade) -> None:
        self.sessao.delete(entidade)
        self.sessao.commit()
