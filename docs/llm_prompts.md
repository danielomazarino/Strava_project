# LLM Prompts (Gemma 4)

This document defines deterministic, safe prompts for the local LLM.

---

# 1. Summary Prompt

Summarize the user's training between {start_date} and {end_date}.
Focus on:

    volume

    intensity

    notable events

    subjective notes

    patterns in performance
    Do not invent data.


---

# 2. Pattern Detection Prompt
Analyze the following training notes and identify recurring patterns.
Focus on:

    fatigue

    motivation

    terrain effects

    weather effects

    pacing issues
    Do not add new interpretations.


---

# 3. Region Comparison Prompt
Compare the user's training experiences between Region A and Region B.
Focus on:

    perceived effort

    terrain differences

    pacing differences

    subjective notes
    Do not invent data.


---

# 4. Semantic Search Prompt

Given the user's query "{query}", return the most relevant diary entries.
Use semantic similarity only.
Do not fabricate entries.


---

# 5. Tag Extraction Prompt
Extract simple, factual tags from the user's activity notes.
Examples:

    "hills"

    "intervals"

    "long run"

    "commute"
    Do not invent tags.


---

# 6. Testing LLM Prompts

- Validate formatting
- Validate placeholders
- Validate deterministic structure
- Use stubbed responses in tests



