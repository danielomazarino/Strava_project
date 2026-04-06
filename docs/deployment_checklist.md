# Deployment Checklist (Railway)

This document ensures safe, predictable deployments to Railway.

See also: [docs/deployment_runbook.md](docs/deployment_runbook.md)

---

# 1. Pre‑Deployment

## 1.1 Code
- [ ] All batch tasks complete
- [ ] No unrelated file changes
- [ ] No TODOs left behind
- [ ] No placeholder code
- [ ] No architecture drift

## 1.2 Tests
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] API tests pass
- [ ] Strava API fully mocked
- [ ] No real network calls

---

# 2. Environment Variables

Ensure the following are set in Railway:

- APP_ENV=production
- STRAVA_CLIENT_ID  
- STRAVA_CLIENT_SECRET  
- DATABASE_URL  
- SECRET_KEY  
- LLM_MODEL_PATH  
- CORS_ORIGINS
- LOG_LEVEL

Railway must use PostgreSQL for `DATABASE_URL`. SQLite is allowed only for local development and tests.
The app now bootstraps the current tables on startup, so a fresh Railway PostgreSQL database should not need a manual schema setup step.

Deployment entrypoint:
- `Dockerfile` should launch `uvicorn app.main:app` on Railway.
- `railway.toml` should use the Dockerfile deployment path.

---

# 3. Application Health

- [ ] App starts locally
- [ ] `/health` endpoint returns 200
- [ ] OAuth login works locally
- [ ] Token refresh works locally

---

# 4. Deployment

- [ ] Commit created
- [ ] Commit message references batch
- [ ] Push to GitHub
- [ ] Railway auto‑deploys
- [ ] Logs show no errors

---

# 5. Post‑Deployment

- [ ] Test `/health` on Railway
- [ ] Test OAuth login on Railway
- [ ] Test import endpoint
- [ ] Test diary endpoint
- [ ] Test LLM endpoints (stubbed)

---

# 6. Rollback Plan

If deployment fails:
- Revert to previous commit
- Push to GitHub
- Railway redeploys stable version

