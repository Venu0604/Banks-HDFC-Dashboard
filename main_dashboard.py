"""
HDFC Unified Analytics Dashboard - Main Entry Point
Modern, Professional Interface with Redesigned UI
"""

import streamlit as st
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
# Modern Design System (Inspired by Design Reboot)
# -------------------------
st.markdown("""<style>
/* =====================================================
   MODERN DESIGN SYSTEM - Clean, Professional & Vibrant
   Based on Tailwind + ShadcnUI Design Principles
   ===================================================== */

/* ---- CSS Variables (HSL Color System) ---- */
:root {
    --background: hsl(222, 47%, 11%);
    --foreground: hsl(210, 40%, 98%);
    --card: hsl(217, 33%, 17%);
    --card-foreground: hsl(210, 40%, 98%);
    --primary: hsl(250, 70%, 65%);
    --primary-gradient-start: hsl(250, 70%, 65%);
    --primary-gradient-end: hsl(270, 60%, 60%);
    --secondary: hsl(217, 32%, 22%);
    --muted: hsl(217, 32%, 20%);
    --muted-foreground: hsl(215, 20%, 65%);
    --accent: hsl(250, 70%, 65%);
    --border: hsl(217, 32%, 25%);
    --input: hsl(217, 32%, 22%);
    --success: hsl(142, 71%, 45%);
    --warning: hsl(38, 92%, 50%);
    --error: hsl(0, 85%, 60%);
    --radius: 0.75rem;
}

/* ---- Main App Background ---- */
.stApp {
    background: linear-gradient(135deg,
        hsl(222, 47%, 11%) 0%,
        hsl(220, 50%, 8%) 50%,
        hsl(222, 47%, 11%) 100%) !important;
}

/* ---- Container Spacing ---- */
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 1rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 100% !important;
}

/* ---- Typography ---- */
h1, h2, h3, h4, h5, h6 {
    font-weight: 700 !important;
    color: var(--foreground) !important;
}

h1 {
    font-size: 2.5rem !important;
    background: linear-gradient(135deg, var(--primary-gradient-start), var(--primary-gradient-end));
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    margin-bottom: 0.5rem !important;
}

h2 {
    font-size: 2rem !important;
    margin-top: 1rem !important;
    margin-bottom: 0.75rem !important;
}

h3 {
    font-size: 1.5rem !important;
    font-weight: 600 !important;
    margin-top: 0.75rem !important;
    margin-bottom: 0.5rem !important;
}

h4 {
    font-size: 1.2rem !important;
    font-weight: 600 !important;
}

p, span, label, li {
    color: var(--muted-foreground) !important;
}

/* ---- Cards & Containers ---- */
.element-container {
    margin-bottom: 0.75rem !important;
}

div[data-testid="stVerticalBlock"] > div {
    gap: 0.75rem !important;
}

/* ---- Module Cards ---- */
.module-card {
    background: linear-gradient(135deg, var(--card) 0%, var(--muted) 100%) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 1.5rem !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    cursor: pointer !important;
}

.module-card:hover {
    transform: translateY(-4px) scale(1.02) !important;
    box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3) !important;
    border-color: var(--primary) !important;
}

/* ---- Metric Cards (Stats) ---- */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, var(--primary-gradient-start), var(--primary-gradient-end)) !important;
    padding: 1.25rem !important;
    border-radius: var(--radius) !important;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4) !important;
    border: none !important;
}

[data-testid="stMetricValue"] {
    font-size: 2rem !important;
    font-weight: 700 !important;
    color: white !important;
}

[data-testid="stMetricLabel"] {
    color: rgba(255, 255, 255, 0.9) !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}

/* ---- Buttons ---- */
.stButton>button {
    background: linear-gradient(135deg, var(--primary-gradient-start), var(--primary-gradient-end)) !important;
    color: white !important;
    border: none !important;
    border-radius: var(--radius) !important;
    padding: 0.625rem 1.25rem !important;
    font-weight: 600 !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3) !important;
}

.stButton>button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 20px rgba(102, 126, 234, 0.5) !important;
}

.stButton>button:active {
    transform: translateY(0) !important;
}

/* ---- Download Buttons ---- */
.stDownloadButton>button {
    background: linear-gradient(135deg, var(--success), hsl(142, 71%, 40%)) !important;
    color: white !important;
    border-radius: var(--radius) !important;
    font-weight: 600 !important;
}

/* ---- Tabs ---- */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem !important;
    background: var(--muted) !important;
    padding: 0.5rem !important;
    border-radius: var(--radius) !important;
    margin-bottom: 1rem !important;
}

.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    color: var(--muted-foreground) !important;
    padding: 0.75rem 1.5rem !important;
    border-radius: calc(var(--radius) - 0.25rem) !important;
    font-weight: 500 !important;
    transition: all 0.3s ease !important;
}

.stTabs [data-baseweb="tab"]:hover {
    background: rgba(102, 126, 234, 0.15) !important;
    color: var(--foreground) !important;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, var(--primary-gradient-start), var(--primary-gradient-end)) !important;
    color: white !important;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3) !important;
}

/* ---- Expanders ---- */
.streamlit-expanderHeader {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 1rem 1.25rem !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
}

.streamlit-expanderHeader:hover {
    background: var(--muted) !important;
    border-color: var(--primary) !important;
}

.streamlit-expanderContent {
    background: var(--card) !important;
    border-radius: 0 0 var(--radius) var(--radius) !important;
    padding: 1.25rem !important;
    border: 1px solid var(--border) !important;
    border-top: none !important;
}

/* ---- Input Fields ---- */
.stSelectbox > div > div,
.stMultiselect > div > div,
.stTextInput > div > div,
.stNumberInput > div > div,
.stDateInput > div > div,
.stTextArea > div > div {
    background: var(--input) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--foreground) !important;
    padding: 0.625rem !important;
    transition: all 0.3s ease !important;
}

.stSelectbox > div > div:focus-within,
.stMultiselect > div > div:focus-within,
.stTextInput > div > div:focus-within,
.stNumberInput > div > div:focus-within,
.stDateInput > div > div:focus-within,
.stTextArea > div > div:focus-within {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
}

/* ---- DataFrames ---- */
[data-testid="stDataFrame"] {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 0.75rem !important;
}

.dataframe {
    font-size: 0.9rem !important;
    color: var(--foreground) !important;
}

.dataframe th {
    background: linear-gradient(135deg, var(--primary-gradient-start), var(--primary-gradient-end)) !important;
    color: white !important;
    font-weight: 600 !important;
    padding: 0.875rem !important;
    text-transform: uppercase !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.5px !important;
}

.dataframe td {
    padding: 0.75rem !important;
    border-bottom: 1px solid var(--border) !important;
}

.dataframe tr:hover {
    background: var(--muted) !important;
}

/* ---- File Upload ---- */
[data-testid="stFileUploader"] {
    background: var(--card) !important;
    border: 2px dashed var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 2rem !important;
    transition: all 0.3s ease !important;
}

[data-testid="stFileUploader"]:hover {
    border-color: var(--primary) !important;
    background: var(--muted) !important;
}

/* ---- Alerts ---- */
.stAlert {
    border-radius: var(--radius) !important;
    border-left: 4px solid !important;
    padding: 1rem 1.25rem !important;
    margin: 1rem 0 !important;
    backdrop-filter: blur(8px) !important;
}

div[data-baseweb="notification"] {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
}

/* ---- Info Alert ---- */
.stAlert[data-baseweb="notification"][kind="info"] {
    background: rgba(102, 126, 234, 0.1) !important;
    border-left-color: var(--primary) !important;
}

/* ---- Success Alert ---- */
.stAlert[data-baseweb="notification"][kind="success"] {
    background: rgba(34, 197, 94, 0.1) !important;
    border-left-color: var(--success) !important;
}

/* ---- Warning Alert ---- */
.stAlert[data-baseweb="notification"][kind="warning"] {
    background: rgba(251, 146, 60, 0.1) !important;
    border-left-color: var(--warning) !important;
}

/* ---- Error Alert ---- */
.stAlert[data-baseweb="notification"][kind="error"] {
    background: rgba(239, 68, 68, 0.1) !important;
    border-left-color: var(--error) !important;
}

/* ---- Horizontal Rules ---- */
hr {
    margin: 1.5rem 0 !important;
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg,
        transparent,
        var(--primary),
        transparent) !important;
}

/* ---- Header Styling ---- */
header[data-testid="stHeader"] {
    background: rgba(217, 33%, 17%, 0.5) !important;
    backdrop-filter: blur(10px) !important;
    border-bottom: 1px solid var(--border) !important;
}

/* ---- Sidebar ---- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--background) 0%, hsl(220, 50%, 8%) 100%) !important;
    border-right: 1px solid var(--border) !important;
}

/* ---- Spinners ---- */
.stSpinner > div {
    border-color: var(--primary) !important;
}

/* ---- Progress Bar ---- */
.stProgress > div > div {
    background: linear-gradient(90deg, var(--primary-gradient-start), var(--primary-gradient-end)) !important;
}

/* ---- Radio Buttons ---- */
.stRadio > label {
    font-weight: 500 !important;
    color: var(--foreground) !important;
}

/* ---- Checkboxes ---- */
.stCheckbox > label {
    font-weight: 500 !important;
    color: var(--foreground) !important;
}

/* ---- Column Gaps ---- */
div[data-testid="column"] {
    padding: 0 0.5rem !important;
}

/* ---- Animations ---- */
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.animate-fade-in {
    animation: fadeIn 0.5s ease-out;
}

/* ---- Status Indicators ---- */
.status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    display: inline-block;
    margin-right: 0.5rem;
}

.status-connected {
    background: var(--success);
    box-shadow: 0 0 8px var(--success);
}

.status-disconnected {
    background: var(--error);
    box-shadow: 0 0 8px var(--error);
}

/* ---- Module Grid ---- */
.module-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.5rem;
    margin-top: 1.5rem;
}

/* ---- Caption Text ---- */
.caption, [data-testid="stCaptionContainer"] {
    color: var(--muted-foreground) !important;
    font-size: 0.875rem !important;
}

/* ---- Markdown Styling ---- */
.stMarkdown {
    color: var(--foreground) !important;
}

.stMarkdown a {
    color: var(--primary) !important;
    text-decoration: none !important;
    font-weight: 500 !important;
}

.stMarkdown a:hover {
    text-decoration: underline !important;
}
</style>""", unsafe_allow_html=True)

