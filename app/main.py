"""BatteryLIMS API."""

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Cell, Experiment, Formulation, Material, ManufacturingRun, Supplier, TestExecution
from app.schemas import (
    CellCreate, CellRead, ExperimentCreate, FormulationCreate, FormulationRead,
    MaterialCreate, MaterialRead, ManufacturingRunCreate, SupplierCreate, SupplierRead,
    TestExecutionCreate,
)

app = FastAPI(title="BatteryLIMS", version="0.2.0", description="Battery R&D traceability and test data API")


def _create(db: Session, model, values: dict):
    record = model(**values)
    db.add(record)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A referenced record is missing or a unique code already exists") from exc
    db.refresh(record)
    return record


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "BatteryLIMS API"}


@app.get("/suppliers", response_model=list[SupplierRead])
def list_suppliers(db: Session = Depends(get_db)):
    return db.query(Supplier).order_by(Supplier.supplier_id).limit(500).all()


@app.post("/suppliers", response_model=SupplierRead, status_code=201)
def create_supplier(payload: SupplierCreate, db: Session = Depends(get_db)):
    return _create(db, Supplier, payload.model_dump())


@app.get("/materials", response_model=list[MaterialRead])
def list_materials(db: Session = Depends(get_db)):
    return db.query(Material).order_by(Material.material_code).limit(500).all()


@app.post("/materials", response_model=MaterialRead, status_code=201)
def create_material(payload: MaterialCreate, db: Session = Depends(get_db)):
    return _create(db, Material, payload.model_dump())


@app.get("/formulations", response_model=list[FormulationRead])
def list_formulations(db: Session = Depends(get_db)):
    return db.query(Formulation).order_by(Formulation.formulation_code).limit(500).all()


@app.post("/formulations", response_model=FormulationRead, status_code=201)
def create_formulation(payload: FormulationCreate, db: Session = Depends(get_db)):
    return _create(db, Formulation, payload.model_dump())


@app.get("/cells", response_model=list[CellRead])
def list_cells(db: Session = Depends(get_db)):
    return db.query(Cell).order_by(Cell.cell_code).limit(500).all()


@app.post("/cells", response_model=CellRead, status_code=201)
def create_cell(payload: CellCreate, db: Session = Depends(get_db)):
    return _create(db, Cell, payload.model_dump())


@app.get("/manufacturing-runs")
def list_manufacturing_runs(db: Session = Depends(get_db)):
    return db.query(ManufacturingRun).order_by(ManufacturingRun.start_time.desc()).limit(500).all()


@app.post("/manufacturing-runs", status_code=201)
def create_manufacturing_run(payload: ManufacturingRunCreate, db: Session = Depends(get_db)):
    return _create(db, ManufacturingRun, payload.model_dump())


@app.post("/experiments", status_code=201)
def create_experiment(payload: ExperimentCreate, db: Session = Depends(get_db)):
    return _create(db, Experiment, payload.model_dump())


@app.post("/test-executions", status_code=201)
def create_test_execution(payload: TestExecutionCreate, db: Session = Depends(get_db)):
    return _create(db, TestExecution, payload.model_dump())
