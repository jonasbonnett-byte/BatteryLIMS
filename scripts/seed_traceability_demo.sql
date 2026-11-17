-- BatteryLIMS Traceability Demo Seed Data
-- Safe to re-run: each demo record is inserted only when its business key is absent.
-- Run after migrations with: docker compose exec -T postgres psql -U postgres -d batterylims < scripts/seed_traceability_demo.sql
BEGIN;
CREATE SCHEMA IF NOT EXISTS battery_lims;
SET LOCAL search_path TO battery_lims, public;

-- Suppliers
INSERT INTO suppliers (supplier_name, contact_name, email)
SELECT v.supplier_name, v.contact_name, v.email
FROM (VALUES
 ('LFP Materials Inc', 'Sarah Chen', 'sales@lfpmaterials.com'),
 ('Graphite Solutions', 'Michael Reed', 'sales@graphitesolutions.com'),
 ('Electrolyte Partners', 'Emma Wilson', 'support@electrolytepartners.com'),
 ('Battery Chemicals', 'James Lee', 'info@batterychemicals.com')
) AS v(supplier_name, contact_name, email)
WHERE NOT EXISTS (SELECT 1 FROM suppliers s WHERE s.supplier_name = v.supplier_name);

-- Materials / supplier lots
INSERT INTO materials (material_code, material_name, material_type, supplier_id, lot_number, purity, storage_location)
SELECT v.material_code, v.material_name, v.material_type, s.supplier_id, v.lot_number, v.purity, v.location
FROM (VALUES
 ('MAT-LFP-001', 'LFP Cathode Powder', 'Cathode', 'LFP Materials Inc', 'LFP2026A', 99.500::numeric, 'DRYROOM-A1'),
 ('MAT-GRA-001', 'Graphite Anode Material', 'Anode', 'Graphite Solutions', 'GRA2026B', 99.200::numeric, 'DRYROOM-A2'),
 ('MAT-ELE-001', 'LP30 Electrolyte', 'Electrolyte', 'Electrolyte Partners', 'ELE2026C', 99.900::numeric, 'CHEM-CAB-01'),
 ('MAT-BIN-001', 'PVDF Binder', 'Binder', 'Battery Chemicals', 'BIN2026D', 98.700::numeric, 'CHEM-CAB-02')
) AS v(material_code, material_name, material_type, supplier_name, lot_number, purity, location)
JOIN suppliers s ON s.supplier_name = v.supplier_name
WHERE NOT EXISTS (SELECT 1 FROM materials m WHERE m.material_code = v.material_code);

-- Inventory balance snapshots
INSERT INTO inventory (material_id, quantity, units, location)
SELECT m.material_id, v.quantity, v.units, v.location
FROM (VALUES
 ('MAT-LFP-001', 5000::numeric, 'g', 'DRYROOM-A1'),
 ('MAT-GRA-001', 3000::numeric, 'g', 'DRYROOM-A2'),
 ('MAT-ELE-001', 1000::numeric, 'ml', 'CHEM-CAB-01'),
 ('MAT-BIN-001', 500::numeric, 'g', 'CHEM-CAB-02')
) AS v(material_code, quantity, units, location)
JOIN materials m ON m.material_code = v.material_code
WHERE NOT EXISTS (SELECT 1 FROM inventory i WHERE i.material_id = m.material_id AND i.units = v.units AND i.location = v.location);

-- Formulation recipe
INSERT INTO formulations (formulation_code, description, created_by)
SELECT 'FORM-001', 'Baseline LFP Cell Formulation', 'Jonas Bonnett'
WHERE NOT EXISTS (SELECT 1 FROM formulations WHERE formulation_code = 'FORM-001');

INSERT INTO formulation_components (formulation_id, material_id, wt_percent)
SELECT f.formulation_id, m.material_id, v.wt_percent
FROM (VALUES ('MAT-LFP-001', 94.0::numeric), ('MAT-BIN-001', 3.0::numeric), ('MAT-GRA-001', 3.0::numeric)) AS v(material_code, wt_percent)
JOIN formulations f ON f.formulation_code = 'FORM-001'
JOIN materials m ON m.material_code = v.material_code
WHERE NOT EXISTS (SELECT 1 FROM formulation_components fc WHERE fc.formulation_id = f.formulation_id AND fc.material_id = m.material_id);

-- Manufacturing run and parameters
INSERT INTO manufacturing_runs (run_code, process_step, operator_name, notes)
SELECT 'RUN-MIX-001', 'Slurry Mixing', 'Jonas Bonnett', 'Baseline mixing run'
WHERE NOT EXISTS (SELECT 1 FROM manufacturing_runs WHERE run_code = 'RUN-MIX-001');

INSERT INTO process_parameters (run_id, parameter_name, parameter_value, unit)
SELECT r.run_id, v.parameter_name, v.parameter_value, v.unit
FROM (VALUES ('Mix RPM', 1500::numeric, 'rpm'), ('Mix Time', 45::numeric, 'min'), ('Temperature', 23::numeric, 'C'), ('Humidity', 1::numeric, '%')) AS v(parameter_name, parameter_value, unit)
JOIN manufacturing_runs r ON r.run_code = 'RUN-MIX-001'
WHERE NOT EXISTS (SELECT 1 FROM process_parameters p WHERE p.run_id = r.run_id AND p.parameter_name = v.parameter_name);

