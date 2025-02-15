import streamlit as st
import pandas as pd 

st.set_page_config(page_title="M7Box Database", page_icon="📊", initial_sidebar_state="collapsed")

#Store username-password pairs
USER_CREDENTIALS = {
    "amer": "NQ",
    "nick": "NQ",
    "tucker": "gamma",
    "armando": "ES",
    "anand": "style"
}

# Initialize session state for authentication
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "username" not in st.session_state:
    st.session_state["username"] = None
if "csv_data" not in st.session_state:
    st.session_state["csv_data"] = None  #  Ensure CSV data state exists

# Show login screen if not authenticated
if not st.session_state["authenticated"]:
    st.title("Login")

    # Username and password fields
    username = st.text_input("Username:")
    password = st.text_input("Password:", type="password")

    # Submit button
    if st.button("Login"):
        if username in USER_CREDENTIALS and password == USER_CREDENTIALS[username]:
            st.session_state["authenticated"] = True
            st.session_state["username"] = username  # Store username
            st.success(f"Welcome, {username}! Redirecting...")
            st.rerun()  # Refresh the page after login
        else:
            st.error("Incorrect username or password. Please try again.")

    # Stop execution if user is not authenticated
    st.stop()

# If authenticated, show the main content
st.sidebar.success(f"Logged in as: **{st.session_state['username']}**")

# Logout button in the sidebar
if st.sidebar.button("Logout"):
    st.session_state["authenticated"] = False
    st.session_state["username"] = None
    st.rerun()

# App Content (Users Only)
st.title("M7Box Database")

# Upload CSV File
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.session_state["csv_data"] = df  # Store DataFrame in session state
    st.success("CSV file uploaded successfully! It is now accessible on other pages.")

# Show the uploaded file (for verification)
if st.session_state["csv_data"] is not None:
    st.write("Stored CSV Data:")
    st.dataframe(st.session_state["csv_data"])
