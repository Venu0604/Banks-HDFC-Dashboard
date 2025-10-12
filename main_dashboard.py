"""
HDFC Unified Analytics Dashboard - Main Entry Point
Modern, Professional Interface
"""

import streamlit as st
from sqlalchemy import create_engine
from pathlib import Path

# Import individual modules
import phone_numbers
import HDFC_campaign
import google_summary
import status_analysis
import Input_MIS
import sql_console


# -------------------------
# Page Configuration
# -------------------------
st.set_page_config(
    page_title="HDFC Analytics Dashboard",
    layout="wide",
    page_icon="🏦",
    initial_sidebar_state="collapsed"
)


# -------------------------
# Modern Grayish Bank Dashboard Styling
# -------------------------
st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global Styles - Dark Gray Bank Theme */
    * {
        font-family: 'Inter', sans-serif;
    }

    .main {
        background: linear-gradient(180deg, #111827 0%, #1f2937 50%, #111827 100%);
        color: #ffffff;
    }

    /* Header Styles - White on Dark */
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #ffffff;
        text-align: center;
        margin: 0;
        padding: 0;
        letter-spacing: -0.5px;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
    }

    .sub-header {
        text-align: center;
        color: #d1d5db;
        margin-top: 0.5rem;
        margin-bottom: 2rem;
        font-size: 1rem;
        font-weight: 400;
    }

    /* Metric Cards - White Cards with Glassmorphism */
    .stMetric {
        background: linear-gradient(135deg, #374151 0%, #4b5563 100%);
        padding: 1.8rem;
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        transition: all 0.3s ease;
        border: 1px solid #4b5563;
        backdrop-filter: blur(10px);
    }

    .stMetric:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5);
        border-color: #6b7280;
        background: linear-gradient(135deg, #4b5563 0%, #6b7280 100%);
    }

    .stMetric label {
        color: #d1d5db !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .stMetric [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }

    .stMetric [data-testid="stMetricDelta"] {
        font-weight: 500 !important;
        color: #10b981 !important;
    }

    /* Headings - White/Light Gray */
    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 700 !important;
        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    }

    h4, h5, h6 {
        color: #e5e7eb !important;
        font-weight: 600 !important;
    }

    /* Tabs - Gray Gradient with Purple Active */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(55, 65, 81, 0.3);
        padding: 8px;
        border-radius: 12px;
        backdrop-filter: blur(10px);
        border: 1px solid #374151;
    }

    .stTabs [data-baseweb="tab-list"] button {
        color: #9ca3af !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        transition: all 0.3s ease !important;
        border: none !important;
        background: transparent !important;
    }

    .stTabs [data-baseweb="tab-list"] button:hover {
        background: linear-gradient(135deg, #4b5563 0%, #6b7280 100%) !important;
        color: #ffffff !important;
    }

    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 20px rgba(139, 92, 246, 0.4) !important;
    }

    /* Buttons - Professional Banking Style */
    .stButton button {
        border-radius: 8px !important;
        font-weight: 500 !important;
        padding: 0.6rem 1.2rem !important;
        transition: all 0.25s ease !important;
        border: 1px solid #4b5563 !important;
        box-shadow: none !important;
        background: #374151 !important;
        color: #e5e7eb !important;
        font-size: 0.95rem !important;
    }

    .stButton button:hover {
        background: #4b5563 !important;
        color: #ffffff !important;
        border-color: #6b7280 !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2) !important;
    }

    .stButton button[kind="primary"] {
        background: #4b5563 !important;
        color: #ffffff !important;
        border: 1px solid #6b7280 !important;
        font-weight: 600 !important;
    }

    .stButton button[kind="primary"]:hover {
        background: #6b7280 !important;
        border-color: #9ca3af !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25) !important;
    }

    /* Secondary button style (for non-active state) */
    .stButton button[kind="secondary"] {
        background: transparent !important;
        color: #9ca3af !important;
        border: 1px solid #374151 !important;
    }

    .stButton button[kind="secondary"]:hover {
        background: #374151 !important;
        color: #e5e7eb !important;
        border-color: #4b5563 !important;
    }

    /* Compact Icon Home Button */
    button[key="home_icon"] {
        min-width: 50px !important;
        width: 50px !important;
        height: 50px !important;
        padding: 0 !important;
        border-radius: 10px !important;
        font-size: 1.6rem !important;
        background: #374151 !important;
        border: 1px solid #4b5563 !important;
        color: #e5e7eb !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    button[key="home_icon"]:hover {
        background: #4b5563 !important;
        border-color: #6b7280 !important;
        color: #ffffff !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3) !important;
    }

    .stDownloadButton button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: white !important;
        box-shadow: 0 4px 20px rgba(16, 185, 129, 0.3) !important;
    }

    .stDownloadButton button:hover {
        background: linear-gradient(135deg, #059669 0%, #10b981 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 24px rgba(16, 185, 129, 0.4) !important;
    }

    /* Alert Boxes - Glassmorphism */
    .stAlert {
        border-radius: 12px !important;
        border: 1px solid #374151 !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3) !important;
        background: rgba(55, 65, 81, 0.6) !important;
        backdrop-filter: blur(10px) !important;
        color: #e5e7eb !important;
    }

    /* DataFrames - White Cards with Shadow */
    .stDataFrame {
        border-radius: 16px !important;
        overflow: hidden !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4) !important;
        border: 1px solid #374151 !important;
        background: #1f2937 !important;
    }

    /* Expander - Gray Gradient */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #374151 0%, #4b5563 100%) !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        color: #ffffff !important;
        border: 1px solid #4b5563 !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3) !important;
    }

    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, #4b5563 0%, #6b7280 100%) !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4) !important;
    }

    /* File Uploader - Gray Card */
    .stFileUploader {
        background: rgba(31, 41, 55, 0.8) !important;
        border-radius: 12px !important;
        border: 2px dashed #6b7280 !important;
        padding: 1.5rem !important;
        backdrop-filter: blur(10px) !important;
    }

    .stFileUploader:hover {
        border-color: #8b5cf6 !important;
    }

    /* Section Divider - Gray Gradient */
    .section-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #6b7280, transparent);
        margin: 2rem 0;
    }

    /* Input Fields - Dark Theme */
    .stTextInput input, .stSelectbox select, .stDateInput input {
        background: #374151 !important;
        color: #ffffff !important;
        border: 1px solid #4b5563 !important;
        border-radius: 8px !important;
    }

    .stTextInput input:focus, .stSelectbox select:focus, .stDateInput input:focus {
        border-color: #8b5cf6 !important;
        box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.2) !important;
    }

    /* Navigation Dropdown Styling */
    .stSelectbox > div > div {
        background: #374151 !important;
        border: 1px solid #4b5563 !important;
        border-radius: 10px !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2) !important;
    }

    .stSelectbox [data-baseweb="select"] > div {
        background: #374151 !important;
        border-color: #4b5563 !important;
        color: #d1d5db !important;
        border-radius: 10px !important;
    }

    .stSelectbox [data-baseweb="select"]:hover > div {
        background: #4b5563 !important;
        border-color: #6b7280 !important;
        color: #ffffff !important;
    }

    /* Dropdown menu options */
    [data-baseweb="popover"] {
        background: #1f2937 !important;
        border: 1px solid #374151 !important;
    }

    [role="listbox"] {
        background: #1f2937 !important;
    }

    [role="option"] {
        background: #1f2937 !important;
        color: #d1d5db !important;
    }

    [role="option"]:hover {
        background: #374151 !important;
        color: #ffffff !important;
    }

    /* Sidebar - Dark Gray */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1f2937 0%, #111827 100%) !important;
    }

    /* Success/Info/Warning/Error Colors */
    .stSuccess {
        background: rgba(16, 185, 129, 0.2) !important;
        color: #10b981 !important;
    }

    .stInfo {
        background: rgba(139, 92, 246, 0.2) !important;
        color: #8b5cf6 !important;
    }

    .stWarning {
        background: rgba(251, 191, 36, 0.2) !important;
        color: #fbbf24 !important;
    }

    .stError {
        background: rgba(239, 68, 68, 0.2) !important;
        color: #ef4444 !important;
    }
    </style>
