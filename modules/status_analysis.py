"""
HDFC Final Status Analysis Module
Analyze final decision counts with creation and final decision date filters
"""

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from io import BytesIO


# Status mapping
FINAL_STATUS_MAP = {
    "IPA APPROVED DROPOFF CASE": "Inprogress",
    "IPA REJECT": "Declined",
    "Decline": "Declined",
    "Approve": "Card Out",
    "approve": "Card Out",
    "APPROVE": "Card Out",
    "Inprocess": "Inprogress",
}


def parse_dates_safely(date_series):
    """Parse dates with multiple format handling"""
    parsed_dates = []
    for date_val in date_series:
        if pd.isna(date_val):
            parsed_dates.append(pd.NaT)
            continue
        try:
            parsed = pd.to_datetime(date_val, dayfirst=True, format='mixed')
            parsed_dates.append(parsed)
        except:
            try:
                parsed = pd.to_datetime(date_val, dayfirst=True)
                parsed_dates.append(parsed)
            except:
                parsed_dates.append(pd.NaT)
    return pd.Series(parsed_dates)


def find_column(df, keywords):
    """Find column that contains any of the keywords (case insensitive)"""
    if isinstance(keywords, str):
        keywords = [keywords]
    for col in df.columns:
        col_clean = str(col).strip().replace('*', '').lower()
        for keyword in keywords:
            if keyword.lower() in col_clean:
                return col
    return None


