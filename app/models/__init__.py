"""Modelos de domínio: entidades do sistema, com seus dados e regras.

Cada entidade é responsável por manter o próprio estado válido: o Usuario
normaliza o próprio e-mail e só aceita a senha em forma de hash; a Tarefa
nasce sempre pendente e não deixa ninguém mudar o status de fora.
"""

# Importar as entidades aqui registra as tabelas no SQLAlchemy, permitindo que
# `criar_tabelas()` use `Base.metadata.create_all()`.
from app.models.tarefa import Tarefa
from app.models.usuario import Usuario

__all__ = ["Tarefa", "Usuario"]
