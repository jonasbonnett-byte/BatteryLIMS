import streamlit as st

st.title("Cells")
st.write("Track build dates, formulations, and cell status.")

st.dataframe(
    [
        {"Cell Code": "CELL0001", "Formulation": "F-001", "Status": "Built", "Type": "Prismatic"},
        {"Cell Code": "CELL0002", "Formulation": "F-002", "Status": "In Test", "Type": "Pouch"},
    ]
)
