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


# === Email Configuration ===
SMTP_SERVER = "smtp.zoho.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "Venugopal.p@paisawapas.com"
EMAIL_PASSWORD = "ntnFcT1P2DVu"
TO_EMAIL = "rishav@paisawapas.com"
CC_EMAILS = ["maruthi.g@extrape.com", "pradeep.kumar@extrape.com", "raghvendra.singh@extrape.com"]


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
        sep_google = sep_all[
            (sep_all["lead_utm_source"].astype(str).str.strip().str.lower().isin([
                "ad_cc", "adword_cc", "hdcc_cc", "hdcc_cn"
            ]))
        ]
        return sep_google, None
    except Exception as e:
        return None, str(e)


def process_google_ads_summary(sep_google, hdfc):
    """Process Google Ads campaigns and match with MIS data"""
    sep_filtered = sep_google.copy()
    sep_filtered["seqId"] = sep_filtered["seqId"].astype(str).str.strip()
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
    seq_values = [f"CG{str(s).strip()}".upper() for s in sep_filtered["seqId"].unique()]
    hdfc_matched = hdfc_clean[hdfc_clean[hdfc_lc2_col].isin(seq_values)].copy()

    matched_seq_ids = set()
    if not hdfc_matched.empty:
        hdfc_matched["seqId"] = (
            hdfc_matched[hdfc_lc2_col]
            .astype(str)
            .str.replace(r'(?i)^cg', '', regex=True)
            .str.strip()
        )
        matched_seq_ids = set(hdfc_matched["seqId"].str.strip().str.upper())
        sep_small = sep_filtered[["seqId", "lead_utm_gclid"]].drop_duplicates()
        final_df = pd.merge(hdfc_matched, sep_small, on="seqId", how="left", validate="m:1")
    else:
        final_df = hdfc_matched.copy()

    sep_campaign_output = sep_filtered.copy()
    sep_campaign_output["Present in MIS"] = (
        sep_campaign_output["seqId"]
        .astype(str)
        .str.strip()
        .str.upper()
        .apply(lambda x: "Yes" if x in matched_seq_ids else "No")
    )

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

    return final_df, sep_campaign_output, pivot_df


def send_email_report(output_data):
    """Send email with Excel report attached using hardcoded configuration"""
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = TO_EMAIL
    msg['CC'] = ', '.join(CC_EMAILS)
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

    part = MIMEBase('application', 'octet-stream')
    part.set_payload(output_data.getvalue())
    encoders.encode_base64(part)
    today = datetime.today().strftime("%d-%b-%Y")
    filename = f"GoogleAds_HDFC_MIS_{today}.xlsx"
    part.add_header('Content-Disposition', f'attachment; filename={filename}')
    msg.attach(part)

    # Connect to SMTP server with better error handling
    server = None
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30)
        server.set_debuglevel(0)  # Set to 1 for debugging
        server.ehlo()
        server.starttls()
        server.ehlo()

        # Login with credentials
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

        # Prepare recipient list
        recipients = [TO_EMAIL] + CC_EMAILS

        # Send email
        server.sendmail(EMAIL_ADDRESS, recipients, msg.as_string())

    except smtplib.SMTPAuthenticationError as e:
        raise Exception(f"Authentication failed. Please check email credentials. Error: {str(e)}")
    except smtplib.SMTPException as e:
        raise Exception(f"SMTP error occurred: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to send email: {str(e)}")
    finally:
        if server:
            try:
                server.quit()
            except:
                pass


