"""Acesso aos dados de tarefa: filtros e busca."""

from dataclasses import dataclass
from datetime import date

from app.models.enums import PrioridadeTarefa, StatusTarefa
from app.models.tarefa import Tarefa
from app.repositories.base import RepositorioBase


@dataclass(frozen=True)
class FiltroDeTarefas:
    """Agrupa critérios opcionais para manter estável a assinatura da listagem."""

    usuario_id: int
    status: StatusTarefa | None = None
    prioridade: PrioridadeTarefa | None = None
    prazo_ate: date | None = None
    busca: str | None = None


class TarefaRepositorio(RepositorioBase[Tarefa]):
    @property
    def modelo(self) -> type[Tarefa]:
        return Tarefa

    def listar(self, filtro: FiltroDeTarefas) -> list[Tarefa]:
        """Lista as tarefas do usuário com os filtros encadeados na consulta."""
        consulta = self.sessao.query(Tarefa).filter(
            Tarefa.usuario_id == filtro.usuario_id
        )
        if filtro.status is not None:
            consulta = consulta.filter(Tarefa.status == filtro.status.value)
        if filtro.prioridade is not None:
            consulta = consulta.filter(Tarefa.prioridade == filtro.prioridade.value)
        if filtro.prazo_ate is not None:
            consulta = consulta.filter(
                Tarefa.prazo.isnot(None), Tarefa.prazo <= filtro.prazo_ate
            )
        if filtro.busca:
            # icontains procura sem diferenciar maiúsculas; autoescape trata % e _ como texto.
            consulta = consulta.filter(
                Tarefa.titulo.icontains(filtro.busca, autoescape=True)
            )
        return consulta.order_by(Tarefa.criado_em.desc(), Tarefa.id.desc()).all()
