<!-- /docs/workflow.md -->
# Hybrid Workflow and Gemma 4 Evaluation

This document describes the hybrid workflow (GPT‑5.4 mini for planning, Gemma 4 for implementation), how to run batch sessions, how to evaluate Gemma 4 in practice, and a clear fallback plan if Gemma 4 proves difficult to operate. Save this file as `/docs/workflow.md`.

---

## 1. Overview

**Purpose:** Provide a repeatable, low‑friction workflow for planning, implementing, validating, and deploying features using two agents: **GPT‑5.4 mini** (planner) and **Gemma 4** (executor). Include an evaluation plan and a fallback strategy to switch to alternative models (local or cloud) if Gemma 4 is impractical.

**Principles**
- **Batching:** group 3–5 atomic tasks per session to minimize model switching.
- **Determinism:** tasks must be atomic, test‑driven, and architecture‑aligned.
- **Safety:** no personal data leaves local systems; all LLM analysis uses local models.
- **Reversibility:** every change must be commit‑scoped and easily reverted.

---

## 2. Batch Session Lifecycle

1. **Plan (GPT‑5.4 mini)**
   - Input: a batch card (3–5 tasks) from `/docs/batches.md` or `project_plan.md`.
   - Output: refined atomic tasks with file paths, test file paths, acceptance criteria, and dependencies.

2. **Implement (Gemma 4)**
   - Stay in Gemma 4 for the entire batch.
   - For each task: paste the single task into the Gemma 4 Task Execution Prompt and implement.
   - Run tests locally after each task.

3. **Validate (Engineer)**
   - Run full test suite for the batch.
   - Manual smoke tests (OAuth login, `/health`, sample import).
   - Use the Batch Review Checklist in `/docs/project_plan.md`.

4. **Deploy (Railway)**
   - Push commits, let CI run, verify Railway deployment, run post‑deploy checks.

---

## 3. Gemma 4 Evaluation Plan

**Goal:** Determine whether Gemma 4 is reliable, deterministic, and practical for day‑to‑day implementation.

### 3.1 Evaluation Metrics
- **Determinism:** repeated runs on the same task produce identical outputs.
- **Atomicity:** Gemma modifies only the files specified in the task.
- **Test Coverage:** Gemma produces unit and integration tests that pass.
- **Local Runability:** code runs locally without cloud dependencies.
- **Import Safety:** no accidental exposure of secrets or tokens.
- **Multi‑file Consistency:** imports, schemas, and tests remain consistent across files.

### 3.2 Evaluation Procedure (3 batches)
- **Batch A (small):** 2 tasks (utility + unit test). Measure determinism and runability.
- **Batch B (medium):** 3 tasks (one model, one repo, one service). Measure multi‑file consistency.
- **Batch C (full):** 4 tasks (end‑to‑end OAuth flow pieces). Measure integration, DB migrations, and deployment readiness.

For each batch:
- Run Gemma 4 once to implement tasks.
- Run tests and record failures.
- Re-run Gemma 4 on the same tasks (fresh session) and compare diffs.
- Score each metric (Pass/Fail + notes).

### 3.3 Decision Criteria
- **Keep Gemma 4** if:
  - Determinism Pass for all batches.
  - Atomicity Pass for all tasks.
  - Tests pass locally and CI passes.
  - No architecture drift.
- **Consider fallback** if:
  - Any metric fails in two or more batches.
  - Frequent multi‑file inconsistencies occur.
  - Gemma 4 requires excessive manual fixes (>30% of time).

Record results in `/docs/evaluation_results.md` (create if needed).

---

## 4. Fallback and Model Switch Strategy

If Gemma 4 proves impractical, follow this controlled fallback plan.

### 4.1 Short‑term fallback (same local environment)
- **Use an alternative local model** (if available) with the same Gemma 4 Task Execution Prompt.
- Keep the same batching workflow and prompts.
- Validate with the same evaluation metrics.

### 4.2 Medium‑term fallback (cloud or hybrid)
- **Allow cloud LLMs only for non‑personal tasks** (planning, code generation for non‑sensitive utilities).
- **Never** send personal data or tokens to cloud LLMs.
- Use strict prompt templates that exclude personal data.
- Add a gating review step: every cloud‑generated change must be reviewed and tested locally before commit.

### 4.3 Switching mechanics (how to switch models in VS Code)
- Use two VS Code profiles: **Architect** (GPT‑5.4 mini) and **Engineer** (Gemma 4 or alternative).
- Keyboard shortcuts:
  - `Ctrl+Alt+M` → GPT‑5.4 mini
  - `Ctrl+Alt+G` → Gemma 4 (or alternative)
- When switching to a new model, run the **Model Sanity Checklist** (below).

### 4.4 Model Sanity Checklist (before using a new model)
- [ ] Confirm model can run locally (if local) or confirm cloud policy for data handling.
- [ ] Run a small test task (utility + unit test).
- [ ] Verify output modifies only intended files.
- [ ] Run tests and ensure no network calls to personal data.
- [ ] Approve model for batch work.

---

## 5. Operational Playbook

### 5.1 Daily Routine
- Morning: open `project_plan.md`, pick a batch, run Planning step.
- Midday: switch to Engineer profile, implement batch in Gemma 4.
- End of day: run full tests, update `batches.md`, push commits.

### 5.2 Emergency Rollback
- If a batch breaks CI or Railway:
  - Revert the batch commit(s).
  - Re‑run tests locally.
  - Reassign tasks and re‑implement.

### 5.3 Logging and Traceability
- Each batch commit message must include:
  - `Batch <n>: <short description>`
  - List of tasks implemented
  - Test status summary

---

## 6. Notes and Next Steps

- Add `/docs/evaluation_results.md` to record Gemma 4 evaluation outcomes.
- If fallback to cloud is required, create a strict policy file `/docs/cloud_llm_policy.md` before any cloud LLM use.
- Keep this workflow document under version control and update after each major evaluation.


