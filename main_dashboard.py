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
/* =====================================================
   BALANCED SPACING - Optimized for Data Visibility
   ===================================================== */

/* ---- Container Spacing (Balanced) ---- */
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 1rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 100% !important;
}

/* ---- Section Spacing (Balanced) ---- */
div[data-testid="stVerticalBlock"] > div {
    gap: 0.75rem !important;
}

/* ---- Headers (Balanced) ---- */
h1, h2, h3, h4 {
    margin-top: 0.75rem !important;
    margin-bottom: 0.75rem !important;
}

h1 {
    font-size: 2rem !important;
    font-weight: 700 !important;
}

h2 {
    font-size: 1.6rem !important;
    font-weight: 600 !important;
    color: #e0e0e0 !important;
}

h3 {
    font-size: 1.3rem !important;
    font-weight: 600 !important;
    color: #d0d0d0 !important;
}

h4 {
    font-size: 1.1rem !important;
    font-weight: 500 !important;
}

/* ---- Horizontal Rules ---- */
hr {
    margin-top: 0.75rem !important;
    margin-bottom: 0.75rem !important;
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, #667eea, transparent) !important;
}

/* ---- Metric Cards (Balanced) ---- */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    padding: 0.75rem !important;
    border-radius: 10px !important;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3) !important;
}

[data-testid="stMetricValue"] {
    font-size: 1.8rem !important;
    font-weight: bold !important;
    color: #fff !important;
}

[data-testid="stMetricLabel"] {
    color: #f0f0f0 !important;
    font-size: 0.95rem !important;
}

/* ---- Buttons (Balanced) ---- */
.stButton>button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.5rem 1rem !important;
    font-weight: 500 !important;
    transition: all 0.3s ease !important;
    margin: 0 !important;
}

.stButton>button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 12px rgba(102, 126, 234, 0.4) !important;
}

/* ---- Tabs (Balanced) ---- */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem !important;
    background: rgba(255, 255, 255, 0.05) !important;
    padding: 0.5rem !important;
    border-radius: 10px !important;
    margin-bottom: 1rem !important;
}

.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    color: #b0b0b0 !important;
    padding: 0.6rem 1.2rem !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
}

.stTabs [data-baseweb="tab"]:hover {
    background: rgba(102, 126, 234, 0.2) !important;
    color: #e0e0e0 !important;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
}

/* ---- Expanders (Balanced) ---- */
.streamlit-expanderHeader {
    background: rgba(255, 255, 255, 0.05) !important;
    border-radius: 8px !important;
    padding: 0.75rem 1rem !important;
    font-weight: 500 !important;
    font-size: 1rem !important;
    transition: all 0.3s ease !important;
}

.streamlit-expanderHeader:hover {
    background: rgba(102, 126, 234, 0.2) !important;
}

.streamlit-expanderContent {
    background: rgba(255, 255, 255, 0.02) !important;
    border-radius: 0 0 8px 8px !important;
    padding: 1rem !important;
    border: 1px solid rgba(102, 126, 234, 0.2) !important;
}

/* ---- DataFrames (Balanced) ---- */
[data-testid="stDataFrame"] {
    background: rgba(255, 255, 255, 0.05) !important;
    border-radius: 8px !important;
    padding: 0.5rem !important;
    margin: 1rem 0 !important;
}

.dataframe {
    font-size: 0.95rem !important;
    color: #e0e0e0 !important;
}

.dataframe th {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    font-weight: 600 !important;
    padding: 0.75rem !important;
}

.dataframe td {
    padding: 0.6rem !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
}

/* ---- Charts (Balanced) ---- */
.js-plotly-plot {
    margin: 1rem 0 !important;
}

.plotly {
    border-radius: 8px !important;
}

/* ---- Select Boxes & Inputs (Balanced) ---- */
.stSelectbox, .stMultiselect, .stTextInput, .stNumberInput, .stDateInput {
    margin-bottom: 0.75rem !important;
}

.stSelectbox > div > div,
.stMultiselect > div > div,
.stTextInput > div > div,
.stNumberInput > div > div,
.stDateInput > div > div {
    background: rgba(255, 255, 255, 0.08) !important;
    border: 1px solid rgba(102, 126, 234, 0.3) !important;
    border-radius: 8px !important;
    color: #e0e0e0 !important;
}

