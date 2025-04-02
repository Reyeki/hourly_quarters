import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(layout='wide')

# ✅ Store username-password pairs
USER_CREDENTIALS = {
    "badboyz": "bangbang",
}

# ✅ Initialize session state for authentication
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "username" not in st.session_state:
    st.session_state["username"] = None

# ✅ Login form (only shown if not authenticated)
if not st.session_state["authenticated"]:
    st.title("Login to M7Box Database")

    # Username and password fields
    username = st.text_input("Username:")
    password = st.text_input("Password:", type="password")

    # Submit button
    if st.button("Login"):
        if username in USER_CREDENTIALS and password == USER_CREDENTIALS[username]:
            st.session_state["authenticated"] = True
            st.session_state["username"] = username  # Store the username
            st.success(f"Welcome, {username}! Redirecting...")
            st.rerun()  # Refresh to load the dashboard
        else:
            st.error("Incorrect username or password. Please try again.")

    # Stop execution if user is not authenticated
    st.stop()

# ✅ If authenticated, show the full app
st.sidebar.success(f"Logged in as: **{st.session_state['username']}**")
st.title("Quartal Database")

# ✅ Logout button in the sidebar
if st.sidebar.button("Logout"):
    st.session_state["authenticated"] = False
    st.session_state["username"] = None
    st.rerun()

# Upload CSV File
url = "https://raw.githubusercontent.com/TuckerArrants/hourly_quarters/refs/heads/main/NQ_Hourly_Quartal_1min_Processed_from_2016.csv"
uploaded_file = pd.read_csv(url)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    ### **Sidebar: Select Instrument and DR Range**
    instrument_options = df['Instrument'].dropna().unique().tolist()
    selected_instrument = st.sidebar.selectbox("Select Instrument", instrument_options)
    hour_options = ['All'] + list(range(0, 24))
    selected_hour= st.sidebar.selectbox("Select Hour", hour_options)
    day_options = ['All'] + ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    selected_day = st.sidebar.selectbox("Day of Week", day_options)

    ### **Main Panel: Filters Above Graph**
    col1, col2 = st.columns(2)
