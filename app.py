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
    st.title("Login to Database")

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
url = "https://raw.githubusercontent.com/TuckerArrants/hourly_quarters/refs/heads/main/Merged_Hourly_Quartal_1min_Processed_from_2016.csv"
df = pd.read_csv(url)

if df is not None:

    ### **Sidebar: Select Instrument and DR Range**
    instrument_options = df['Instrument'].dropna().unique().tolist()
    selected_instrument = st.sidebar.selectbox("Select Instrument", instrument_options)
    hour_options = ['All'] + list(range(0, 24))
    selected_hour = st.sidebar.selectbox("Select Hour", hour_options)
    day_options = ['All'] + ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    selected_day = st.sidebar.selectbox("Day of Week", day_options)

    # Centered line with four Q-direction dropdowns
    st.markdown("### Filter by Quartal Directions")
    q_col1, q_col2, q_col3, q_col4, _ = st.columns([1, 1, 1, 1, 2])  # Extra column for centering

    q1_filter = q_col1.selectbox("Q1", options=["All"] + sorted(df["Q1_direction"].dropna().unique().tolist()))
    q2_filter = q_col2.selectbox("Q2", options=["All"] + sorted(df["Q2_direction"].dropna().unique().tolist()))
    q3_filter = q_col3.selectbox("Q3", options=["All"] + sorted(df["Q3_direction"].dropna().unique().tolist()))
    q4_filter = q_col4.selectbox("Q4", options=["All"] + sorted(df["Q4_direction"].dropna().unique().tolist()))

    ###  Apply Filters
    filtered_df = df[df['Instrument'] == selected_instrument]

    # Optional: Apply hour filter (if it's not "All")
    if selected_hour != 'All':
        # Assumes you have a column like 'Hour' as int. If not, adapt accordingly.
        filtered_df = filtered_df[filtered_df['hour'] == selected_hour]

    # Optional: Apply day filter (if it's not "All")
    if selected_day != 'All':
        # Assumes you have a column like 'Day' with string values like 'Monday'
        filtered_df = filtered_df[filtered_df['day_of_week'] == selected_day]

    # Filter by Q directions
    if q1_filter != "All":
        filtered_df = filtered_df[filtered_df['Q1_direction'] == q1_filter]
    if q2_filter != "All":
        filtered_df = filtered_df[filtered_df['Q2_direction'] == q2_filter]
    if q3_filter != "All":
        filtered_df = filtered_df[filtered_df['Q3_direction'] == q3_filter]
    if q4_filter != "All":
        filtered_df = filtered_df[filtered_df['Q4_direction'] == q4_filter]

    # Calculate probability distributions for "low bucket" and "high bucket"
    low_counts = filtered_df["low_bucket"].value_counts(normalize=True).reset_index()
    low_counts.columns = ["value", "probability"]

    high_counts = filtered_df["high_bucket"].value_counts(normalize=True).reset_index()
    high_counts.columns = ["value", "probability"]

    # Create a bar chart for "low bucket" probabilities with text annotations
    desired_order = ["Q1", "Q2", "Q3", "Q4"]
    fig_low = px.bar(
        low_counts,
        x="value",
        y="probability",
        title="Probability Distribution of Low Bucket",
        labels={"value": "Low Bucket", "probability": "Probability"},
        # Format the probability as a percentage (e.g., "12.34%")
        text=low_counts["probability"].apply(lambda x: f"{x:.2%}")
    )
    # Position the text annotations outside the bars
    fig_low.update_traces(textposition="outside")
    fig_low.update_layout(
    xaxis=dict(
        categoryorder='array',
        categoryarray=desired_order
    )
)

    # Create a bar chart for "high bucket" probabilities with text annotations
    fig_high = px.bar(
        high_counts,
        x="value",
        y="probability",
        title="Probability Distribution of High Bucket",
        labels={"value": "High Bucket", "probability": "Probability"},
        text=high_counts["probability"].apply(lambda x: f"{x:.2%}")
    )
    fig_high.update_traces(textposition="outside")
    fig_high.update_layout(
    xaxis=dict(
        categoryorder='array',
        categoryarray=desired_order
    )
)

    # Display the two charts side by side using st.columns
    col1, col2 = st.columns(2)
    col1.plotly_chart(fig_low, use_container_width=True)
    col2.plotly_chart(fig_high, use_container_width=True)

# Calculate distribution of hour_direction in the filtered data
hour_direction_counts = filtered_df['hour_direction'].value_counts().reset_index()
hour_direction_counts.columns = ['direction', 'count']

# Create a pie chart using Plotly
fig_pie = px.pie(
    hour_direction_counts,
    names='direction',
    values='count',
    title='Hour Direction Distribution',
    hole=0.3  # Optional: Makes it a donut chart. Remove if you want a solid pie.
)

# Display the pie chart full-width
st.plotly_chart(fig_pie, use_container_width=True)
