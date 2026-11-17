import pandas as pd
import streamlit as st

st.set_page_config(page_title="BatteryLIMS", page_icon="🔋", layout="wide")
st.title("BatteryLIMS Dashboard")
st.caption("Battery R&D, material traceability, cell genealogy, and test operations")

st.info("Dashboard demo data only. Connect the API before using these figures for lab decisions.")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Materials", "—")
col2.metric("Cells", "—")
col3.metric("Test executions", "—")
col4.metric("Experiments", "—")

st.subheader("Example capacity retention")
sample = pd.DataFrame({"Cycle": range(1, 11), "Capacity retention": [1.00, .99, .97, .96, .94, .91, .89, .87, .84, .81]})
st.line_chart(sample.set_index("Cycle"))
st.caption("Illustrative series only; not connected to a cycler or database.")
