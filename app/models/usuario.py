"""Entidade Usuario: dados e regras de quem usa o sistema.

As entidades não são apenas listas de colunas (o chamado "modelo anêmico"):
cada uma é responsável por manter o próprio estado válido. O e-mail é
normalizado aqui, e a senha só entra para definir_senha, que garante o hash.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship, validates

from app.core.datas import agora_utc
from app.core.exceptions import ValorInvalido
from app.core.security import HashDeSenha
from app.db.database import Base

if TYPE_CHECKING:
    # Importado apenas para anotações de tipo; evita importação circular.
    from app.models.tarefa import Tarefa


class Usuario(Base):
    """Usuário do sistema, dono de um conjunto de tarefas."""

    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(120), nullable=False)
    email = Column(String(180), nullable=False, unique=True, index=True)
    # O hash é privado: nenhuma camada da aplicação nem resposta JSON deve ler este valor.
    _senha_hash = Column("senha_hash", String(255), nullable=False)
    criado_em = Column(
        DateTime(timezone=True), nullable=False, default=agora_utc
    )
    tarefas = relationship(
        "Tarefa",
        back_populates="usuario",
        cascade="all, delete-orphan",
    )

    def __init__(self, *, nome: str, email: str) -> None:
        """Cria um usuário com o e-mail sem espaços e em letras minúsculas."""
        self.nome = nome
        self.email = self.normalizar_email(email)

    @staticmethod
    def normalizar_email(email: str) -> str:
        """Padroniza o e-mail antes de gravar ou comparar."""
        return email.strip().lower()

    def definir_senha(self, senha: str, hasher: HashDeSenha) -> None:
        """Grava a senha em forma de hash, nunca a senha original."""
        self._senha_hash = hasher.gerar(senha)

    def senha_confere(self, senha: str, hasher: HashDeSenha) -> bool:
        """Informa se a senha apresentada corresponde à cadastrada."""
        return hasher.verificar(senha, self._senha_hash)

    @validates("nome")
    def validar_nome(self, _campo: str, valor: str) -> str:
        if not valor or not valor.strip():
            raise ValorInvalido("O nome do usuário não pode ficar vazio.")
        return valor.strip()

    def __repr__(self) -> str:
        return f"Usuario(id={self.id!r} email={self.email!r})"
