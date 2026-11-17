# BatteryLIMS — run it locally

BatteryLIMS provides a local PostgreSQL database, API, and Streamlit interface for battery R&D tracking. This is an early prototype: use test data until you have validated permissions, backups, audit requirements, vendor-specific imports, and data retention for your lab.

## Start the complete system (recommended)

Install Docker Desktop (or Docker Engine with Compose), clone this repository, then run:

```bash
cp .env.example .env
docker compose up --build
```

Open:
- Dashboard: http://localhost:8501
- API documentation: http://localhost:8000/docs
- Health check: http://localhost:8000/health

Stop with `Ctrl+C`; run `docker compose down` to stop services. Database files persist in the Docker volume. To permanently reset local data, run `docker compose down -v` (destructive).

The default password is for local development only. Change `POSTGRES_PASSWORD` in `.env` before exposing services beyond your machine. Do not expose this prototype directly to the internet.

## Start without Docker for the app

Run PostgreSQL locally, create an empty `batterylims` database, then:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

In another terminal run `streamlit run streamlit_app/Home.py`. Set `DATABASE_URL` and `API_URL` in `.env` if your local configuration differs.

## Workflows available in the UI

- Register suppliers/material lots and inventory records
- Create formulations and add material components
- Register cells and link them to formulations
- Create manufacturing runs, associate cells, and record process parameters
- Create experiments, link cells, and record ELN entries
- Define test protocols, create test executions, and import cycle-summary CSVs
- Browse cycle records and operational lists

The API validates required fields and unique codes. It does not yet include authentication, role permissions, append-only inventory transactions, attachment upload, automatic summary result calculation, or production-ready audit trail.

## Cycler CSV import requirements

Import requires a CSV with one summary row per cycle and a recognized cycle column (`cycle`, `cycle index`, `cycle_number`, etc.). Common capacity, energy, resistance, efficiency, and timestamp headers are normalized. Values are preserved as supplied; confirm units and vendor-specific column meaning before importing. Raw uploaded CSVs are stored in `data/cycler` and linked to the execution. Exact duplicate uploads for one execution are rejected. This is a generic summary-data importer, not a validated Arbin/Maccor/Neware parser or raw time-series importer.

## Development and tests

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest
```

Database migrations are applied automatically when the Compose API starts. For local app runs, use `alembic upgrade head` before starting the API.
