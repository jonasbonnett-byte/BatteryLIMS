# BatteryLIMS

BatteryLIMS is a personal battery R&D platform for material traceability, cell genealogy, cycler data ingestion, process tracking, analytics, and DOE-driven optimization.

## Project goal

Create a lightweight but industry-inspired battery lab management stack that combines:

- LIMS for material and sample traceability
- ELN for experimental notes and procedures
- MES-lite for manufacturing process tracking
- Cycler import pipeline for Arbin, Maccor, and Neware files
- Python analytics for cycle life and performance modeling
- Streamlit dashboard for operational visibility
- PostgreSQL as the single source of truth

## Architecture

- API: FastAPI
- Database: PostgreSQL + SQLAlchemy
- Migrations: Alembic
- Dashboard: Streamlit
- Analytics: pandas, numpy, scipy, scikit-learn
- ETL: Python batch ingestion for cycler exports

## Project plan

### Phase 1 — Foundation
- Set up repository, dependencies, database, and migration flow
- Design core entities: materials, formulations, cells, tests, process records
- Create baseline CRUD endpoints

### Phase 2 — Data ingestion
- Build CSV/XLSX import scripts for Arbin, Maccor, and Neware test exports
- Map raw cycler data into normalized `test_results` tables
- Add validation and data quality checks

### Phase 3 — Analytics and ML
- Compute capacity retention, cycle life, and coulombic efficiency
- Build regression models for cycle life and performance prediction
- Track DOE factors and responses

### Phase 4 — Manufacturing intelligence
- Add process variables and genealogy tracking
- Correlate mixing, coating, calendering, and formation parameters with outcomes
- Build yield and scrap insights

### Phase 5 — Reporting and operations
- Streamlit dashboards for R&D, process, and inventory summaries
- Generate reports and export CSV summaries for JMP or Power BI

## Repository layout

- `app/` — FastAPI app and database models
- `streamlit_app/` — dashboard front-end
- `scripts/` — utilities and seed scripts
- `alembic/` — migrations for schema changes
- `docker-compose.yml` — local PostgreSQL environment

## Quick start

1. Create the local environment
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Start PostgreSQL
   ```bash
   docker compose up -d postgres
   ```

3. Copy environment settings
   ```bash
   cp .env.example .env
   ```

4. Initialize database
   ```bash
   alembic upgrade head
   ```

5. Start the API
   ```bash
   uvicorn app.main:app --reload
   ```

6. Start the dashboard
   ```bash
   streamlit run streamlit_app/Home.py
   ```

## Example data model

Core domain objects:

- `materials`: supplier, lot, chemistry, purity
- `formulations`: anode, cathode, electrolyte, binder
- `cells`: cell code, build date, cell type, status
- `test_results`: capacity, energy, resistance, cycle count, cycler source
- `process_steps`: mixing, coating, calendering, formation metadata
- `doe_experiments`: DOE factors and responses

## Suggested next milestones

- Add strong validation for material traceability and cell genealogy
- Build an upload UI for cycler files
- Add JWT-based user auth for lab users
- Add CSV export for JMP and reporting workflows
- Add ML model endpoint for pre-build predictions

## License

This project is intended as a portfolio and applied R&D starter project.
