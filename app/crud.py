from sqlalchemy.orm import Session

from app.models import Cell, Formulation, Material, ProcessStep, Supplier, TestResult


def create_supplier(db: Session, supplier_data: dict):
    supplier = Supplier(**supplier_data)
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


def get_suppliers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Supplier).offset(skip).limit(limit).all()


def create_material(db: Session, material_data: dict):
    material = Material(**material_data)
    db.add(material)
    db.commit()
    db.refresh(material)
    return material


def get_materials(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Material).offset(skip).limit(limit).all()


def create_formulation(db: Session, formulation_data: dict):
    formulation = Formulation(**formulation_data)
    db.add(formulation)
    db.commit()
    db.refresh(formulation)
    return formulation


def get_formulations(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Formulation).offset(skip).limit(limit).all()


def create_cell(db: Session, cell_data: dict):
    cell = Cell(**cell_data)
    db.add(cell)
    db.commit()
    db.refresh(cell)
    return cell


def get_cells(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Cell).offset(skip).limit(limit).all()


def create_test_result(db: Session, test_result_data: dict):
    test_result = TestResult(**test_result_data)
    db.add(test_result)
    db.commit()
    db.refresh(test_result)
    return test_result


def get_test_results(db: Session, skip: int = 0, limit: int = 200):
    return db.query(TestResult).offset(skip).limit(limit).all()


def create_process_step(db: Session, process_step_data: dict):
    process_step = ProcessStep(**process_step_data)
    db.add(process_step)
    db.commit()
    db.refresh(process_step)
    return process_step


def get_process_steps(db: Session, skip: int = 0, limit: int = 200):
    return db.query(ProcessStep).offset(skip).limit(limit).all()
