"""
HDFC Unified Analytics Dashboard - Main Entry Point
Modern, Professional Interface
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import configuration
from config import APP_TITLE, APP_ICON, PAGE_LAYOUT
from database.connection import get_db_engine

# Import modules
from modules import phone_numbers
from modules import HDFC_campaign
from modules import google_summary
from modules import status_analysis
from modules import Input_MIS
from modules import sql_console

# -------------------------
# Page Configuration
# -------------------------
st.set_page_config(
    page_title=APP_TITLE,
    layout=PAGE_LAYOUT,
    page_icon=APP_ICON,
    initial_sidebar_state="collapsed"
)

# -------------------------
# Custom Styling (Dark Bank Theme)
# -------------------------
st.markdown("""<style>
/* Main Theme Colors */
:root {
    --primary-color: #004C8C;
    --secondary-color: #ED1C24;
    --background-dark: #0E1117;
    --text-light: #FAFAFA;
}

/* Overall Background */
.stApp {
    background: linear-gradient(135deg, #0E1117 0%, #1a1f2e 100%);
}

/* Balanced Container Spacing */
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 1rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 100% !important;
}

/* Balanced Section Spacing */
div[data-testid="stVerticalBlock"] > div {
    gap: 0.75rem !important;
}

/* Header Styling */
h1, h2, h3, h4 {
    color: var(--text-light) !important;
    font-weight: 600 !important;
    margin-top: 0.75rem !important;
    margin-bottom: 0.75rem !important;
}

h1 {
    font-size: 2rem !important;
}

h2 {
    font-size: 1.6rem !important;
}

h3 {
    font-size: 1.3rem !important;
}

h4 {
    font-size: 1.1rem !important;
}

/* Horizontal Rule Spacing */
hr {
    margin-top: 0.75rem !important;
    margin-bottom: 0.75rem !important;
}

/* Metric Cards */
[data-testid="stMetricValue"] {
    font-size: 1.8rem !important;
    font-weight: 700 !important;
    color: #fff !important;
}

[data-testid="stMetric"] {
    padding: 0.75rem !important;
}

[data-testid="stMetricLabel"] {
    font-size: 1rem !important;
}

