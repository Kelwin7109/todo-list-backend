"""Enumerações do domínio.

Os valores válidos de status e prioridade ficam em um único lugar para evitar
textos duplicados nas camadas. Herdar de `str` permite usar cada membro como
texto ao persistir no banco e serializar no JSON.
"""

from enum import Enum


class StatusTarefa(str, Enum):
    """Situação em que uma tarefa pode estar."""

    PENDENTE = "pendente"
    CONCLUIDA = "concluida"


class PrioridadeTarefa(str, Enum):
    """Nível de prioridade de uma tarefa, da menor para a maior."""

    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"
    URGENTE = "urgente"

    @property
    def peso(self) -> int:
        """Posição na ordenação por prioridade; zero é a mais urgente."""
        return _PESOS[self]

    @classmethod
    def mapa_de_pesos(cls) -> dict[str, int]:
        """Mapa valor → peso, no formato consumido pela ordenação SQL."""
        return {prioridade.value: prioridade.peso for prioridade in cls}


_PESOS = {
    PrioridadeTarefa.URGENTE: 0,
    PrioridadeTarefa.ALTA: 1,
    PrioridadeTarefa.MEDIA: 2,
    PrioridadeTarefa.BAIXA: 3,
}
