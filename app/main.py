"""Ponto de entrada: cria o app, registra as rotas e traduz erros em HTTP."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.routers import tasks, usuarios
from app.core.config import obter_configuracao
from app.core.exceptions import (
    EmailJaCadastrado,
    ErroDeDominio,
    NaoAutenticado,
    RegraDeNegocioViolada,
    RecursoNaoEncontrado,
    UsuarioNaoEncontrado,
    ValorInvalido,
)
from app.db.database import criar_tabelas


# Cada família de erro de domínio corresponde a um código HTTP. A ordem
# importa: um erro mais específico que herda de ErroDeDominio fica acima dele.
STATUS_POR_ERRO: tuple[tuple[type[ErroDeDominio], int], ...] = (
    (NaoAutenticado, 401),
    (UsuarioNaoEncontrado, 404),
    (RecursoNaoEncontrado, 404),
    (EmailJaCadastrado, 409),
    (ValorInvalido, 422),
    (RegraDeNegocioViolada, 422),
    (ErroDeDominio, 400),
)


@asynccontextmanager
async def ciclo_de_vida(app: FastAPI) -> AsyncIterator[None]:
    """Confere a configuração e prepara o banco na subida da aplicação.

    `segredo_jwt()` é chamado aqui de propósito: se JWT_SECRET estiver ausente,
    a API se recusa a subir com uma mensagem explicando o que fazer, em vez de
    subir e só falhar no primeiro login.
    """
    obter_configuracao().segredo_jwt()
    criar_tabelas()
    yield


app = FastAPI(
    title="Todo List API",
    description="Backend da Todo List – CURSO Desenvolvedor Full Stack (SENAC).",
    version="0.7.0",
    lifespan=ciclo_de_vida,
)


@app.exception_handler(ErroDeDominio)
async def tratar_erro_de_dominio(
    request: Request, excecao: ErroDeDominio
) -> JSONResponse:
    """Converte qualquer erro de domínio na resposta HTTP correspondente."""
    codigo = next(
        (codigo for tipo, codigo in STATUS_POR_ERRO if isinstance(excecao, tipo)),
        400,
    )
    # O padrao HTTP pede WWW-Authenticate nas respostas de nao autenticado.
    cabecalhos = {"WWW-Authenticate": "Bearer"} if codigo == 401 else None
    return JSONResponse(
        status_code=codigo,
        content={"detail": excecao.mensagem},
        headers=cabecalhos,
    )


def _mensagem_de_validacao(erro: dict[str, Any]) -> tuple[str, str]:
    """Traduz um erro do Pydantic em campo e mensagem em português."""
    campo = str(erro.get("loc", [""])[-1])
    tipo = erro.get("type", "")
    ctx = erro.get("ctx", {})
    valores_enum = ctx.get("expected", [])
    if isinstance(valores_enum, str):
        valores_enum = valores_enum.replace("'", "").replace(" or ", ", ")
    else:
        valores_enum = ", ".join(str(valor) for valor in valores_enum)
    mensagens = {
        "missing": f"O campo '{campo}' é obrigatório.",
        "string_too_short": (
            f"O campo '{campo}' precisa ter pelo menos "
            f"{ctx.get('min_length')} caracteres."
        ),
        "string_too_long": (
            f"O campo '{campo}' pode ter no máximo "
            f"{ctx.get('max_length')} caracteres."
        ),
        "string_pattern_mismatch": (
            f"O campo '{campo}' deve seguir o padrão {ctx.get('pattern')}."
        ),
        "enum": (
            f"Valor inválido para '{campo}'. Valores aceitos: "
            + valores_enum
        ),
        "date_parsing": f"Data inválida em '{campo}'. Use o formato AAAA-MM-DD.",
        "date_from_datetime_parsing": (
            f"Data inválida em '{campo}'. Use o formato AAAA-MM-DD."
        ),
        "int_parsing": f"O campo '{campo}' precisa ser um número inteiro.",
        "greater_than_equal": (
            f"O campo '{campo}' precisa ser no mínimo {ctx.get('ge')}."
        ),
        "less_than_equal": f"O campo '{campo}' pode ser no máximo {ctx.get('le')}.",
        "json_invalid": "O corpo da requisição não é um JSON válido.",
    }
    if tipo == "value_error":
        if campo == "email":
            return campo, "E-mail inválido."
        # Mensagens dos nossos próprios validadores já estão em português.
        return campo, str(erro.get("msg", ""))
    return campo, mensagens.get(tipo, f"Valor inválido para '{campo}'.")


@app.exception_handler(RequestValidationError)
async def tratar_erro_de_validacao(
    request: Request, excecao: RequestValidationError
) -> JSONResponse:
    """Responde 422 com detail sempre em texto, em português."""
    erros = [
        {"campo": campo, "mensagem": mensagem}
        for erro in excecao.errors()
        for campo, mensagem in [_mensagem_de_validacao(erro)]
    ]
    return JSONResponse(
        status_code=422,
        content={
            "detail": erros[0]["mensagem"] if erros else "Dados inválidos.",
            "erros": erros,
        },
    )


@app.get("/", tags=["Status"], summary="Verificar se a API está no ar")
def raiz() -> dict[str, str]:
    """Confirma que a API está acessível e informa a documentação."""
    return {"mensagem": "Todo List API no ar", "documentação": "/docs"}


app.include_router(usuarios.router)
app.include_router(tasks.router)