def render_status_analysis_module(df_mis=None, db_engine=None):
    """Main render function for status analysis module"""
    st.markdown("## 📊 Final Status Analysis")

    # === Data Source Section ===
    st.markdown("### 📊 MIS Data Source")

    # Track data source type
    if 'status_mis_source' not in st.session_state:
        st.session_state.status_mis_source = None

    # Check if MIS data exists from main dashboard
    if df_mis is not None and 'status_mis_data' in st.session_state:
        del st.session_state.status_mis_data
        st.session_state.status_mis_source = None

    if df_mis is None and 'status_mis_data' in st.session_state:
        df_mis = st.session_state.status_mis_data

    # Display current status with source info
    if df_mis is not None:
        source_text = f" (from {st.session_state.status_mis_source})" if st.session_state.status_mis_source else ""
        st.success(f"✅ Loaded: {len(df_mis):,} MIS records{source_text}")
    else:
        st.info("ℹ️ No MIS data loaded")

    # MIS data source options
    mis_source_tab1, mis_source_tab2 = st.tabs(["📁 Upload File", "🗄️ Load from DB"])

    with mis_source_tab1:
        uploaded_mis = st.file_uploader(
            "Upload MIS Excel/CSV File",
            type=['xlsx', 'xls', 'csv'],
            key="status_mis_file_uploader",
            help="Upload HDFC MIS data file (takes priority over database)"
        )
        if uploaded_mis:
            try:
                if uploaded_mis.name.endswith('.csv'):
                    df_mis_uploaded = pd.read_csv(uploaded_mis)
                else:
                    df_mis_uploaded = pd.read_excel(uploaded_mis)

                df_mis_uploaded.columns = df_mis_uploaded.columns.str.strip()
                st.session_state.status_mis_data = df_mis_uploaded
                st.session_state.status_mis_source = "uploaded file"
                st.success(f"✅ Uploaded {len(df_mis_uploaded):,} records (file upload takes priority)")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error reading file: {str(e)}")

    with mis_source_tab2:
        # Disable database load if file is uploaded
        if st.session_state.status_mis_source == "uploaded file":
            st.warning("⚠️ File uploaded - database loading disabled. Remove file to use database.")
            st.button("🗄️ Load MIS from Database", key="status_load_mis_db", use_container_width=True, disabled=True)
        else:
            if st.button("🗄️ Load MIS from Database", key="status_load_mis_db", use_container_width=True):
                if db_engine:
                    with st.spinner("Loading MIS data from database..."):
                        try:
                            df_mis_loaded = pd.read_sql('SELECT * FROM "HDFC_MIS_Data"', db_engine)
                            df_mis_loaded.columns = df_mis_loaded.columns.str.strip()
                            st.session_state.status_mis_data = df_mis_loaded
                            st.session_state.status_mis_source = "database"
                            st.success(f"✅ Loaded {len(df_mis_loaded):,} records from DB")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Database error: {str(e)[:100]}")
                else:
                    st.error("❌ Database not available")

    st.markdown("---")

    # Update df_mis from session state if not from main dashboard
    if df_mis is None and 'status_mis_data' in st.session_state:
        df_mis = st.session_state.status_mis_data

    if df_mis is not None:
        try:

                # Find date columns
                creation_col = find_column(df_mis, ['created', 'creation', 'date'])
                final_decision_col = find_column(df_mis, ['final_decision_date', 'decision_date', 'final date'])
                final_status_col = find_column(df_mis, ['final_decision', 'final_status'])
                ipa_status_col = find_column(df_mis, ['ipa_status', 'ipa status'])

                if not creation_col and not final_decision_col:
                    st.warning("⚠️ No date columns found. Available columns: " + ", ".join(df_mis.columns.tolist()))
                    return

                # Parse dates
                if creation_col:
                    df_mis[creation_col] = parse_dates_safely(df_mis[creation_col])
                if final_decision_col:
                    df_mis[final_decision_col] = parse_dates_safely(df_mis[final_decision_col])

                # Get date ranges from CREATION_DATE_TIME - filter out invalid dates properly
                if creation_col:
                    # Filter for valid dates only (not NaT and after year 2000 to avoid epoch dates)
                    valid_creation = df_mis[
                        (df_mis[creation_col].notna()) &
                        (df_mis[creation_col] > pd.Timestamp('2000-01-01'))
                    ]
                    if len(valid_creation) > 0:
                        min_creation = valid_creation[creation_col].min()
                        max_creation = valid_creation[creation_col].max()
                    else:
                        st.error("❌ No valid creation dates found (dates must be after 2000-01-01)")
                        return
                else:
                    st.error("❌ Creation date column not found")
                    return

                if final_decision_col:
                    # Filter for valid dates only (not NaT and after year 2000)
                    valid_decision = df_mis[
                        (df_mis[final_decision_col].notna()) &
                        (df_mis[final_decision_col] > pd.Timestamp('2000-01-01'))
                    ]
                    if len(valid_decision) > 0:
                        min_decision = valid_decision[final_decision_col].min()
                        max_decision = valid_decision[final_decision_col].max()

                # Date filter selection
                st.markdown("### 📅 Filter Options")

                filter_type = st.radio(
                    "Filter by:",
                    ["Creation Date", "Final Decision Date", "Both Dates"],
                    horizontal=True
                )

                # Initialize session state for search
                if 'search_clicked' not in st.session_state:
                    st.session_state.search_clicked = False
                if 'start_date' not in st.session_state:
                    st.session_state.start_date = min_creation.date()
                if 'end_date' not in st.session_state:
                    st.session_state.end_date = max_creation.date()

                # Date range inputs
                col1, col2, col3 = st.columns([2, 2, 1])

                with col1:
                    if filter_type == "Creation Date":
                        start_date = st.date_input(
                            "Start Date (Creation)",
                            value=min_creation.date(),
                            min_value=min_creation.date(),
                            max_value=max_creation.date(),
                            key="start_date_input"
                        )
                    elif filter_type == "Final Decision Date" and final_decision_col:
                        start_date = st.date_input(
                            "Start Date (Final Decision)",
                            value=min_decision.date() if final_decision_col else min_creation.date(),
                            min_value=min_decision.date() if final_decision_col else min_creation.date(),
                            max_value=max_decision.date() if final_decision_col else max_creation.date(),
                            key="start_date_input"
                        )
                    elif filter_type == "Both Dates":
                        start_date_creation = st.date_input(
                            "Start Date (Creation)",
                            value=min_creation.date(),
                            min_value=min_creation.date(),
                            max_value=max_creation.date(),
                            key="start_date_creation_input"
                        )

                with col2:
                    if filter_type == "Creation Date":
                        end_date = st.date_input(
                            "End Date (Creation)",
                            value=max_creation.date(),
                            min_value=min_creation.date(),
                            max_value=max_creation.date(),
                            key="end_date_input"
                        )
                    elif filter_type == "Final Decision Date" and final_decision_col:
                        end_date = st.date_input(
                            "End Date (Final Decision)",
                            value=max_decision.date() if final_decision_col else max_creation.date(),
                            min_value=min_decision.date() if final_decision_col else min_creation.date(),
                            max_value=max_decision.date() if final_decision_col else max_creation.date(),
                            key="end_date_input"
                        )
                    elif filter_type == "Both Dates":
                        end_date_decision = st.date_input(
                            "End Date (Final Decision)",
                            value=max_decision.date() if final_decision_col else max_creation.date(),
                            min_value=min_decision.date() if final_decision_col else min_creation.date(),
                            max_value=max_decision.date() if final_decision_col else max_creation.date(),
                            key="end_date_decision_input"
                        )

                with col3:
                    st.markdown("<br>", unsafe_allow_html=True)
                    search_button = st.button("🔍 Search", use_container_width=True, type="primary")

                # Apply filters
                df_filtered = df_mis.copy()

                if filter_type == "Creation Date" and creation_col:
                    df_filtered = df_filtered[
                        (df_filtered[creation_col] >= pd.Timestamp(start_date)) &
                        (df_filtered[creation_col] <= pd.Timestamp(end_date))
                    ]
                    date_range_text = f"Creation Date: {start_date.strftime('%b %d, %Y')} to {end_date.strftime('%b %d, %Y')}"
                elif filter_type == "Final Decision Date" and final_decision_col:
                    df_filtered = df_filtered[
                        (df_filtered[final_decision_col] >= pd.Timestamp(start_date)) &
                        (df_filtered[final_decision_col] <= pd.Timestamp(end_date))
                    ]
                    date_range_text = f"Final Decision Date: {start_date.strftime('%b %d, %Y')} to {end_date.strftime('%b %d, %Y')}"
                elif filter_type == "Both Dates":
                    if creation_col:
                        df_filtered = df_filtered[
                            (df_filtered[creation_col] >= pd.Timestamp(start_date_creation)) &
                            (df_filtered[creation_col] <= pd.Timestamp(max_creation))
                        ]
                    if final_decision_col:
                        df_filtered = df_filtered[
                            (df_filtered[final_decision_col] >= pd.Timestamp(min_decision)) &
                            (df_filtered[final_decision_col] <= pd.Timestamp(end_date_decision))
                        ]
                    date_range_text = f"Creation: {start_date_creation.strftime('%b %d, %Y')}+ | Decision: until {end_date_decision.strftime('%b %d, %Y')}"

                if len(df_filtered) == 0:
                    st.warning("⚠️ No records found in selected date range")
                    return

                # Calculate status counts
                status_counts = {}

                # Prepare columns
                if final_status_col:
                    df_filtered['final_decision_upper'] = df_filtered[final_status_col].astype(str).str.upper().str.strip()

                if ipa_status_col:
                    df_filtered['ipa_status_upper'] = df_filtered[ipa_status_col].astype(str).str.upper().str.strip()

                # IPA Approved: Use IPA_STATUS column ONLY
                if ipa_status_col:
                    ipa_approved_count = int((df_filtered['ipa_status_upper'] == "APPROVE").sum())
                    status_counts["IPA Approved"] = ipa_approved_count
                else:
                    status_counts["IPA Approved"] = 0

                # Card Out: when FINAL_DECISION is "Approve"
                if final_status_col:
                    approve_count = int((df_filtered['final_decision_upper'] == "APPROVE").sum())
                    status_counts["Card Out"] = approve_count

                    # Declined: when FINAL_DECISION is "IPA REJECT" or "Decline"
                    declined_mask = (
                        (df_filtered['final_decision_upper'] == "IPA REJECT") |
                        (df_filtered['final_decision_upper'] == "DECLINE")
                    )
                    status_counts["Declined"] = int(declined_mask.sum())

                    # Inprogress: when FINAL_DECISION is "IPA APPROVED DROPOFF CASE" or "Inprocess"
                    inprogress_mask = (
                        (df_filtered['final_decision_upper'] == "IPA APPROVED DROPOFF CASE") |
                        (df_filtered['final_decision_upper'] == "INPROCESS")
                    )
                    status_counts["Inprogress"] = int(inprogress_mask.sum())

                    # Other: everything else
                    categorized_mask = (
                        (df_filtered['final_decision_upper'] == "APPROVE") |
                        declined_mask |
                        inprogress_mask
                    )
                    status_counts["Other"] = int((~categorized_mask).sum())

                    # Create mapped status for display
                    df_filtered['mapped_status'] = "Other"
                    df_filtered.loc[df_filtered['final_decision_upper'] == "APPROVE", 'mapped_status'] = "Card Out"
                    df_filtered.loc[declined_mask, 'mapped_status'] = "Declined"
                    df_filtered.loc[inprogress_mask, 'mapped_status'] = "Inprogress"
                else:
                    status_counts.update({"Card Out": 0, "Declined": 0, "Inprogress": 0, "Other": 0})

                status_counts["Total Applications"] = len(df_filtered)

                # Display metrics
                col1, col2, col3, col4, col5 = st.columns(5)

                with col1:
                    st.metric("📝 Total Applications", f"{status_counts['Total Applications']:,}")
                with col2:
                    st.metric("✅ IPA Approved", f"{status_counts['IPA Approved']:,}")
                with col3:
                    st.metric("💳 Card Out", f"{status_counts['Card Out']:,}")
                with col4:
                    st.metric("❌ Declined", f"{status_counts['Declined']:,}")
                with col5:
                    st.metric("⏳ Inprogress", f"{status_counts['Inprogress']:,}")

                # Tabs for visualizations and data
                tab1, tab2, tab3 = st.tabs(["📊 Visualizations", "📋 Detailed Data", "📥 Download"])

                with tab1:
                    st.markdown("### 📊 Visualizations")

                    # Get categorical columns
                    categorical_cols = df_filtered.select_dtypes(include=['object']).columns.tolist()

                    st.markdown("---")

                    # Chart 1: Pie Chart
                    st.markdown("#### 📊 Chart 1: Status Distribution Pie Chart")
                    with st.expander("⚙️ Customize Pie Chart", expanded=True):
                        pie_col1, pie_col2 = st.columns(2)

                        with pie_col1:
                            pie_status_filter = st.multiselect(
                                "Select statuses:",
                                options=['Card Out', 'Declined', 'Inprogress', 'Other'],
                                default=['Card Out', 'Declined', 'Inprogress', 'Other'],
                                help="Choose which statuses to show",
                                key="pie_status_filter"
                            )

                        with pie_col2:
                            pie_chart_type = st.selectbox(
                                "Chart Style:",
                                options=["Donut (Hole)", "Full Pie"],
                                key="pie_chart_type"
                            )

                    status_df_pie = pd.DataFrame({
                        'Status': ['Card Out', 'Declined', 'Inprogress', 'Other'],
                        'Count': [
                            status_counts['Card Out'],
                            status_counts['Declined'],
                            status_counts['Inprogress'],
                            status_counts['Other']
                        ]
                    })
                    status_df_pie = status_df_pie[status_df_pie['Status'].isin(pie_status_filter)]
                    status_df_pie = status_df_pie[status_df_pie['Count'] > 0]

                    viz_col1, viz_col2 = st.columns(2)

                    with viz_col1:
                        if not status_df_pie.empty:
                            fig1 = px.pie(
                                status_df_pie,
                                values='Count',
                                names='Status',
                                title='Final Decision Distribution',
                                hole=0.4 if pie_chart_type == "Donut (Hole)" else 0,
                                color='Status',
                                color_discrete_map={
                                    'Card Out': '#10B981',
                                    'Declined': '#EF4444',
                                    'Inprogress': '#3B82F6',
                                    'Other': '#6B7280'
                                }
                            )
                            fig1.update_traces(textposition='inside', textinfo='percent+label+value')
                            st.plotly_chart(fig1, use_container_width=True)
                        else:
                            st.info("No data to display - select at least one status")

                    with viz_col2:
                        # Chart 2: Bar Chart
                        st.markdown("#### 📊 Chart 2: Status Count Bar Chart")
                        with st.expander("⚙️ Customize Bar Chart", expanded=False):
                            bar_col1, bar_col2 = st.columns(2)

                            with bar_col1:
                                bar_status_filter = st.multiselect(
                                    "Select statuses:",
                                    options=['Card Out', 'Declined', 'Inprogress', 'Other'],
                                    default=['Card Out', 'Declined', 'Inprogress', 'Other'],
                                    key="bar_status_filter"
                                )

                            with bar_col2:
                                bar_orientation = st.selectbox(
                                    "Orientation:",
                                    options=["Vertical", "Horizontal"],
                                    key="bar_orientation"
                                )

                        status_df_bar = pd.DataFrame({
                            'Status': ['Card Out', 'Declined', 'Inprogress', 'Other'],
                            'Count': [
                                status_counts['Card Out'],
                                status_counts['Declined'],
                                status_counts['Inprogress'],
                                status_counts['Other']
                            ]
                        })
                        status_df_bar = status_df_bar[status_df_bar['Status'].isin(bar_status_filter)]
                        status_df_bar = status_df_bar[status_df_bar['Count'] > 0]

                        if not status_df_bar.empty:
                            if bar_orientation == "Vertical":
                                fig2 = px.bar(
                                    status_df_bar,
                                    x='Status',
                                    y='Count',
                                    title='Status Counts',
                                    color='Status',
                                    color_discrete_map={
                                        'Card Out': '#10B981',
                                        'Declined': '#EF4444',
                                        'Inprogress': '#3B82F6',
                                        'Other': '#6B7280'
                                    },
                                    text='Count'
                                )
                                fig2.update_traces(textposition='outside')
                            else:
                                fig2 = px.bar(
                                    status_df_bar,
                                    y='Status',
                                    x='Count',
                                    title='Status Counts',
                                    orientation='h',
                                    color='Status',
                                    color_discrete_map={
                                        'Card Out': '#10B981',
                                        'Declined': '#EF4444',
                                        'Inprogress': '#3B82F6',
                                        'Other': '#6B7280'
                                    },
                                    text='Count'
                                )
                                fig2.update_traces(textposition='outside')

                            fig2.update_layout(showlegend=False)
                            st.plotly_chart(fig2, use_container_width=True)

                    # Chart 3: Conversion Funnel
                    st.markdown("#### 📊 Chart 3: Conversion Funnel")
                    with st.expander("⚙️ Customize Funnel", expanded=False):
                        funnel_col1, funnel_col2 = st.columns(2)

                        with funnel_col1:
                            funnel_stages = st.multiselect(
                                "Funnel stages:",
                                options=["Total Applications", "IPA Approved", "Card Out"],
                                default=["Total Applications", "IPA Approved", "Card Out"],
                                help="Choose stages for the conversion funnel",
                                key="funnel_stages"
                            )

                        with funnel_col2:
                            funnel_show_percentages = st.checkbox(
                                "Show percentages",
                                value=True,
                                key="funnel_show_percentages"
                            )

                    funnel_y = []
                    funnel_x = []

                    if "Total Applications" in funnel_stages:
                        funnel_y.append("Total Applications")
                        funnel_x.append(status_counts['Total Applications'])
                    if "IPA Approved" in funnel_stages:
                        funnel_y.append("IPA Approved")
                        funnel_x.append(status_counts['IPA Approved'])
                    if "Card Out" in funnel_stages:
                        funnel_y.append("Card Out")
                        funnel_x.append(status_counts['Card Out'])

                    if funnel_y:
                        fig3 = go.Figure(go.Funnel(
                            y=funnel_y,
                            x=funnel_x,
                            textposition="inside",
                            textinfo="value+percent initial" if funnel_show_percentages else "value",
                            marker={
                                "color": ["#3B82F6", "#764ba2", "#10B981"][:len(funnel_y)],
                                "line": {"width": 1, "color": "white"}
                            }
                        ))
                        fig3.update_layout(title="Conversion Funnel", height=400)
                        st.plotly_chart(fig3, use_container_width=True)

                    # Chart 4: Custom Breakdown
                    st.markdown("#### 📊 Chart 4: Custom Category Breakdown")
                    with st.expander("⚙️ Customize Breakdown Chart", expanded=False):
                        custom_col1, custom_col2, custom_col3 = st.columns(3)

                        with custom_col1:
                            if categorical_cols:
                                custom_category_col = st.selectbox(
                                    "Select column:",
                                    options=['None'] + categorical_cols,
                                    help="Select a column to create breakdown chart",
                                    key="custom_category_col"
                                )
                            else:
                                custom_category_col = 'None'

                        with custom_col2:
                            custom_top_n = st.number_input(
                                "Show Top N:",
                                min_value=5,
                                max_value=50,
                                value=10,
                                key="custom_top_n"
                            )

                        with custom_col3:
                            custom_chart_type = st.selectbox(
                                "Chart Type:",
                                options=["Bar Chart", "Pie Chart"],
                                key="custom_chart_type"
                            )

                    if custom_category_col != 'None' and custom_category_col in df_filtered.columns:
                        category_counts = df_filtered[custom_category_col].value_counts().head(custom_top_n)

                        if custom_chart_type == "Bar Chart":
                            fig_custom = px.bar(
                                x=category_counts.index,
                                y=category_counts.values,
                                title=f"Top {custom_top_n} - Distribution by {custom_category_col}",
                                labels={'x': custom_category_col, 'y': 'Count'},
                                color=category_counts.values,
                                color_continuous_scale="Viridis",
                                text=category_counts.values
                            )
                            fig_custom.update_traces(textposition='outside')
                            fig_custom.update_layout(showlegend=False, height=400)
                        else:
                            fig_custom = px.pie(
                                values=category_counts.values,
                                names=category_counts.index,
                                title=f"Top {custom_top_n} - Distribution by {custom_category_col}",
                                hole=0.4
                            )
                            fig_custom.update_traces(textposition='inside', textinfo='percent+label+value')
                            fig_custom.update_layout(height=400)

                        st.plotly_chart(fig_custom, use_container_width=True)

                    # Conversion rates
                    st.markdown("#### 📈 Conversion Rates")
                    conv_col1, conv_col2, conv_col3 = st.columns(3)

                    with conv_col1:
                        ipa_rate = (status_counts['IPA Approved'] / status_counts['Total Applications'] * 100) if status_counts['Total Applications'] > 0 else 0
                        st.metric("IPA Approval Rate", f"{ipa_rate:.2f}%")

                    with conv_col2:
                        card_out_rate = (status_counts['Card Out'] / status_counts['Total Applications'] * 100) if status_counts['Total Applications'] > 0 else 0
                        st.metric("Card Out Rate", f"{card_out_rate:.2f}%")

                    with conv_col3:
                        decline_rate = (status_counts['Declined'] / status_counts['Total Applications'] * 100) if status_counts['Total Applications'] > 0 else 0
                        st.metric("Decline Rate", f"{decline_rate:.2f}%")

                with tab2:
                    # Default important columns
                    default_cols = [creation_col, final_decision_col, ipa_status_col, final_status_col]
                    default_cols = [col for col in default_cols if col is not None]

                    # Add mapped_status to default
                    if 'mapped_status' in df_filtered.columns:
                        default_cols.append('mapped_status')

                    # Column selector
                    col_select1, col_select2 = st.columns([3, 1])

                    with col_select1:
                        # Get all available columns
                        all_cols = df_filtered.columns.tolist()

                        # Multiselect for columns
                        selected_cols = st.multiselect(
                            "Select columns to display:",
                            options=all_cols,
                            default=[col for col in default_cols if col in all_cols],
                            help="Choose which columns you want to see in the table"
                        )

                    with col_select2:
                        if st.button("Reset Columns", use_container_width=True):
                            selected_cols = default_cols

                    # Use selected columns or default
                    display_cols = selected_cols if selected_cols else default_cols

                    # Column value filters
                    filter_col1, filter_col2, filter_col3 = st.columns(3)

                    # Initialize filtered dataframe
                    display_df = df_filtered.copy()

                    # Add filters for each displayed column
                    with filter_col1:
                        if final_status_col and final_status_col in display_cols:
                            unique_values = sorted(df_filtered[final_status_col].dropna().unique().tolist())
                            selected_status = st.multiselect(
                                f"Filter {final_status_col}:",
                                options=unique_values,
                                help="Select one or more values to filter"
                            )
                            if selected_status:
                                display_df = display_df[display_df[final_status_col].isin(selected_status)]

                    with filter_col2:
                        if ipa_status_col and ipa_status_col in display_cols:
                            unique_values = sorted(df_filtered[ipa_status_col].dropna().unique().tolist())
                            selected_ipa = st.multiselect(
                                f"Filter {ipa_status_col}:",
                                options=unique_values,
                                help="Select one or more values to filter"
                            )
                            if selected_ipa:
                                display_df = display_df[display_df[ipa_status_col].isin(selected_ipa)]

                    with filter_col3:
                        if 'mapped_status' in df_filtered.columns and 'mapped_status' in display_cols:
                            unique_values = sorted(df_filtered['mapped_status'].dropna().unique().tolist())
                            selected_mapped = st.multiselect(
                                "Filter Status Category:",
                                options=unique_values,
                                help="Select one or more values to filter"
                            )
                            if selected_mapped:
                                display_df = display_df[display_df['mapped_status'].isin(selected_mapped)]

                    # Additional column filters (expandable)
                    with st.expander("➕ More Column Filters", expanded=False):
                        other_cols = [col for col in display_cols if col not in [final_status_col, ipa_status_col, 'mapped_status', creation_col, final_decision_col]]

                        if other_cols:
                            filter_cols = st.columns(min(3, len(other_cols)))
                            for idx, col in enumerate(other_cols):
                                with filter_cols[idx % 3]:
                                    if df_filtered[col].dtype == 'object':
                                        unique_values = sorted(df_filtered[col].dropna().unique().tolist())
                                        if len(unique_values) <= 50:  # Only show filter if reasonable number of unique values
                                            selected_vals = st.multiselect(
                                                f"Filter {col}:",
                                                options=unique_values,
                                                key=f"filter_{col}"
                                            )
                                            if selected_vals:
                                                display_df = display_df[display_df[col].isin(selected_vals)]

                    # Select only chosen columns
                    display_df = display_df[display_cols].copy()

                    # Sort by creation date in ascending order if available
                    if creation_col and creation_col in display_df.columns:
                        display_df = display_df.sort_values(by=creation_col, ascending=True)

                    # Rename columns for better readability
                    rename_map = {}
                    if final_status_col and final_status_col in display_df.columns:
                        rename_map[final_status_col] = 'FINAL_DECISION'
                    if 'mapped_status' in display_df.columns:
                        rename_map['mapped_status'] = 'STATUS_CATEGORY'

                    if rename_map:
                        display_df = display_df.rename(columns=rename_map)

                    st.dataframe(
                        display_df,
                        use_container_width=True,
                        height=500
                    )

                    st.caption(f"Showing {len(display_df):,} of {len(df_filtered):,} filtered records ({len(df_mis):,} total)")

                with tab3:
                    col1, col2 = st.columns(2)

                    with col1:
                        # Summary CSV
                        summary_df = pd.DataFrame([status_counts])
                        csv_summary = summary_df.to_csv(index=False)

                        st.download_button(
                            label="📊 Download Status Summary (CSV)",
                            data=csv_summary,
                            file_name=f"Status_Summary_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )

                    with col2:
                        # Filtered data Excel
                        output = BytesIO()
                        with pd.ExcelWriter(output, engine="openpyxl") as writer:
                            df_filtered.to_excel(writer, sheet_name="Filtered Data", index=False)
                            summary_df.to_excel(writer, sheet_name="Summary", index=False)
                        output.seek(0)

                        st.download_button(
                            label="📥 Download Filtered Data (Excel)",
                            data=output,
                            file_name=f"Status_Analysis_{datetime.now().strftime('%Y%m%d')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )

        except Exception as e:
            st.error(f"❌ Error processing data: {e}")
            with st.expander("🔍 View Error Details"):
                st.exception(e)
    else:
        st.warning("⚠️ Please load MIS data to begin analysis")


if __name__ == "__main__":
    st.set_page_config(page_title="Status Analysis", layout="wide", page_icon="📊")
    render_status_analysis_module()
