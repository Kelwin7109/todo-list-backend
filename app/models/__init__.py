"""Modelos de domínio: entidades do sistema, com dados e regras próprias.

Antes, as classes eram apenas listas de colunas (modelos anêmicos) e as regras
viviam nas rotas. Agora cada entidade mantém o próprio estado válido: o Usuario
normaliza o e-mail e protege a senha, e a Tarefa implementa suas operações.
A RN-03 está nos métodos concluir e reabrir, o único caminho para mudar o status.
"""

# Estes imports registram as duas tabelas (usuarios e tarefas) na metadata do SQLAlchemy.
from app.models.tarefa import Tarefa
from app.models.usuario import Usuario

__all__ = ["Tarefa", "Usuario"]
