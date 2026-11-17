"""BatteryLIMS API for core laboratory workflows."""

import hashlib
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import (
    Cell, CellManufacturing, CycleData, ELNEntry, Experiment, ExperimentCell,
    Formulation, FormulationComponent, Inventory, ManufacturingRun, Material,
    ProcessParameter, Supplier, TestExecution, TestProtocol,
)
from app.schemas import (
    CellCreate, CellRead, ExperimentCreate, FormulationCreate, FormulationRead,
    MaterialCreate, MaterialRead, ManufacturingRunCreate, SupplierCreate, SupplierRead,
    TestExecutionCreate,
)
from app.services.cycler_import import import_cycler_csv
from app.workflow_schemas import (
    CellRunLinkCreate, ELNEntryCreate, ExperimentCellLinkCreate,
    FormulationComponentCreate, InventoryCreate, ProcessParameterCreate, TestProtocolCreate,
)

app = FastAPI(title="BatteryLIMS", version="0.3.0", description="Battery R&D traceability and test data API")
RAW_DATA_DIR = Path("data/cycler")


def _create(db: Session, model, values: dict):
    record = model(**values)
    db.add(record)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="A referenced record is missing or a unique code already exists") from exc
    db.refresh(record)
    return record


def _list(db: Session, model, order_by, limit: int = 500):
    return db.query(model).order_by(order_by).limit(limit).all()


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "BatteryLIMS API"}


@app.get("/suppliers", response_model=list[SupplierRead])
def list_suppliers(db: Session = Depends(get_db)):
    return _list(db, Supplier, Supplier.supplier_id)


@app.post("/suppliers", response_model=SupplierRead, status_code=201)
def create_supplier(payload: SupplierCreate, db: Session = Depends(get_db)):
    return _create(db, Supplier, payload.model_dump())


@app.get("/materials", response_model=list[MaterialRead])
def list_materials(db: Session = Depends(get_db)):
    return _list(db, Material, Material.material_code)


@app.post("/materials", response_model=MaterialRead, status_code=201)
def create_material(payload: MaterialCreate, db: Session = Depends(get_db)):
    return _create(db, Material, payload.model_dump())


@app.post("/materials/{material_id}/inventory", status_code=201)
def add_inventory(material_id: uuid.UUID, payload: InventoryCreate, db: Session = Depends(get_db)):
    if material_id != payload.material_id:
        raise HTTPException(422, "Material ID in path and body must match")
    return _create(db, Inventory, payload.model_dump())


@app.get("/inventory")
def list_inventory(db: Session = Depends(get_db)):
    return _list(db, Inventory, Inventory.inventory_id)


@app.get("/formulations", response_model=list[FormulationRead])
def list_formulations(db: Session = Depends(get_db)):
    return _list(db, Formulation, Formulation.formulation_code)


@app.post("/formulations", response_model=FormulationRead, status_code=201)
def create_formulation(payload: FormulationCreate, db: Session = Depends(get_db)):
    return _create(db, Formulation, payload.model_dump())


@app.get("/formulations/{formulation_id}/components")
def list_components(formulation_id: uuid.UUID, db: Session = Depends(get_db)):
    return db.query(FormulationComponent).filter_by(formulation_id=formulation_id).all()


@app.post("/formulations/{formulation_id}/components", status_code=201)
def add_component(formulation_id: uuid.UUID, payload: FormulationComponentCreate, db: Session = Depends(get_db)):
    return _create(db, FormulationComponent, {"formulation_id": formulation_id, **payload.model_dump()})


@app.get("/cells", response_model=list[CellRead])
def list_cells(db: Session = Depends(get_db)):
    return _list(db, Cell, Cell.cell_code)


@app.post("/cells", response_model=CellRead, status_code=201)
def create_cell(payload: CellCreate, db: Session = Depends(get_db)):
    return _create(db, Cell, payload.model_dump())


@app.get("/manufacturing-runs")
def list_runs(db: Session = Depends(get_db)):
    return _list(db, ManufacturingRun, ManufacturingRun.run_code)


@app.post("/manufacturing-runs", status_code=201)
def create_run(payload: ManufacturingRunCreate, db: Session = Depends(get_db)):
    return _create(db, ManufacturingRun, payload.model_dump())


@app.post("/manufacturing-runs/{run_id}/parameters", status_code=201)
def add_process_parameter(run_id: uuid.UUID, payload: ProcessParameterCreate, db: Session = Depends(get_db)):
    return _create(db, ProcessParameter, {"run_id": run_id, **payload.model_dump()})


@app.post("/manufacturing-runs/{run_id}/cells", status_code=201)
def link_cell_to_run(run_id: uuid.UUID, payload: CellRunLinkCreate, db: Session = Depends(get_db)):
    return _create(db, CellManufacturing, {"run_id": run_id, "cell_id": payload.cell_id})


