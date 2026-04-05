# Architecture Deep Dive

This document expands on the architecture skeleton defined in `project_plan.md`.

---

# 1. High‑Level Overview

The system consists of:

- **FastAPI backend** — API, services, workers
- **PostgreSQL database** — persistent storage
- **Local LLM engine (Gemma 4)** — analysis layer
- **Railway deployment** — hosting + DB
- **Strava API** — data ingestion

All personal data stays local or in the private database.

---

# 2. Backend Structure

/app
/api
/core
/db
/services
/schemas
/workers
main.py


### API Layer
- Thin controllers
- No business logic
- Input/output validation via Pydantic schemas

### Services Layer
- Pure logic
- No HTTP or DB side effects
- Easy to test

### DB Layer
- SQLAlchemy models
- Repositories for CRUD
- Session management

### Workers
- Background sync
- Token refresh
- Scheduled tasks

---

# 3. Security Model

- OAuth tokens encrypted at rest
- No cross‑user access
- No cloud LLM usage for personal data
- Strict CORS
- No public endpoints except `/health`

---

# 4. LLM Integration

- Local inference only
- Async calls from FastAPI
- No personal data leaves the machine
- Deterministic prompts

---

# 5. Deployment Architecture

- Railway app (FastAPI)
- Railway PostgreSQL
- Environment variables:
  - STRAVA_CLIENT_ID
  - STRAVA_CLIENT_SECRET
  - DATABASE_URL
  - SECRET_KEY
  - LLM_MODEL_PATH

---

# 6. Testing Architecture

- Unit tests for services
- Integration tests for DB + API
- API tests with mocked Strava
- No real network calls



