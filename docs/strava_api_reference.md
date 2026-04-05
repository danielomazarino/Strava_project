# Strava API Reference (Project‑Specific)

This document summarizes the Strava API endpoints used by the project.

---

# 1. OAuth Endpoints

## Authorization URL
https://www.strava.com/oauth/authorize


Parameters:
- client_id
- redirect_uri
- response_type=code
- scope=activity:read_all

## Token Exchange
POST https://www.strava.com/oauth/token


Used for:
- exchanging authorization code
- refreshing tokens

---

# 2. Activity Endpoints

## List Activities
GET https://www.strava.com/api/v3/athlete/activities (strava.com in Bing)

Parameters:
- page
- per_page
- before
- after

Used for:
- historical import
- ongoing sync

---

## Activity Detail
GET https://www.strava.com/api/v3/activities/{id} (strava.com in Bing)


Used for:
- full metadata
- description
- polyline
- stats

---

# 3. Rate Limits

Strava rate limits:
- 100 requests every 15 minutes
- 1000 requests per day

Our strategy:
- batch requests
- store sync metadata
- avoid duplicate fetches

---

# 4. Mocking Strategy

All Strava calls must be mocked in tests:
- token exchange
- token refresh
- activity list
- activity detail

Mocks live in:
/app/tests/mocks/


