<!-- /docs/roadmap.md -->
# Roadmap

This document outlines the high‑level roadmap, milestones, and timeline for the Strava Training Diary project. Save as `/docs/roadmap.md`.

---

## 1. Objectives and Timeline

**Objective:** Deliver a secure, local‑LLM powered training diary with Strava ingestion and analysis.

**High‑level timeline (approximate)**
- **Phase 0 (Weeks 0–1):** Project setup, docs, batch workflow
- **Phase 1 (Weeks 2–4):** OAuth Foundation + DB base layer
- **Phase 2 (Weeks 5–8):** Historical import + storage
- **Phase 3 (Weeks 9–12):** Diary, search, and basic LLM analysis
- **Phase 4 (Weeks 13–16):** Heatmaps, geo insights, sync worker
- **Phase 5 (Weeks 17–20):** Hardening, CI, Railway deployment, security review

Adjust timelines based on team velocity and Gemma 4 evaluation.

## Current Status

Implementation through Batch 8 is complete.

Current stage:
- Phase 5 — Hardening, CI, Railway deployment, security review

Immediate next step:
- Deploy to Railway and run the post-deployment smoke checks in `deployment_checklist.md`.

---

## 2. Milestones

### Milestone 1 — Foundation Complete
- **Deliverables**
  - Project skeleton
  - DB session and base models
  - OAuth endpoints and token storage
  - Local test DB setup
- **Acceptance**
  - Local OAuth login works
  - Tests for base models pass

### Milestone 2 — Historical Import
- **Deliverables**
  - `/activities/import` endpoint
  - Activity storage and streams
  - Import tests with mocked Strava
- **Acceptance**
  - Import completes for a sample user
  - No duplicate activities stored

### Milestone 3 — Diary and Search
- **Deliverables**
  - Diary endpoints
  - Keyword search
  - Semantic search stub (LLM integration)
- **Acceptance**
  - Diary entries retrievable and filterable
  - Semantic search returns plausible candidates (stubbed)

### Milestone 4 — LLM Analysis and Heatmaps
- **Deliverables**
  - LLM service wrapper
  - Summary and pattern endpoints
  - Polyline decoding and heatmap generation
- **Acceptance**
  - LLM endpoints return deterministic outputs (stubbed in tests)
  - Heatmap generation pipeline runs locally

### Milestone 5 — Sync Worker and Deployment
- **Deliverables**
  - Background sync worker
  - Token refresh integration
  - Railway deployment and CI
- **Acceptance**
  - Worker syncs new activities for a test user
  - Railway deployment passes health checks

---

## 3. Risk Register and Mitigations

- **Risk:** Gemma 4 not reliable for implementation  
  **Mitigation:** Run evaluation plan early; prepare fallback models and cloud policy.

- **Risk:** Strava rate limits slow import  
  **Mitigation:** Implement batching, backoff, and incremental sync.

- **Risk:** Secrets leakage  
  **Mitigation:** Strict secrets policy, encryption, and audits.

- **Risk:** Large data volumes (streams, geo)  
  **Mitigation:** Consider compression, separate storage, or partitioning.

---

## 4. Resource Plan

- **Primary roles**
  - Architect (GPT‑5.4 mini for planning)
  - Implementer (Gemma 4 or alternative)
  - Reviewer (you)
- **Infrastructure**
  - Railway app + PostgreSQL
  - Local LLM runtime for Gemma 4
- **CI**
  - GitHub Actions or equivalent to run pytest and linters

---

## 5. Acceptance Criteria per Phase

- All tests pass locally and in CI.
- No architecture drift.
- Multiuser isolation verified.
- No personal data sent to cloud LLMs.
- Deployment to Railway succeeds and `/health` returns 200.

---

## 6. Next Steps

1. Deploy the current build to Railway.
2. Run the post-deployment smoke checks in `deployment_checklist.md`.
3. Update the roadmap if any deployment findings require follow-up.

---

