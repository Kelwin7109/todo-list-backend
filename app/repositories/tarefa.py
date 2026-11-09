"""Acesso a dados de tarefas."""

from app.models.tarefa import Tarefa
from app.repositories.base import RepositorioBase


class TarefaRepositorio(RepositorioBase[Tarefa]):
    @property
    def modelo(self) -> type[Tarefa]:
        return Tarefa

    def listar(self, usuario_id: int) -> list[Tarefa]:
        """Lista só as tarefas do usuário, filtrando o dono direto na consulta ao banco."""
        return (
            self.sessao.query(Tarefa)
            .filter(Tarefa.usuario_id == usuario_id)
            # Desempate pelo id: tarefas criadas no mesmo instante mantêm a ordem.
            .order_by(Tarefa.criado_em.desc(), Tarefa.id.desc())
            .all()
        )
