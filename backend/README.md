# Saudagar.ai — Backend

FastAPI service that powers the "karyawan digital" assistant: natural-language
bookkeeping & stock, auto customer service + upsell, dashboard insight
narratives, and multi-language catalog copywriting.

**AI stack:** LangChain + Google Gemini, with RAG grounding over the store's own
catalog/rules and MCP-style tools that let the agent read & mutate the database
in real time.

> Runs with **zero API key** in a deterministic "mock mode" so you can develop
> the frontend immediately. Add a `GEMINI_API_KEY` to unlock the full AI.

## Quick start

```bash
cd backend

# 1. activate the venv (already created in ./venv)
#    Windows PowerShell:
venv\Scripts\Activate.ps1
#    Git Bash:
source venv/Scripts/activate

# 2. install dependencies
pip install -r requirements.txt

# 3. configure env
cp .env.example .env        # then edit .env and add GEMINI_API_KEY (optional)

# 4. run
uvicorn app.main:app --reload --port 8000
```

- API docs (Swagger): http://localhost:8000/docs
- Health: http://localhost:8000/api/health

On first boot the database (`saudagar.db`) is created and seeded with a demo
store ("Warung Bu Sari"), a product catalog, and a week of transactions.

## Architecture

```
app/
├── main.py              FastAPI app, CORS, router wiring, startup seed
├── config.py            Env-driven settings (pydantic-settings)
├── database.py          SQLModel engine + session
├── models.py            Store, Product, Transaction tables
├── schemas.py           Pydantic request/response models
├── services.py          Core ops (record sale/expense, stock) — shared by API + AI
├── seed.py              Demo data
├── ai/
│   ├── llm.py           Gemini chat + embedding factories (None in mock mode)
│   ├── rag.py           In-memory vector store over catalog + store rules
│   ├── tools.py         MCP-style StructuredTools (record_sale, check_stock, …)
│   ├── agent.py         Function-calling loop + rule-based fallback
│   └── analyst.py       Insights, catalog copywriting, CS reply generators
└── routers/             /api/chat, /api/cs, /api/insights, /api/catalog,
                         /api/products, /api/transactions
```

### How RAG + MCP fit together

- **RAG** (`ai/rag.py`): every assistant/CS turn retrieves the most relevant
  catalog + store-rule snippets and injects them into the prompt, so the model
  answers from *this* store's data instead of hallucinating.
- **MCP-style tools** (`ai/tools.py`): the model can only change data through a
  small, audited tool set (record a sale, adjust stock, add a product, …). The
  agent loop in `ai/agent.py` executes those tool calls against the live DB and
  feeds results back until the model produces a final answer.

## Key endpoints

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/chat` | NL bookkeeping/stock assistant (the WhatsApp bot brain) |
| POST | `/api/cs` | Auto customer-service reply + upsell suggestion |
| GET  | `/api/insights?days=7` | Dashboard analytics narrative + recommendations |
| POST | `/api/catalog/generate` | Multi-language product copywriting |
| GET/POST/PATCH/DELETE | `/api/products` | Catalog & stock CRUD |
| GET/POST | `/api/transactions` | Income/expense ledger |

## Configuration

See [`.env.example`](./.env.example). Notable keys: `GEMINI_API_KEY`,
`GEMINI_MODEL` (default `gemini-2.5-flash`), `DATABASE_URL`, `CORS_ORIGINS`.