@app.get("/experiments")
def list_experiments(db: Session = Depends(get_db)):
    return _list(db, Experiment, Experiment.created_at.desc())


@app.post("/experiments", status_code=201)
def create_experiment(payload: ExperimentCreate, db: Session = Depends(get_db)):
    return _create(db, Experiment, payload.model_dump())


@app.post("/experiments/{experiment_id}/cells", status_code=201)
def link_cell_to_experiment(experiment_id: uuid.UUID, payload: ExperimentCellLinkCreate, db: Session = Depends(get_db)):
    return _create(db, ExperimentCell, {"experiment_id": experiment_id, "cell_id": payload.cell_id})


@app.get("/eln-entries")
def list_eln_entries(db: Session = Depends(get_db)):
    return _list(db, ELNEntry, ELNEntry.created_at.desc())


@app.post("/eln-entries", status_code=201)
def create_eln_entry(payload: ELNEntryCreate, db: Session = Depends(get_db)):
    return _create(db, ELNEntry, payload.model_dump())


@app.get("/test-protocols")
def list_protocols(db: Session = Depends(get_db)):
    return _list(db, TestProtocol, TestProtocol.protocol_name)


@app.post("/test-protocols", status_code=201)
def create_protocol(payload: TestProtocolCreate, db: Session = Depends(get_db)):
    return _create(db, TestProtocol, payload.model_dump())


@app.get("/test-executions")
def list_executions(db: Session = Depends(get_db)):
    return _list(db, TestExecution, TestExecution.start_time.desc())


@app.post("/test-executions", status_code=201)
def create_execution(payload: TestExecutionCreate, db: Session = Depends(get_db)):
    return _create(db, TestExecution, payload.model_dump())


@app.get("/test-executions/{execution_id}/cycles")
def list_cycles(execution_id: uuid.UUID, db: Session = Depends(get_db)):
    return db.query(CycleData).filter_by(execution_id=execution_id).order_by(CycleData.cycle_number).limit(10000).all()


@app.post("/test-executions/{execution_id}/import-csv", status_code=201)
def import_cycles(execution_id: uuid.UUID, file: UploadFile = File(...), cycler_type: str = "unknown", db: Session = Depends(get_db)):
    execution = db.get(TestExecution, execution_id)
    if execution is None:
        raise HTTPException(404, "Test execution not found")
    if not file.filename or Path(file.filename).suffix.lower() != ".csv":
        raise HTTPException(415, "Upload a CSV cycle-summary export")
    content = file.file.read()
    if not content or len(content) > 50 * 1024 * 1024:
        raise HTTPException(413, "CSV must be non-empty and no larger than 50 MB")
    digest = hashlib.sha256(content).hexdigest()
    if db.query(CycleImport).filter_by(execution_id=execution_id, sha256=digest).first():
        raise HTTPException(409, "This exact file has already been imported for the execution")
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    raw_path = RAW_DATA_DIR / f"{uuid.uuid4()}.csv"
    raw_path.write_bytes(content)
    try:
        frame = import_cycler_csv(raw_path, cycler_type=cycler_type)
        if "cycle_number" not in frame or frame.empty:
            raise ValueError("CSV needs a recognized cycle number column and at least one row")
        if frame["cycle_number"].isna().any() or frame["cycle_number"].duplicated().any():
            raise ValueError("Cycle numbers must be present and unique (upload one summary row per cycle)")
        allowed = {"cycle_number", "charge_capacity", "discharge_capacity", "coulombic_efficiency", "energy_wh", "dc_resistance", "timestamp_recorded"}
        records = []
        for row in frame.to_dict(orient="records"):
            values = {key: (None if value is None or (isinstance(value, float) and value != value) else value) for key, value in row.items() if key in allowed}
            values["execution_id"] = execution_id
            if values.get("timestamp_recorded") is not None:
                values["timestamp_recorded"] = values["timestamp_recorded"].to_pydatetime()
            records.append(CycleData(**values))
        db.add_all(records)
        execution.cycler_type = cycler_type
        execution.raw_file_path = str(raw_path)
        execution.status = "IMPORTED"
        db.add(CycleImport(execution_id=execution_id, original_filename=Path(file.filename).name, raw_file_path=str(raw_path), sha256=digest, row_count=len(records), imported_at=datetime.now(timezone.utc)))
        db.commit()
        return {"execution_id": str(execution_id), "rows_imported": len(records), "sha256": digest, "raw_file_path": str(raw_path)}
    except (ValueError, KeyError) as exc:
        db.rollback()
        raw_path.unlink(missing_ok=True)
        raise HTTPException(422, str(exc)) from exc
    except IntegrityError as exc:
        db.rollback()
        raw_path.unlink(missing_ok=True)
        raise HTTPException(409, "Cycle data conflicts with existing imported data") from exc


# Imported here after declarations above to keep the API module's domain imports readable.
from app.models import CycleImport  # noqa: E402
