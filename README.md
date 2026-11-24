# Todo List API

API REST para cadastro de usuários e gerenciamento de tarefas, construída no curso Desenvolvedor Full Stack do SENAC Minas Gerais.

## Projeto e arquitetura

A aplicação usa FastAPI para expor os endpoints. As rotas traduzem requisições HTTP, os serviços aplicam regras de negócio, os repositórios consultam o banco com SQLAlchemy, os modelos mantêm o estado válido das entidades e os schemas definem os contratos JSON. O serviço de Analytics transforma as tarefas do usuário em uma tabela pandas para calcular indicadores.

## Pré-requisitos e instalação

- Python 3.12.
- Git para clonar o projeto.

Na raiz do repositório, crie e ative o ambiente virtual e instale as dependências:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
Copy-Item .env.example .env
python -m pip install -r requirements.txt
```

Gere um segredo JWT com `python -c "import secrets; print(secrets.token_urlsafe(32))"` e substitua o valor de `JWT_SECRET` no `.env`. Inicie a API com:

```powershell
python -m uvicorn app.main:app --reload --reload-dir app
```

A documentação interativa fica em <http://127.0.0.1:8000/docs>.

## Banco de dados

### SQLite local

O `.env.example` já deixa ativo `DATABASE_URL=sqlite:///./todo_list.db`. A aplicação cria o arquivo e as tabelas na primeira inicialização.

### PostgreSQL no Render

No painel do banco Render, copie a **External Database URL**. No `.env`, comente a linha SQLite e configure `DATABASE_URL` usando o prefixo `postgresql+psycopg://` e o sufixo `?sslmode=require`, conforme o exemplo comentado no `.env.example`.

## Autenticação

Cadastre-se em `POST /usuarios` e faça login em `POST /usuarios/login` com `email` e `senha`. A resposta contém `accessToken`. Envie esse valor nas rotas protegidas pelo cabeçalho:

```text
Authorization: Bearer <accessToken>
```

No `/docs`, use **Authorize** e informe o token. O token expira conforme `JWT_EXPIRA_MINUTOS` (120 minutos por padrão); a API não oferece renovação automática.

## Endpoints

Rotas de usuário:

| Método | Endpoint | Uso | Autenticação |
| --- | --- | --- | --- |
| POST | `/usuarios` | Cadastrar usuário | Não |
| POST | `/usuarios/login` | Entrar e receber token | Não |
| GET | `/usuarios/me` | Consultar usuário logado | Sim |

Rotas de tarefas:

| Método | Endpoint | Uso | Autenticação |
| --- | --- | --- | --- |
| POST | `/tasks` | Criar tarefa para o usuário logado | Sim |
| GET | `/tasks` | Listar, filtrar, ordenar e paginar tarefas | Sim |
| GET | `/tasks/resumo` | Consultar números do Painel | Sim |
| GET | `/tasks/analytics` | Consultar métricas e insights | Sim |
| GET | `/tasks/{tarefa_id}` | Consultar tarefa | Sim |
| PATCH | `/tasks/{tarefa_id}` | Atualizar parcialmente uma tarefa | Sim |
| DELETE | `/tasks/{tarefa_id}` | Remover tarefa | Sim |

Também há `GET /` para conferir se a API está no ar. A listagem aceita `status`, `prioridade`, `prazoAte`, `busca`, `ordenarPor`, `ordem`, `limit` e `offset`; devolve o total sem paginação no cabeçalho `X-Total-Count`. A consulta do Analytics aceita `dias` entre 1 e 90, com padrão 7.

### Entrada e resposta de cada rota

| Rota | O que enviar | Sucesso | Erros relevantes |
| --- | --- | --- | --- |
| `GET /` | Nada | `200`: mensagem de status e caminho de `/docs` | — |
| `POST /usuarios` | JSON `nome`, `email`, `senha` | `201`: usuário criado (`id`, `nome`, `email`, `criadoEm`) | `409`: e-mail cadastrado; `422`: campos inválidos |
| `POST /usuarios/login` | JSON `email`, `senha` | `200`: `accessToken`, `tokenType`, `expiraEm`, `usuario` | `401`: credenciais inválidas; `422`: campos inválidos |
| `GET /usuarios/me` | Token Bearer | `200`: dados do usuário autenticado | `401`: token ausente, inválido ou expirado |
| `POST /tasks` | Token Bearer e JSON `titulo`; `prioridade` e `prazo` são opcionais | `201`: tarefa criada, inicialmente pendente | `401`: sem autenticação; `422`: campos inválidos |
| `GET /tasks` | Token Bearer e filtros opcionais descritos abaixo | `200`: lista de tarefas; `X-Total-Count` informa o total antes da paginação | `401`: sem autenticação; `422`: filtro inválido |
| `GET /tasks/resumo` | Token Bearer | `200`: `total`, `pendentes`, `concluidas`, `atrasadas` | `401`: sem autenticação |
| `GET /tasks/analytics` | Token Bearer e `dias` opcional (1 a 90; padrão 7) | `200`: métricas e insights do usuário autenticado | `401`: sem autenticação; `422`: `dias` fora do intervalo |
| `GET /tasks/{tarefa_id}` | Token Bearer e ID inteiro no caminho | `200`: tarefa encontrada | `401`: sem autenticação; `403`: tarefa de outro usuário; `404`: não encontrada; `422`: ID inválido |
| `PATCH /tasks/{tarefa_id}` | Token Bearer, ID e JSON parcial com `titulo`, `status`, `prioridade` e/ou `prazo` | `200`: tarefa atualizada | `401`: sem autenticação; `403`: tarefa de outro usuário; `404`: não encontrada; `422`: ID ou campos inválidos |
| `DELETE /tasks/{tarefa_id}` | Token Bearer e ID inteiro no caminho | `204`: tarefa removida, sem corpo de resposta | `401`: sem autenticação; `403`: tarefa de outro usuário; `404`: não encontrada; `422`: ID inválido |

