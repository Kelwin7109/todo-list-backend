"""Formato da resposta do endpoint de login."""

from pydantic import BaseModel, EmailStr

from app.schemas.base import EsquemaDeEntrada


class CredenciaisLogin(EsquemaDeEntrada):
    """Dados JSON usados pelo endpoint explícito de login."""

    email: EmailStr
    senha: str


class TokenAcesso(BaseModel):
    access_token: str
    token_type: str = "bearer"
