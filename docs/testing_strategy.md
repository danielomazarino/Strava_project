# Testing Strategy

This document defines the complete testing strategy for the Strava Training Diary project.

The goal is to ensure:
- deterministic behavior
- reproducibility
- multiuser safety
- zero regressions
- confidence before deployment

---

# 1. Test Types

## 1.1 Unit Tests
Purpose:
- Validate pure logic in services
- Validate utility functions
- Validate token refresh logic
- Validate LLM prompt formatting

Location:
/tests/unit/


Characteristics:
- No DB access
- No network access
- No FastAPI test client

---

## 1.2 Integration Tests
Purpose:
- Validate DB interactions
- Validate repository logic
- Validate model relationships
- Validate migrations (if used)

Location:
/tests/integration/


Characteristics:
- Uses a test database
- Rolls back after each test
- No external API calls

---

## 1.3 API Tests
Purpose:
- Validate FastAPI endpoints
- Validate request/response schemas
- Validate authentication flow
- Validate error handling

Location:
/tests/api/

Characteristics:
- Uses FastAPI TestClient
- Uses mocked Strava API
- Uses test DB

---

## 1.4 Mocking Strategy

### Strava API
All Strava API calls must be mocked:
- token exchange
- token refresh
- activity list
- activity detail

Mocks live in:
/tests/mocks/


---

# 2. Test Data

Use:
- factory functions
- lightweight fixtures
- UUIDs for user/activity IDs

Never use:
- real Strava data
- real tokens
- real network calls

---

# 3. Test Coverage Goals

- 100% for services
- 100% for OAuth flow
- 90%+ for API endpoints
- 80%+ for repositories
- 100% for LLM prompt formatting

---

# 4. Running Tests

pytest -q


---

# 5. CI Requirements

- All tests must pass before deployment
- No skipped tests allowed
- No warnings allowed





