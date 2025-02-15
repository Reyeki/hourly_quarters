import streamlit as st
import pandas as pd
import plotly.express as px
st.title("Dates of Occurrences")

# ✅ Authentication check
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("You must log in first!")
    st.stop()

st.title("Main Page")

if 'filtered_data' in st.session_state and st.session_state.filtered_data is not None:
    filtered_df = st.session_state.filtered_data

    # Show date statistics
    st.subheader("Filtered Dates")
    st.dataframe(filtered_df[['Instrument', 'Date', 'Day of Week', 'contract']])
else:
    st.write("Please apply filters on the main page first")
