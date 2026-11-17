# BatteryLIMS

BatteryLIMS is a starter platform for battery R&D traceability: material lots and inventory, formulation recipes, cell genealogy, manufacturing runs, ELN records, DOE experiments, test protocols/executions, and cycle-level cycler data.

> **Prototype status:** This is a software scaffold, not a validated laboratory information system. Verify units, instrument export mappings, data integrity, access controls, retention, and backups before operational use. The Streamlit page currently shows illustrative data only.

## Project plan

### Milestone 1 — Foundation (implemented scaffold)
- PostgreSQL schema under `battery_lims`
- SQLAlchemy domain models and Alembic bootstrap migration
- FastAPI CRUD starter endpoints for suppliers, materials, formulations, cells, manufacturing runs, experiments, and test executions
- CSV cycler column normalization helpers and basic analytics
- Streamlit dashboard placeholder

### Milestone 2 — Lab workflows
- Add inventory transaction history (receipts, consumption, adjustments) rather than editing only a balance
- Add formulation component and cell-to-run APIs with genealogy validation
- Add ELN attachment storage integration and immutable audit events
- Add protocol management and test execution state transitions

### Milestone 3 — Data ingestion and quality
- Implement vendor-specific Arbin, Maccor, and Neware adapters with representative, authorized export fixtures
- Validate headers, units, duplicate cycles, timestamps, and source checksums before import
- Store raw files in durable object storage and link imports to execution records
- Make imports idempotent and preserve source provenance; never silently overwrite raw data

### Milestone 4 — Analytics and reporting
- Calculate retention, cycle-to-threshold, coulombic efficiency, resistance growth, and yield with defined conventions
- Export curated DOE tables to JMP/CSV; record factor/response units and experiment design metadata
- Connect Streamlit to read-only API endpoints; mark sample/demo data clearly

### Milestone 5 — Operational readiness
- Authentication/authorization, audit trail, secrets management, migrations/backups, monitoring, and tests
- Validate with lab users and instrument-specific fixtures before production deployment

## Data model

The PostgreSQL schema is `battery_lims`. UUIDs identify materials, formulations, cells, experiments, test protocols/executions, and result records; supplier and join/measurement records use integer keys. Recipe components represent arbitrary material mixtures. Cells link to manufacturing runs and experiments through association tables. Test executions link a cell to a protocol and cycler; `cycle_data` stores the per-cycle series and `test_results` stores one summary per execution.

| Area | Tables |
|---|---|
| Supplier/material/inventory | `suppliers`, `materials`, `inventory` |
| Formulations/cells | `formulations`, `formulation_components`, `cells` |
| MES-lite | `manufacturing_runs`, `process_parameters`, `cell_manufacturing` |
| DOE/ELN | `experiments`, `experiment_cells`, `eln_entries` |
| Testing | `test_protocols`, `test_executions`, `cycle_data`, `test_results` |

## Quick start

Requires Python 3.10+ and Docker Compose.

```bash
cp .env.example .env
docker compose up -d postgres
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Open API docs at `http://localhost:8000/docs`. In another terminal, run `streamlit run streamlit_app/Home.py`.

`DATABASE_URL` can be set in `.env`; the default local URL is `postgresql://postgres:postgres@localhost:5432/batterylims`. The application tables are created in the `battery_lims` PostgreSQL schema.

## Example API payloads

Create a supplier:

```json
{"supplier_name":"Example supplier","contact_name":"Lab contact","email":"lab@example.com"}
```

Create a material lot:

```json
{"material_code":"MAT-0001","material_name":"Graphite powder","material_type":"Anode","lot_number":"LOT-001","purity":99.8,"received_date":"2026-01-15"}
```

See the OpenAPI page for current endpoints and request shapes.

## Cycler importer

`app.services.cycler_import.import_cycler_csv(path, cycler_type="Arbin")` reads a CSV and normalizes common column names to `cycle_number`, `charge_capacity`, `discharge_capacity`, `coulombic_efficiency`, `energy_wh`, `dc_resistance`, and `timestamp_recorded`. Vendor exports differ, so confirm source units and headers and review the imported dataframe before saving it. The current helper does **not** persist results to the database and is not a certified vendor parser.

## Notes on schema evolution

The first Alembic revision bootstraps the model metadata for a new database. Treat released migrations as immutable; create explicit Alembic revisions for subsequent schema changes. `create_all` is used only for this initial empty-database bootstrap, not as a production migration strategy.
