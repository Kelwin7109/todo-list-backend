"""Configurações comuns dos contratos JSON."""

from datetime import datetime, timezone
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


def _garantir_utc(valor: datetime) -> datetime:
    if valor.tzinfo is None:
        return valor.replace(tzinfo=timezone.utc)
    return valor.astimezone(timezone.utc)


DataHoraUTC = Annotated[datetime, AfterValidator(_garantir_utc)]


class EsquemaDeEntrada(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class EsquemaDeSaida(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )
