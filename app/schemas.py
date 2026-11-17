from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SupplierCreate(BaseModel):
    name: str
    country: Optional[str] = None


class SupplierRead(SupplierCreate):
    id: int
    created_at: datetime


class MaterialCreate(BaseModel):
    material_code: str = Field(..., min_length=3)
    supplier_id: Optional[int] = None
    chemistry: str
    lot_number: Optional[str] = None
    received_date: Optional[datetime] = None
    purity: Optional[float] = None
    storage_location: Optional[str] = None


class MaterialRead(MaterialCreate):
    id: int
    created_at: datetime


class FormulationCreate(BaseModel):
    name: str
    anode_material_id: int
    cathode_material_id: int
    electrolyte: str
    binder: Optional[str] = None
    notes: Optional[str] = None


class FormulationRead(FormulationCreate):
    id: int
    created_at: datetime


class CellCreate(BaseModel):
    cell_code: str
    formulation_id: int
    build_date: Optional[datetime] = None
    cell_type: str
    status: Optional[str] = "planned"
    notes: Optional[str] = None


class CellRead(CellCreate):
    id: int
    created_at: datetime


class TestResultCreate(BaseModel):
    test_code: str
    cell_id: int
    cycler: str
    cycle_count: int = 0
    capacity_mah: Optional[float] = None
    energy_wh: Optional[float] = None
    resistance_ohm: Optional[float] = None
    test_date: Optional[datetime] = None
    import_source: Optional[str] = None


class TestResultRead(TestResultCreate):
    id: int
    created_at: datetime


class ProcessStepCreate(BaseModel):
    cell_id: int
    step_name: str
    mixing_time_min: Optional[float] = None
    rpm: Optional[float] = None
    temperature_c: Optional[float] = None
    humidity_pct: Optional[float] = None
    web_speed_mms: Optional[float] = None
    coating_gap_mm: Optional[float] = None
    calendering_pressure_mpa: Optional[float] = None
    formation_charge_rate_c: Optional[float] = None
    rest_time_min: Optional[float] = None


class ProcessStepRead(ProcessStepCreate):
    id: int
    created_at: datetime
