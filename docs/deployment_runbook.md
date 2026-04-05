# Railway Deployment Runbook

This runbook turns the deployment checklist into the exact sequence to follow once the code is ready.

## 1. Preflight

- Confirm the local test suite passes.
- Confirm `APP_ENV=production` is set in Railway.
- Confirm `DATABASE_URL` points to Railway PostgreSQL.
- Confirm `CORS_ORIGINS` contains only approved frontend origins.
- Confirm `SECRET_KEY`, `STRAVA_CLIENT_ID`, `STRAVA_CLIENT_SECRET`, and `LLM_MODEL_PATH` are present.

## 2. Deploy

- Push the current branch to GitHub.
- Let Railway auto-deploy from the connected repository.
- Verify the build uses the repository Dockerfile and starts with `uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}`.
- Keep `railway.toml` in sync with the Docker-based deployment path.

## 3. Smoke Checks

- `GET /health` returns `200`.
- `GET /auth/login` redirects to Strava authorization.
- `POST /activities/import` works for a test user with mocked Strava data.
- `GET /diary` returns diary entries for the test user.
- `GET /search/keyword` and `GET /search/semantic` return results for the test user.
- `GET /insights/summary`, `GET /insights/patterns`, and `GET /insights/regions/comparison` return deterministic responses.
- `GET /heatmaps/tiles/{z}/{x}/{y}` returns a valid tile payload.

## 4. If Something Fails

- Check Railway logs first.
- Verify the production environment variables.
- Verify PostgreSQL connectivity.
- Re-run the local suite before attempting another deploy.
- If the issue is in the latest batch, fix locally and redeploy from a new commit.

## 5. Rollback

- Revert the failing commit.
- Push the revert to GitHub.
- Let Railway redeploy the previous stable version.
