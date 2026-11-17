# BatteryLIMS — run it locally

BatteryLIMS provides a local PostgreSQL database, API, and Streamlit interface for battery R&D tracking. This is an early prototype: use test data until you validate permissions, backups, audit requirements, vendor-specific imports, and data retention.

## Start the complete system

Install Docker Desktop (or Docker Engine with Compose), clone the repository, then run:

```bash
cp .env.example .env
docker compose up --build
```

Open dashboard at http://localhost:8501, API docs at http://localhost:8000/docs, and health check at http://localhost:8000/health. Stop with Ctrl+C. Data persists in the Docker volume. `docker compose down -v` permanently deletes local database data.

The default password is for local development only. Change `POSTGRES_PASSWORD` in `.env` before exposing services beyond your machine; do not expose this prototype directly to the internet.

## Load traceability demo data

After the services are running and migrations have completed, open a second terminal in the repository and run:

```bash
docker compose exec -T postgres psql -U postgres -d batterylims < scripts/seed_traceability_demo.sql
```

The seed script can be re-run without duplicating the demo business records. Refresh the dashboard to view suppliers/materials, inventory, formulations, ten cells, manufacturing genealogy, experiment/ELN data, and the sample test execution. Data is illustrative and should not be treated as measured performance.

## Workflows

The Streamlit app supports supplier/material registration, inventory records, formulation recipes, cell builds, manufacturing runs/parameters, experiment and ELN entry, protocols, test execution, and cycle-summary CSV import. API docs are available at `/docs`.

CSV imports require one summary row per cycle and recognized cycle-number headers. Confirm units and vendor column meaning before importing. Raw uploads are retained in `data/cycler`; this is not a validated vendor parser or raw time-series importer. Authentication, role permissions, append-only inventory transactions, attachment storage, and production-grade audit controls are not yet implemented.

## Development

```bash
pip install -r requirements.txt -r requirements-dev.txt
alembic upgrade head
pytest
```
