from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    country = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    materials = relationship("Material", back_populates="supplier")


class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    material_code = Column(String(50), unique=True, index=True, nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    chemistry = Column(String(150), nullable=False)
    lot_number = Column(String(100), nullable=True)
    received_date = Column(DateTime, nullable=True)
    purity = Column(Float, nullable=True)
    storage_location = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    supplier = relationship("Supplier", back_populates="materials")
    formulations = relationship("Formulation", back_populates="anode_material_rel")


class Formulation(Base):
    __tablename__ = "formulations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    anode_material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    cathode_material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    electrolyte = Column(String(200), nullable=False)
    binder = Column(String(200), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    anode_material_rel = relationship("Material", foreign_keys=[anode_material_id], back_populates="formulations")
    cathode_material_rel = relationship("Material", foreign_keys=[cathode_material_id])
    cells = relationship("Cell", back_populates="formulation")


class Cell(Base):
    __tablename__ = "cells"

    id = Column(Integer, primary_key=True, index=True)
    cell_code = Column(String(50), unique=True, index=True, nullable=False)
    formulation_id = Column(Integer, ForeignKey("formulations.id"), nullable=False)
    build_date = Column(DateTime, nullable=True)
    cell_type = Column(String(100), nullable=False)
    status = Column(String(50), default="planned", nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    formulation = relationship("Formulation", back_populates="cells")
    test_results = relationship("TestResult", back_populates="cell")
    process_steps = relationship("ProcessStep", back_populates="cell")


class TestResult(Base):
    __tablename__ = "test_results"

    id = Column(Integer, primary_key=True, index=True)
    test_code = Column(String(50), unique=True, index=True, nullable=False)
    cell_id = Column(Integer, ForeignKey("cells.id"), nullable=False)
    cycler = Column(String(50), nullable=False)
    cycle_count = Column(Integer, default=0, nullable=False)
    capacity_mah = Column(Float, nullable=True)
    energy_wh = Column(Float, nullable=True)
    resistance_ohm = Column(Float, nullable=True)
    test_date = Column(DateTime, nullable=True)
    import_source = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    cell = relationship("Cell", back_populates="test_results")


class ProcessStep(Base):
    __tablename__ = "process_steps"

    id = Column(Integer, primary_key=True, index=True)
    cell_id = Column(Integer, ForeignKey("cells.id"), nullable=False)
    step_name = Column(String(100), nullable=False)
    mixing_time_min = Column(Float, nullable=True)
    rpm = Column(Float, nullable=True)
    temperature_c = Column(Float, nullable=True)
    humidity_pct = Column(Float, nullable=True)
    web_speed_mms = Column(Float, nullable=True)
    coating_gap_mm = Column(Float, nullable=True)
    calendering_pressure_mpa = Column(Float, nullable=True)
    formation_charge_rate_c = Column(Float, nullable=True)
    rest_time_min = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    cell = relationship("Cell", back_populates="process_steps")


class DOEExperiment(Base):
    __tablename__ = "doe_experiments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    objective = Column(Text, nullable=True)
    variables = Column(Text, nullable=True)
    initial_capacity = Column(Float, nullable=True)
    capacity_retention = Column(Float, nullable=True)
    resistance = Column(Float, nullable=True)
    cycle_life = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