# -------------------------
# Helper Functions
# -------------------------
@st.cache_data(ttl=3600, show_spinner=False)  # Cache for 1 hour
def load_mis_data_from_db(_engine):
    """Load MIS data from database with caching"""
    import pandas as pd

    try:
        df = pd.read_sql('SELECT * FROM "HDFC_MIS_Data"', _engine)
        df.columns = df.columns.str.strip()
        return df, None
    except Exception as e:
        return None, str(e)


def auto_load_data(engine):
    """Automatically load MIS data from database on startup if not already loaded"""
    # Only load if data is not already in session state
    if st.session_state.mis_data is None and engine is not None:
        # Check if we should auto-load (only on first run)
        if 'auto_load_attempted' not in st.session_state:
            st.session_state.auto_load_attempted = True

            with st.spinner("🔄 Loading MIS data from database..."):
                df, error = load_mis_data_from_db(engine)

                if df is not None and len(df) > 0:
                    st.session_state.mis_data = df
                    st.session_state.mis_filename = "Database (Auto-loaded)"
                    st.session_state.mis_source = "database"
                    st.success(f"✅ Auto-loaded {len(df):,} MIS records from database")
                elif error:
                    st.session_state.auto_load_attempted = False  # Allow retry
                    st.warning(f"⚠️ Could not auto-load data: {error[:100]}")


