"""Acesso aos dados de tarefa: filtros, ordenação e paginação."""

from dataclasses import dataclass
from datetime import date

from sqlalchemy import case

from app.models.enums import (
    CampoOrdenacao,
    Ordem,
    PrioridadeTarefa,
    StatusTarefa,
)
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
    ordenar_por: CampoOrdenacao = CampoOrdenacao.CRIADO_EM
    ordem: Ordem = Ordem.DESC
    limite: int = 100
    deslocamento: int = 0


@dataclass(frozen=True)
class PaginaDeTarefas:
    """Devolve a fatia solicitada e o total que atende aos filtros."""

    tarefas: list[Tarefa]
    total: int


class TarefaRepositorio(RepositorioBase[Tarefa]):
    # Usa os pesos de prioridade, não a ordem alfabética dos textos.
    _ORDEM_POR_PRIORIDADE = case(
        PrioridadeTarefa.mapa_de_pesos(), value=Tarefa.prioridade, else_=99
    )

    @property
    def modelo(self) -> type[Tarefa]:
        return Tarefa

    def _coluna_de_ordenacao(self, campo: CampoOrdenacao):
        """Devolve a expressão correspondente ao campo de ordenação."""
        colunas = {
            CampoOrdenacao.CRIADO_EM: Tarefa.criado_em,
            CampoOrdenacao.PRAZO: Tarefa.prazo,
            CampoOrdenacao.PRIORIDADE: self._ORDEM_POR_PRIORIDADE,
        }
        return colunas[campo]

    def listar(self, filtro: FiltroDeTarefas) -> PaginaDeTarefas:
        """Filtra, conta, ordena e devolve uma página das tarefas do usuário."""
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
        total = consulta.order_by(None).count()
        coluna = self._coluna_de_ordenacao(filtro.ordenar_por)
        ordenacao = [coluna.desc() if filtro.ordem is Ordem.DESC else coluna.asc()]
        if filtro.ordenar_por is CampoOrdenacao.PRAZO:
            ordenacao.insert(0, case((Tarefa.prazo.is_(None), 1), else_=0))
        ordenacao.append(Tarefa.id.desc())
        tarefas = (
            consulta.order_by(*ordenacao)
            .offset(filtro.deslocamento)
            .limit(filtro.limite)
            .all()
        )
        return PaginaDeTarefas(tarefas=tarefas, total=total)

    def todas_do_usuario(self, usuario_id: int) -> list[Tarefa]:
        """Devolve todas as tarefas do usuário, sem filtro nem limite (para o resumo)."""
        return self.sessao.query(Tarefa).filter(
            Tarefa.usuario_id == usuario_id
        ).all()
