"""Configuracao da aplicacao, lida do ambiente (arquivo .env)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


class ConfiguracaoInvalida(RuntimeError):
    """Falta (ou esta errada) uma variavel de ambiente obrigatoria."""


@dataclass(frozen=True)
class Configuracao:
    """Parametros de execucao da aplicacao."""

    database_url: str = ""
    jwt_secret: str = ""
    jwt_expira_minutos: int = 120

    @classmethod
    def do_ambiente(cls) -> Configuracao:
        """Monta a configuracao a partir das variaveis de ambiente."""
        return cls(
            database_url=os.getenv("DATABASE_URL", "").strip(),
            jwt_secret=os.getenv("JWT_SECRET", "").strip(),
            jwt_expira_minutos=int(os.getenv("JWT_EXPIRA_MINUTOS", "120")),
        )

    @property
    def url_banco(self) -> str:
        """Utiliza a variavel de ambiente DATABASE_URL, ou explica como cria-la."""
        if not self.database_url:
            raise ConfiguracaoInvalida(
                "DATABASE_URL esta vazia. Copie o arquivo .env.example para .env e "
                "deixe ativo um dos dois caminhos: SQLite (local) ou PostgreSQL no Render."
            )
        return self.database_url

    def segredo_jwt(self) -> str:
        """Devolve a variavel de ambiente JWT_SECRET, ou explica como cria-la."""
        if len(self.jwt_secret) < 32:
            raise ConfiguracaoInvalida(
                "JWT_SECRET esta ausente ou curto demais (minimo 32 caracteres).\n"
                'Gere um com: python -c "import secrets; print(secrets.token_hex(32))"\n'
                "e coloque no arquivo .env."
            )
        return self.jwt_secret


@lru_cache
def obter_configuracao() -> Configuracao:
    """Devolve a configuracao da aplicacao, carregada uma unica vez."""
    return Configuracao.do_ambiente()
