"""Consultas de persistência de usuários."""

from sqlalchemy import select

from app.models.usuario import Usuario
from app.repositories.base import RepositorioBase


class UsuarioRepositorio(RepositorioBase[Usuario]):
    @property
    def modelo(self) -> type[Usuario]:
        return Usuario

    def buscar_por_email(self, email: str) -> Usuario | None:
        email_normalizado = Usuario.normalizar_email(email)
        return self.sessao.scalar(select(Usuario).where(Usuario.email == email_normalizado))

    def email_existe(self, email: str) -> bool:
        return self.buscar_por_email(email) is not None
