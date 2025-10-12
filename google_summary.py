"""
Google Ads Summary Module
Process and analyze Google Ads campaigns with MIS data
"""

import pandas as pd
import streamlit as st
from io import BytesIO
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import plotly.express as px
import plotly.graph_objects as go


def find_col(df, candidate_names, fallback_index=None):
    """Find column by matching candidate names"""
    lookup = {c.strip().lower(): c for c in df.columns}
    for cand in candidate_names:
        key = cand.strip().lower()
        if key in lookup:
            return lookup[key]
    for key, orig in lookup.items():
        for cand in candidate_names:
            if cand.strip().lower() in key:
                return orig
    if fallback_index is not None and 0 <= fallback_index < len(df.columns):
        return df.columns[fallback_index]
    raise KeyError(f"None of {candidate_names} found in columns")


def load_google_ads_data(engine):
    """Load Google Ads campaign data from database"""
    query = """
    SELECT 
        "seqId", "lead_utm_source", "lead_utm_medium", 
        "lead_utm_gclid", "promoterId", "storeSlug",
        "userName", "phoneNo"
    FROM "Campaign_Data"
    WHERE "storeSlug" ILIKE %s
    """
    
    try:
        sep_all = pd.read_sql(query, engine, params=("%hdfc%",))
        
        # Filter Google Ads campaigns
        sep_google = sep_all[
            (sep_all["lead_utm_source"].astype(str).str.strip().str.lower() == "ad_cc") &
            (sep_all["lead_utm_medium"].astype(str).str.strip().str.lower().isin(["search_hdcc", "search_hdcn"]))
        ]
        
        return sep_google, None
    except Exception as e:
        return None, str(e)


def process_google_ads_summary(sep_google, hdfc):
    """Process Google Ads campaigns and match with MIS data"""
    # Process campaign data
    sep_filtered = sep_google.copy()
    sep_filtered["seqId"] = sep_filtered["seqId"].astype(str).str.strip()
    
    # Process MIS data
    hdfc_clean = hdfc.copy()
    
    try:
        hdfc_lc2_col = find_col(hdfc, ["LC2_CODE"], 10)
        hdfc_lg_col = find_col(hdfc, ["LG_CODE"], 11)
        hdfc_lc1_col = find_col(hdfc, ["LC1_CODE"], 9)
        hdfc_app_col = find_col(hdfc, ["APPLICATION_REFERENCE_NUMBER"], 0)
        hdfc_date_col = find_col(hdfc, ["CREATION_DATE_TIME"], None)
        hdfc_dec_col = find_col(hdfc, ["FINAL_DECISION"], None)
    except KeyError as e:
        raise KeyError(f"Required column not found: {e}")
    
    hdfc_clean[hdfc_lc2_col] = hdfc_clean[hdfc_lc2_col].astype(str).str.strip().str.upper()
    
    # Match with CG prefix
    seq_values = [f"CG{str(s).strip()}".upper() for s in sep_filtered["seqId"].unique()]
    hdfc_matched = hdfc_clean[hdfc_clean[hdfc_lc2_col].isin(seq_values)].copy()
    
    # Track matched seq IDs
    matched_seq_ids = set()
    if not hdfc_matched.empty:
        hdfc_matched["seqId"] = (
            hdfc_matched[hdfc_lc2_col]
            .astype(str)
            .str.replace(r'(?i)^cg', '', regex=True)
            .str.strip()
        )
        matched_seq_ids = set(hdfc_matched["seqId"].str.strip().str.upper())
        
        # Merge with GCLID
        sep_small = sep_filtered[["seqId", "lead_utm_gclid"]].drop_duplicates()
        final_df = pd.merge(hdfc_matched, sep_small, on="seqId", how="left", validate="m:1")
    else:
        final_df = hdfc_matched.copy()
    
    # Add "Present in MIS" column to campaign data
    sep_campaign_output = sep_filtered.copy()
    sep_campaign_output["Present in MIS"] = (
        sep_campaign_output["seqId"]
        .astype(str)
        .str.strip()
        .str.upper()
        .apply(lambda x: "Yes" if x in matched_seq_ids else "No")
    )
    
    # Create pivot table
    pivot_df = None
    if not final_df.empty and hdfc_date_col and hdfc_dec_col:
        try:
            final_df[hdfc_dec_col] = final_df[hdfc_dec_col].astype(str).str.strip().str.upper()
            final_df[hdfc_date_col] = pd.to_datetime(final_df[hdfc_date_col], errors="coerce").dt.date
            
            if "FINAL_DECISION_DATE" in final_df.columns:
                final_df["FINAL_DECISION_DATE"] = pd.to_datetime(
                    final_df["FINAL_DECISION_DATE"], 
                    errors="coerce"
                ).dt.date
            
            pivot_base = final_df.dropna(subset=[hdfc_dec_col, hdfc_date_col])
            if not pivot_base.empty:
                pivot_df = pd.pivot_table(
                    pivot_base,
                    index=hdfc_date_col,
                    columns=hdfc_dec_col,
                    values=hdfc_app_col,
                    aggfunc='count',
                    fill_value=0
                ).sort_index(axis=0).sort_index(axis=1)
                
                pivot_df["Total"] = pivot_df.sum(axis=1)
                grand_total = pivot_df.sum(numeric_only=True)
                grand_total.name = "Grand Total"
                pivot_df = pd.concat([pivot_df, pd.DataFrame([grand_total])])
        except Exception as e:
            st.warning(f"Could not create pivot table: {e}")
    
    # Create derived sheets
    derived_sheets = {}
    if not final_df.empty and hdfc_date_col and "FINAL_DECISION_DATE" in final_df.columns and hdfc_dec_col:
        try:
            creation_dt = pd.to_datetime(final_df[hdfc_date_col], errors="coerce")
            decision_dt = pd.to_datetime(final_df["FINAL_DECISION_DATE"], errors="coerce")
            decision_col = final_df[hdfc_dec_col].astype(str).str.upper()
            
            # Approved on same day
            derived_sheets["Approved on same day"] = final_df[
                (decision_col == "APPROVE") &
                ((decision_dt == creation_dt) | (decision_dt == creation_dt + pd.Timedelta(days=1)))
            ]
            
            # Same month cardout
            derived_sheets["Same month Cardout"] = final_df[
                (creation_dt.notna()) & (decision_dt.notna()) &
                (creation_dt.dt.month == decision_dt.dt.month)
            ]
            
            # Different month cardout
            derived_sheets["Different month Cardout"] = final_df[
                (creation_dt.notna()) & (decision_dt.notna()) &
                (creation_dt.dt.month != decision_dt.dt.month)
            ]
        except Exception as e:
            st.warning(f"Could not create derived sheets: {e}")
    
    return final_df, sep_campaign_output, pivot_df, derived_sheets


