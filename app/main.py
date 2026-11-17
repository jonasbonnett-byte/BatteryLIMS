from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.crud import create_cell, create_formulation, create_material, create_process_step, create_supplier, create_test_result, get_cells, get_formulations, get_materials, get_process_steps, get_suppliers, get_test_results
from app.db import get_db
from app.schemas import CellCreate, FormulationCreate, MaterialCreate, ProcessStepCreate, SupplierCreate, TestResultCreate

app = FastAPI(title="BatteryLIMS", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "BatteryLIMS API"}


@app.get("/suppliers")
def list_suppliers(db: Session = Depends(get_db)):
    return get_suppliers(db)


@app.post("/suppliers")
def create_supplier_endpoint(payload: SupplierCreate, db: Session = Depends(get_db)):
    return create_supplier(db, payload.model_dump())


@app.get("/materials")
def list_materials(db: Session = Depends(get_db)):
    return get_materials(db)


@app.post("/materials")
def create_material_endpoint(payload: MaterialCreate, db: Session = Depends(get_db)):
    return create_material(db, payload.model_dump())


@app.get("/formulations")
def list_formulations(db: Session = Depends(get_db)):
    return get_formulations(db)


@app.post("/formulations")
def create_formulation_endpoint(payload: FormulationCreate, db: Session = Depends(get_db)):
    return create_formulation(db, payload.model_dump())


@app.get("/cells")
def list_cells(db: Session = Depends(get_db)):
    return get_cells(db)


@app.post("/cells")
def create_cell_endpoint(payload: CellCreate, db: Session = Depends(get_db)):
    return create_cell(db, payload.model_dump())


@app.get("/test-results")
def list_test_results(db: Session = Depends(get_db)):
    return get_test_results(db)


@app.post("/test-results")
def create_test_result_endpoint(payload: TestResultCreate, db: Session = Depends(get_db)):
    return create_test_result(db, payload.model_dump())


@app.get("/process-steps")
def list_process_steps(db: Session = Depends(get_db)):
    return get_process_steps(db)


@app.post("/process-steps")
def create_process_step_endpoint(payload: ProcessStepCreate, db: Session = Depends(get_db)):
    return create_process_step(db, payload.model_dump())
