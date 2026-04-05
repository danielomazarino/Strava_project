<!-- /docs/data_model.md -->
# Data Model

This document details the canonical data model, relationships, indexes, and constraints. Save as `/docs/data_model.md`.

---

## 1. Design Principles

- **User isolation:** every record belongs to a `user_id` (UUID).
- **Immutability where appropriate:** keep original Strava IDs and raw payloads for audit.
- **Normalized core models:** activities, streams, tags, geo.
- **Efficient queries:** add indexes for common filters (user_id, start_date, strava_activity_id).
- **UUID primary keys:** use UUIDs for internal IDs to avoid leaking Strava IDs.

---

## 2. Core Tables

### users
- **id**: UUID, PK  
- **strava_athlete_id**: bigint, unique, indexed  
- **access_token_encrypted**: text/bytea  
- **refresh_token_encrypted**: text/bytea  
- **token_expires_at**: timestamptz, indexed  
- **created_at**: timestamptz  
- **updated_at**: timestamptz

**Notes**
- `strava_athlete_id` is unique per user.
- Encryption metadata stored in `token_encryption_version`.

---

### activities
- **id**: UUID, PK  
- **user_id**: UUID, FK -> users.id, indexed  
- **strava_activity_id**: bigint, indexed (unique per user)  
- **name**: text  
- **type**: text  
- **start_date**: timestamptz, indexed  
- **distance**: numeric (meters)  
- **moving_time**: integer (seconds)  
- **elapsed_time**: integer (seconds)  
- **elevation_gain**: numeric (meters)  
- **description**: text  
- **polyline**: text (encoded polyline)  
- **timezone**: text  
- **location_country**: text  
- **raw_payload**: jsonb (optional, for audit)  
- **created_at**: timestamptz  
- **updated_at**: timestamptz

**Indexes**
- `(user_id, start_date)` for timeline queries
- `(user_id, strava_activity_id)` unique constraint

---

### activity_tags
- **id**: UUID, PK  
- **activity_id**: UUID, FK -> activities.id, indexed  
- **user_id**: UUID, FK -> users.id, indexed  
- **tag**: text  
- **created_at**: timestamptz

**Notes**
- Store `user_id` to simplify multiuser queries and enforce isolation.

---

### activity_streams
- **id**: UUID, PK  
- **activity_id**: UUID, FK -> activities.id, indexed  
- **type**: text (e.g., latlng, altitude, cadence)  
- **data**: jsonb or array type  
- **created_at**: timestamptz

**Notes**
- Streams may be large; consider separate storage or compression for very large streams.

---

### activity_geo (optional)
- **id**: UUID, PK  
- **activity_id**: UUID, FK -> activities.id, indexed  
- **geom**: geometry (PostGIS) or geojson in jsonb  
- **bbox**: geometry or numeric fields for bounding box  
- **created_at**: timestamptz

**Notes**
- PostGIS optional; if used, add spatial indexes for heatmap queries.

---

## 3. Relationships

- `users` 1 — * `activities`
- `activities` 1 — * `activity_tags`
- `activities` 1 — * `activity_streams`
- `activities` 1 — 1 `activity_geo` (optional)

All relationships must include `user_id` checks in repository methods to enforce isolation.

---

## 4. Constraints and Migrations

- Use Alembic for migrations.
- Migration policy:
  - Small, incremental migrations per batch.
  - Backwards compatible changes preferred.
  - Add `token_encryption_version` when rotating keys.
- Constraints:
  - `activities` unique constraint on `(user_id, strava_activity_id)`.
  - Foreign keys with `ON DELETE CASCADE` for user deletion (optional; prefer soft delete).

---

## 5. Indexing and Performance

- Indexes:
  - `users(strava_athlete_id)`
  - `activities(user_id, start_date)`
  - `activities(user_id, strava_activity_id)`
  - `activities(start_date)` for global queries (if needed)
- Consider partial indexes for active users or recent activities.
- For large datasets, consider partitioning `activities` by year or user cohort.

---

## 6. Retention and Privacy

- **Retention policy:** keep raw payloads for 1 year by default; configurable per user.
- **Deletion:** support user data deletion (GDPR style) — cascade or anonymize records.
- **Backups:** regular DB backups; ensure backups are encrypted.


