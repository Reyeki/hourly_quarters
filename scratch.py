

if merged_tf is not None:
    st.markdown("### Combined Data (Hourly and 3H Filters Applied)")

    # Initialize filtered_merged based on Instrument (common filter)
    merged_filtered = merged_tf[merged_tf['Instrument'] == selected_instrument].copy()
    
    # (Optional) Create shifted columns for previous direction if needed
    merged_filtered['prev_hour_direction_hourly'] = merged_filtered['hour_direction'].shift(1)
    merged_filtered['prev_three_hour_direction'] = merged_filtered['three_hour_direction'].shift(1)
    
    # Apply time and day filters
    if selected_hour != 'All':
        merged_filtered = merged_filtered[merged_filtered['hour'] == selected_hour]
    if selected_three_hour != 'All':
        # Here we use the three-hour field. Note: you might also use 'three_hour_start' from the hourly side—choose the one that
        # best reflects the intended filtering.
        merged_filtered = merged_filtered[merged_filtered['start_hour'] == selected_three_hour]
    if selected_day != 'All':
        merged_filtered = merged_filtered[merged_filtered['day_of_week'] == selected_day]
    
    # Apply the hourly Q-direction filters
    if q1_filter != "All":
        merged_filtered = merged_filtered[merged_filtered['Q1_direction_hourly'].str.strip().str.title() == q1_filter]
    if q2_filter != "All":
        merged_filtered = merged_filtered[merged_filtered['Q2_direction_hourly'].str.strip().str.title() == q2_filter]
    if q3_filter != "All":
        merged_filtered = merged_filtered[merged_filtered['Q3_direction_hourly'].str.strip().str.title() == q3_filter]
    if q4_filter != "All":
        merged_filtered = merged_filtered[merged_filtered['Q4_direction_hourly'].str.strip().str.title() == q4_filter]
    if prev_hour_filter != 'All':
        merged_filtered = merged_filtered[merged_filtered['prev_hour_direction_hourly'] == prev_hour_filter]
    if orb_filter != 'All':
        merged_filtered = merged_filtered[merged_filtered['ORB_direction_hourly'] == orb_filter]
    
    # Apply the 3H Q-direction filters
    if q1_filter_3h != "All":
        merged_filtered = merged_filtered[merged_filtered['Q1_direction_3h'].str.strip().str.title() == q1_filter_3h]
    if q2_filter_3h != "All":
        merged_filtered = merged_filtered[merged_filtered['Q2_direction_3h'].str.strip().str.title() == q2_filter_3h]
    if q3_filter_3h != "All":
        merged_filtered = merged_filtered[merged_filtered['Q3_direction_3h'].str.strip().str.title() == q3_filter_3h]
    if q4_filter_3h != "All":
        merged_filtered = merged_filtered[merged_filtered['Q4_direction_3h'].str.strip().str.title() == q4_filter_3h]
    if prev_hour_filter_3h != 'All':
        merged_filtered = merged_filtered[merged_filtered['prev_three_hour_direction'] == prev_hour_filter_3h]
    if orb_filter_3h != 'All':
        merged_filtered = merged_filtered[merged_filtered['ORB_direction_3h'] == orb_filter_3h]
    
    # Apply low/high bucket exclusions.
    # Note: Depending on your needs you might want to exclude based on the hourly values, the 3H values, or both.
    if low_filter:
        merged_filtered = merged_filtered[~merged_filtered['low_bucket_hourly'].isin(low_filter)]
    if high_filter:
        merged_filtered = merged_filtered[~merged_filtered['high_bucket_hourly'].isin(high_filter)]
    if low_filter_3h:
        merged_filtered = merged_filtered[~merged_filtered['low_bucket_3h'].isin(low_filter_3h)]
    if high_filter_3h:
        merged_filtered = merged_filtered[~merged_filtered['high_bucket_3h'].isin(high_filter_3h)]
    
    # === Bar Charts for Bucket Distributions ===
    # For the hourly side (low/high buckets from the hourly columns)
    low_counts_merged_hourly = merged_filtered["low_bucket_hourly"].value_counts(normalize=True).reset_index()
    low_counts_merged_hourly.columns = ["value", "probability"]
    high_counts_merged_hourly = merged_filtered["high_bucket_hourly"].value_counts(normalize=True).reset_index()
    high_counts_merged_hourly.columns = ["value", "probability"]
    
    # Create bar chart for hourly low bucket
    fig_low_merged_hourly = px.bar(
        low_counts_merged_hourly,
        x="value",
        y="probability",
        title="Combined Low of Hour Bucket",
        labels={"value": "Low Bucket", "probability": "Probability"},
        text=low_counts_merged_hourly["probability"].apply(lambda x: f"{x:.2%}")
    )
    fig_low_merged_hourly.update_traces(textposition="outside")
    # Use the same desired order as before (ensure desired_order is defined, e.g., desired_order = ["Q1", "Q2", "Q3", "Q4"])
    fig_low_merged_hourly.update_layout(xaxis=dict(categoryorder='array', categoryarray=desired_order))
    
    # Create bar chart for hourly high bucket
    fig_high_merged_hourly = px.bar(
        high_counts_merged_hourly,
        x="value",
        y="probability",
        title="Combined High of Hour Bucket",
        labels={"value": "High Bucket", "probability": "Probability"},
        text=high_counts_merged_hourly["probability"].apply(lambda x: f"{x:.2%}")
    )
    fig_high_merged_hourly.update_traces(textposition="outside")
    fig_high_merged_hourly.update_layout(xaxis=dict(categoryorder='array', categoryarray=desired_order))
    
    # Display the two bar charts side by side
    col1_merged, col2_merged = st.columns(2)
    col1_merged.plotly_chart(fig_low_merged_hourly, use_container_width=True)
    col2_merged.plotly_chart(fig_high_merged_hourly, use_container_width=True)
    
    # Optionally, you can also do similar bar charts for the 3H side:
    low_counts_merged_3h = merged_filtered["low_bucket_3h"].value_counts(normalize=True).reset_index()
    low_counts_merged_3h.columns = ["value", "probability"]
    high_counts_merged_3h = merged_filtered["high_bucket_3h"].value_counts(normalize=True).reset_index()
    high_counts_merged_3h.columns = ["value", "probability"]
    
    fig_low_merged_3h = px.bar(
        low_counts_merged_3h,
        x="value",
        y="probability",
        title="Combined Low of 3H Bucket",
        labels={"value": "Low Bucket", "probability": "Probability"},
        text=low_counts_merged_3h["probability"].apply(lambda x: f"{x:.2%}")
    )
    fig_low_merged_3h.update_traces(textposition="outside")
    fig_low_merged_3h.update_layout(xaxis=dict(categoryorder='array', categoryarray=desired_order))
    
    fig_high_merged_3h = px.bar(
        high_counts_merged_3h,
        x="value",
        y="probability",
        title="Combined High of 3H Bucket",
        labels={"value": "High Bucket", "probability": "Probability"},
        text=high_counts_merged_3h["probability"].apply(lambda x: f"{x:.2%}")
    )
    fig_high_merged_3h.update_traces(textposition="outside")
    fig_high_merged_3h.update_layout(xaxis=dict(categoryorder='array', categoryarray=desired_order))
    
    col1_merged_3h, col2_merged_3h = st.columns(2)
    col1_merged_3h.plotly_chart(fig_low_merged_3h, use_container_width=True)
    col2_merged_3h.plotly_chart(fig_high_merged_3h, use_container_width=True)
    
    # === Pie Charts for Directional Statistics ===
    # For the hourly directional stats in the merged dataframe
    st.markdown("### Combined Directional Stats (Hourly)")
    quartals_hourly = ["Q1_direction_hourly", "Q2_direction_hourly", "Q3_direction_hourly", "Q4_direction_hourly", "hour_direction"]
    quartal_titles_hourly = ["Q1 Direction", "Q2 Direction", "Q3 Direction", "Q4 Direction", "Hour Direction"]
    
    q_cols_merged_hourly = st.columns(5)
    for i, col_name in enumerate(quartals_hourly):
        merged_filtered[col_name] = merged_filtered[col_name].str.strip().str.title()
        q_counts = merged_filtered[col_name].value_counts().reset_index()
        q_counts.columns = ['direction', 'count']
    
        fig_q = px.pie(
            q_counts,
            names='direction',
            values='count',
            color='direction',
            title=quartal_titles_hourly[i],
            hole=0.3,
            category_orders={'direction': direction_order},
            color_discrete_map=direction_colors
        )
        fig_q.update_traces(textinfo='percent+label')
        q_cols_merged_hourly[i].plotly_chart(fig_q, use_container_width=True)
    
    st.caption(f"Combined sample size (Hourly): {len(merged_filtered):,} rows")
    
    # And similarly for the 3H directional stats:
    st.markdown("### Combined Directional Stats (3H)")
    quartals_3h = ["Q1_direction_3h", "Q2_direction_3h", "Q3_direction_3h", "Q4_direction_3h", "three_hour_direction"]
    quartal_titles_3h = ["Q1 Direction", "Q2 Direction", "Q3 Direction", "Q4 Direction", "3H Direction"]
    
    q_cols_merged_3h = st.columns(5)
    for i, col_name in enumerate(quartals_3h):
        merged_filtered[col_name] = merged_filtered[col_name].str.strip().str.title()
        q_counts = merged_filtered[col_name].value_counts().reset_index()
        q_counts.columns = ['direction', 'count']
    
        fig_q = px.pie(
            q_counts,
            names='direction',
            values='count',
            color='direction',
            title=quartal_titles_3h[i],
            hole=0.3,
            category_orders={'direction': direction_order},
            color_discrete_map=direction_colors
        )
        fig_q.update_traces(textinfo='percent+label')
        q_cols_merged_3h[i].plotly_chart(fig_q, use_container_width=True)
    
    st.caption(f"Combined sample size (3H): {len(merged_filtered):,} rows")
