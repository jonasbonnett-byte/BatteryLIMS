"""Pydantic request/response models for the API."""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class SupplierCreate(BaseModel):
    supplier_name: str = Field(min_length=1, max_length=255)
    contact_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class SupplierRead(SupplierCreate, ORMModel):
    supplier_id: int
    created_at: datetime


class MaterialCreate(BaseModel):
    material_code: str = Field(min_length=1, max_length=50)
    material_name: str = Field(min_length=1, max_length=255)
    material_type: str = Field(min_length=1, max_length=50)
    supplier_id: Optional[int] = None
    lot_number: Optional[str] = None
    purity: Optional[Decimal] = Field(default=None, ge=0, le=100)
    storage_location: Optional[str] = None
    received_date: Optional[date] = None
    expiration_date: Optional[date] = None
    notes: Optional[str] = None


class MaterialRead(MaterialCreate, ORMModel):
    material_id: UUID
    created_at: datetime


class InventoryCreate(BaseModel):
    material_id: UUID
    quantity: Optional[Decimal] = Field(default=None, ge=0)
    units: Optional[str] = None
    location: Optional[str] = None


class FormulationCreate(BaseModel):
    formulation_code: str = Field(min_length=1, max_length=50)
    description: Optional[str] = None
    created_by: Optional[str] = None


class FormulationRead(FormulationCreate, ORMModel):
    formulation_id: UUID
    created_at: datetime


class CellCreate(BaseModel):
    cell_code: str = Field(min_length=1, max_length=50)
    formulation_id: Optional[UUID] = None
    cell_type: Optional[str] = None
    build_date: Optional[date] = None
    operator_name: Optional[str] = None
    status: Optional[str] = "ACTIVE"
    notes: Optional[str] = None


class CellRead(CellCreate, ORMModel):
    cell_id: UUID
    created_at: datetime


class ManufacturingRunCreate(BaseModel):
    run_code: str = Field(min_length=1, max_length=50)
    process_step: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    operator_name: Optional[str] = None
    notes: Optional[str] = None


class ExperimentCreate(BaseModel):
    experiment_code: str = Field(min_length=1, max_length=50)
    objective: Optional[str] = None
    created_by: Optional[str] = None


class ELNEntryCreate(BaseModel):
    experiment_id: Optional[UUID] = None
    title: Optional[str] = None
    notebook_text: Optional[str] = None
    attachment_path: Optional[str] = None
    entered_by: Optional[str] = None


class TestExecutionCreate(BaseModel):
    cell_id: Optional[UUID] = None
    protocol_id: Optional[UUID] = None
    cycler_type: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    raw_file_path: Optional[str] = None
    status: Optional[str] = "PLANNED"
