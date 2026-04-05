# Batching Dashboard

This file tracks all development batches using the hybrid GPT‑5.4 mini + Gemma 4 workflow.

Each batch contains:
- 3–5 atomic tasks
- Implemented in one Gemma session
- Fully tested
- Validated before deployment

---

## Batch 0 — Runtime Scaffold
Status: ☐ Not started / ☐ In progress / ☑ Done

Tasks:
- [ ] App settings and environment loading
- [ ] Database base and session helpers
- [ ] Health router wiring
- [ ] Test harness alignment

Notes:
- Dependencies: None
- Risks: Keep imports lazy so the app still starts without a local database

---

## Batch 1 — OAuth Foundation
Status: ☐ Not started / ☐ In progress / ☑ Done

Tasks:
- [ ] /auth/login endpoint
- [ ] /auth/callback endpoint
- [ ] Token storage model
- [ ] Token refresh logic
- [ ] OAuth tests

Notes:
- Dependencies: Batch 0
- Risks: Strava API mocking

---

## Batch 2 — Database Base Layer
Status: ☐ Not started / ☐ In progress / ☑ Done

Tasks:
- [ ] DB session + engine
- [ ] Base models
- [ ] User model
- [ ] Activity model
- [ ] Test DB setup

---

## Batch 3 — Historical Import (API)
Status: ☐ Not started / ☐ In progress / ☑ Done

Tasks:
- [ ] /activities/import endpoint
- [ ] Pagination logic
- [ ] Activity detail fetch
- [ ] Storage logic
- [ ] Import tests

---

## Batch 4 — Diary & Search Base
Status: ☐ Not started / ☐ In progress / ☑ Done

Tasks:
- [ ] Diary list endpoint
- [ ] Keyword search
- [ ] Semantic search stub
- [ ] Diary tests

---

## Batch 5 — LLM Analysis Layer
Status: ☐ Not started / ☐ In progress / ☑ Done

Tasks:
- [ ] LLM service wrapper
- [ ] Summary endpoint
- [ ] Pattern detection endpoint
- [ ] Region comparison endpoint
- [ ] LLM tests

---

## Batch 6 — Heatmaps & Geo Insights
Status: ☐ Not started / ☐ In progress / ☑ Done

Tasks:
- [ ] Polyline decoding
- [ ] Geo extraction
- [ ] Heatmap tile generation
- [ ] Heatmap filters
- [ ] Geo tests

---

## Batch 7 — Sync Worker
Status: ☐ Not started / ☐ In progress / ☑ Done

Tasks:
- [ ] Background worker
- [ ] Sync logic
- [ ] Token refresh integration
- [ ] Worker tests

---

## Batch 8 — Deployment & Hardening
Status: ☐ Not started / ☐ In progress / ☑ Done

Tasks:
- [ ] Railway config
- [ ] Environment variable audit
- [ ] Logging hardening
- [ ] Security review
- [ ] Final test suite

