import streamlit as st

st.title("Materials")
st.write("Track material lots, suppliers, and chemistry inventory.")

st.dataframe(
    [
        {"Material Code": "MAT0001", "Chemistry": "Graphite", "Supplier": "Sila", "Purity": "99.8%"},
        {"Material Code": "MAT0002", "Chemistry": "NMC811", "Supplier": "Umicore", "Purity": "99.6%"},
    ]
)
