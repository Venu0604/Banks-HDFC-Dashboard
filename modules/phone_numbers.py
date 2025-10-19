"""
Phone Numbers Extraction Module
Extract and map phone numbers from campaign data using LC2 codes
"""

import pandas as pd
import streamlit as st
from io import BytesIO
from datetime import datetime
import re
from sqlalchemy import create_engine


def find_col(df, candidate_names, fallback_index=None):
    """Find column by matching candidate names"""
    cols = list(df.columns)
    lower_cols = [c.strip().lower() for c in cols]
    for cand in candidate_names:
        cand_l = cand.strip().lower()
        for i, lc in enumerate(lower_cols):
            if lc == cand_l:
                return cols[i]
    if fallback_index is not None and 0 <= fallback_index < len(cols):
        return cols[fallback_index]
    raise KeyError(f"None of {candidate_names} found in columns")


def derive_phone_from_lc2(s):
    """Derive phone number from LC2 code using various transformations"""
    if not s:
        return None
    
    s_up = s.upper().strip()
    
    # Handle IV prefix (base36 conversion)
    if s_up.startswith('IV') and len(s_up) > 2:
        try:
            base36_part = s_up[2:]
            phone_num = int(base36_part, 36)
            return str(phone_num)
        except ValueError:
            pass
    
    # Handle MNOPQRSTUV conversion
    mapping = str.maketrans("MNOPQRSTUV", "0123456789")
    mapping_keys = set("MNOPQRSTUV")
    
    s_no_cg = re.sub(r'(?i)^CG', '', s_up)
    if len(s_no_cg) == 10 and set(s_no_cg).issubset(mapping_keys):
        return s_no_cg.translate(mapping)
    if len(s_up) == 10 and set(s_up).issubset(mapping_keys):
        return s_up.translate(mapping)
    
    return None


def load_campaign_data_from_db(engine):
    """Load campaign data from PostgreSQL database"""
    query = """
    SELECT "seqId", "phoneNo"
    FROM "Campaign_Data"
    WHERE "storeSlug" ILIKE %s
    """
    try:
        df = pd.read_sql(query, engine, params=("%hdfc%",))
        return df, None
    except Exception as e:
        return None, str(e)


def process_phone_numbers(sep, hdfc):
    """Process and merge phone numbers from campaign and MIS data"""
    # Process campaign data
    sep_clean = sep[["seqId", "phoneNo"]].copy()
    sep_clean["seqId"] = sep_clean["seqId"].astype(str).str.strip().str.upper()
    sep_clean["phoneNo"] = (
        sep_clean["phoneNo"]
        .astype(str)
        .str.strip()
        .str.replace(r'\.0$', '', regex=True)
        .str.replace(r'\D+', '', regex=True)
    )
    sep_clean = sep_clean.drop_duplicates(subset=["seqId"], keep="first")

    # Process MIS LC2 codes
    hdfc_lc2_col = find_col(hdfc, ["LC2_CODE"], 10)
    hdfc_app_col = find_col(hdfc, ["APPLICATION_REFERENCE_NUMBER"], 0)

    hdfc["LC2_raw"] = hdfc[hdfc_lc2_col].fillna("").astype(str).str.strip()
    hdfc["DerivedPhone"] = hdfc["LC2_raw"].apply(derive_phone_from_lc2)

    lc2_no_cg = hdfc["LC2_raw"].str.upper().str.replace(r'(?i)^CG', '', regex=True).str.strip()
    hdfc["seqId"] = lc2_no_cg.where(hdfc["DerivedPhone"].isna(), None)
    hdfc = hdfc.rename(columns={hdfc_app_col: "APPLICATION_REFERENCE_NUMBER"})

    # Merge
    merged = pd.merge(hdfc, sep_clean, on="seqId", how="left")
    merged["FinalPhone"] = merged["DerivedPhone"].fillna(merged["phoneNo"])
    merged = merged.drop(columns=["phoneNo", "DerivedPhone", "LC2_raw"])

    # Reorder columns - prioritize important columns
    priority_cols = ["APPLICATION_REFERENCE_NUMBER"]

    # Add final decision columns if they exist
    if "FINAL_DECISION" in merged.columns:
        priority_cols.append("FINAL_DECISION")
    if "FINAL_DECISION_DATE" in merged.columns:
        priority_cols.append("FINAL_DECISION_DATE")

    # Add phone-related columns
    priority_cols.extend(["seqId", "FinalPhone"])

    # Get remaining columns
    other_cols = [c for c in merged.columns if c not in priority_cols]

    # Reorder: priority columns first, then others
    final_order = [c for c in priority_cols if c in merged.columns] + other_cols
    merged = merged[final_order]

    return merged


