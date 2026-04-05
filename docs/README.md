# Strava Training Diary — Project Overview

This repository contains a personal training diary and analysis system built on:

- FastAPI backend
- PostgreSQL (Railway)
- Local LLM analysis (Gemma 4)
- Strava API ingestion (historical + ongoing)
- Secure multiuser isolation
- Test‑driven development
- Deterministic, reproducible workflows

The system is designed to extract insights from personal Strava data using local AI models, without exposing any personal data to cloud LLMs.

## Current Stage

The project is in Phase 5 of the roadmap: hardening, CI, Railway deployment, and security review.

Completed batches:
- Batch 0: Runtime scaffold
- Batch 1: OAuth foundation
- Batch 2: Database base layer
- Batch 3: Historical import
- Batch 4: Diary and search
- Batch 5: LLM analysis
- Batch 6: Heatmaps and geo insights
- Batch 7: Sync worker
- Batch 8: Deployment and hardening

The current gate is local validation. The full test suite passes locally, and the next step is Railway deployment followed by post-deploy smoke checks.

---

## Key Features

- OAuth login with Strava
- Full historical import (API‑based)
- Ongoing activity sync
- Diary and notes system
- Semantic search
- Local LLM analysis (Gemma 4)
- Heatmaps and geographical insights
- Multiuser support (private only)
- Railway deployment

---

## Documentation Structure

- `project_plan.md` — Master document (vision, architecture, epics, user stories)
- `batches.md` — Batch‑based development Kanban
- `architecture.md` — Deep‑dive into backend architecture
- `llm_integration.md` — Local LLM integration strategy
- `testing_strategy.md` — Test plan
- `deployment_checklist.md` — Railway deployment safety
- `strava_api_reference.md` — API summary
- `llm_prompts.md` — Deterministic LLM prompts

---

## Development Workflow

1. Use GPT‑5.4 mini for planning and task refinement
2. Use Gemma 4 for deterministic implementation
3. Validate locally with tests before deployment
4. Deploy to Railway
5. Run post-deploy smoke checks
6. Repeat in batches

This workflow ensures stability, reproducibility, and zero drift.

---

## Requirements

- Python 3.11+
- FastAPI
- SQLAlchemy
- PostgreSQL
- Railway account
- Local LLM runtime (for Gemma 4)
- Strava API credentials

---

## License

Private project — not intended for public distribution.

