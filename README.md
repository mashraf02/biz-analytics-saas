# Business Analytics SaaS

A multi-tenant business analytics platform built for small businesses — especially Facebook-based sellers (bakeries, clothing shops, cosmetics sellers, home businesses) who need a simple way to track sales, customers, and revenue without spreadsheets.

Built as an end-to-end demonstration of production SaaS patterns: multi-tenancy, transactional data integrity, containerization, and honestly-scoped AI/ML features.

## What it does

- **Multi-tenant auth** — each business gets an isolated account; data is never accessible across tenants, enforced at the query level
- **Customer, product, and order management** — manual entry or bulk CSV import
- **Analytics dashboard** — revenue summaries, best-selling products, daily revenue trends
- **ML insights** — revenue forecasting, customer segmentation, and low-performer detection, with built-in honesty guardrails that refuse to show unreliable predictions when there isn't enough data yet, rather than faking confidence
- **CSV export** — download customers, products, or orders at any time
- **Audit log** — every create action is recorded per tenant
- **Subscription plans** — free tier usage limits (products/customers), ready for real billing integration
- **Facebook/Instagram sync (mocked)** — a structurally complete integration pipeline using realistic mock data, pending Meta Developer app approval for live API access

## Tech stack

**Backend**
- FastAPI (Python)
- PostgreSQL + SQLAlchemy
- JWT auth with bcrypt password hashing
- scikit-learn for forecasting
- Docker + Docker Compose

**Frontend**
- React + Vite
- Tailwind CSS
- React Router
- Recharts
- Axios

## Architecture

Multi-tenancy uses a shared-table design: every business-owned row (customers, products, orders, order items) carries a `tenant_id`, and every query is filtered by the authenticated user's tenant server-side — never trusted from client input.

See [ARCHITECTURE.md](./ARCHITECTURE.md) for the full data pipeline and notes on where Airflow, S3, and Kafka would plug in at larger scale.

## Running locally

### Backend

```bash
docker compose up --build
```

This starts the FastAPI API (port `8000`) and PostgreSQL (port `5432`) together, with a health check ensuring the API waits for the database to be ready.

API docs available at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Runs at `http://localhost:5173` (or the next available port).

## Project structure
biz-analytics-saas/
├── app/
│ ├── models/ # SQLAlchemy models
│ ├── routers/ # API endpoints
│ ├── core/ # Auth, limits, audit logging helpers
│ ├── ml/ # Forecasting and insights logic
│ ├── integrations/ # Mocked external integrations
│ └── main.py
├── frontend/
│ └── src/
│ ├── pages/ # Dashboard, Customers, Products, Orders, Insights
│ ├── components/ # Layout, ProtectedRoute
│ ├── context/ # Auth state
│ └── api/ # Axios client
├── Dockerfile
├── docker-compose.yml
└── ARCHITECTURE.md

## Notes on scope

This project was built incrementally in phases, each fully tested before moving to the next: authentication → data ingestion → analytics → containerization → external integration → ML insights → SaaS productization → frontend. A few things are intentionally scoped rather than fully built out, consistent with treating this as a real MVP:

- The Facebook integration uses realistic mock data rather than live API calls, since Meta's Graph API requires app review approval that takes days to weeks — the sync logic itself (find-or-create customers/products, price snapshotting) is fully real and would only need the mock data source swapped for a real one.
- Subscription plans have working usage-limit enforcement but no real payment processing wired up.
- Database schema changes currently use SQLAlchemy's `create_all()` rather than a migration tool like Alembic — fine for this stage, but a real next step for schema evolution.
