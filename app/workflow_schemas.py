"""Additional request models for BatteryLIMS workflows."""

from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class InventoryCreate(BaseModel):
    material_id: UUID
    quantity: Decimal = Field(ge=0)
    units: str = Field(min_length=1, max_length=20)
    location: Optional[str] = None


class FormulationComponentCreate(BaseModel):
    material_id: UUID
    wt_percent: Decimal = Field(ge=0, le=100)


class ProcessParameterCreate(BaseModel):
    parameter_name: str = Field(min_length=1, max_length=100)
    parameter_value: Decimal
    unit: Optional[str] = None


class CellRunLinkCreate(BaseModel):
    cell_id: UUID


class ExperimentCellLinkCreate(BaseModel):
    cell_id: UUID


class ELNEntryCreate(BaseModel):
    experiment_id: Optional[UUID] = None
    title: str = Field(min_length=1, max_length=255)
    notebook_text: str = ""
    entered_by: Optional[str] = None
    attachment_path: Optional[str] = None


class TestProtocolCreate(BaseModel):
    protocol_name: str = Field(min_length=1, max_length=255)
    charge_rate: Optional[Decimal] = None
    discharge_rate: Optional[Decimal] = None
    voltage_min: Optional[Decimal] = None
    voltage_max: Optional[Decimal] = None
    temperature_c: Optional[Decimal] = None