Na listagem, `status` aceita `pendente` ou `concluida`; `prioridade` aceita `baixa`, `media`, `alta` ou `urgente`; `prazoAte` recebe uma data `AAAA-MM-DD`; `busca` procura no título. `ordenarPor` aceita `criadoEm`, `prazo` ou `prioridade`; `ordem` aceita `asc` ou `desc`; `limit` varia de 1 a 1000 (padrão 100) e `offset` começa em 0. As tarefas pertencem sempre ao usuário do token: não se envia `usuarioId` para criá-las.

## Contrato JSON

Os nomes das propriedades JSON usam camelCase. O cadastro recebe `nome`, `email` e `senha`; a senha tem pelo menos 6 caracteres. Uma tarefa recebe `titulo`, `prioridade` (baixa, media, alta ou urgente) e `prazo` opcional (`AAAA-MM-DD`). Tarefas nascem pendentes; `status` pode ser alterado por PATCH para `concluida` ou `pendente`. A resposta de tarefa inclui `id`, `usuarioId`, `titulo`, `status`, `prioridade`, `prazo`, `criadoEm`, `atualizadoEm` e `concluidoEm`.

O login devolve `accessToken`, `tokenType`, `expiraEm` e `usuario`. Respostas de usuário não incluem senha nem hash. Respostas de validação usam `detail` em português.

## Análises do Analytics

`GET /tasks/analytics` exige autenticação e considera apenas as tarefas de quem está logado. A resposta inclui total e concluídas, taxa de conclusão, conclusões em cada dia da janela, pendentes por prioridade, tempo médio entre criação e conclusão, conclusões por dia da semana e percentual concluído no prazo.

`tempoMedioConclusaoDias` é `null` quando não há tarefas concluídas. `percentualNoPrazo` é `null` quando não há tarefa concluída com prazo. Concluir no próprio dia do prazo conta como estar no prazo. O dia da conclusão usa o fuso horário do servidor; os dias da semana consideram todo o histórico.

Exemplo resumido:

```json
{
  "total": 6,
  "concluidas": 3,
  "taxaConclusao": 50,
  "concluidasNaJanela": 2,
  "concluidasPorDia": [
    {"dia": "2026-11-17", "quantidade": 0},
    {"dia": "2026-11-18", "quantidade": 0},
    {"dia": "2026-11-19", "quantidade": 0},
    {"dia": "2026-11-20", "quantidade": 0},
    {"dia": "2026-11-21", "quantidade": 0},
    {"dia": "2026-11-22", "quantidade": 0},
    {"dia": "2026-11-23", "quantidade": 2}
  ],
  "pendentesPorPrioridade": {
    "urgente": 1,
    "alta": 0,
    "media": 1,
    "baixa": 1
  },
  "tempoMedioConclusaoDias": 1.5,
  "concluidasPorDiaDaSemana": {
    "seg": 1,
    "ter": 0,
    "qua": 0,
    "qui": 0,
    "sex": 1,
    "sab": 0,
    "dom": 1
  },
  "percentualNoPrazo": 100
}
```

## Integração com o front-end

| Função da interface | Endpoint |
| --- | --- |
| Criar conta | `POST /usuarios` |
| Entrar e guardar token | `POST /usuarios/login` |
| Carregar perfil | `GET /usuarios/me` |
| Criar tarefa | `POST /tasks` |
| Listar, buscar, filtrar, ordenar e paginar | `GET /tasks` |
| Consultar Painel | `GET /tasks/resumo` |
| Consultar Analytics e insights | `GET /tasks/analytics` |
| Abrir, editar ou concluir tarefa | `GET` e `PATCH /tasks/{tarefa_id}` |
| Excluir tarefa | `DELETE /tasks/{tarefa_id}` |

O script `cliente.py` demonstra o login e a consulta autenticada do Analytics. Execute `python cliente.py` com a API ativa; ele solicita e-mail e senha no terminal.

## Limitações conhecidas

- Não há renovação de token, logout remoto nem recuperação de senha.
- A API não inclui uma interface web; o front-end React é integrado separadamente.
- SQLite é indicado para desenvolvimento local; a configuração PostgreSQL do Render é oferecida para publicação.
- O percentual no prazo considera apenas tarefas concluídas que possuem prazo.

## Construção em 14 dias

| Dia | Funcionalidade |
| --- | --- |
| 1 | Consultar se a API está no ar |
| 2 | Criar uma conta |
| 3 | Cadastro com e-mail único e erros em português |
| 4 | Entrar no sistema (login) |
| 5 | Ver o perfil autenticado pelo token |
| 6 | Criar uma tarefa |
| 7 | Listar as tarefas do usuário |
| 8 | Consultar, editar e excluir uma tarefa |
| 9 | Concluir e reabrir uma tarefa (RN-03) |
| 10 | Filtrar e buscar tarefas |
| 11 | Ordenar, paginar e configurar CORS |
| 12 | Ver os números do Painel |
| 13 | Ver as análises com pandas |
| 14 | Ver insights de produtividade e entregar o projeto |
