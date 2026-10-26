from fastapi import FastAPI

app = FastAPI(
    title="Todo List API",
    description="Backend sistema todo list",
    version="0.0.1"
)
@app.get("/", tags=["Status"], summary="verifica se a API está online")
def raiz () -> dict[str, str]:
    return {"mensagem": "todo list API está online!", "documentação": "/docs"}