def render_header():
    """Render modern dashboard header using Streamlit columns"""
    # Create centered header container
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # Title with gradient
        st.markdown("""
        <div style="text-align: center;">
            <h1 style="
                margin: 0;
                font-size: 2rem;
                background: linear-gradient(135deg, hsl(250, 70%, 65%), hsl(270, 60%, 60%));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            ">🏦 HDFC Analytics Dashboard</h1>
            <p style="margin: 0.5rem 0 0 0; color: hsl(215, 20%, 65%); font-size: 0.95rem;">
                Unified Campaign Intelligence Platform
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Data badge
        if st.session_state.mis_data is not None:
            record_count = len(st.session_state.mis_data)
            st.markdown(f"""
            <div style="text-align: center; margin-top: 0.75rem;">
                <span style="
                    font-size: 0.8rem;
                    background: rgba(34, 197, 94, 0.2);
                    color: hsl(142, 71%, 60%);
                    padding: 0.4rem 0.8rem;
                    border-radius: 0.5rem;
                    border: 1px solid rgba(34, 197, 94, 0.4);
                ">📊 {record_count:,} records loaded</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)


def render_module_card(title, description, icon, module_key):
    """Render a modern module card"""
    col1, col2 = st.columns([1, 20])

    with col1:
        st.markdown(f"""
            <div style="
                width: 48px;
                height: 48px;
                background: linear-gradient(135deg, hsl(250, 70%, 65%), hsl(270, 60%, 60%));
                border-radius: 0.75rem;
                display: flex;
                align-items: center;
                justify-center;
                font-size: 1.5rem;
            ">
                {icon}
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"### {title}")
        st.caption(description)

    if st.button(f"Open {title}", key=f"btn_{module_key}", use_container_width=True):
        st.session_state.selected_module = module_key
        st.rerun()


def render_system_status(db_connected):
    """Render system status card"""
    status_icon = "🟢" if db_connected else "🔴"
    status_text = "Connected" if db_connected else "Disconnected"

    # Data status
    data_loaded = st.session_state.mis_data is not None
    data_icon = "🟢" if data_loaded else "🟡"
    data_text = f"Loaded ({len(st.session_state.mis_data):,} records)" if data_loaded else "Not loaded"

    st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, hsl(217, 33%, 17%), hsl(217, 32%, 20%));
            padding: 1.5rem;
            border-radius: 0.75rem;
            border: 1px solid hsl(217, 32%, 25%);
            margin-top: 2rem;
        ">
            <h3 style="margin-top: 0;">⚡ System Status</h3>
            <div style="display: flex; flex-direction: column; gap: 0.75rem; margin-top: 1rem;">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    {status_icon}
                    <span style="color: hsl(215, 20%, 65%);">Database: {status_text}</span>
                </div>
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    {data_icon}
                    <span style="color: hsl(215, 20%, 65%);">MIS Data: {data_text}</span>
                </div>
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    🟢
                    <span style="color: hsl(215, 20%, 65%);">Analytics Engine: Active</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)


# -------------------------
# Main Dashboard
# -------------------------
def main():
    """Main dashboard orchestrator"""

    # Initialize session state
    for key, default in [
        ('selected_module', None),
        ('mis_data', None),
        ('mis_filename', None),
        ('mis_source', None),
        ('auto_load_attempted', False),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    # Database connection
    engine, _ = get_db_engine()
    db_connected = engine is not None

    # Auto-load data from database on first run
    auto_load_data(engine)

    # Render Header
    render_header()

    # Navigation
    module = st.session_state.selected_module

    if module is not None:
        # Back button
        if st.button("⬅️ Back to Dashboard", key="back_btn"):
            st.session_state.selected_module = None
            st.rerun()
        st.markdown("---")

    # Module Routing
    if module is None:
        # ===== HOME PAGE =====

        # Data Management Section
        if st.session_state.mis_data is not None:
            col1, col2, col3 = st.columns([2, 1, 1])

            with col1:
                st.markdown("### 💾 Data Status")
                st.info(f"""
                    📊 **{len(st.session_state.mis_data):,}** MIS records loaded
                    📁 Source: **{st.session_state.mis_source or 'Unknown'}**
                    🏷️ Filename: **{st.session_state.mis_filename or 'N/A'}**
                """)

            with col2:
                if st.button("🔄 Reload from DB", use_container_width=True, help="Refresh data from database"):
                    if engine:
                        with st.spinner("Reloading..."):
                            # Clear cache and reload
                            load_mis_data_from_db.clear()
                            df, error = load_mis_data_from_db(engine)
                            if df is not None:
                                st.session_state.mis_data = df
                                st.session_state.mis_filename = "Database (Reloaded)"
                                st.session_state.mis_source = "database"
                                st.success(f"✅ Reloaded {len(df):,} records")
                                st.rerun()
                            else:
                                st.error(f"❌ Error: {error}")
                    else:
                        st.error("❌ Database not available")

            with col3:
                if st.button("🗑️ Clear Data", use_container_width=True, help="Clear loaded data"):
                    st.session_state.mis_data = None
                    st.session_state.mis_filename = None
                    st.session_state.mis_source = None
                    st.session_state.auto_load_attempted = False
                    st.rerun()
        else:
            st.info("ℹ️ No MIS data loaded. Data will auto-load from database on next refresh if available.")
            if st.button("📥 Load from Database Now", use_container_width=False):
                if engine:
                    with st.spinner("Loading..."):
                        df, error = load_mis_data_from_db(engine)
                        if df is not None:
                            st.session_state.mis_data = df
                            st.session_state.mis_filename = "Database"
                            st.session_state.mis_source = "database"
                            st.success(f"✅ Loaded {len(df):,} records")
                            st.rerun()
                        else:
                            st.error(f"❌ Error: {error}")
                else:
                    st.error("❌ Database not available")

        st.markdown("---")

        st.markdown("## 📊 Analytics Modules")
        st.markdown("Select a module to access campaign analytics, data processing, and reporting tools")
        st.markdown("<br>", unsafe_allow_html=True)

        # Module Grid (2 columns)
        col1, col2 = st.columns(2)

        with col1:
            with st.container():
                st.markdown("""
                    <div class="module-card">
                """, unsafe_allow_html=True)
                render_module_card(
                    "Google Ads Summary",
                    "Process and analyze Google Ads campaigns with MIS data integration",
                    "📈",
                    "google"
                )
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            with st.container():
                st.markdown("""
                    <div class="module-card">
                """, unsafe_allow_html=True)
                render_module_card(
                    "Status Analysis",
                    "Track final decision counts with creation and decision date filters",
                    "📊",
                    "status"
                )
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            with st.container():
                st.markdown("""
                    <div class="module-card">
                """, unsafe_allow_html=True)
                render_module_card(
                    "Phone Numbers",
                    "Extract and map phone numbers from campaign data using LC2 codes",
                    "📞",
                    "phone"
                )
                st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            with st.container():
                st.markdown("""
                    <div class="module-card">
                """, unsafe_allow_html=True)
                render_module_card(
                    "Campaign Analysis",
                    "Analyze campaign performance across multiple channels with cost tracking",
                    "🎯",
                    "campaign"
                )
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            with st.container():
                st.markdown("""
                    <div class="module-card">
                """, unsafe_allow_html=True)
                render_module_card(
                    "MIS Upload",
                    "Upload and manage MIS data from Excel/CSV files to database",
                    "📤",
                    "upload"
                )
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            with st.container():
                st.markdown("""
                    <div class="module-card">
                """, unsafe_allow_html=True)
                render_module_card(
                    "SQL Console",
                    "Execute SQL queries and export data directly from the database",
                    "💻",
                    "sql"
                )
                st.markdown("</div>", unsafe_allow_html=True)

        # System Status
        render_system_status(db_connected)

    elif module == "google":
        google_summary.render_google_ads_module(engine, st.session_state.mis_data)
    elif module == "campaign":
        HDFC_campaign.render_campaign_analysis_module(st.session_state.mis_data, engine)
    elif module == "status":
        status_analysis.render_status_analysis_module(st.session_state.mis_data, engine)
    elif module == "phone":
        phone_numbers.render_phone_numbers_module(engine, st.session_state.mis_data)
    elif module == "upload":
        Input_MIS.render_mis_upload_module(engine)
    elif module == "sql":
        sql_console.render_sql_console_module(engine)


# -------------------------
# Run Application
# -------------------------
if __name__ == "__main__":
    main()