/* ---- Checkboxes & Radio (Balanced) ---- */
.stCheckbox, .stRadio {
    margin-bottom: 0.5rem !important;
}

/* ---- Column Gaps (Balanced) ---- */
div[data-testid="column"] {
    padding: 0 0.5rem !important;
}

/* ---- Sidebar Styling ---- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%) !important;
    border-right: 2px solid rgba(102, 126, 234, 0.3) !important;
}

/* ---- Navigation ---- */
.stRadio > label {
    font-weight: 500 !important;
    color: #e0e0e0 !important;
}

/* ---- Info, Warning, Success, Error Boxes ---- */
.stAlert {
    border-radius: 8px !important;
    border-left: 4px solid !important;
    padding: 0.75rem 1rem !important;
    margin: 0.75rem 0 !important;
}

/* ---- Upload Widget ---- */
[data-testid="stFileUploader"] {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 2px dashed rgba(102, 126, 234, 0.4) !important;
    border-radius: 8px !important;
    padding: 1rem !important;
    margin: 0.75rem 0 !important;
}

/* ---- Main Background ---- */
.stApp {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%) !important;
}

/* ---- Download Button Special ---- */
.stDownloadButton>button {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
    color: white !important;
    border-radius: 8px !important;
    padding: 0.5rem 1rem !important;
    font-weight: 500 !important;
}

/* ---- Text Elements ---- */
p, li, span, label {
    color: #d0d0d0 !important;
}

/* ---- Markdown Elements ---- */
.stMarkdown {
    color: #e0e0e0 !important;
}

/* ---- Spinner ---- */
.stSpinner > div {
    border-color: #667eea !important;
}

/* ---- Progress Bar ---- */
.stProgress > div > div {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
}

/* ---- Caption Text ---- */
.caption {
    color: #a0a0a0 !important;
    font-size: 0.9rem !important;
}
</style>""", unsafe_allow_html=True)

# -------------------------
# Date Filter Function
# -------------------------
def apply_date_filter(df):
    """Apply date filter based on session state"""
    import pandas as pd

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
    import pandas as pd

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
        logo_path = Path("Public/hdfc credit .png")
        if logo_path.exists():
            st.image(str(logo_path), width=150)

        banner_path = None
        module = st.session_state.get('selected_module')
        if module is None:
            banner_path = Path("Public/HDFC-Credit-Cards.png")
        elif module == "campaign":
            banner_path = Path("Public/HDFC campaign Analysis.png")

        if banner_path and banner_path.exists():
            st.image(str(banner_path), width=150)

    with col2:
        st.markdown(
            "<h1 style='text-align:center;color:#fff;'>HDFC Analytics Dashboard</h1>",
            unsafe_allow_html=True
        )

    with col3:
        st.markdown("🟢 **DB Connected**" if engine else "🔴 **DB Error**")
        st.markdown("<br>", unsafe_allow_html=True)

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

    st.markdown("---")

    # -------------------------
    # Date Filter
    # -------------------------
    st.markdown("## 📅 Date Filter")
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
                        st.markdown("<br>", unsafe_allow_html=True)
                        filtered_count = len(apply_date_filter(st.session_state.mis_data))
                        total_count = len(st.session_state.mis_data)
                        st.info(f"📊 **{filtered_count:,}** of **{total_count:,}** records")
                else:
                    with fc2:
                        st.warning("⚠️ No valid dates in selected column")
            except Exception as e:
                with fc2:
                    st.error(f"❌ Error: {str(e)[:30]}")
        else:
            with fc2:
                st.warning("⚠️ No date columns found")
    elif st.session_state.date_filter_enabled and st.session_state.mis_data is None:
        with fc2:
            st.info("ℹ️ Load data first to enable date filter")

    st.markdown("---")

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

        st.markdown("---")
        if st.session_state.mis_data is not None:
            st.markdown("**📊 Current Data**")
            source_icon = "📁" if st.session_state.mis_source == "file" else "🗄️"
            st.caption(f"{source_icon} {st.session_state.mis_filename}")
            st.caption(f"📊 {len(st.session_state.mis_data):,} records")
        else:
            st.caption("⚠️ No data loaded")

    with main_col:
        filtered_data = apply_date_filter(st.session_state.mis_data) if st.session_state.mis_data is not None else None
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
