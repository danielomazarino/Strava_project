# Strava Training Diary — Project Plan (Master Document)

This document defines the full vision, constraints, architecture, epics, user stories, and workflow for generating tasks for Gemma 4 using GPT‑5.4 mini.

It is the **single source of truth** for the entire project.

---

# 1. Vision

Create a personal training diary and analysis system that:

- securely ingests all Strava activity data (2013 → now)
- stores it in a local PostgreSQL database
- enables advanced querying, filtering, and semantic search
- uses a **local LLM (Gemma 4)** for analysis
- supports multiple users, each isolated to their own data
- does NOT replicate Strava’s UI or social features
- focuses on extracting insights from personal notes, tags, and GPS data

---

# 2. Constraints

- Backend: FastAPI
- Database: PostgreSQL (Railway)
- ORM: SQLAlchemy
- Local LLM: Gemma 4
- Cloud LLM: GPT‑5.4 mini **only for planning**
- Deployment: Railway
- Tests: pytest
- No cloud LLM sees personal data
- No creativity from GPT‑5.4 mini beyond planning
- No cross‑user data access
- No Strava ZIP import — **API‑based import only**

---

# 3. Architecture Skeleton

## Folder Structure
/app
/api
auth.py
activities.py
diary.py
search.py
insights.py
health.py
/core
config.py
security.py
logging.py
exceptions.py
/db
base.py
session.py
models/
user.py
activity.py
activity_stream.py
activity_tag.py
activity_geo.py
repositories/
user_repo.py
activity_repo.py
/services
oauth_service.py
strava_import_service.py
strava_sync_service.py
diary_service.py
llm_service.py
heatmap_service.py
/schemas
user.py
activity.py
diary.py
search.py
insights.py
/workers
sync_worker.py
/tests
/unit
/integration
/api
/mocks
main.py


## Database Schema (Initial)

### users
- id (UUID)
- strava_athlete_id (int)
- access_token (encrypted)
- refresh_token (encrypted)
- token_expires_at (datetime)
- created_at
- updated_at

### activities
- id (UUID)
- user_id (FK)
- strava_activity_id (int)
- name
- type
- start_date
- distance
- moving_time
- elapsed_time
- elevation_gain
- description
- polyline
- timezone
- location_country
- created_at
- updated_at

### activity_tags
- id
- activity_id
- tag

---

# 4. Epics

## Epic 1 — User Authentication & OAuth
## Epic 2 — Historical Data Import (API)
## Epic 3 — Ongoing Sync
## Epic 4 — Training Diary & Notes
## Epic 5 — Local LLM Analysis
## Epic 6 — Heatmaps & Geographical Insights
## Epic 7 — Multiuser Support
## Epic 8 — Infrastructure, Testing & Deployment

---

# 5. User Stories

(Only the most relevant examples shown here — full list available on request.)

### US‑1.1 — Log in with Strava  
### US‑1.2 — Store OAuth tokens securely  
### US‑2.1 — Import all historical activities  
### US‑4.1 — View diary entries  
### US‑5.4 — Analyze race strategies  
### US‑6.1 — View personal heatmap  
### US‑7.1 — Isolated user data  

---

# 6. Batch Workflow

## Batch Structure
Each batch contains:
- 3–5 tasks
- atomic, testable, architecture‑aligned
- implemented in one Gemma 4 session

## Batch Cycle
1. Planning (GPT‑5.4 mini)
2. Implementation (Gemma 4)
3. Validation (You)
4. Deployment (Railway)

## 6.1 Recommended Build Sequence

Use this order when turning the plan into code:

1. Runtime scaffold: config, database session, declarative base, and test harness alignment.
2. Batch 1 — OAuth foundation.
3. Batch 2 — database base layer.
4. Batch 3 — historical import.
5. Batch 4 — diary and search.
6. Batch 5 — LLM analysis.
7. Batch 6 — heatmaps and geo insights.
8. Batch 7 — sync worker.
9. Batch 8 — deployment and hardening.

Keep the docs updated as each batch lands so the current implementation state stays visible.

---

# 7. Batch 1 — OAuth Foundation (Input for GPT‑5.4 mini)

Refine these tasks into atomic, test‑driven tasks with file paths, test paths, acceptance criteria, and dependencies:

    Implement /auth/login endpoint

    Implement /auth/callback endpoint

    Implement token storage model

    Implement token refresh logic

    Write tests for OAuth flow

Follow the architecture skeleton exactly.
No creativity.
No new endpoints.
No new models.
No scope drift.


---

# 8. Gemma 4 Task Execution Prompt
You are implementing ONE task from the task plan.
Follow these rules strictly:

    Do not invent anything.

    Modify only the files listed in the task.

    Follow the architecture skeleton exactly.

    Write deterministic, minimal code.

    Include full test coverage.

    Mock all external services.

    Ensure multiuser safety.

    Output only code blocks for modified files.

[TASK GOES HERE]

---

# 9. Batch Review Checklist

- All tasks implemented
- No unrelated files modified
- All tests pass
- Strava API fully mocked
- No architecture drift
- No sensitive data logged
- App starts locally
- `/health` works
- Ready for Railway deployment

---

# 10. How to Use This Document

- Use GPT‑5.4 mini to generate refined tasks from batches
- Use Gemma 4 to implement tasks
- Use this file as the stable reference for the entire project
- Never rely on long chat history
- Always return to this file as the source of truth



