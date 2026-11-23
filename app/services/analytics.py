"""As quatro primeiras métricas repetem as da página do front; as três últimas são análises novas."""

import math
from dataclasses import dataclass
from datetime import date, datetime, timedelta

import pandas as pd

from app.models.enums import PrioridadeTarefa, StatusTarefa
from app.models.tarefa import Tarefa
from app.repositories.tarefa import TarefaRepositorio

DIAS_DA_SEMANA = ["seg", "ter", "qua", "qui", "sex", "sab", "dom"]
# No pandas, 0 = segunda.


def arredondar(valor: float) -> int:
    """Arredonda como Math.round do JavaScript, diferente do round() do Python."""
    return math.floor(valor + 0.5)


@dataclass(frozen=True)
class Analytics:
    total: int
    concluidas: int
    taxa_conclusao: int
    concluidas_na_janela: int
    concluidas_por_dia: list[dict]
    pendentes_por_prioridade: dict[PrioridadeTarefa, int]
    tempo_medio_conclusao_dias: float | None
    concluidas_por_dia_da_semana: dict[str, int]
    percentual_no_prazo: int | None


class AnalyticsServico:
    def __init__(self, tarefas: TarefaRepositorio) -> None:
        self._tarefas = tarefas

    def calcular(
        self, usuario_id: int, dias: int = 7, hoje: date | None = None
    ) -> Analytics:
        hoje = hoje or date.today()
        tabela = self._montar_tabela(self._tarefas.todas_do_usuario(usuario_id))
        concluida = tabela["status"] == StatusTarefa.CONCLUIDA.value
        concluidas = tabela[concluida]  # Somente as linhas concluídas.
        pendentes = tabela[~concluida]  # As demais linhas são pendentes.

        total = len(tabela)
        por_dia = self._concluidas_por_dia(concluidas, dias, hoje)
        return Analytics(
            total=total,
            concluidas=len(concluidas),
            taxa_conclusao=(
                arredondar(len(concluidas) / total * 100) if total else 0
            ),
            concluidas_na_janela=sum(item["quantidade"] for item in por_dia),
            concluidas_por_dia=por_dia,
            pendentes_por_prioridade=self._pendentes_por_prioridade(pendentes),
            tempo_medio_conclusao_dias=self._tempo_medio_conclusao(concluidas),
            concluidas_por_dia_da_semana=self._por_dia_da_semana(concluidas),
            percentual_no_prazo=self._percentual_no_prazo(concluidas),
        )

    # --- a tabela
    @staticmethod
    def _montar_tabela(tarefas: list[Tarefa]) -> pd.DataFrame:
        fuso_do_servidor = datetime.now().astimezone().tzinfo
        tabela = pd.DataFrame(
            {
                "status": [t.status.value for t in tarefas],
                "prioridade": [t.prioridade for t in tarefas],
                "prazo": [t.prazo for t in tarefas],
                "criado_em": [t.criado_em for t in tarefas],
                "concluido_em": [t.concluido_em for t in tarefas],
            }
        )
        for coluna in ("criado_em", "concluido_em"):
            tabela[coluna] = pd.to_datetime(
                tabela[coluna], utc=True
            ).dt.tz_convert(fuso_do_servidor)
        tabela["dia_conclusao"] = tabela["concluido_em"].dt.date
        return tabela

    # --- as métricas que o front já usa
    @staticmethod
    def _concluidas_por_dia(
        concluidas: pd.DataFrame, dias: int, hoje: date
    ) -> list[dict]:
        janela = [
            hoje - timedelta(days=n) for n in range(dias - 1, -1, -1)
        ]
        contagem = concluidas["dia_conclusao"].value_counts().reindex(
            janela, fill_value=0
        )
        return [
            {"dia": dia, "quantidade": int(qtd)}
            for dia, qtd in contagem.items()
        ]

    @staticmethod
    def _pendentes_por_prioridade(
        pendentes: pd.DataFrame,
    ) -> dict[PrioridadeTarefa, int]:
        ordem = [
            prioridade.value
            for prioridade in sorted(PrioridadeTarefa, key=lambda p: p.peso)
        ]
        contagem = pendentes["prioridade"].value_counts().reindex(
            ordem, fill_value=0
        )
        return {
            PrioridadeTarefa(prioridade): int(qtd)
            for prioridade, qtd in contagem.items()
        }

    # --- análises novas (pandas)
    @staticmethod
    def _tempo_medio_conclusao(
        concluidas: pd.DataFrame,
    ) -> float | None:
        """Subtrai as datas de criação e conclusão para calcular a duração média."""
        if concluidas.empty:
            return None
        duracao = concluidas["concluido_em"] - concluidas["criado_em"]
        return round(float((duracao.dt.total_seconds() / 86400).mean()), 1)

    @staticmethod
    def _por_dia_da_semana(concluidas: pd.DataFrame) -> dict[str, int]:
        contagem = concluidas["concluido_em"].dt.dayofweek.value_counts().reindex(
            range(7), fill_value=0
        )
        return {
            DIAS_DA_SEMANA[numero]: int(qtd)
            for numero, qtd in contagem.items()
        }

    @staticmethod
    def _percentual_no_prazo(concluidas: pd.DataFrame) -> int | None:
        """Considera no prazo a conclusão feita até o próprio dia do prazo."""
        com_prazo = concluidas[concluidas["prazo"].notna()]
        if com_prazo.empty:
            return None
        no_prazo = com_prazo["dia_conclusao"] <= com_prazo["prazo"]
        # A média de True/False é a proporção de True.
        return arredondar(no_prazo.mean() * 100)
