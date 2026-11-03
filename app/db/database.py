"""Conexão e ciclo de sessões do banco."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import obter_configuracao


def _opcoes_do_engine(url: str) -> dict:
    if url.startswith("sqlite"):
        options: dict = {"connect_args": {"check_same_thread": False}}
        if url in {"sqlite://", "sqlite:///:memory:"}:
            options["poolclass"] = StaticPool
        return options
    return {"pool_pre_ping": True}


engine: Engine = create_engine(
    obter_configuracao().url_banco,
    **_opcoes_do_engine(obter_configuracao().url_banco),
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def criar_tabelas() -> None:
    import app.models  # noqa: F401  registra os modelos antes do create_all

    Base.metadata.create_all(bind=engine)


def obter_sessao() -> Generator:
    sessao = SessionLocal()
    try:
        yield sessao
    finally:
        sessao.close()
