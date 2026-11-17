from sqlalchemy.orm import Session

from app.config import settings
from app.db import SessionLocal
from app.models import Cell, DOEExperiment, Formulation, Material, ProcessStep, Supplier, TestResult


def seed_data():
    db: Session = SessionLocal()
    try:
        if db.query(Supplier).first() is not None:
            return

        supplier = Supplier(name="Sila", country="USA")
        db.add(supplier)
        db.commit()
        db.refresh(supplier)

        graphite = Material(material_code="MAT0001", supplier_id=supplier.id, chemistry="Graphite", lot_number="LOT-001", purity=99.8, storage_location="Shelf-A1")
        nmc = Material(material_code="MAT0002", supplier_id=supplier.id, chemistry="NMC811", lot_number="LOT-002", purity=99.6, storage_location="Shelf-B2")
        db.add_all([graphite, nmc])
        db.commit()
        db.refresh(graphite)
        db.refresh(nmc)

        formulation = Formulation(name="F-001", anode_material_id=graphite.id, cathode_material_id=nmc.id, electrolyte="LP57", binder="PVDF", notes="Baseline graphite/NMC blend")
        db.add(formulation)
        db.commit()
        db.refresh(formulation)

        cell = Cell(cell_code="CELL0001", formulation_id=formulation.id, cell_type="Pouch", status="built")
        db.add(cell)
        db.commit()
        db.refresh(cell)

        test = TestResult(test_code="TEST0001", cell_id=cell.id, cycler="Arbin", cycle_count=120, capacity_mah=2200, energy_wh=8.3, resistance_ohm=0.025, import_source="demo_import")
        process = ProcessStep(cell_id=cell.id, step_name="mixing", mixing_time_min=15, rpm=800, temperature_c=30, humidity_pct=35)
        doe = DOEExperiment(name="DOE-001", objective="Evaluate silicon blend", variables="Si %: 5; Binder %: 3", initial_capacity=650, capacity_retention=92.4, resistance=0.018, cycle_life=500)
        db.add_all([test, process, doe])
        db.commit()
        print("Seed data inserted successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
