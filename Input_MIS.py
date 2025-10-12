"""
MIS Upload Module
Upload Excel files and update HDFC_MIS_Data table in database
"""

import pandas as pd
import streamlit as st
from datetime import datetime
from io import BytesIO
import time


def update_mis_in_database(df, engine):
    """Update MIS data in database and log the update"""
    try:
        # Start transaction
        with engine.begin() as conn:
            # Truncate and reload the table
            conn.execute('TRUNCATE TABLE "HDFC_MIS_Data"')

            # Insert new data
            df.to_sql('HDFC_MIS_Data', conn, if_exists='append', index=False)

            # Log the update
            update_log = pd.DataFrame([{
                'table_name': 'HDFC_MIS_Data',
                'record_count': len(df),
                'updated_at': datetime.now(),
                'updated_by': 'Dashboard User'
            }])
            update_log.to_sql('MIS_Update_Log', conn, if_exists='append', index=False)

        return True, None
    except Exception as e:
        return False, str(e)


def get_last_update_info(engine):
    """Get information about the last MIS update"""
    try:
        query = """
        SELECT table_name, record_count, updated_at, updated_by
        FROM "MIS_Update_Log"
        WHERE table_name = 'HDFC_MIS_Data'
        ORDER BY updated_at DESC
        LIMIT 1
        """
        df = pd.read_sql(query, engine)
        if len(df) > 0:
            return df.iloc[0].to_dict()
        return None
    except:
        return None


def render_mis_upload_module(engine):
    """Main render function for MIS upload module"""
    st.markdown("## Upload MIS Data")
    st.info("Upload Excel file to update HDFC_MIS_Data table in database")

    # Show last update info
    if engine:
        with st.spinner("Loading last update info..."):
            last_update = get_last_update_info(engine)

        if last_update:
            st.markdown("### Last Update Information")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Table", last_update['table_name'])
            with col2:
                st.metric("Records", f"{last_update['record_count']:,}")
            with col3:
                updated_time = pd.to_datetime(last_update['updated_at'])
                st.metric("Updated", updated_time.strftime("%Y-%m-%d %H:%M:%S"))
            with col4:
                st.metric("By", last_update['updated_by'])
        else:
            st.warning("No previous updates found. This will be the first upload.")
    else:
        st.error("Database connection not available")
        return

    st.markdown("---")

    # File upload section
    st.markdown("### Upload New MIS File")

    col1, col2 = st.columns([3, 1])

    with col1:
        uploaded_file = st.file_uploader(
            "Choose Excel file to upload",
            type=['xlsx', 'xls'],
            key="mis_upload_file",
            help="Upload Excel file to replace all data in HDFC_MIS_Data table"
        )

    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        upload_button = st.button(
            "Upload & Update Database",
            type="primary",
            use_container_width=True,
            disabled=uploaded_file is None
        )

    if uploaded_file:
        # Show file preview
        try:
            df_preview = pd.read_excel(uploaded_file, nrows=5)

            st.markdown("#### File Preview (First 5 rows)")
            st.dataframe(df_preview, use_container_width=True)

            # Show file info
            uploaded_file.seek(0)  # Reset file pointer
            df_full = pd.read_excel(uploaded_file)

            info_col1, info_col2, info_col3 = st.columns(3)
            with info_col1:
                st.metric("Total Rows", f"{len(df_full):,}")
            with info_col2:
                st.metric("Total Columns", len(df_full.columns))
            with info_col3:
                file_size = uploaded_file.size / (1024 * 1024)  # Convert to MB
                st.metric("File Size", f"{file_size:.2f} MB")

            # Upload button action
            if upload_button:
                st.markdown("---")
                st.markdown("### Processing Upload...")

                progress_bar = st.progress(0)
                status_text = st.empty()

                # Step 1: Validate data
                status_text.text("Step 1/4: Validating data...")
                progress_bar.progress(25)
                time.sleep(0.5)

                # Clean column names
                df_full.columns = df_full.columns.str.strip()

                # Step 2: Backup check
                status_text.text("Step 2/4: Checking database connection...")
                progress_bar.progress(50)
                time.sleep(0.5)

                if not engine:
                    st.error("Database connection failed!")
                    return

                # Step 3: Update database
                status_text.text("Step 3/4: Updating database...")
                progress_bar.progress(75)

                success, error = update_mis_in_database(df_full, engine)

                if success:
                    # Step 4: Complete
                    status_text.text("Step 4/4: Finalizing...")
                    progress_bar.progress(100)
                    time.sleep(0.5)

                    st.success(f"Successfully uploaded {len(df_full):,} records to HDFC_MIS_Data!")

                    # Show success metrics
                    st.markdown("### Upload Summary")
                    summary_col1, summary_col2, summary_col3 = st.columns(3)

                    with summary_col1:
                        st.metric("Records Uploaded", f"{len(df_full):,}")
                    with summary_col2:
                        st.metric("Columns", len(df_full.columns))
                    with summary_col3:
                        st.metric("Upload Time", datetime.now().strftime("%H:%M:%S"))

                    # Update session state to refresh other modules
                    if 'mis_data' in st.session_state:
                        st.session_state.mis_data = df_full
                        st.session_state.mis_source = "database"
                        st.session_state.mis_filename = "HDFC_MIS_Data (Just Updated)"

                    st.balloons()

                    # Refresh button
                    if st.button("Refresh Dashboard", type="primary"):
                        st.rerun()
                else:
                    progress_bar.progress(100)
                    st.error(f"Upload failed: {error}")

                    with st.expander("View Error Details"):
                        st.code(error)

        except Exception as e:
            st.error(f"Error reading file: {e}")
            with st.expander("View Error Details"):
                st.exception(e)

    # Instructions section
    st.markdown("---")
    st.markdown("### Instructions")

    with st.expander("How to use this module", expanded=False):
        st.markdown("""
        **Step-by-step guide:**

        1. **Prepare your Excel file**
           - Ensure all required columns are present
           - Remove any empty rows or columns
           - Make sure data types are correct

        2. **Upload the file**
           - Click "Browse files" and select your Excel file
           - Preview will show the first 5 rows
           - Verify the data looks correct

        3. **Update database**
           - Click "Upload & Update Database"
           - Wait for the process to complete
           - All existing data will be replaced

        4. **Verify**
           - Check the success message
           - Verify record count matches your file
           - Refresh dashboard to see updated data

        **Important Notes:**
        - This will **replace all existing data** in HDFC_MIS_Data table
        - Make sure you have the latest complete dataset
        - A backup is recommended before large updates
        - Update logs are maintained for tracking
        """)


if __name__ == "__main__":
    st.set_page_config(page_title="MIS Upload", layout="wide", page_icon="U")

    # Test mode
    try:
        from sqlalchemy import create_engine
        engine = create_engine("postgresql+psycopg2://postgres:1234@localhost:5432/Nxtify")
    except:
        engine = None

    render_mis_upload_module(engine)