def send_email_report(output_data, email_config):
    """Send email with Excel report attached"""
    msg = MIMEMultipart()
    msg['From'] = email_config['from']
    msg['To'] = email_config['to']
    msg['CC'] = email_config['cc']
    msg['Subject'] = f"HDFC Google Ads MIS Report - {datetime.now().strftime('%d-%b-%Y')}"
    
    body = """Hello,

Please find attached the Google Ads HDFC MIS report for your review.

Key Highlights:
- Total Google Ads Campaigns Processed
- MIS Match Analysis
- Pivot Tables and Detailed Breakdowns

Best Regards,
Venugopal"""
    
    msg.attach(MIMEText(body, 'plain'))
    
    # Attach Excel file
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(output_data.getvalue())
    encoders.encode_base64(part)
    
    today = datetime.today().strftime("%d-%b-%Y")
    filename = f"GoogleAds_HDFC_MIS_{today}.xlsx"
    part.add_header('Content-Disposition', f'attachment; filename={filename}')
    msg.attach(part)
    
    # Send email
    server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
    server.starttls()
    server.login(email_config['from'], email_config['password'])
    
    recipients = [email_config['to']] + email_config['cc'].split(',')
    server.sendmail(email_config['from'], recipients, msg.as_string())
    server.quit()


def render_google_ads_module(engine, df_mis=None):
    """Main render function for Google Ads module"""
    st.markdown("## 🎯 Google Ads Campaign Summary")
    st.info("📊 Process Google Ads campaigns and generate detailed MIS reports")

    # Email configuration in sidebar
    with st.sidebar:
        st.markdown("### 📧 Email Configuration")
        with st.expander("Email Settings", expanded=False):
            email_config = {
                'smtp_server': st.text_input("SMTP Server", value="smtp.zoho.com"),
                'smtp_port': st.number_input("SMTP Port", value=587, min_value=1, max_value=65535),
                'from': st.text_input("From Email", value="Venugopal.p@paisawapas.com"),
                'password': st.text_input("Password", type="password", value="ntnFcT1P2DVu"),
                'to': st.text_input("To Email", value="rishav@paisawapas.com"),
                'cc': st.text_area(
                    "CC Emails (comma-separated)",
                    value="maruthi.g@extrape.com,pradeep.kumar@extrape.com"
                )
            }
            st.session_state.email_config = email_config

    # Check if MIS data exists in session state (from module-specific load)
    if df_mis is None and 'google_mis_data' in st.session_state:
        df_mis = st.session_state.google_mis_data

    # Main content - Load buttons
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        if df_mis is not None:
            source = "🗄️ database" if 'google_mis_data' in st.session_state else "main dashboard"
            st.success(f"✅ Using {len(df_mis):,} MIS records from {source}")
        else:
            st.info("ℹ️ Load MIS data from database or upload from main dashboard")

    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗄️ Load MIS from DB", key="load_google_mis_db", use_container_width=True):
            if engine:
                with st.spinner("Loading MIS data from database..."):
                    try:
                        query = 'SELECT * FROM "HDFC_MIS_Data"'
                        df_mis_loaded = pd.read_sql(query, engine)
                        df_mis_loaded.columns = df_mis_loaded.columns.str.strip()
                        st.session_state.google_mis_data = df_mis_loaded
                        st.success(f"✅ Loaded {len(df_mis_loaded):,} MIS records")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
            else:
                st.error("❌ Database connection not available")

    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Load Google Ads Data", key="load_google_campaign_db", use_container_width=True):
            if engine:
                with st.spinner("Loading Google Ads campaign data..."):
                    google_data, error = load_google_ads_data(engine)
                    if error:
                        st.error(f"❌ Error: {error}")
                    else:
                        st.session_state.google_campaign_data = google_data
                        st.success(f"✅ Loaded {len(google_data):,} Google Ads records")
            else:
                st.error("❌ Database connection not available")

    # Process if both are available
    if df_mis is not None and 'google_campaign_data' in st.session_state:
        try:
            with st.spinner("🔄 Processing Google Ads data..."):
                hdfc = df_mis.copy()
                sep_google = st.session_state.google_campaign_data
                
                # Process data
                final_df, sep_campaign_output, pivot_df, derived_sheets = process_google_ads_summary(
                    sep_google, hdfc
                )
                
                # Display metrics
                st.markdown("### 📊 Processing Summary")
                col1, col2, col3, col4 = st.columns(4)
                
                total_campaigns = len(sep_google)
                matched_count = len(final_df)
                present_in_mis = (sep_campaign_output["Present in MIS"] == "Yes").sum()
                match_rate = (matched_count / total_campaigns * 100) if total_campaigns > 0 else 0
                
                with col1:
                    st.metric("📱 Total Campaigns", f"{total_campaigns:,}")
                with col2:
                    st.metric("✅ Matched in MIS", f"{matched_count:,}")
                with col3:
                    st.metric("🎯 Present in MIS", f"{present_in_mis:,}")
                with col4:
                    st.metric("📈 Match Rate", f"{match_rate:.1f}%")
                
                st.markdown("---")
                
                # Tabs for different views
                tab1, tab2, tab3, tab4, tab5 = st.tabs([
                    "📊 Overview",
                    "📋 Pivot Analysis",
                    "📁 Campaign Data",
                    "📈 Derived Reports",
                    "📥 Download & Email"
                ])
                
                with tab1:
                    st.markdown("### 📊 Matched MIS Data")
                    
                    if not final_df.empty:
                        # Show statistics
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Decision distribution
                            if "FINAL_DECISION" in final_df.columns:
                                decision_col = [c for c in final_df.columns if "FINAL_DECISION" in c.upper()][0]
                                decision_dist = final_df[decision_col].value_counts()
                                
                                fig1 = px.pie(
                                    values=decision_dist.values,
                                    names=decision_dist.index,
                                    title="Decision Distribution",
                                    hole=0.4
                                )
                                st.plotly_chart(fig1, use_container_width=True)
                        
                        with col2:
                            # Match status
                            match_status = sep_campaign_output["Present in MIS"].value_counts()
                            
                            fig2 = px.bar(
                                x=match_status.index,
                                y=match_status.values,
                                title="Campaign MIS Match Status",
                                labels={'x': 'Status', 'y': 'Count'},
                                color=match_status.values,
                                color_continuous_scale="Blues"
                            )
                            st.plotly_chart(fig2, use_container_width=True)
                        
                        # Data preview
                        st.markdown("#### 📋 Matched Data Preview (First 100 rows)")
                        st.dataframe(final_df.head(100), use_container_width=True, height=400)
                        st.caption(f"Showing 100 of {len(final_df):,} matched records")
                    else:
                        st.warning("⚠️ No matched data found")
                
                with tab2:
                    st.markdown("### 📋 Pivot Table Analysis")
                    
                    if pivot_df is not None and not pivot_df.empty:
                        st.dataframe(pivot_df, use_container_width=True)
                        
                        # Trend visualization
                        if len(pivot_df) > 1:
                            pivot_viz = pivot_df.iloc[:-1].copy()  # Exclude Grand Total
                            
                            fig = go.Figure()
                            for col in pivot_viz.columns:
                                if col != "Total":
                                    fig.add_trace(go.Scatter(
                                        x=pivot_viz.index,
                                        y=pivot_viz[col],
                                        mode='lines+markers',
                                        name=col
                                    ))
                            
                            fig.update_layout(
                                title="Daily Decision Trends",
                                xaxis_title="Date",
                                yaxis_title="Count",
                                height=400
                            )
                            st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("ℹ️ No pivot data available")
                
                with tab3:
                    st.markdown("### 📁 Campaign Data with MIS Status")
                    
                    # Filter options
                    col1, col2 = st.columns(2)
                    with col1:
                        status_filter = st.multiselect(
                            "Filter by MIS Status:",
                            ["Yes", "No"],
                            default=["Yes", "No"]
                        )
                    with col2:
                        search = st.text_input("🔍 Search SeqId:", "")
                    
                    # Apply filters
                    filtered_campaigns = sep_campaign_output[
                        sep_campaign_output["Present in MIS"].isin(status_filter)
                    ]
                    
                    if search:
                        filtered_campaigns = filtered_campaigns[
                            filtered_campaigns["seqId"].astype(str).str.contains(search, case=False)
                        ]
                    
                    st.dataframe(filtered_campaigns, use_container_width=True, height=500)
                    st.caption(f"Showing {len(filtered_campaigns):,} of {len(sep_campaign_output):,} campaigns")
                
                with tab4:
                    st.markdown("### 📈 Derived Reports")
                    
                    if derived_sheets:
                        for sheet_name, sheet_df in derived_sheets.items():
                            if not sheet_df.empty:
                                with st.expander(f"📊 {sheet_name} ({len(sheet_df):,} records)", expanded=False):
                                    st.dataframe(sheet_df, use_container_width=True, height=300)
                            else:
                                st.info(f"ℹ️ {sheet_name}: No data available")
                    else:
                        st.info("ℹ️ No derived reports available")
                
                with tab5:
                    st.markdown("### 📥 Download & Email Options")
                    
                    # Prepare Excel file
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine="openpyxl") as writer:
                        final_df.to_excel(writer, index=False, sheet_name="Matched Data")
                        
                        if pivot_df is not None and not pivot_df.empty:
                            pivot_df.to_excel(writer, sheet_name="Pivot Table")
                        
                        sep_campaign_output.to_excel(writer, index=False, sheet_name="Campaign Sheet")
                        
                        # Add derived sheets
                        if derived_sheets:
                            for sheet_name, sheet_df in derived_sheets.items():
                                if not sheet_df.empty:
                                    # Truncate sheet name to 31 chars (Excel limit)
                                    safe_name = sheet_name[:31]
                                    sheet_df.to_excel(writer, index=False, sheet_name=safe_name)
                    
                    output.seek(0)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### 📊 Download Report")
                        today = datetime.today().strftime("%d-%b-%Y")
                        st.download_button(
                            label="⬇️ Download Excel Report",
                            data=output,
                            file_name=f"GoogleAds_HDFC_MIS_{today}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                        
                        # CSV downloads
                        csv_matched = final_df.to_csv(index=False)
                        st.download_button(
                            label="📄 Download Matched Data CSV",
                            data=csv_matched,
                            file_name=f"GoogleAds_Matched_{today}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                    
                    with col2:
                        st.markdown("#### 📧 Email Report")
                        
                        if st.button("📧 Send Report via Email", use_container_width=True):
                            if 'email_config' in st.session_state:
                                try:
                                    with st.spinner("Sending email..."):
                                        output.seek(0)  # Reset buffer
                                        send_email_report(output, st.session_state.email_config)
                                        st.success("✅ Email sent successfully!")
                                except Exception as e:
                                    st.error(f"❌ Error sending email: {e}")
                            else:
                                st.error("❌ Email configuration not found")
                        
                        st.caption("Configure email settings in the sidebar")
        
        except Exception as e:
            st.error(f"❌ Error processing Google Ads data: {e}")
            with st.expander("🔍 View Error Details"):
                st.exception(e)

    elif df_mis is None:
        st.warning("⚠️ Please upload the MIS file from the main dashboard")
    elif 'google_campaign_data' not in st.session_state:
        st.warning("⚠️ Please load Google Ads data from the database using the button above")


if __name__ == "__main__":
    st.set_page_config(page_title="Google Ads Summary", layout="wide", page_icon="🎯")
    
    # Test mode
    try:
        from sqlalchemy import create_engine
        engine = create_engine("postgresql+psycopg://postgres:1234@localhost:5432/Nxtify")
    except:
        engine = None
    
    render_google_ads_module(engine)