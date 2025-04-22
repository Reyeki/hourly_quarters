import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(layout='wide')

# ✅ Store username-password pairs
USER_CREDENTIALS = {
    "badboyz": "bangbang",
    "dreamteam" : "strike",
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
url_1h_eq = "https://raw.githubusercontent.com/TuckerArrants/hourly_quarters/main/ES_NQ_YM_Hourly_Quartal_1min_Processed_from_2016.csv"
url_1h_comm = "https://raw.githubusercontent.com/TuckerArrants/hourly_quarters/main/CL_GC_Hourly_Quartal_1min_Processed_from_2016.csv"
url_3h_eq = "https://raw.githubusercontent.com/TuckerArrants/hourly_quarters/main/ES_NQ_YM_3H_Quartal_1min_Processed_from_2016.csv"
url_3h_comm = "https://raw.githubusercontent.com/TuckerArrants/hourly_quarters/main/CL_GC_3H_Quartal_1min_Processed_from_2016.csv"

# merge separate dataframes
df_1h_eq = pd.read_csv(url_1h_eq)
df_1h_comm = pd.read_csv(url_1h_comm)
df_1h = pd.concat([df_1h_eq, df_1h_comm])

df_3h_eq = pd.read_csv(url_3h_eq)
df_3h_comm = pd.read_csv(url_3h_comm)
df_3h = pd.concat([df_3h_eq, df_3h_comm])

df_1h = df_1h.drop(columns=['Unnamed: 0', 'Unnamed: 0.1', 'phh_hit_time', 'phl_hit_time', 'date'])
df_3h = df_3h.drop(columns=['Unnamed: 0', 'Unnamed: 0.1', 'phh_hit_time', 'phl_hit_time', 'date'])

for col in [
    'Instrument','Q1_direction','Q2_direction','Q3_direction','Q4_direction',
    'ORB_direction','ORB_valid','hour_direction',
    'day_of_week','phh_hit_bucket','phl_hit_bucket',
    'low_bucket','high_bucket'
]:
    if col in df_1h:
        df_1h[col] = df_1h[col].astype('category')
    if col in df_3h:
        df_3h[col] = df_3h[col].astype('category')

df_1h["three_hour_start"] = (df_1h["hour"] // 3) * 3


if df_1h is not None:

    ### **Sidebar: Select Instrument and DR Range**
    instrument_options = df_1h['Instrument'].dropna().unique().tolist()
    selected_instrument = st.sidebar.selectbox("Select Instrument", instrument_options)
    hour_options = ['All'] + list(range(0, 24))
    hour_options.remove(17)
    three_hour_options = ['All'] + [0, 3, 6, 9, 12, 15, 18, 21]
    selected_hour = st.sidebar.selectbox("Select Hour", hour_options)
    selected_three_hour = st.sidebar.selectbox("Select 3H Start", three_hour_options)
    day_options = ['All'] + ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    selected_day = st.sidebar.selectbox("Day of Week", day_options)

    # Centered line with four Q-direction dropdowns
    st.markdown("### Hour Filters")
    q_col1, q_col2, q_col3, q_col4, q_col5, q_col6, q_col7, q_col8, q_col9, q_col10, q_col11 = st.columns([0.75, 0.75, 0.75, 0.75, 0.8, 0.75, 0.8, 0.7, 0.7, 1.2, 1.5])  # Extra column for centering

    q1_filter = q_col1.radio(
        "Q1",
        options=["All"] + sorted(df_1h["Q1_direction"].dropna().unique().tolist()),
        horizontal=False
    )
    q2_filter = q_col2.radio(
        "Q2",
        options=["All"] + sorted(df_1h["Q2_direction"].dropna().unique().tolist()),
        horizontal=False
    )
    q3_filter = q_col3.radio(
        "Q3",
        options=["All"] + sorted(df_1h["Q3_direction"].dropna().unique().tolist()),
        horizontal=False
    )
    q4_filter = q_col4.radio(
        "Q4",
        options=["All"] + sorted(df_1h["Q4_direction"].dropna().unique().tolist()),
        horizontal=False
    )
    
    prev_hour_filter = q_col5.radio("Prev. Hour Direction", 
                                    options=["All"] + ["Long", "Short", "Neutral"],
                                    horizontal=False)
    orb_filter = q_col6.radio("5m ORB Direction",
                              options=["All"] + sorted(df_1h["ORB_direction"].dropna().unique().tolist()),
                              horizontal=False)
    orb_true_filter = q_col7.radio("ORB True/False",
                              options=["All"] + sorted(df_1h["ORB_valid"].dropna().unique().tolist()),
                              horizontal=False)
    hourly_open_position = q_col10.radio("Hourly Open Position",
                              options=["All"] + ['0% >= x > 25%', '25% >= x > 50%', '50% >= x > 75%', '75% >= x > 100%'],
                              horizontal=False)

    phh_hit_time_filter = q_col8.radio("PHH Hit Time",
                        options=["All"] + sorted(df_1h["phh_hit_bucket"].dropna().unique().tolist()),
                        horizontal=False,
                        )
    phl_hit_time_filter = q_col9.radio("PHL Hit Time",
                        options=["All"] + sorted(df_1h["phl_hit_bucket"].dropna().unique().tolist()),
                        horizontal=False,
                        )
    
    
    with q_col11:
        low_filter = st.multiselect(
            "Low Exclusion",
            options=sorted(df_1h["low_bucket"].dropna().unique().tolist())
        )
        high_filter = st.multiselect(
            "High Exclusion",
            options=sorted(df_1h["high_bucket"].dropna().unique().tolist())
        )

    ###  Apply Filters
    filtered_df_1h = df_1h[df_1h['Instrument'] == selected_instrument]
    filtered_df_1h['prev_hour_direction'] = filtered_df_1h['hour_direction'].shift(1)

    # Optional: Apply hour filter (if it's not "All")
    if selected_hour != 'All':
        # Assumes you have a column like 'Hour' as int. If not, adapt accordingly.
        filtered_df_1h = filtered_df_1h[filtered_df_1h['hour'] == selected_hour]

    # Optional: Apply day filter (if it's not "All")
    if selected_day != 'All':
        # Assumes you have a column like 'Day' with string values like 'Monday'
        filtered_df_1h = filtered_df_1h[filtered_df_1h['day_of_week'] == selected_day]

    # Filter by Q directions
    if q1_filter != "All":
        filtered_df_1h = filtered_df_1h[filtered_df_1h['Q1_direction'] == q1_filter]
    if q2_filter != "All":
        filtered_df_1h = filtered_df_1h[filtered_df_1h['Q2_direction'] == q2_filter]
    if q3_filter != "All":
        filtered_df_1h = filtered_df_1h[filtered_df_1h['Q3_direction'] == q3_filter]
    if q4_filter != "All":
        filtered_df_1h = filtered_df_1h[filtered_df_1h['Q4_direction'] == q4_filter]
    if prev_hour_filter != 'All':
        filtered_df_1h = filtered_df_1h[filtered_df_1h['prev_hour_direction'] == prev_hour_filter] 
    if orb_filter != 'All':
        filtered_df_1h = filtered_df_1h[filtered_df_1h['ORB_direction'] == orb_filter] 
    if orb_true_filter != 'All':
        filtered_df_1h = filtered_df_1h[filtered_df_1h['ORB_valid'] == orb_true_filter] 
        
    if hourly_open_position != 'All':

        if hourly_open_position == '0% >= x > 25%':
            filtered_df_1h = filtered_df_1h[(filtered_df_1h['hourly_open_position'] >= 0) &
                                            (filtered_df_1h['hourly_open_position'] < 0.25)] 
        if hourly_open_position == '25% >= x > 50%':
            filtered_df_1h = filtered_df_1h[(filtered_df_1h['hourly_open_position'] >= 0.25) &
                                            (filtered_df_1h['hourly_open_position'] < 0.50)] 
        if hourly_open_position == '50% >= x > 75%':
            filtered_df_1h = filtered_df_1h[(filtered_df_1h['hourly_open_position'] >= 0.50) &
                                            (filtered_df_1h['hourly_open_position'] < 0.75)] 
        if hourly_open_position == '75% >= x > 100%':
            filtered_df_1h = filtered_df_1h[(filtered_df_1h['hourly_open_position'] >= 0.75) &
                                            (filtered_df_1h['hourly_open_position'] < 1.00)] 

    if phh_hit_time_filter != 'All':
        filtered_df_1h = filtered_df_1h[filtered_df_1h['phh_hit_bucket'] == phh_hit_time_filter] 
    if phl_hit_time_filter != 'All':
        filtered_df_1h = filtered_df_1h[filtered_df_1h['phl_hit_bucket'] == phl_hit_time_filter] 
        
    if low_filter:
        filtered_df_1h = filtered_df_1h[~filtered_df_1h['low_bucket'].isin(low_filter)]
    if high_filter:
        filtered_df_1h = filtered_df_1h[~filtered_df_1h['high_bucket'].isin(high_filter)]

        # ORB Validity Rate
    if 'ORB_valid' in filtered_df_1h.columns and not filtered_df_1h.empty:
        orb_counts = filtered_df_1h['ORB_valid'].value_counts(normalize=True)
        true_rate = orb_counts.get(True, 0)  # Default to 0 if True isn't present
        st.metric(label="ORB True Rate (1m Body Close)", value=f"{true_rate:.2%}")

    # Calculate probability distributions for "low bucket" and "high bucket"
    low_counts = filtered_df_1h["low_bucket"].value_counts(normalize=True).reset_index()
    low_counts.columns = ["value", "probability"]

    high_counts = filtered_df_1h["high_bucket"].value_counts(normalize=True).reset_index()
    high_counts.columns = ["value", "probability"]

    # Create a bar chart for "low bucket" probabilities with text annotations
    desired_order = ["Q1", "Q2", "Q3", "Q4"]
    fig_low = px.bar(
        low_counts,
        x="value",
        y="probability",
        title="Low of Hour Bucket",
        labels={"value": "Low Bucket", "probability": "Probability"},
        # Format the probability as a percentage (e.g., "12.34%")
        text=low_counts["probability"].apply(lambda x: f"{x:.2%}")
    )
    # Position the text annotations outside the bars
    fig_low.update_traces(textposition="outside")
    fig_low.update_layout(
        title={'x': 0.5, 'xanchor': 'center'},
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
        title="High of Hour Bucket",
        labels={"value": "High Bucket", "probability": "Probability"},
        text=high_counts["probability"].apply(lambda x: f"{x:.2%}")
    )
    fig_high.update_traces(textposition="outside")
    fig_high.update_layout(
        title={'x': 0.5, 'xanchor': 'center'},
        xaxis=dict(
        categoryorder='array',
        categoryarray=desired_order
    )
)

    # Here, the proportion (mean) of True values in a boolean series represents the percentage hit.
    phh_hit_pct = filtered_df_1h['phh_hit'].mean()
    phl_hit_pct = filtered_df_1h['phl_hit'].mean()
    pmid_hit_pct = filtered_df_1h['pmid_hit'].mean()
    
    # Create a DataFrame for plotting
    hit_pct_df = pd.DataFrame({
        'Hit Type': ['PHH Hit', 'PHL Hit', 'PHM Hit'],
        'Percentage': [phh_hit_pct, phl_hit_pct, pmid_hit_pct]
    })
    
    # Create a bar chart for hit percentages
    fig_hits = px.bar(
        hit_pct_df,
        x="Hit Type",
        y="Percentage",
        title="PHH / PHL / PHM Hit Rate",
        labels={"Hit Type": "Hit Type", "Percentage": "Hit Percentage"},
        text=hit_pct_df["Percentage"].apply(lambda x: f"{x:.2%}")
    )
    fig_hits.update_layout(title={'x': 0.5, 'xanchor': 'center'})

    fig_hits.update_traces(textposition='outside')
    fig_hits.update_yaxes(range=[0, 1])

    # Display the two charts side by side using st.columns
    col1, col2, col3 = st.columns((1, 2, 2))
    col1.plotly_chart(fig_hits, use_container_width=True)
    col2.plotly_chart(fig_low, use_container_width=True)
    col3.plotly_chart(fig_high, use_container_width=True)

    # Calculate distribution of hour_direction in the filtered data
    # Normalize direction values
    filtered_df_1h['hour_direction'] = filtered_df_1h['hour_direction'].str.strip().str.title()
    
    # Recalculate counts
    hour_direction_counts = filtered_df_1h['hour_direction'].value_counts().reset_index()
    hour_direction_counts.columns = ['direction', 'count']
    
    direction_order = ["Long", "Short", "Neutral"]
    direction_colors = {
        "Long": "#2ecc71",       # Green
        "Short": "#e74c3c",     # Red
        "Neutral": "#5d6d7e"   # Gray
    }
    
    
    st.markdown("### Quarter and Hourly Direction")
    
    quartals = ["Q1_direction", "Q2_direction", "Q3_direction", "Q4_direction", "hour_direction"]
    quartal_titles = ["Q1 Direction", "Q2 Direction", "Q3 Direction", "Q4 Direction", "Hour Direction"]
    
    q_cols = st.columns(5)
    
    for i, q_col in enumerate(quartals):
        # Normalize and count values
        filtered_df_1h[q_col] = filtered_df_1h[q_col].str.strip().str.title()
        q_counts = filtered_df_1h[q_col].value_counts().reset_index()
        q_counts.columns = ['direction', 'count']
    
        # Build pie chart
        fig_q = px.pie(
            q_counts,
            names='direction',
            values='count',
            color='direction',
            title=quartal_titles[i],
            hole=0.3,
            category_orders={'direction': direction_order},
            color_discrete_map=direction_colors
        )
        fig_q.update_traces(textinfo='percent+label')
        q_cols[i].plotly_chart(fig_q, use_container_width=True)
    
    st.caption(f"Sample size: {len(filtered_df_1h):,} rows")

if df_3h is not None:

    # Centered line with four Q-direction dropdowns
    st.markdown("### 3H Filters")
    q_col1_3h, q_col2_3h, q_col3_3h, q_col4_3h, q_col5_3h, q_col6_3h, q_col7_3h, q_col8_3h, q_col9_3h, q_col10_3h, q_col11_3h = st.columns([0.75, 0.75, 0.75, 0.75, 0.8, 0.75, 0.8, 0.7, 0.7, 1.2, 1.5]) # Extra column for centering

    q1_filter_3h = q_col1_3h.radio(
        "Q1",
        options=["All"] + sorted(df_3h["Q1_direction"].dropna().unique().tolist()),
        horizontal=False,
        key="q1_filter_3h"
    )
    q2_filter_3h = q_col2_3h.radio(
        "Q2",
        options=["All"] + sorted(df_3h["Q2_direction"].dropna().unique().tolist()),
        horizontal=False,
        key="q2_filter_3h"
    )
    q3_filter_3h = q_col3_3h.radio(
        "Q3",
        options=["All"] + sorted(df_3h["Q3_direction"].dropna().unique().tolist()),
        horizontal=False,
        key="q3_filter_3h"
    )
    q4_filter_3h = q_col4_3h.radio(
        "Q4",
        options=["All"] + sorted(df_3h["Q4_direction"].dropna().unique().tolist()),
        horizontal=False,
        key="q4_filter_3h"
    )
    
    prev_hour_filter_3h = q_col5_3h.radio("Prev. 3H Direction",
                                          options=["All"] + ["Long", "Short", "Neutral"],
                                          horizontal=False,
                                          key="prev_hour_filter_3h")
    orb_filter_3h = q_col6_3h.radio("15m ORB Direction",
                                    options=["All"] +sorted(df_3h["ORB_direction"].dropna().unique().tolist()),
                                    horizontal=False,
                                    key="orb_filter_3h")
    orb_true_filter_3h = q_col7_3h.radio("15m ORB True/False",
                                    options=["All"] +sorted(df_3h["ORB_valid"].dropna().unique().tolist()),
                                    horizontal=False,
                                    key="orb_true_3h")
    period_open_position = q_col10_3h.radio("3H Open Position",
                              options=["All"] + ['0% >= x > 25%', '25% >= x > 50%', '50% >= x > 75%', '75% >= x > 100%'],
                              horizontal=False)

    pph_hit_time_filter = q_col8_3h.radio("PPH Hit Time",
                        options=["All"] + sorted(df_3h["phh_hit_bucket"].dropna().unique().tolist()),
                        horizontal=False,
                        )
    ppl_hit_time_filter = q_col9_3h.radio("PPL Hit Time",
                        options=["All"] + sorted(df_3h["phl_hit_bucket"].dropna().unique().tolist()),
                        horizontal=False,
                        )
    

    with q_col11_3h:
        low_filter_3h = st.multiselect(
            "Low Exclusion",
            options=sorted(df_3h["low_bucket"].dropna().unique().tolist()),
            key="low_filter_3h"
        )
        high_filter_3h = st.multiselect(
            "High Exclusion",
            options=sorted(df_3h["high_bucket"].dropna().unique().tolist()),
            key="high_filter_3h"
        )


    ###  Apply Filters
    filtered_df_3h = df_3h[df_3h['Instrument'] == selected_instrument]
    filtered_df_3h['prev_three_hour_direction'] = filtered_df_3h['three_hour_direction'].shift(1)

    # Optional: Apply hour filter (if it's not "All")
    if selected_three_hour != 'All':
        # Assumes you have a column like 'Hour' as int. If not, adapt accordingly.
        filtered_df_3h = filtered_df_3h[filtered_df_3h['start_hour'] == selected_three_hour]

    # Optional: Apply day filter (if it's not "All")
    if selected_day != 'All':
        # Assumes you have a column like 'Day' with string values like 'Monday'
        filtered_df_3h = filtered_df_3h[filtered_df_3h['day_of_week'] == selected_day]

    # Filter by Q directions
    if q1_filter_3h != "All":
        filtered_df_3h = filtered_df_3h[filtered_df_3h['Q1_direction'] == q1_filter_3h]
    if q2_filter_3h != "All":
        filtered_df_3h = filtered_df_3h[filtered_df_3h['Q2_direction'] == q2_filter_3h]
    if q3_filter_3h != "All":
        filtered_df_3h = filtered_df_3h[filtered_df_3h['Q3_direction'] == q3_filter_3h]
    if q4_filter_3h != "All":
        filtered_df_3h = filtered_df_3h[filtered_df_3h['Q4_direction'] == q4_filter_3h]
    if prev_hour_filter_3h != 'All':
        filtered_df_3h = filtered_df_3h[filtered_df_3h['prev_three_hour_direction'] == prev_hour_filter_3h] 
    if orb_filter_3h != 'All':
        filtered_df_3h = filtered_df_3h[filtered_df_3h['ORB_direction'] == orb_filter_3h] 
    if orb_true_filter_3h != 'All':
        filtered_df_3h = filtered_df_3h[filtered_df_3h['ORB_valid'] == orb_true_filter_3h] 
        
    if period_open_position != 'All':

        if period_open_position == '0% >= x > 25%':
            filtered_df_3h = filtered_df_3h[(filtered_df_3h['three_hour_open_position'] >= 0) &
                                            (filtered_df_3h['three_hour_open_position'] < 0.25)] 
        if period_open_position == '25% >= x > 50%':
            filtered_df_3h = filtered_df_3h[(filtered_df_3h['three_hour_open_position'] >= 0.25) &
                                            (filtered_df_3h['three_hour_open_position'] < 0.50)] 
        if period_open_position == '50% >= x > 75%':
            filtered_df_3h = filtered_df_3h[(filtered_df_3h['three_hour_open_position'] >= 0.50) &
                                            (filtered_df_3h['three_hour_open_position'] < 0.75)] 
        if period_open_position == '75% >= x > 100%':
            filtered_df_3h = filtered_df_3h[(filtered_df_3h['three_hour_open_position'] >= 0.75) &
                                            (filtered_df_3h['three_hour_open_position'] < 1.00)] 

    if pph_hit_time_filter != 'All':
        filtered_df_3h = filtered_df_3h[filtered_df_3h['phh_hit_bucket'] == pph_hit_time_filter] 
    if ppl_hit_time_filter != 'All':
        filtered_df_3h = filtered_df_3h[filtered_df_3h['phl_hit_bucket'] == ppl_hit_time_filter] 
            
    if low_filter_3h:
        filtered_df_3h = filtered_df_3h[~filtered_df_3h['low_bucket'].isin(low_filter_3h)]
    if high_filter_3h:
        filtered_df_3h = filtered_df_3h[~filtered_df_3h['high_bucket'].isin(high_filter_3h)]

    # ORB Validity Rate
    if 'ORB_valid' in filtered_df_3h.columns and not filtered_df_3h.empty:
        orb_counts = filtered_df_3h['ORB_valid'].value_counts(normalize=True)
        true_rate = orb_counts.get(True, 0)  # Default to 0 if True isn't present
        st.metric(label="ORB True Rate (1m Body Close)", value=f"{true_rate:.2%}")

    # Calculate probability distributions for "low bucket" and "high bucket"
    low_counts = filtered_df_3h["low_bucket"].value_counts(normalize=True).reset_index()
    low_counts.columns = ["value", "probability"]

    high_counts = filtered_df_3h["high_bucket"].value_counts(normalize=True).reset_index()
    high_counts.columns = ["value", "probability"]

    # Create a bar chart for "low bucket" probabilities with text annotations
    desired_order = ["Q1", "Q2", "Q3", "Q4"]
    fig_low = px.bar(
        low_counts,
        x="value",
        y="probability",
        title="Low of 3H Bucket",
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
        title="High of 3H Bucket",
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

    # Here, the proportion (mean) of True values in a boolean series represents the percentage hit.
    pph_hit_pct = filtered_df_3h['phh_hit'].mean()
    ppl_hit_pct = filtered_df_3h['phl_hit'].mean()
    ppmid_hit_pct = filtered_df_3h['pmid_hit'].mean()
    
    # Create a DataFrame for plotting
    hit_pct_df = pd.DataFrame({
        'Hit Type': ['PPH Hit', 'PPL Hit', 'PPM Hit'],
        'Percentage': [pph_hit_pct, ppl_hit_pct, ppmid_hit_pct]
    })
    
    # Create a bar chart for hit percentages
    fig_hits = px.bar(
        hit_pct_df,
        x="Hit Type",
        y="Percentage",
        title="PPH / PPL / PPM Hit Rate",
        labels={"Hit Type": "Hit Type", "Percentage": "Hit Percentage"},
        text=hit_pct_df["Percentage"].apply(lambda x: f"{x:.2%}")
    )
    fig_hits.update_layout(title={'x': 0.5, 'xanchor': 'center'})

    fig_hits.update_traces(textposition='outside')
    fig_hits.update_yaxes(range=[0, 1])

    # Display the two charts side by side using st.columns
    col1, col2, col3 = st.columns((1, 2, 2))
    col1.plotly_chart(fig_hits, use_container_width=True)
    col2.plotly_chart(fig_low, use_container_width=True)
    col3.plotly_chart(fig_high, use_container_width=True)


# Calculate distribution of hour_direction in the filtered data
# Normalize direction values
filtered_df_3h['three_hour_direction'] = filtered_df_3h['three_hour_direction'].str.strip().str.title()

# Recalculate counts
three_hour_direction_counts = filtered_df_3h['three_hour_direction'].value_counts().reset_index()
three_hour_direction_counts.columns = ['direction', 'count']

direction_order = ["Long", "Short", "Neutral"]
direction_colors = {
    "Long": "#2ecc71",       # Green
    "Short": "#e74c3c",     # Red
    "Neutral": "#5d6d7e"   # Gray
}

quartals = ["Q1_direction", "Q2_direction", "Q3_direction", "Q4_direction", "three_hour_direction"]
quartal_titles = ["Q1 Direction", "Q2 Direction", "Q3 Direction", "Q4 Direction", "Hour Direction"]

q_cols = st.columns(5)

for i, q_col in enumerate(quartals):
    # Normalize and count values
    filtered_df_3h[q_col] = filtered_df_3h[q_col].str.strip().str.title()
    q_counts = filtered_df_3h[q_col].value_counts().reset_index()
    q_counts.columns = ['direction', 'count']

    # Build pie chart
    fig_q = px.pie(
        q_counts,
        names='direction',
        values='count',
        color='direction',
        title=quartal_titles[i],
        hole=0.3,
        category_orders={'direction': direction_order},
        color_discrete_map=direction_colors
    )
    fig_q.update_traces(textinfo='percent+label')
    q_cols[i].plotly_chart(fig_q, use_container_width=True)

st.caption(f"Sample size: {len(filtered_df_3h):,} rows")
