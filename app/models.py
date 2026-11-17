"""SQLAlchemy models for BatteryLIMS PostgreSQL tables."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

SCHEMA = "battery_lims"


class Supplier(Base):
    __tablename__ = "suppliers"
    __table_args__ = {"schema": SCHEMA}
    supplier_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    supplier_name: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_name: Mapped[Optional[str]] = mapped_column(String(255))
    email: Mapped[Optional[str]] = mapped_column(String(255))
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    materials: Mapped[list["Material"]] = relationship(back_populates="supplier")


class Material(Base):
    __tablename__ = "materials"
    __table_args__ = (CheckConstraint("purity IS NULL OR (purity >= 0 AND purity <= 100)", name="ck_material_purity_pct"), Index("ix_materials_material_code", "material_code", unique=True), {"schema": SCHEMA})
    material_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    material_code: Mapped[str] = mapped_column(String(50), nullable=False)
    material_name: Mapped[str] = mapped_column(String(255), nullable=False)
    material_type: Mapped[str] = mapped_column(String(50), nullable=False)
    supplier_id: Mapped[Optional[int]] = mapped_column(ForeignKey(f"{SCHEMA}.suppliers.supplier_id"))
    lot_number: Mapped[Optional[str]] = mapped_column(String(100))
    purity: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 3))
    storage_location: Mapped[Optional[str]] = mapped_column(String(255))
    received_date: Mapped[Optional[datetime]] = mapped_column(Date)
    expiration_date: Mapped[Optional[datetime]] = mapped_column(Date)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    supplier: Mapped[Optional[Supplier]] = relationship(back_populates="materials")
    inventory: Mapped[list["Inventory"]] = relationship(back_populates="material", cascade="all, delete-orphan")
    formulation_components: Mapped[list["FormulationComponent"]] = relationship(back_populates="material")


class Inventory(Base):
    __tablename__ = "inventory"
    __table_args__ = (CheckConstraint("quantity IS NULL OR quantity >= 0", name="ck_inventory_nonnegative_quantity"), Index("ix_inventory_material_id", "material_id"), {"schema": SCHEMA})
    inventory_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    material_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(f"{SCHEMA}.materials.material_id"), nullable=False)
    quantity: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 3))
    units: Mapped[Optional[str]] = mapped_column(String(20))
    location: Mapped[Optional[str]] = mapped_column(String(100))
    last_updated: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    material: Mapped[Material] = relationship(back_populates="inventory")


class Formulation(Base):
    __tablename__ = "formulations"
    __table_args__ = (Index("ix_formulations_formulation_code", "formulation_code", unique=True), {"schema": SCHEMA})
    formulation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    formulation_code: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_by: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    components: Mapped[list["FormulationComponent"]] = relationship(back_populates="formulation", cascade="all, delete-orphan")
    cells: Mapped[list["Cell"]] = relationship(back_populates="formulation")


class FormulationComponent(Base):
    __tablename__ = "formulation_components"
    __table_args__ = (UniqueConstraint("formulation_id", "material_id", name="uq_formulation_component_material"), CheckConstraint("wt_percent IS NULL OR (wt_percent >= 0 AND wt_percent <= 100)", name="ck_component_wt_percent"), {"schema": SCHEMA})
    component_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    formulation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(f"{SCHEMA}.formulations.formulation_id"), nullable=False)
    material_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(f"{SCHEMA}.materials.material_id"), nullable=False)
    wt_percent: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 4))
    formulation: Mapped[Formulation] = relationship(back_populates="components")
    material: Mapped[Material] = relationship(back_populates="formulation_components")


class Cell(Base):
    __tablename__ = "cells"
    __table_args__ = (Index("ix_cells_cell_code", "cell_code", unique=True), Index("ix_cells_formulation_id", "formulation_id"), {"schema": SCHEMA})
    cell_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cell_code: Mapped[str] = mapped_column(String(50), nullable=False)
    formulation_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey(f"{SCHEMA}.formulations.formulation_id"))
    cell_type: Mapped[Optional[str]] = mapped_column(String(50))
    build_date: Mapped[Optional[datetime]] = mapped_column(Date)
    operator_name: Mapped[Optional[str]] = mapped_column(String(100))
    status: Mapped[Optional[str]] = mapped_column(String(50), default="ACTIVE", server_default="ACTIVE")
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    formulation: Mapped[Optional[Formulation]] = relationship(back_populates="cells")
    manufacturing_runs: Mapped[list["CellManufacturing"]] = relationship(back_populates="cell", cascade="all, delete-orphan")
    experiment_links: Mapped[list["ExperimentCell"]] = relationship(back_populates="cell")
    test_executions: Mapped[list["TestExecution"]] = relationship(back_populates="cell")


class ManufacturingRun(Base):
    __tablename__ = "manufacturing_runs"
    __table_args__ = (Index("ix_manufacturing_runs_run_code", "run_code", unique=True), {"schema": SCHEMA})
    run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_code: Mapped[str] = mapped_column(String(50), nullable=False)
    process_step: Mapped[Optional[str]] = mapped_column(String(100))
    start_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    operator_name: Mapped[Optional[str]] = mapped_column(String(100))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    parameters: Mapped[list["ProcessParameter"]] = relationship(back_populates="run", cascade="all, delete-orphan")
    cells: Mapped[list["CellManufacturing"]] = relationship(back_populates="run", cascade="all, delete-orphan")


class ProcessParameter(Base):
    __tablename__ = "process_parameters"
    __table_args__ = (Index("ix_process_parameters_run_id", "run_id"), {"schema": SCHEMA})
    parameter_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey(f"{SCHEMA}.manufacturing_runs.run_id"))
    parameter_name: Mapped[Optional[str]] = mapped_column(String(100))
    parameter_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 6))
    unit: Mapped[Optional[str]] = mapped_column(String(40))
    run: Mapped[Optional[ManufacturingRun]] = relationship(back_populates="parameters")


class CellManufacturing(Base):
    __tablename__ = "cell_manufacturing"
    __table_args__ = (UniqueConstraint("cell_id", "run_id", name="uq_cell_manufacturing_pair"), {"schema": SCHEMA})
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cell_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey(f"{SCHEMA}.cells.cell_id"))
    run_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey(f"{SCHEMA}.manufacturing_runs.run_id"))
    cell: Mapped[Optional[Cell]] = relationship(back_populates="manufacturing_runs")
    run: Mapped[Optional[ManufacturingRun]] = relationship(back_populates="cells")


class Experiment(Base):
    __tablename__ = "experiments"
    __table_args__ = (Index("ix_experiments_experiment_code", "experiment_code", unique=True), {"schema": SCHEMA})
    experiment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    experiment_code: Mapped[str] = mapped_column(String(50), nullable=False)
    objective: Mapped[Optional[str]] = mapped_column(Text)
    created_by: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    cells: Mapped[list["ExperimentCell"]] = relationship(back_populates="experiment", cascade="all, delete-orphan")
    eln_entries: Mapped[list["ELNEntry"]] = relationship(back_populates="experiment", cascade="all, delete-orphan")


class ExperimentCell(Base):
    __tablename__ = "experiment_cells"
    __table_args__ = (UniqueConstraint("experiment_id", "cell_id", name="uq_experiment_cell_pair"), {"schema": SCHEMA})
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    experiment_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey(f"{SCHEMA}.experiments.experiment_id"))
    cell_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey(f"{SCHEMA}.cells.cell_id"))
    experiment: Mapped[Optional[Experiment]] = relationship(back_populates="cells")
    cell: Mapped[Optional[Cell]] = relationship(back_populates="experiment_links")


class ELNEntry(Base):
    __tablename__ = "eln_entries"
    __table_args__ = (Index("ix_eln_entries_experiment_id", "experiment_id"), {"schema": SCHEMA})
    eln_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    experiment_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey(f"{SCHEMA}.experiments.experiment_id"))
    title: Mapped[Optional[str]] = mapped_column(String(255))
    notebook_text: Mapped[Optional[str]] = mapped_column(Text)
    attachment_path: Mapped[Optional[str]] = mapped_column(Text)
    entered_by: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    experiment: Mapped[Optional[Experiment]] = relationship(back_populates="eln_entries")


class TestProtocol(Base):
    __tablename__ = "test_protocols"
    __table_args__ = {"schema": SCHEMA}
    protocol_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    protocol_name: Mapped[Optional[str]] = mapped_column(String(255))
    charge_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 3))
    discharge_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 3))
    voltage_min: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 3))
    voltage_max: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 3))
    temperature_c: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2))
    executions: Mapped[list["TestExecution"]] = relationship(back_populates="protocol")


class TestExecution(Base):
    __tablename__ = "test_executions"
    __table_args__ = (Index("ix_test_executions_cell_id", "cell_id"), {"schema": SCHEMA})
    execution_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cell_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey(f"{SCHEMA}.cells.cell_id"))
    protocol_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey(f"{SCHEMA}.test_protocols.protocol_id"))
    cycler_type: Mapped[Optional[str]] = mapped_column(String(50))
    start_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    raw_file_path: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[Optional[str]] = mapped_column(String(50))
    cell: Mapped[Optional[Cell]] = relationship(back_populates="test_executions")
    protocol: Mapped[Optional[TestProtocol]] = relationship(back_populates="executions")
    cycle_data: Mapped[list["CycleData"]] = relationship(back_populates="execution", cascade="all, delete-orphan")
    result: Mapped[Optional["TestResult"]] = relationship(back_populates="execution", cascade="all, delete-orphan", uselist=False)
    imports: Mapped[list["CycleImport"]] = relationship(back_populates="execution", cascade="all, delete-orphan")


class CycleData(Base):
    __tablename__ = "cycle_data"
    __table_args__ = (UniqueConstraint("execution_id", "cycle_number", name="uq_cycle_data_execution_cycle"), CheckConstraint("cycle_number IS NULL OR cycle_number >= 0", name="ck_cycle_number_nonnegative"), Index("ix_cycle_data_execution_cycle", "execution_id", "cycle_number"), {"schema": SCHEMA})
    cycle_data_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    execution_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey(f"{SCHEMA}.test_executions.execution_id"))
    cycle_number: Mapped[Optional[int]] = mapped_column(Integer)
    charge_capacity: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 6))
    discharge_capacity: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 6))
    coulombic_efficiency: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))
    energy_wh: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 6))
    dc_resistance: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 6))
    timestamp_recorded: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    execution: Mapped[Optional[TestExecution]] = relationship(back_populates="cycle_data")


class TestResult(Base):
    __tablename__ = "test_results"
    __table_args__ = (Index("ix_test_results_execution_id", "execution_id", unique=True), {"schema": SCHEMA})
    result_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    execution_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey(f"{SCHEMA}.test_executions.execution_id"), unique=True)
    initial_capacity: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 6))
    cycles_to_80_percent: Mapped[Optional[int]] = mapped_column(Integer)
    max_temperature: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 3))
    final_resistance: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 6))
    pass_fail: Mapped[Optional[str]] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    execution: Mapped[Optional[TestExecution]] = relationship(back_populates="result")


class CycleImport(Base):
    __tablename__ = "cycle_imports"
    __table_args__ = (Index("ix_cycle_imports_execution_id", "execution_id"), UniqueConstraint("execution_id", "sha256", name="uq_cycle_import_execution_sha256"), {"schema": SCHEMA})
    import_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    execution_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(f"{SCHEMA}.test_executions.execution_id"), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    raw_file_path: Mapped[str] = mapped_column(Text, nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    row_count: Mapped[int] = mapped_column(Integer, nullable=False)
    imported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    execution: Mapped[TestExecution] = relationship(back_populates="imports")
