"""Funções para trabalhar com datas."""

from datetime import datetime, timezone


def agora_utc() -> datetime:
    """Retorna o instante atual com fuso UTC para evitar datas ambíguas entre servidores."""
    return datetime.now(timezone.utc)