/* Navigation Buttons */
.stButton>button {
    background: linear-gradient(90deg, var(--primary-color), #0066CC);
    color: white !important;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    font-weight: 600;
    transition: all 0.3s ease;
}

.stButton>button:hover {
    background: linear-gradient(90deg, #0066CC, var(--primary-color));
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(237, 28, 36, 0.3);
}

/* Selectbox */
.stSelectbox {
    color: white !important;
}

.stSelectbox label {
    font-size: 0.95rem !important;
    margin-bottom: 0.5rem !important;
}

/* Info Boxes */
.stAlert {
    border-radius: 10px;
    border-left: 4px solid var(--secondary-color);
    padding: 0.75rem 1rem !important;
    margin: 0.75rem 0 !important;
}

/* Dataframes */
.dataframe {
    border-radius: 8px;
    font-size: 0.95rem !important;
}

[data-testid="stDataFrame"] {
    margin: 1rem 0 !important;
}

/* File Uploader */
[data-testid="stFileUploader"] {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 10px;
    padding: 1rem;
    margin: 0.75rem 0 !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    padding-top: 0.75rem;
    margin-bottom: 1rem;
}

.stTabs [data-baseweb="tab"] {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 8px 8px 0 0;
    color: white;
    padding: 0.6rem 1.2rem;
    font-size: 0.95rem;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(90deg, var(--primary-color), #0066CC);
    font-weight: 600;
}

/* Expanders */
.streamlit-expanderHeader {
    padding: 0.75rem 1rem !important;
    font-size: 1rem !important;
    font-weight: 600;
    background: rgba(255, 255, 255, 0.03) !important;
    border-radius: 8px;
}

.streamlit-expanderContent {
    padding: 1rem !important;
    margin-top: 0.5rem;
}

/* Column Spacing */
div[data-testid="column"] {
    padding: 0 0.75rem !important;
}

/* Form Elements */
.stCheckbox, .stRadio {
    padding: 0.25rem 0 !important;
}

.stCheckbox label, .stRadio label {
    font-size: 0.95rem !important;
}

/* Markdown Spacing */
.stMarkdown {
    margin-bottom: 0.5rem !important;
}

.stMarkdown p {
    margin-bottom: 0.5rem !important;
}

/* Input Fields */
.stDateInput, .stNumberInput, .stTextInput {
    margin-bottom: 0.5rem !important;
}

.stDateInput label, .stNumberInput label, .stTextInput label {
    margin-bottom: 0.5rem !important;
}

/* Plotly Charts */
.js-plotly-plot {
    margin: 1rem 0 !important;
}

/* Multiselect */
.stMultiSelect label {
    font-size: 0.95rem !important;
    margin-bottom: 0.5rem !important;
}

/* Caption Text */
.caption {
    font-size: 0.85rem !important;
    line-height: 1.4 !important;
}

/* Improve Readability */
body {
    line-height: 1.6 !important;
}

/* Ensure all text is visible */
* {
    overflow: visible !important;
}

/* Fix any truncated content */
.element-container {
    overflow: visible !important;
}
</style>""", unsafe_allow_html=True)

# -------------------------
# Date Filter Function
# -------------------------
def apply_date_filter(df):
    """Apply date filter based on session state"""
    if not st.session_state.get('date_filter_enabled', False) or df is None:
        return df

    start_date = st.session_state.get('date_filter_start')
    end_date = st.session_state.get('date_filter_end')
    if not start_date or not end_date:
        return df

    date_col = st.session_state.get('selected_date_column')
    if not date_col:
        date_col = next((c for c in df.columns if 'date' in c.lower() or 'time' in c.lower()), None)
    if not date_col or date_col not in df.columns:
        return df

    try:
        df_filtered = df.copy()
        df_filtered[date_col] = pd.to_datetime(df_filtered[date_col], errors='coerce')
        mask = (df_filtered[date_col] >= pd.to_datetime(start_date)) & \
               (df_filtered[date_col] <= pd.to_datetime(end_date))
        return df_filtered[mask]
    except Exception as e:
        st.error(f"Date filter error: {str(e)}")
        return df

# -------------------------
# Main Dashboard
# -------------------------
def main():
    """Main dashboard orchestrator"""
    # Initialize session state
    for key, default in [
        ('mis_data', None), ('mis_filename', None), ('mis_source', None),
        ('date_filter_enabled', False), ('date_filter_start', None),
        ('date_filter_end', None), ('selected_module', None),
        ('nav_dropdown_widget', "Select Module...")
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    # Database connection
    engine, db_error = get_db_engine()

    # -------------------------
    # Header
    # -------------------------
    col1, col2, col3 = st.columns([1.5, 3, 1.5])

    with col1:
        logo_path = Path("assets/images/hdfc credit .png")
        if logo_path.exists():
            st.image(str(logo_path), width=150)

        banner_path = None
        module = st.session_state.get('selected_module')
        if module is None:
            banner_path = Path("assets/images/HDFC-Credit-Cards.png")
        elif module == "campaign":
            banner_path = Path("assets/images/HDFC campaign Analysis.png")

        if banner_path and banner_path.exists():
            st.image(str(banner_path), width=150)

    with col2:
        st.markdown(
            f"<h1 style='text-align:center;color:#fff;'>{APP_TITLE}</h1>",
            unsafe_allow_html=True
        )

    with col3:
        st.markdown("🟢 **DB Connected**" if engine else "🔴 **DB Error**")

        nav_options = {
            "Select Module...": None,
            "📞 Phone Numbers": "phone",
            "📈 Campaign Analysis": "campaign",
            "🎯 Google Ads": "google",
            "📤 MIS Upload": "upload",
            "💻 SQL Console": "sql"
        }

        nav_row = st.columns([1, 3])

        with nav_row[0]:
            if st.button("🏠", key="home_icon", help="Dashboard Home", use_container_width=False):
                st.session_state.selected_module = None
                st.session_state.nav_dropdown_widget = "Select Module..."
                st.rerun()

        with nav_row[1]:
            current_label = [k for k, v in nav_options.items() if v == module][0] if module else "Select Module..."

            def update_module():
                sel = nav_options.get(st.session_state.nav_dropdown_widget)
                if sel != st.session_state.selected_module:
                    st.session_state.selected_module = sel

            st.selectbox(
                "Modules",
                options=list(nav_options.keys()),
                index=list(nav_options.keys()).index(current_label),
                key="nav_dropdown_widget",
                label_visibility="collapsed",
                on_change=update_module
            )

    st.markdown("<hr style='margin:0.75rem 0'>", unsafe_allow_html=True)

    # -------------------------
    # Date Filter
    # -------------------------
    st.markdown("### 📅 Date Filter")
    filter_cols = st.columns([1, 2, 1.5, 1.5, 2])
    fc1, fc2, fc3, fc4, fc5 = filter_cols

    with fc1:
        st.session_state.date_filter_enabled = st.checkbox(
            "Enable Filter",
            value=st.session_state.date_filter_enabled
        )

    if st.session_state.date_filter_enabled and st.session_state.mis_data is not None:
        date_columns = [c for c in st.session_state.mis_data.columns if 'date' in c.lower() or 'time' in c.lower()]
        if date_columns:
            with fc2:
                selected_date_col = st.selectbox("Date Column", date_columns, key="date_column_select")
                st.session_state.selected_date_column = selected_date_col

            try:
                dates = pd.to_datetime(st.session_state.mis_data[selected_date_col], errors='coerce')
                min_date, max_date = dates.min(), dates.max()
                if pd.notna(min_date) and pd.notna(max_date):
                    with fc3:
                        st.session_state.date_filter_start = st.date_input(
                            "From Date", value=st.session_state.date_filter_start or min_date,
                            min_value=min_date, max_value=max_date
                        )
                    with fc4:
                        st.session_state.date_filter_end = st.date_input(
                            "To Date", value=st.session_state.date_filter_end or max_date,
                            min_value=min_date, max_value=max_date
                        )
                    with fc5:
                        filtered_count = len(apply_date_filter(st.session_state.mis_data))
                        total_count = len(st.session_state.mis_data)
                        st.info(f"📊 **{filtered_count:,}** / **{total_count:,}** records")
                else:
                    with fc2:
                        st.warning("⚠️ No valid dates")
            except Exception as e:
                with fc2:
                    st.error(f"❌ {str(e)[:30]}")
        else:
            with fc2:
                st.warning("⚠️ No date columns")
    elif st.session_state.date_filter_enabled and st.session_state.mis_data is None:
        with fc2:
            st.info("ℹ️ Load data first")

    st.markdown("<hr style='margin:0.75rem 0'>", unsafe_allow_html=True)

    # -------------------------
    # Sidebar & Main Area
    # -------------------------
    sidebar_col, main_col = st.columns([1, 4])

    with sidebar_col:
        st.markdown("### 📁 Data Source")
        mis_options = ["Current Data", "📁 Upload New File", "🗄️ Reload from Database"]
        selected_source = st.selectbox("Choose Action", options=mis_options, key="mis_source_selector", label_visibility="collapsed")

        if selected_source == "📁 Upload New File":
            mis_file = st.file_uploader("Upload Excel", type=["xlsx"], key="main_mis_upload", label_visibility="collapsed")
            if mis_file:
                with st.spinner("Loading..."):
                    df_mis = pd.read_excel(mis_file, sheet_name="Sheet1")
                    df_mis.columns = df_mis.columns.str.strip()
                    st.session_state.update({'mis_data': df_mis, 'mis_filename': mis_file.name, 'mis_source': 'file'})
                    st.success(f"✅ {len(df_mis):,} records")
                    st.rerun()

        elif selected_source == "🗄️ Reload from Database" and engine:
            if st.button("Load Now", use_container_width=True, type="primary"):
                with st.spinner("Loading..."):
                    try:
                        df_mis = pd.read_sql('SELECT * FROM "HDFC_MIS_Data"', engine)
                        df_mis.columns = df_mis.columns.str.strip()
                        st.session_state.update({'mis_data': df_mis, 'mis_filename': 'Database', 'mis_source': 'database'})
                        st.success(f"✅ {len(df_mis):,} records")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)[:50]}")

        st.markdown("<hr style='margin:0.75rem 0'>", unsafe_allow_html=True)
        if st.session_state.mis_data is not None:
            st.markdown("**📊 Current Data**")
            source_icon = "📁" if st.session_state.mis_source == "file" else "🗄️"
            st.caption(f"{source_icon} {st.session_state.mis_filename}")
            st.caption(f"{len(st.session_state.mis_data):,} records")
        else:
            st.caption("⚠️ No data loaded")

    with main_col:
        filtered_data = apply_date_filter(st.session_state.mis_data) if st.session_state.mis_data else None
        module = st.session_state.selected_module

        if module is None:
            status_analysis.render_status_analysis_module(filtered_data, engine)
        elif module == "phone":
            phone_numbers.render_phone_numbers_module(engine, filtered_data)
        elif module == "campaign":
            HDFC_campaign.render_campaign_analysis_module(filtered_data, engine)
        elif module == "google":
            google_summary.render_google_ads_module(engine, filtered_data)
        elif module == "upload":
            Input_MIS.render_mis_upload_module(engine)
        elif module == "sql":
            sql_console.render_sql_console_module(engine)

# -------------------------
# Run Application
# -------------------------
if __name__ == "__main__":
    main()
