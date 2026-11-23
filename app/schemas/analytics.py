"""Os quatro primeiros campos repetem os da AnalyticsPage."""

from datetime import date

from pydantic import Field

from app.models.enums import PrioridadeTarefa
from app.schemas.base import EsquemaDeSaida


class ConcluidasNoDia(EsquemaDeSaida):
    dia: date
    quantidade: int


class AnalyticsOut(EsquemaDeSaida):
    total: int
    concluidas: int
    taxa_conclusao: int = Field(description="Percentual de tarefas concluídas.")
    concluidas_na_janela: int = Field(
        description="Quantidade de tarefas concluídas na janela de dias."
    )
    concluidas_por_dia: list[ConcluidasNoDia]
    pendentes_por_prioridade: dict[PrioridadeTarefa, int]
    tempo_medio_conclusao_dias: float | None = Field(
        description="Média de dias entre criação e conclusão; null se não houver tarefas concluídas."
    )
    concluidas_por_dia_da_semana: dict[str, int] = Field(
        description="Conclusões por dia da semana no histórico inteiro."
    )
    percentual_no_prazo: int | None = Field(
        description="Percentual no prazo; null se não houver tarefa concluída com prazo."
    )
