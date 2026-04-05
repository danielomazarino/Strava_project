<!-- /docs/security_model.md -->
# Security Model

This document defines the security model for the Strava Training Diary project. Save as `/docs/security_model.md`.

---

## 1. Security Goals

- **Confidentiality:** protect user tokens, personal notes, and activity data.
- **Integrity:** prevent unauthorized modification of data.
- **Availability:** ensure the service is resilient and recoverable.
- **Least Privilege:** services and processes run with minimal permissions.
- **Auditability:** all sensitive actions are logged for review.

---

## 2. Secrets and Credentials

**Environment Variables**
- Store all secrets in Railway environment variables or a secrets manager.
- Required variables:
  - `STRAVA_CLIENT_ID`
  - `STRAVA_CLIENT_SECRET`
  - `DATABASE_URL`
  - `SECRET_KEY` (app signing)
  - `LLM_MODEL_PATH` (local model path)
- **Never** commit secrets to source control.

**Local Development**
- Use a `.env` file for local development, excluded from VCS.
- Use a local secrets helper script to load secrets into the environment for local runs.

**Key Rotation**
- Rotate `STRAVA_CLIENT_SECRET` and `SECRET_KEY` periodically (every 90 days).
- Document rotation steps in `/docs/security_model.md`.

---

## 3. Token Storage and Encryption

**Encryption at Rest**
- Encrypt OAuth tokens before storing in the database.
- Use a symmetric encryption key derived from `SECRET_KEY` or a dedicated key stored in Railway secrets.
- Store only encrypted `access_token` and `refresh_token` fields.

**Token Handling**
- Tokens are decrypted only in memory within the service that needs them.
- Avoid logging tokens or decrypted values.
- Use short‑lived access tokens and refresh as needed.

**Database Column Design**
- `access_token_encrypted` (bytea or text)
- `refresh_token_encrypted` (bytea or text)
- `token_encryption_version` (int) to support key rotation

---

## 4. Access Control and Multiuser Isolation

**User Isolation**
- All queries must be scoped by `user_id`.
- Repositories must enforce `user_id` filters at the query level.
- No endpoint returns data for multiple users in a single response.

**Role Model**
- Initially: single role (user). Admin role reserved for maintenance.
- Admin endpoints must be protected and audited.

**API Authentication**
- Use session cookies or JWTs for authenticated API calls.
- Tokens for API access must be short‑lived and revocable.

---

## 5. Network and Infrastructure Security

**Transport**
- Enforce HTTPS in production (Railway provides TLS).
- Local dev: use `uvicorn` with `--reload` and local proxies as needed.

**CORS**
- Restrict CORS to known origins (local dev and deployed domain).
- Default to strict CORS policy.

**Rate Limiting**
- Implement rate limiting on endpoints that trigger Strava API calls to avoid abuse and to respect Strava limits.

---

## 6. Logging, Monitoring, and Auditing

**Logging**
- Log structured events (JSON) with:
  - timestamp
  - user_id (when applicable)
  - action
  - outcome (success/failure)
- **Do not log** tokens, decrypted secrets, or PII.

**Monitoring**
- Health checks (`/health`) for app and DB.
- Alert on repeated failures in token refresh or sync worker.

**Auditing**
- Record security‑relevant events:
  - OAuth logins
  - Token refresh failures
  - Admin actions
- Retain audit logs for a defined period (e.g., 90 days).

---

## 7. Incident Response

**Initial Steps**
- Revoke compromised secrets immediately.
- Rotate keys and secrets.
- Revert recent commits if code introduced a leak.

**Communication**
- Document incident in `/docs/security_incidents.md`.
- Notify affected users if personal data exposure occurred.

---

## 8. Testing Security

- Include security tests in CI:
  - Ensure tokens are encrypted in DB.
  - Ensure no network calls in unit tests.
  - Ensure endpoints enforce `user_id` scoping.
- Run periodic security reviews before major releases.


