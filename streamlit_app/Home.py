import os
import requests
import streamlit as st

API = os.getenv("API_URL", "http://localhost:8000").rstrip("/")
st.set_page_config(page_title="BatteryLIMS", page_icon="🔋", layout="wide")
st.title("🔋 BatteryLIMS")
st.caption("Materials • inventory • formulations • cells • manufacturing • ELN • cycler tests")


def get(path):
    try:
        response = requests.get(f"{API}{path}", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        st.error(f"API unavailable ({API}): {exc}. Start the stack with `docker compose up --build`.")
        return None


def post(path, payload):
    response = requests.post(f"{API}{path}", json=payload, timeout=20)
    response.raise_for_status()
    return response.json()


def options(path, label):
    rows = get(path)
    if rows is None:
        return [], {}
    return [r for r in rows], {label(r): r for r in rows}

with st.sidebar:
    st.success("Connected to API" if get("/health") else "API offline")
    section = st.radio("Workspace", ["Overview", "Materials & inventory", "Formulations", "Cells", "Manufacturing", "Experiments & ELN", "Cycler tests"])

if section == "Overview":
    data = {"Materials": get("/materials"), "Cells": get("/cells"), "Tests": get("/test-executions"), "Experiments": get("/experiments")}
    cols = st.columns(4)
    for col, (label, rows) in zip(cols, data.items()):
        col.metric(label, len(rows) if rows is not None else "—")
    st.subheader("Recent test executions")
    if data["Tests"] is not None:
        st.dataframe(data["Tests"], use_container_width=True)

elif section == "Materials & inventory":
    st.header("Materials and stock")
    with st.form("material_form"):
        code = st.text_input("Material code*", placeholder="MAT-0001")
        name = st.text_input("Material name*")
        kind = st.selectbox("Type", ["Cathode", "Anode", "Binder", "Electrolyte", "Additive", "Separator", "Solvent", "Other"])
        lot = st.text_input("Lot number")
        purity = st.number_input("Purity (%)", min_value=0.0, max_value=100.0, value=99.0)
        location = st.text_input("Storage location")
        submitted = st.form_submit_button("Register material")
    if submitted:
        try:
            post("/materials", {"material_code": code, "material_name": name, "material_type": kind, "lot_number": lot or None, "purity": purity, "storage_location": location or None})
            st.success("Material registered"); st.rerun()
        except requests.RequestException as exc: st.error(f"Could not register material: {exc} {getattr(exc, 'response', '')}")
    materials = get("/materials")
    if materials is not None:
        st.dataframe(materials, use_container_width=True)
        by_code = {f"{m['material_code']} — {m['material_name']}": m for m in materials}
        if by_code:
            with st.form("stock_form"):
                selection = st.selectbox("Material lot", list(by_code))
                quantity = st.number_input("Quantity to record", min_value=0.001, value=1.0)
                units = st.text_input("Units", value="g")
                place = st.text_input("Inventory location")
                stock_submit = st.form_submit_button("Add stock record")
            if stock_submit:
                try:
                    m = by_code[selection]
                    post(f"/materials/{m['material_id']}/inventory", {"material_id": m["material_id"], "quantity": quantity, "units": units, "location": place or None})
                    st.success("Inventory record added"); st.rerun()
                except requests.RequestException as exc: st.error(f"Could not add stock: {exc}")
    stock = get("/inventory")
    if stock is not None: st.subheader("Inventory records"); st.dataframe(stock, use_container_width=True)

elif section == "Formulations":
    st.header("Formulations")
    with st.form("formulation_form"):
        code = st.text_input("Formulation code*")
        description = st.text_area("Description")
        author = st.text_input("Created by")
        save = st.form_submit_button("Create formulation")
    if save:
        try: post("/formulations", {"formulation_code": code, "description": description or None, "created_by": author or None}); st.success("Formulation created"); st.rerun()
        except requests.RequestException as exc: st.error(f"Could not create formulation: {exc}")
    fs, fmap = options("/formulations", lambda f: f["formulation_code"])
    if fs: st.dataframe(fs, use_container_width=True)
    ms, mmap = options("/materials", lambda m: f"{m['material_code']} — {m['material_name']}")
    if fs and ms:
        with st.form("component_form"):
            fkey = st.selectbox("Formulation", list(fmap))
            mkey = st.selectbox("Component material lot", list(mmap))
            wt = st.number_input("Weight percent", min_value=0.0, max_value=100.0, value=100.0)
            save_component = st.form_submit_button("Add component")
        if save_component:
            try: post(f"/formulations/{fmap[fkey]['formulation_id']}/components", {"material_id": mmap[mkey]["material_id"], "wt_percent": wt}); st.success("Component added"); st.rerun()
            except requests.RequestException as exc: st.error(f"Could not add component: {exc}")
        fkey = st.selectbox("Show recipe for", list(fmap), key="recipe")
        components = get(f"/formulations/{fmap[fkey]['formulation_id']}/components")
        if components is not None: st.dataframe(components, use_container_width=True)

elif section == "Cells":
    st.header("Cell builds")
    fs, fmap = options("/formulations", lambda f: f["formulation_code"])
    with st.form("cell_form"):
        code = st.text_input("Cell code*")
        formulation = st.selectbox("Formulation", ["(none)"] + list(fmap))
        cell_type = st.selectbox("Cell type", ["coin", "pouch", "cylindrical", "other"])
        operator = st.text_input("Operator")
        build_date = st.date_input("Build date")
        save = st.form_submit_button("Register cell")
    if save:
        try:
            payload = {"cell_code": code, "formulation_id": fmap[formulation]["formulation_id"] if formulation != "(none)" else None, "cell_type": cell_type, "operator_name": operator or None, "build_date": build_date.isoformat()}
            post("/cells", payload); st.success("Cell registered"); st.rerun()
        except requests.RequestException as exc: st.error(f"Could not register cell: {exc}")
    cells = get("/cells")
    if cells is not None: st.dataframe(cells, use_container_width=True)

elif section == "Manufacturing":
    st.header("Manufacturing runs")
    with st.form("run_form"):
        code = st.text_input("Run code*"); step = st.text_input("Process step", placeholder="Mixing / coating / calendering / formation"); operator = st.text_input("Operator"); notes = st.text_area("Notes")
        save = st.form_submit_button("Create manufacturing run")
    if save:
        try: post("/manufacturing-runs", {"run_code": code, "process_step": step or None, "operator_name": operator or None, "notes": notes or None}); st.success("Run created"); st.rerun()
        except requests.RequestException as exc: st.error(f"Could not create run: {exc}")
    runs = get("/manufacturing-runs"); cells, cmap = options("/cells", lambda c: c["cell_code"])
    if runs is not None: st.dataframe(runs, use_container_width=True)
    if runs and cells:
        rmap = {r["run_code"]: r for r in runs}
        with st.form("link_run"):
            rk = st.selectbox("Run", list(rmap)); ck = st.selectbox("Cell", list(cmap)); link = st.form_submit_button("Link cell to run")
        if link:
            try: post(f"/manufacturing-runs/{rmap[rk]['run_id']}/cells", {"cell_id": cmap[ck]["cell_id"]}); st.success("Genealogy link added")
            except requests.RequestException as exc: st.error(f"Could not link cell: {exc}")
        with st.form("parameter_form"):
            rk2 = st.selectbox("Run for parameter", list(rmap), key="parameter_run"); pname = st.text_input("Parameter", placeholder="Mixing RPM"); pvalue = st.number_input("Value", value=0.0); unit = st.text_input("Unit", value="rpm"); add = st.form_submit_button("Add parameter")
        if add:
            try: post(f"/manufacturing-runs/{rmap[rk2]['run_id']}/parameters", {"parameter_name": pname, "parameter_value": pvalue, "unit": unit or None}); st.success("Parameter recorded")
            except requests.RequestException as exc: st.error(f"Could not add parameter: {exc}")

elif section == "Experiments & ELN":
    st.header("Experiments and notebook")
    with st.form("experiment_form"):
        code = st.text_input("Experiment code*"); objective = st.text_area("Objective"); author = st.text_input("Created by"); save = st.form_submit_button("Create experiment")
    if save:
        try: post("/experiments", {"experiment_code": code, "objective": objective or None, "created_by": author or None}); st.success("Experiment created"); st.rerun()
        except requests.RequestException as exc: st.error(f"Could not create experiment: {exc}")
    exps, emap = options("/experiments", lambda e: e["experiment_code"])
    if exps: st.dataframe(exps, use_container_width=True)
    cells, cmap = options("/cells", lambda c: c["cell_code"])
    if exps and cells:
        with st.form("exp_cell_form"):
            ek = st.selectbox("Experiment", list(emap)); ck = st.selectbox("Cell", list(cmap)); link = st.form_submit_button("Link cell to experiment")
        if link:
            try: post(f"/experiments/{emap[ek]['experiment_id']}/cells", {"cell_id": cmap[ck]["cell_id"]}); st.success("Cell linked")
            except requests.RequestException as exc: st.error(f"Could not link cell: {exc}")
    with st.form("eln_form"):
        ek = st.selectbox("ELN experiment", ["(none)"] + list(emap)); title = st.text_input("Entry title*"); text = st.text_area("Notebook text", height=180); entered = st.text_input("Entered by"); save_eln = st.form_submit_button("Save ELN entry")
    if save_eln:
        try: post("/eln-entries", {"experiment_id": emap[ek]["experiment_id"] if ek != "(none)" else None, "title": title, "notebook_text": text, "entered_by": entered or None}); st.success("ELN entry saved"); st.rerun()
        except requests.RequestException as exc: st.error(f"Could not save entry: {exc}")
    entries = get("/eln-entries")
    if entries is not None: st.dataframe(entries, use_container_width=True)

elif section == "Cycler tests":
    st.header("Test protocols, executions, and cycle imports")
    with st.form("protocol_form"):
        protocol_name = st.text_input("Protocol name*"); c_rate = st.number_input("Charge rate (C)", min_value=0.0, value=0.5); d_rate = st.number_input("Discharge rate (C)", min_value=0.0, value=0.5); vmin = st.number_input("Voltage min (V)", min_value=0.0, value=2.5); vmax = st.number_input("Voltage max (V)", min_value=0.0, value=4.2); temp = st.number_input("Temperature (°C)", value=25.0); save = st.form_submit_button("Create protocol")
    if save:
        try: post("/test-protocols", {"protocol_name": protocol_name, "charge_rate": c_rate, "discharge_rate": d_rate, "voltage_min": vmin, "voltage_max": vmax, "temperature_c": temp}); st.success("Protocol created"); st.rerun()
        except requests.RequestException as exc: st.error(f"Could not create protocol: {exc}")
    protocols, pmap = options("/test-protocols", lambda p: p["protocol_name"]); cells, cmap = options("/cells", lambda c: c["cell_code"])
    if protocols and cells:
        with st.form("execution_form"):
            ck = st.selectbox("Cell for test", list(cmap)); pk = st.selectbox("Protocol", list(pmap)); cycler = st.selectbox("Cycler", ["Arbin", "Maccor", "Neware", "Other"]); create = st.form_submit_button("Create test execution")
        if create:
            try: post("/test-executions", {"cell_id": cmap[ck]["cell_id"], "protocol_id": pmap[pk]["protocol_id"], "cycler_type": cycler, "status": "PLANNED"}); st.success("Test execution created"); st.rerun()
            except requests.RequestException as exc: st.error(f"Could not create execution: {exc}")
    executions = get("/test-executions")
    if executions is not None:
        st.dataframe(executions, use_container_width=True)
        if executions:
            emap2 = {str(e["execution_id"]): e for e in executions}
            with st.form("csv_import"):
                selected = st.selectbox("Execution", list(emap2)); cycler_type = st.selectbox("Source cycler", ["Arbin", "Maccor", "Neware", "Other"]); upload = st.file_uploader("Upload one-row-per-cycle CSV", type=["csv"]); import_button = st.form_submit_button("Import cycle data")
            if import_button and upload:
                try:
                    response = requests.post(f"{API}/test-executions/{selected}/import-csv", params={"cycler_type": cycler_type}, files={"file": (upload.name, upload.getvalue(), "text/csv")}, timeout=120)
                    response.raise_for_status(); st.success(f"Imported {response.json()['rows_imported']} cycle rows"); st.rerun()
                except requests.RequestException as exc: st.error(f"Import failed: {exc} — {getattr(exc, 'response', None).text if getattr(exc, 'response', None) else ''}")
            selected_cycle = st.selectbox("View cycles for execution", list(emap2), key="cycle_view")
            cycles = get(f"/test-executions/{selected_cycle}/cycles")
            if cycles is not None: st.dataframe(cycles, use_container_width=True)
