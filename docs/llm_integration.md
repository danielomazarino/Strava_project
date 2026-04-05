# Local LLM Integration (Gemma 4)

This document defines how the backend interacts with the local LLM.

---

# 1. Principles

- All LLM processing is local
- No personal data sent to cloud models
- Deterministic prompts
- No creativity beyond defined tasks
- LLM used only for:
  - summaries
  - pattern detection
  - semantic search
  - region comparison
  - tag extraction

---

# 2. LLM Service Structure

File: `/app/services/llm_service.py`

Responsibilities:
- Load local model
- Provide async inference
- Expose helper functions:
  - summarize_period()
  - detect_patterns()
  - compare_regions()
  - semantic_search()
  - extract_tags()

Current implementation status:
- The service is wrapped behind a deterministic adapter with stubbed local outputs for tests.
- API endpoints live under `/insights` for summary, pattern detection, and region comparison.
- A real local model client can be wired in later without changing the public API.

---

# 3. Prompt Structure

Prompts must be:
- deterministic
- minimal
- context‑bounded
- free of personal data leakage
- aligned with user stories

---

# 4. Testing LLM Logic

- Use stubbed responses
- No real model calls in tests
- Validate:
  - prompt formatting
  - input sanitization
  - output parsing

---

# 5. Future Extensions

- Embedding‑based search
- Vector database (optional)
- Model upgrades (Gemma 4 → newer local models)

