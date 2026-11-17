import pandas as pd
import streamlit as st

st.set_page_config(page_title="BatteryLIMS", page_icon="🔋", layout="wide")

st.title("BatteryLIMS Dashboard")
st.caption("Battery R&D, materials traceability, and process intelligence")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Active Materials", 145)
col2.metric("Cells in Build", 38)
col3.metric("Avg Capacity Retention", "92.4%")
col4.metric("DOE Experiments", 12)

st.subheader("Core signals")

sample = pd.DataFrame(
    {
        "Cycle": list(range(1, 11)),
        "Capacity Retention": [1.00, 0.99, 0.97, 0.96, 0.94, 0.91, 0.89, 0.87, 0.84, 0.81],
    }
)

st.line_chart(sample.set_index("Cycle"))

st.subheader("Operational summary")
with st.container():
    st.write("- Material inventory and lot tracking")
    st.write("- Cell genealogy and build status")
    st.write("- Cycler import queue for Arbin/Maccor/Neware")
    st.write("- DOE and manufacturing parameter correlations")