def render_phone_numbers_module(engine, df_mis=None):
    """Main render function for phone numbers module"""
    st.markdown("## 📞 Phone Numbers Extraction Module")
    st.info("📋 Extract and map phone numbers from campaign data using LC2 codes")

    # === Data Source Section ===
    st.markdown("### 📊 Data Sources")

    # Two columns: MIS Data and Campaign Data
    data_col1, data_col2 = st.columns(2)

    # === MIS Data Source ===
    with data_col1:
        st.markdown("#### 📋 MIS Data")

        # Check if MIS data exists from main dashboard
        if df_mis is not None and 'phone_mis_data' in st.session_state:
            del st.session_state.phone_mis_data

        if df_mis is None and 'phone_mis_data' in st.session_state:
            df_mis = st.session_state.phone_mis_data

        # Display current status
        if df_mis is not None:
            st.success(f"✅ Loaded: {len(df_mis):,} records")
        else:
            st.info("ℹ️ No MIS data loaded")

        # MIS data source options
        mis_source_tab1, mis_source_tab2 = st.tabs(["📁 Upload File", "🗄️ Load from DB"])

        with mis_source_tab1:
            uploaded_mis = st.file_uploader(
                "Upload MIS Excel/CSV File",
                type=['xlsx', 'xls', 'csv'],
                key="phone_mis_file_uploader",
                help="Upload HDFC MIS data file"
            )
            if uploaded_mis:
                try:
                    if uploaded_mis.name.endswith('.csv'):
                        df_mis_uploaded = pd.read_csv(uploaded_mis)
                    else:
                        df_mis_uploaded = pd.read_excel(uploaded_mis)

                    df_mis_uploaded.columns = df_mis_uploaded.columns.str.strip()
                    st.session_state.phone_mis_data = df_mis_uploaded
                    st.success(f"✅ Uploaded {len(df_mis_uploaded):,} records")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error reading file: {str(e)}")

        with mis_source_tab2:
            if st.button("🗄️ Load MIS from Database", key="phone_load_mis_db", use_container_width=True):
                if engine:
                    with st.spinner("Loading MIS data from database..."):
                        try:
                            df_mis_loaded = pd.read_sql('SELECT * FROM "HDFC_MIS_Data"', engine)
                            df_mis_loaded.columns = df_mis_loaded.columns.str.strip()
                            st.session_state.phone_mis_data = df_mis_loaded
                            st.success(f"✅ Loaded {len(df_mis_loaded):,} records from DB")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Database error: {str(e)[:100]}")
                else:
                    st.error("❌ Database not available")

    # === Campaign Data Source ===
    with data_col2:
        st.markdown("#### 📞 Campaign Data")

        # Display current status
        if 'phone_campaign_data' in st.session_state:
            st.success(f"✅ Loaded: {len(st.session_state.phone_campaign_data):,} records")
        else:
            st.info("ℹ️ No campaign data loaded")

        # Campaign data source options
        campaign_source_tab1, campaign_source_tab2 = st.tabs(["📁 Upload File", "🗄️ Load from DB"])

        with campaign_source_tab1:
            uploaded_campaign = st.file_uploader(
                "Upload Campaign Excel/CSV File",
                type=['xlsx', 'xls', 'csv'],
                key="phone_campaign_file_uploader",
                help="Upload campaign data with seqId and phoneNo columns"
            )
            if uploaded_campaign:
                try:
                    if uploaded_campaign.name.endswith('.csv'):
                        df_campaign_uploaded = pd.read_csv(uploaded_campaign)
                    else:
                        df_campaign_uploaded = pd.read_excel(uploaded_campaign)

                    df_campaign_uploaded.columns = df_campaign_uploaded.columns.str.strip()
                    st.session_state.phone_campaign_data = df_campaign_uploaded
                    st.success(f"✅ Uploaded {len(df_campaign_uploaded):,} campaigns")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error reading file: {str(e)}")

        with campaign_source_tab2:
            if st.button("🗄️ Load Campaign from Database", key="phone_load_campaign_db", use_container_width=True):
                if engine:
                    with st.spinner("Loading campaign data from database..."):
                        campaign_data, error = load_campaign_data_from_db(engine)
                        if error:
                            st.error(f"❌ Database error: {error}")
                        else:
                            st.session_state.phone_campaign_data = campaign_data
                            st.success(f"✅ Loaded {len(campaign_data):,} campaign records from DB")
                            st.rerun()
                else:
                    st.error("❌ Database not available")

    st.markdown("---")

    # Update df_mis from session state if not from main dashboard
    if df_mis is None and 'phone_mis_data' in st.session_state:
        df_mis = st.session_state.phone_mis_data

    # Process if both files are available
    if df_mis is not None and 'phone_campaign_data' in st.session_state:
        try:
            with st.spinner("🔄 Processing phone numbers..."):
                # Use MIS data from main dashboard
                hdfc = df_mis.copy()
                sep = st.session_state.phone_campaign_data
                
                # Process
                merged = process_phone_numbers(sep, hdfc)
                
                # Display metrics
                st.markdown("### 📊 Processing Results")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("📄 Total Records", f"{len(merged):,}")
                with col2:
                    phone_count = merged['FinalPhone'].notna().sum()
                    st.metric("📞 Phone Numbers Found", f"{phone_count:,}")
                with col3:
                    success_rate = (phone_count / len(merged) * 100) if len(merged) > 0 else 0
                    st.metric("✅ Success Rate", f"{success_rate:.1f}%")
                with col4:
                    missing_count = merged['FinalPhone'].isna().sum()
                    st.metric("❌ Missing Numbers", f"{missing_count:,}")
                
                st.markdown("---")
                
                # Display data in tabs
                tab1, tab2, tab3 = st.tabs(["📊 Preview", "📈 Statistics", "📥 Download"])
                
                with tab1:
                    st.markdown("### 📊 Data Preview (First 100 rows)")
                    st.dataframe(
                        merged.head(100),
                        use_container_width=True,
                        height=500
                    )
                    st.caption(f"Showing 100 of {len(merged):,} total records")
                
                with tab2:
                    st.markdown("### 📈 Phone Number Statistics")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Phone number length distribution
                        phone_lengths = merged['FinalPhone'].dropna().astype(str).str.len()
                        length_dist = phone_lengths.value_counts().sort_index()
                        
                        st.markdown("#### 📏 Phone Number Length Distribution")
                        st.bar_chart(length_dist)
                    
                    with col2:
                        # Source distribution
                        st.markdown("#### 🔍 Phone Number Source")
                        
                        # Check if phone was derived or from campaign
                        source_stats = pd.DataFrame({
                            'Source': ['Derived from LC2', 'From Campaign Data', 'Missing'],
                            'Count': [
                                hdfc['DerivedPhone'].notna().sum() if 'DerivedPhone' in locals() else 0,
                                phone_count - (hdfc['DerivedPhone'].notna().sum() if 'DerivedPhone' in locals() else 0),
                                missing_count
                            ]
                        })
                        st.dataframe(source_stats, use_container_width=True, hide_index=True)
                
                with tab3:
                    st.markdown("### 📥 Download Processed Data")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Excel download
                        output = BytesIO()
                        with pd.ExcelWriter(output, engine="openpyxl") as writer:
                            merged.to_excel(writer, index=False, sheet_name="Phone Numbers")
                            
                            # Add summary sheet
                            summary_df = pd.DataFrame({
                                'Metric': ['Total Records', 'Phone Numbers Found', 'Success Rate', 'Missing Numbers'],
                                'Value': [
                                    len(merged),
                                    phone_count,
                                    f"{success_rate:.1f}%",
                                    missing_count
                                ]
                            })
                            summary_df.to_excel(writer, index=False, sheet_name="Summary")
                        output.seek(0)
                        
                        today = datetime.today().strftime("%d-%b-%Y")
                        st.download_button(
                            label="📊 Download Excel Report",
                            data=output,
                            file_name=f"HDFC_Phone_Numbers_{today}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                    
                    with col2:
                        # CSV download
                        csv = merged.to_csv(index=False)
                        st.download_button(
                            label="📄 Download CSV",
                            data=csv,
                            file_name=f"HDFC_Phone_Numbers_{today}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                
        except Exception as e:
            st.error(f"❌ Error processing phone numbers: {e}")
            with st.expander("🔍 View Error Details"):
                st.exception(e)

    else:
        st.warning("⚠️ Please load both MIS Data and Campaign Data to begin processing")


if __name__ == "__main__":
    st.set_page_config(page_title="Phone Numbers Extraction", layout="wide", page_icon="📞")
    
    # Test mode - create dummy engine
    try:
        engine = create_engine("postgresql+psycopg://postgres:112406@localhost:5432/Nxtify")
    except:
        engine = None
    
    render_phone_numbers_module(engine)