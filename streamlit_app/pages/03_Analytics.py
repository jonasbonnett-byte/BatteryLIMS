import streamlit as st

st.title("Analytics")
st.write("View retention, resistance growth, cycle life, and DOE response summaries.")

st.bar_chart({"Capacity Retention": [96, 94, 91, 87], "Resistance Growth": [1.2, 1.5, 2.0, 2.6]})