""", unsafe_allow_html=True)


# -------------------------
# Database Connection
# -------------------------
@st.cache_resource
def get_db_engine():
    """Initialize database connection"""
    try:
        engine = create_engine("postgresql+psycopg2://postgres:1234@localhost:5432/Nxtify")
        with engine.connect() as conn:
            pass
        return engine, None
    except Exception as e:
        return None, str(e)


@st.cache_data
def load_image(image_path):
    """Load and cache images for faster display"""
    from pathlib import Path
    if Path(image_path).exists():
        return str(image_path)
    return None


# -------------------------
# Main Dashboard
# -------------------------
def main():
    """Main dashboard orchestrator"""
    import pandas as pd

    # Get database engine
    engine, error = get_db_engine()

    # Header with Logo and module images on extreme left
    col1, col2, col3 = st.columns([1.5, 3, 1.5])

    with col1:
        # Show logo and module-specific image stacked vertically
        logo_path = Path("Public/hdfc credit .png")
        if logo_path.exists():
            cached_logo = load_image(str(logo_path))
            if cached_logo:
                st.image(cached_logo, width=150)

        # Module-specific banner image below logo
        if st.session_state.get('selected_module') is None:
            banner_path = Path("Public/HDFC-Credit-Cards.png")
            if banner_path.exists():
                cached_banner = load_image(str(banner_path))
                if cached_banner:
                    st.image(cached_banner, width=150)
        elif st.session_state.get('selected_module') == "google":
            banner_files = list(Path("Public").glob("GoogleAdd*HDFC.png"))
            if banner_files and banner_files[0].exists():
                cached_banner = load_image(str(banner_files[0]))
                if cached_banner:
                    st.image(cached_banner, width=150)
        elif st.session_state.get('selected_module') == "campaign":
            banner_path = Path("Public/HDFC campaign Analysis.png")
            if banner_path.exists():
                cached_banner = load_image(str(banner_path))
                if cached_banner:
                    st.image(cached_banner, width=150)

    with col2:
        st.markdown("<h1 style='text-align: center; color: #ffffff; font-weight: 700; font-size: 2.2rem; text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);'>HDFC Analytics Dashboard</h1>", unsafe_allow_html=True)

    with col3:
        if engine:
            st.markdown("🟢 **DB Connected**")
        else:
            st.markdown("🔴 **DB Error**")

        st.markdown("<br>", unsafe_allow_html=True)

        if 'selected_module' not in st.session_state:
            st.session_state.selected_module = None

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
                st.rerun()

        with nav_row[1]:
            if st.session_state.selected_module is None:
                current_label = "Select Module..."
            else:
                current_label = [k for k, v in nav_options.items() if v == st.session_state.selected_module][0]

            def update_module():
                selected_value = nav_options[st.session_state.nav_dropdown_widget]
                if selected_value != st.session_state.selected_module:
                    st.session_state.selected_module = selected_value

            st.selectbox(
                "Modules",
                options=list(nav_options.keys()),
                index=list(nav_options.keys()).index(current_label),
                key="nav_dropdown_widget",
                label_visibility="collapsed",
                on_change=update_module
            )

    # Divider
    st.markdown("---")

    # Initialize session state for MIS data
    if 'mis_data' not in st.session_state:
        st.session_state.mis_data = None
    if 'mis_filename' not in st.session_state:
        st.session_state.mis_filename = None
    if 'mis_source' not in st.session_state:
        st.session_state.mis_source = None
    if 'data_preloaded' not in st.session_state:
        st.session_state.data_preloaded = False

    # Preload data from database on first run
    if not st.session_state.data_preloaded and engine:
        try:
            import pandas as pd
            query = 'SELECT * FROM "HDFC_MIS_Data"'
            df_mis = pd.read_sql(query, engine)
            if len(df_mis) > 0:
                df_mis.columns = df_mis.columns.str.strip()
                st.session_state.mis_data = df_mis
                st.session_state.mis_filename = "Database"
                st.session_state.mis_source = "database"
                st.session_state.data_preloaded = True
        except:
            pass  # Table might not exist, user can upload manually

    # Two columns: Left sidebar for data source, Right main content area
    sidebar_col, main_col = st.columns([1, 4])

    with sidebar_col:
        st.markdown("### 📁 Data Source")

        # MIS source selection dropdown
        mis_options = ["Current Data", "📁 Upload New File", "🗄️ Reload from Database"]

        selected_source = st.selectbox(
            "Choose Action",
            options=mis_options,
            key="mis_source_selector",
            label_visibility="collapsed"
        )

        # Handle file upload
        if selected_source == "📁 Upload New File":
            mis_file = st.file_uploader(
                "Upload Excel",
                type=["xlsx"],
                key="main_mis_upload",
                label_visibility="collapsed"
            )

            if mis_file:
                with st.spinner("Loading..."):
                    import pandas as pd
                    df_mis = pd.read_excel(mis_file, sheet_name="Sheet1")
                    df_mis.columns = df_mis.columns.str.strip()
                    st.session_state.mis_data = df_mis
                    st.session_state.mis_filename = mis_file.name
                    st.session_state.mis_source = "file"
                    st.success(f"✅ {len(df_mis):,} records")
                    st.rerun()

        # Handle database reload
        elif selected_source == "🗄️ Reload from Database":
            if st.button("Load Now", use_container_width=True, type="primary"):
                if engine:
                    with st.spinner("Loading..."):
                        try:
                            import pandas as pd
                            query = 'SELECT * FROM "HDFC_MIS_Data"'
                            df_mis = pd.read_sql(query, engine)
                            df_mis.columns = df_mis.columns.str.strip()
                            st.session_state.mis_data = df_mis
                            st.session_state.mis_filename = "Database"
                            st.session_state.mis_source = "database"
                            st.success(f"✅ {len(df_mis):,} records")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)[:30]}")
                else:
                    st.error("DB not available")

        # Show current data info
        st.markdown("---")
        if st.session_state.mis_data is not None:
            st.markdown("**📊 Current Data**")
            source_icon = "📁" if st.session_state.mis_source == "file" else "🗄️"
            st.caption(f"{source_icon} {st.session_state.mis_filename}")
            st.caption(f"📊 {len(st.session_state.mis_data):,} records")

            # Show last DB update time
            if engine and st.session_state.mis_source == "database":
                try:
                    import pandas as pd
                    query = """
                    SELECT updated_at
                    FROM "MIS_Update_Log"
                    WHERE table_name = 'HDFC_MIS_Data'
                    ORDER BY updated_at DESC
                    LIMIT 1
                    """
                    last_update_df = pd.read_sql(query, engine)
                    if len(last_update_df) > 0:
                        update_time = pd.to_datetime(last_update_df.iloc[0]['updated_at'])
                        st.caption(f"🕐 {update_time.strftime('%Y-%m-%d %H:%M')}")
                except:
                    pass
        else:
            st.caption("⚠️ No data loaded")

    # Main Content Based on Selection
    with main_col:
        if st.session_state.mis_data is not None:
            # Show different content based on selected module
            if st.session_state.selected_module is None:
                # Dashboard View - Show Status Analysis
                status_analysis.render_status_analysis_module(st.session_state.mis_data, engine)

            elif st.session_state.selected_module == "phone":
                phone_numbers.render_phone_numbers_module(engine, st.session_state.mis_data)

            elif st.session_state.selected_module == "campaign":
                HDFC_campaign.render_campaign_analysis_module(st.session_state.mis_data, engine)

            elif st.session_state.selected_module == "google":
                google_summary.render_google_ads_module(engine, st.session_state.mis_data)

            elif st.session_state.selected_module == "upload":
                Input_MIS.render_mis_upload_module(engine)

            elif st.session_state.selected_module == "sql":
                sql_console.render_sql_console_module(engine)

        else:
            # Allow access to modules even without uploaded MIS (they can load from DB)
            if st.session_state.selected_module == "campaign":
                HDFC_campaign.render_campaign_analysis_module(None, engine)
            elif st.session_state.selected_module == "phone":
                phone_numbers.render_phone_numbers_module(engine, None)
            elif st.session_state.selected_module == "google":
                google_summary.render_google_ads_module(engine, None)
            elif st.session_state.selected_module == "upload":
                Input_MIS.render_mis_upload_module(engine)
            elif st.session_state.selected_module == "sql":
                sql_console.render_sql_console_module(engine)
            elif st.session_state.selected_module is None:
                # Dashboard view - show status analysis option to load from DB
                status_analysis.render_status_analysis_module(None, engine)
            else:
                st.warning("⚠️ Please load MIS data from database or upload the MIS file to begin analysis")


# -------------------------
# Run Application
# -------------------------
if __name__ == "__main__":
    main()