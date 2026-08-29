# Architecture Overview

## Current Stack (MVP)

- **API**: FastAPI, containerized via Docker
- **Database**: PostgreSQL, containerized via Docker, with a named volume for persistence
- **Multi-tenancy**: shared tables, isolated via `tenant_id` on every business-owned row (customers, products, orders, order_items). Every query is scoped server-side via the authenticated user's tenant — never trusted from client input.
- **Auth**: JWT-based, bcrypt password hashing. Token payload carries `tenant_id`, decoded fresh from the DB on every request via `get_current_user`.

## Current Data Pipeline

CSV ingestion currently follows an explicit validate → insert flow per row, with per-row error collection rather than all-or-nothing failure — appropriate for small business owners uploading imperfect spreadsheets.

## Where Future Components Would Plug In

These are **not built yet** — deliberately, to avoid over-engineering the MVP. This section documents where they'd attach when actually needed:

- **Airflow**: would replace manual/on-demand CSV upload with scheduled pipelines (e.g. nightly pulls from external APIs). Would call the same validation/transform functions the upload endpoint uses today, just on a schedule instead of a human trigger.
- **S3 (or equivalent object storage)**: would sit between "raw upload" and "validated insert" — raw files would be archived here before processing, enabling reprocessing/audit without needing the original upload again.
- **Kafka**: would matter once real-time events exist (e.g. a live Facebook/Instagram webhook feed in Phase 5) — decouples ingestion from processing so spikes in incoming events don't block the API.
- **Spark**: would only become relevant at a data volume where PostgreSQL aggregation queries (current `GROUP BY`-based analytics) become too slow for a single database to handle.

## Local Development

```bash
docker compose up --build
```

Runs FastAPI (`api`) and PostgreSQL (`db`) together, with a health check ensuring the API waits for the database to be ready before starting.