def render_google_ads_module(engine, df_mis=None):
    """Main render function for Google Ads module"""
    st.markdown("## 🎯 Google Ads Campaign Summary")
    st.info("📊 Process Google Ads campaigns and generate detailed MIS reports")

    data_source = "main dashboard (filtered)" if df_mis is not None else None

    if df_mis is not None and 'google_mis_data' in st.session_state:
        del st.session_state.google_mis_data

    if df_mis is None and 'google_mis_data' in st.session_state:
        df_mis = st.session_state.google_mis_data
        data_source = "module database"

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        if df_mis is not None:
            st.success(f"✅ Using {len(df_mis):,} MIS records from {data_source}")
        else:
            st.info("ℹ️ Load MIS data from database or upload from main dashboard")

    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗄️ Load MIS from DB", key="load_google_mis_db", use_container_width=True):
            if engine:
                with st.spinner("Loading MIS data..."):
                    try:
                        df_mis_loaded = pd.read_sql('SELECT * FROM "HDFC_MIS_Data"', engine)
                        df_mis_loaded.columns = df_mis_loaded.columns.str.strip()
                        st.session_state.google_mis_data = df_mis_loaded
                        st.success(f"✅ Loaded {len(df_mis_loaded):,} records (unfiltered)")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)[:50]}")
            else:
                st.error("❌ Database not available")

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

    st.markdown("---")

    # Process data
    if df_mis is not None and 'google_campaign_data' in st.session_state:
        try:
            with st.spinner("🔄 Processing Google Ads data..."):
                hdfc = df_mis.copy()
                sep_google = st.session_state.google_campaign_data

                final_df, sep_campaign_output, pivot_df = process_google_ads_summary(sep_google, hdfc)

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

                tab1, tab2, tab3, tab4 = st.tabs([
                    "📊 Overview",
                    "📋 Pivot Analysis",
                    "📁 Campaign Data",
                    "📥 Download & Email"
                ])

                with tab1:
                    if not final_df.empty:
                        st.markdown("### 📊 Overview & Analysis")

                        # Get decision column if exists
                        decision_col = None
                        if "FINAL_DECISION" in final_df.columns:
                            decision_col = [c for c in final_df.columns if "FINAL_DECISION" in c.upper()][0]

                        # Global Filters
                        st.markdown("#### 🎯 Global Filters (Apply to All Charts)")
                        global_filter_col1, global_filter_col2 = st.columns(2)

                        with global_filter_col1:
                            if decision_col:
                                all_decisions = final_df[decision_col].dropna().unique().tolist()
                                global_decision_filter = st.multiselect(
                                    "Filter by Final Decision (Global):",
                                    options=all_decisions,
                                    default=all_decisions,
                                    help="Global filter - applies to all visualizations",
                                    key="google_global_decision"
                                )
                            else:
                                global_decision_filter = None

                        with global_filter_col2:
                            global_mis_filter = st.multiselect(
                                "Filter by MIS Match (Global):",
                                options=["Yes", "No"],
                                default=["Yes", "No"],
                                help="Global filter - applies to all visualizations",
                                key="google_global_mis"
                            )

                        # Apply global filters
                        df_global = final_df.copy()
                        if decision_col and global_decision_filter:
                            df_global = df_global[df_global[decision_col].isin(global_decision_filter)]

                        # Get categorical columns for customization
                        categorical_cols = df_global.select_dtypes(include=['object']).columns.tolist()

                        st.markdown("---")

                        # Chart 1: Custom Pie Chart
                        st.markdown("#### 📊 Chart 1: Distribution Pie Chart")
                        with st.expander("⚙️ Customize Pie Chart", expanded=True):
                            pie_col1, pie_col2, pie_col3 = st.columns(3)

                            with pie_col1:
                                pie_category_col = st.selectbox(
                                    "Category Column:",
                                    options=categorical_cols,
                                    index=categorical_cols.index(decision_col) if decision_col and decision_col in categorical_cols else 0,
                                    key="pie_category_col"
                                )

                            with pie_col2:
                                if pie_category_col:
                                    pie_categories = df_global[pie_category_col].dropna().unique().tolist()
                                    pie_filter = st.multiselect(
                                        "Filter Categories:",
                                        options=pie_categories,
                                        default=pie_categories[:min(10, len(pie_categories))],
                                        key="pie_filter"
                                    )

                            with pie_col3:
                                pie_top_n = st.number_input(
                                    "Show Top N:",
                                    min_value=3,
                                    max_value=20,
                                    value=10,
                                    key="pie_top_n"
                                )

                        df_pie = df_global.copy()
                        if pie_category_col and pie_filter:
                            df_pie = df_pie[df_pie[pie_category_col].isin(pie_filter)]
                            pie_data = df_pie[pie_category_col].value_counts().head(pie_top_n)

                            fig1 = px.pie(
                                values=pie_data.values,
                                names=pie_data.index,
                                title=f"{pie_category_col} Distribution (Top {pie_top_n})",
                                hole=0.4
                            )
                            fig1.update_traces(textposition='inside', textinfo='percent+label+value')
                            st.plotly_chart(fig1, use_container_width=True)

                        col1, col2 = st.columns(2)

                        with col1:
                            # Chart 2: MIS Match Status
                            st.markdown("#### 📊 Chart 2: MIS Match Status")
                            with st.expander("⚙️ Customize MIS Match Chart", expanded=False):
                                mis_chart_col1, mis_chart_col2 = st.columns(2)

                                with mis_chart_col1:
                                    mis_chart_filter = st.multiselect(
                                        "MIS Status:",
                                        options=["Yes", "No"],
                                        default=["Yes", "No"],
                                        key="mis_chart_filter"
                                    )

                                with mis_chart_col2:
                                    mis_chart_type = st.selectbox(
                                        "Chart Type:",
                                        options=["Bar Chart", "Pie Chart"],
                                        key="mis_chart_type"
                                    )

                            sep_filtered_output = sep_campaign_output[
                                sep_campaign_output["Present in MIS"].isin(mis_chart_filter)
                            ]
                            match_status = sep_filtered_output["Present in MIS"].value_counts()

                            if mis_chart_type == "Bar Chart":
                                fig2 = px.bar(
                                    x=match_status.index,
                                    y=match_status.values,
                                    title="Campaign MIS Match Status",
                                    labels={'x': 'Status', 'y': 'Count'},
                                    color=match_status.values,
                                    color_continuous_scale="Blues",
                                    text=match_status.values
                                )
                                fig2.update_traces(textposition='outside')
                            else:
                                fig2 = px.pie(
                                    values=match_status.values,
                                    names=match_status.index,
                                    title="Campaign MIS Match Status",
                                    hole=0.4
                                )
                                fig2.update_traces(textposition='inside', textinfo='percent+label+value')

                            st.plotly_chart(fig2, use_container_width=True)

                        with col2:
                            # Chart 3: Custom Bar Chart
                            st.markdown("#### 📊 Chart 3: Custom Breakdown")
                            with st.expander("⚙️ Customize Breakdown Chart", expanded=False):
                                bar_col1, bar_col2, bar_col3 = st.columns(3)

                                with bar_col1:
                                    bar_groupby_col = st.selectbox(
                                        "Group By:",
                                        options=categorical_cols,
                                        index=categorical_cols.index(decision_col) if decision_col and decision_col in categorical_cols else 0,
                                        key="bar_groupby_col"
                                    )

                                with bar_col2:
                                    bar_top_n = st.number_input(
                                        "Show Top N:",
                                        min_value=3,
                                        max_value=30,
                                        value=10,
                                        key="bar_top_n"
                                    )

                                with bar_col3:
                                    bar_sort = st.selectbox(
                                        "Sort:",
                                        options=["Descending", "Ascending"],
                                        key="bar_sort"
                                    )

                            if bar_groupby_col:
                                groupby_data = df_global[bar_groupby_col].value_counts().head(bar_top_n)
                                if bar_sort == "Ascending":
                                    groupby_data = groupby_data.sort_values()

                                fig3 = px.bar(
                                    x=groupby_data.index,
                                    y=groupby_data.values,
                                    title=f"Top {bar_top_n} by {bar_groupby_col}",
                                    labels={'x': bar_groupby_col, 'y': 'Count'},
                                    color=groupby_data.values,
                                    color_continuous_scale="Viridis",
                                    text=groupby_data.values
                                )
                                fig3.update_traces(textposition='outside')
                                fig3.update_layout(showlegend=False)
                                st.plotly_chart(fig3, use_container_width=True)

                        st.markdown("#### 📋 Filtered Data Preview")
                        st.dataframe(df_global.head(100), use_container_width=True, height=400)
                        st.caption(f"Showing 100 of {len(df_global):,} filtered records (Total matched: {len(final_df):,})")
                    else:
                        st.warning("⚠️ No matched data found")

                with tab2:
                    st.markdown("### 📊 Pivot Analysis")
                    if pivot_df is not None and not pivot_df.empty:
                        # Custom column selection for pivot visualization
                        with st.expander("⚙️ Customize Pivot Chart", expanded=False):
                            st.markdown("**Select columns to display in trend chart:**")

                            available_cols = [col for col in pivot_df.columns if col != "Total"]
                            selected_pivot_cols = st.multiselect(
                                "Select decision statuses to plot:",
                                options=available_cols,
                                default=available_cols,
                                help="Choose which decision statuses to show in the trend chart"
                            )

                        st.dataframe(pivot_df, use_container_width=True)

                        if len(pivot_df) > 1 and selected_pivot_cols:
                            pivot_viz = pivot_df.iloc[:-1].copy()
                            fig = go.Figure()

                            for col in selected_pivot_cols:
                                if col in pivot_viz.columns:
                                    fig.add_trace(go.Scatter(
                                        x=pivot_viz.index,
                                        y=pivot_viz[col],
                                        mode='lines+markers',
                                        name=col
                                    ))

                            fig.update_layout(
                                title="Daily Decision Trends (Customized)",
                                xaxis_title="Date",
                                yaxis_title="Count",
                                height=400,
                                hovermode='x unified'
                            )
                            st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("ℹ️ No pivot data available")

                with tab3:
                    col1, col2 = st.columns(2)
                    with col1:
                        status_filter = st.multiselect("Filter by MIS Status:", ["Yes", "No"], default=["Yes", "No"])
                    with col2:
                        search = st.text_input("🔍 Search SeqId:", "")
                    filtered_campaigns = sep_campaign_output[
                        sep_campaign_output["Present in MIS"].isin(status_filter)
                    ]
                    if search:
                        filtered_campaigns = filtered_campaigns[
                            filtered_campaigns["seqId"].astype(str).str.contains(search, case=False)
                        ]
                    st.dataframe(filtered_campaigns, use_container_width=True, height=500)

                with tab4:
                    st.markdown("### 📥 Download & Email Options")

                    # ✅ Only export Matched Data, Pivot Table, and Campaign Data
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine="openpyxl") as writer:
                        final_df.to_excel(writer, index=False, sheet_name="Matched Data")
                        if pivot_df is not None and not pivot_df.empty:
                            pivot_df.to_excel(writer, sheet_name="Pivot Table")
                        sep_campaign_output.to_excel(writer, index=False, sheet_name="Campaign Data")
                    output.seek(0)

                    col1, col2 = st.columns(2)
                    with col1:
                        today = datetime.today().strftime("%d-%b-%Y")
                        st.download_button(
                            label="⬇️ Download Excel Report",
                            data=output,
                            file_name=f"GoogleAds_HDFC_MIS_{today}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                        csv_matched = final_df.to_csv(index=False)
                        st.download_button(
                            label="📄 Download Matched Data CSV",
                            data=csv_matched,
                            file_name=f"GoogleAds_Matched_{today}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                    with col2:
                        if st.button("📧 Send Report via Email", use_container_width=True):
                            try:
                                with st.spinner("Sending email..."):
                                    output.seek(0)
                                    send_email_report(output)
                                    st.success(f"✅ Email sent successfully to {TO_EMAIL}!")
                                    st.info(f"📬 CC: {', '.join(CC_EMAILS)}")
                            except Exception as e:
                                st.error(f"❌ Error sending email: {e}")
                        st.caption(f"📧 Email will be sent to: {TO_EMAIL}")

        except Exception as e:
            st.error(f"❌ Error processing Google Ads data: {e}")
            with st.expander("🔍 View Error Details"):
                st.exception(e)
    else:
        st.warning("⚠️ Please load both MIS and Google Ads data to proceed.")


if __name__ == "__main__":
    st.set_page_config(page_title="Google Ads Summary", layout="wide", page_icon="🎯")
    try:
        from sqlalchemy import create_engine
        engine = create_engine("postgresql+psycopg2://postgres:112406@localhost:5432/Nxtify")
    except:
        engine = None
    render_google_ads_module(engine)