-- Ten traceable coin cells
INSERT INTO cells (cell_code, formulation_id, cell_type, build_date, operator_name)
SELECT 'CELL-' || lpad(gs::text, 4, '0'), f.formulation_id, 'Coin', CURRENT_DATE, 'Jonas Bonnett'
FROM formulations f CROSS JOIN generate_series(1, 10) AS gs
WHERE f.formulation_code = 'FORM-001'
AND NOT EXISTS (SELECT 1 FROM cells c WHERE c.cell_code = 'CELL-' || lpad(gs::text, 4, '0'));

INSERT INTO cell_manufacturing (cell_id, run_id)
SELECT c.cell_id, r.run_id FROM cells c CROSS JOIN manufacturing_runs r
WHERE c.cell_code BETWEEN 'CELL-0001' AND 'CELL-0010' AND r.run_code = 'RUN-MIX-001'
AND NOT EXISTS (SELECT 1 FROM cell_manufacturing cm WHERE cm.cell_id = c.cell_id AND cm.run_id = r.run_id);

-- DOE experiment, cell links, and ELN entry
INSERT INTO experiments (experiment_code, objective, created_by)
SELECT 'EXP-LFP-001', 'Baseline LFP evaluation', 'Jonas Bonnett'
WHERE NOT EXISTS (SELECT 1 FROM experiments WHERE experiment_code = 'EXP-LFP-001');

INSERT INTO experiment_cells (experiment_id, cell_id)
SELECT e.experiment_id, c.cell_id FROM experiments e CROSS JOIN cells c
WHERE e.experiment_code = 'EXP-LFP-001' AND c.cell_code BETWEEN 'CELL-0001' AND 'CELL-0010'
AND NOT EXISTS (SELECT 1 FROM experiment_cells ec WHERE ec.experiment_id = e.experiment_id AND ec.cell_id = c.cell_id);

INSERT INTO eln_entries (experiment_id, title, notebook_text, entered_by)
SELECT e.experiment_id, 'Baseline Build', 'Built initial lot of ten LFP cells for cycling evaluation.', 'Jonas Bonnett'
FROM experiments e WHERE e.experiment_code = 'EXP-LFP-001'
AND NOT EXISTS (SELECT 1 FROM eln_entries n WHERE n.experiment_id = e.experiment_id AND n.title = 'Baseline Build');

-- Test protocol
INSERT INTO test_protocols (protocol_name, charge_rate, discharge_rate, voltage_min, voltage_max, temperature_c)
SELECT 'LFP-1C', 1.0, 1.0, 2.5, 4.2, 25
WHERE NOT EXISTS (SELECT 1 FROM test_protocols WHERE protocol_name = 'LFP-1C');

-- One representative execution, idempotently identified by cell/protocol/cycler.
INSERT INTO test_executions (cell_id, protocol_id, cycler_type, start_time, status, raw_file_path)
SELECT c.cell_id, p.protocol_id, 'Arbin', CURRENT_TIMESTAMP, 'Completed', '/data/arbin/CELL-0001.csv'
FROM cells c CROSS JOIN test_protocols p
WHERE c.cell_code = 'CELL-0001' AND p.protocol_name = 'LFP-1C'
AND NOT EXISTS (SELECT 1 FROM test_executions x WHERE x.cell_id = c.cell_id AND x.protocol_id = p.protocol_id AND x.cycler_type = 'Arbin');

-- Representative cycle summaries; original supplied capacities/energy/resistance are retained.
INSERT INTO cycle_data (execution_id, cycle_number, charge_capacity, discharge_capacity, coulombic_efficiency, energy_wh, dc_resistance, timestamp_recorded)
SELECT e.execution_id, v.cycle_number, v.charge_capacity, v.discharge_capacity,
       round((v.discharge_capacity / NULLIF(v.charge_capacity, 0)) * 100, 4),
       v.discharge_capacity * 3.3, v.resistance, CURRENT_TIMESTAMP
FROM test_executions e
CROSS JOIN (VALUES
 (1, 1.52::numeric, 1.50::numeric, 0.052::numeric),
 (2, 1.51::numeric, 1.49::numeric, 0.053::numeric),
 (3, 1.50::numeric, 1.48::numeric, 0.054::numeric),
 (4, 1.49::numeric, 1.47::numeric, 0.055::numeric),
 (5, 1.48::numeric, 1.46::numeric, 0.055::numeric),
 (100, 1.36::numeric, 1.33::numeric, 0.073::numeric),
 (200, 1.27::numeric, 1.20::numeric, 0.090::numeric)
) AS v(cycle_number, charge_capacity, discharge_capacity, resistance)
WHERE e.raw_file_path = '/data/arbin/CELL-0001.csv'
AND NOT EXISTS (SELECT 1 FROM cycle_data d WHERE d.execution_id = e.execution_id AND d.cycle_number = v.cycle_number);

INSERT INTO test_results (execution_id, initial_capacity, cycles_to_80_percent, max_temperature, final_resistance, pass_fail)
SELECT e.execution_id, 1.50, 187, 29.5, 0.090, 'PASS'
FROM test_executions e WHERE e.raw_file_path = '/data/arbin/CELL-0001.csv'
AND NOT EXISTS (SELECT 1 FROM test_results r WHERE r.execution_id = e.execution_id);

COMMIT;
