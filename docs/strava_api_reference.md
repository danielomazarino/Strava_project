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

Current project usage:
- not used by the historical import path
- reserved for future enrichment flows if we need fields that are not present in the list payload

---

# 3. Rate Limits

Strava rate limits:
- 100 requests every 15 minutes
- 1000 requests per day

Our strategy:
- batch requests
- use the paginated athlete-activities list payload for historical import and sync
- avoid one detail request per activity
- store sync metadata
- avoid duplicate fetches
- retry 429 responses with backoff and continue the same page until Strava returns an empty page

---

# 4. Mocking Strategy

All Strava calls must be mocked in tests:
- token exchange
- token refresh
- activity list
- activity detail

Mocks live in:
/app/tests/mocks/


