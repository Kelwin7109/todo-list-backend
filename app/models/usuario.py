"""Entidade e regras próprias de usuário."""

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, validates

from app.core.datas import agora_utc
from app.core.exceptions import ValorInvalido
from app.core.security import HashDeSenha
from app.db.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(180), unique=True, index=True, nullable=False)
    _senha_hash: Mapped[str] = mapped_column("senha_hash", String(255), nullable=False)
    criado_em: Mapped[object] = mapped_column(DateTime(timezone=True), default=agora_utc, nullable=False)

    def __init__(self, *, nome: str, email: str) -> None:
        self.nome = nome
        self.email = self.normalizar_email(email)

    @staticmethod
    def normalizar_email(email: str) -> str:
        return email.strip().lower()

    def definir_senha(self, senha: str, hasher: HashDeSenha) -> None:
        self._senha_hash = hasher.gerar(senha)

    def senha_confere(self, senha: str, hasher: HashDeSenha) -> bool:
        return hasher.verificar(senha, self._senha_hash)

    @validates("nome")
    def validar_nome(self, _chave: str, nome: str) -> str:
        nome = nome.strip()
        if not nome:
            raise ValorInvalido("O nome não pode ser vazio.")
        return nome

    def __repr__(self) -> str:
        return f"Usuario(id={self.id!r}, nome={self.nome!r}, email={self.email!r})"
