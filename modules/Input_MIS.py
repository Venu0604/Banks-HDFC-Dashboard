"""
MIS Upload Module
Upload and manage MIS data from Excel/CSV files to PostgreSQL database
"""

import pandas as pd
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.types import DateTime
import streamlit as st
from datetime import datetime
import os

# =====================================================================
# 🏦 BANK CONFIGURATION
# =====================================================================
BANK_NAME = "HDFC"
TABLE_NAME = f"{BANK_NAME}_MIS_Data"   # Table name: HDFC_MIS_Data
UNIQUE_ID_COL = "APPLICATION_REFERENCE_NUMBER"   # ✅ Use APPLICATION_REFERENCE_NUMBER as unique id


def render_mis_upload_module(db_engine=None):
    """Main render function for MIS upload module"""
    st.markdown("## 📤 MIS Data Upload")

    if db_engine is None:
        st.error("❌ Database connection not available")
        return

    st.markdown(f"""
    Upload MIS data files to the **{TABLE_NAME}** database table.

    **Features:**
    - Supports Excel (.xlsx) and CSV (.csv) files
    - Automatic duplicate detection and upsert (update existing, insert new)
    - Date validation and cleaning
    - Column matching with existing table
    """)

    # File uploader
    uploaded_file = st.file_uploader(
        "Choose an Excel or CSV file",
        type=['xlsx', 'csv'],
        help="Upload your MIS data file"
    )

    if uploaded_file is not None:
        st.info(f"📁 File selected: **{uploaded_file.name}** ({uploaded_file.size:,} bytes)")

        # Process button
        if st.button("🚀 Upload to Database", type="primary", use_container_width=True):
            process_mis_upload(uploaded_file, db_engine)


def process_mis_upload(uploaded_file, engine):
    """Process and upload MIS file to database"""

    # Create progress container
    progress_container = st.container()

    with progress_container:
        with st.spinner("Processing file..."):
            try:
                # =====================================================================
                # 📥 LOAD DATA
                # =====================================================================
                st.write("📂 Loading file...")
                if uploaded_file.name.endswith(".xlsx"):
                    df = pd.read_excel(uploaded_file)
                elif uploaded_file.name.endswith(".csv"):
                    df = pd.read_csv(uploaded_file)
                else:
                    st.error("❌ Unsupported file format. Please use .xlsx or .csv")
                    return

                st.success(f"✅ File loaded: {df.shape[0]:,} rows, {df.shape[1]} columns")

                # =====================================================================
                # 📋 CHECK IF TABLE EXISTS
                # =====================================================================
                st.write("🔍 Checking database table...")
                inspector = inspect(engine)
                table_exists = inspector.has_table(TABLE_NAME)

                if table_exists:
                    st.info(f"✅ Table '{TABLE_NAME}' exists. Will upsert data.")
                    try:
                        existing_df = pd.read_sql_table(TABLE_NAME, engine)
                        st.write(f"📊 Existing table has {len(existing_df):,} rows")

                        # Match columns
                        common_columns = list(set(df.columns) & set(existing_df.columns))
                        st.write(f"🔗 Found {len(common_columns)} matching columns")

                        if not common_columns:
                            st.error("❌ No matching columns between file and existing table!")
                            return

                        df = df[common_columns]
                        date_columns = [col for col in common_columns if pd.api.types.is_datetime64_any_dtype(existing_df[col])]

                    except Exception as e:
                        st.error(f"❌ Error reading existing table: {e}")
                        return
                else:
                    st.warning(f"⚠️ Table '{TABLE_NAME}' does not exist. It will be created.")
                    existing_df = None
                    date_columns = [col for col in df.columns if "date" in col.lower() or "time" in col.lower()]
                    common_columns = df.columns.tolist()

                # =====================================================================
                # 🧹 CLEAN INVALID DATE COLUMNS
                # =====================================================================
                st.write("🧹 Cleaning invalid dates...")
                if date_columns:
                    for col in date_columns:
                        if col in df.columns:
                            df[col] = pd.to_datetime(df[col], errors='coerce')
                            invalid_mask = (df[col].dt.year < 1900) | (df[col].dt.year > 9999)
                            invalid_count = invalid_mask.sum()
                            if invalid_count > 0:
                                st.write(f"⚠️ {col}: {invalid_count} invalid dates → NULL")
                                df.loc[invalid_mask, col] = pd.NaT
                    st.success(f"✅ Cleaned {len(date_columns)} date columns")

                # =====================================================================
                # 🔁 REMOVE DUPLICATES WITHIN NEW DATA
                # =====================================================================
                st.write("🔍 Checking for duplicates...")
                if UNIQUE_ID_COL not in df.columns:
                    st.error(f"❌ '{UNIQUE_ID_COL}' column not found — required for deduplication.")
                    return

                before_count = len(df)
                df = df.drop_duplicates(subset=[UNIQUE_ID_COL], keep="last")
                duplicates_removed = before_count - len(df)
                if duplicates_removed > 0:
                    st.write(f"🗑️ Removed {duplicates_removed} duplicate {UNIQUE_ID_COL} within new data")

                # =====================================================================
                # 🔄 CHECK FOR DUPLICATES (UPSERT: UPDATE IF EXISTS, INSERT IF NEW)
                # =====================================================================
                new_records = 0
                updated_records = 0

                if table_exists and existing_df is not None and len(existing_df) > 0:
                    st.write("🔍 Checking against existing database records...")
                    existing_ids = set(existing_df[UNIQUE_ID_COL])
                    duplicate_ids = set(df[UNIQUE_ID_COL]) & existing_ids

                    if duplicate_ids:
                        updated_records = len(duplicate_ids)
                        new_records = len(df) - updated_records
                        st.info(f"🔄 Found {updated_records} existing records to UPDATE")
                        st.info(f"➕ Found {new_records} new records to INSERT")
                    else:
                        new_records = len(df)
                        st.info(f"➕ All {new_records} records are new")
                else:
                    new_records = len(df)
                    st.info(f"➕ Creating new table with {new_records} records")

                # =====================================================================
                # 🚀 UPSERT TO POSTGRESQL (INSERT NEW + UPDATE EXISTING)
                # =====================================================================
                if len(df) > 0:
                    st.write("🚀 Uploading to database...")

                    if table_exists:
                        # Ensure date columns match the existing table's data types
                        with engine.connect() as conn:
                            # Get existing table column types
                            type_query = text(f'''
                                SELECT column_name, data_type
                                FROM information_schema.columns
                                WHERE table_name = '{TABLE_NAME}'
                            ''')
                            existing_types = {row[0]: row[1] for row in conn.execute(type_query)}

                        # Convert date columns to proper datetime format and build dtype mapping
                        dtype_mapping = {}
                        for col in df.columns:
                            if col in existing_types and 'timestamp' in existing_types[col].lower():
                                df[col] = pd.to_datetime(df[col], errors='coerce')
                                dtype_mapping[col] = DateTime()

                        # First, upload to a temporary table
                        temp_table = f"{TABLE_NAME}_temp"
                        df.to_sql(temp_table, engine, if_exists='replace', index=False, dtype=dtype_mapping)

                        with engine.connect() as conn:
                            # Delete duplicates from main table
                            delete_query = text(f'''
                                DELETE FROM "{TABLE_NAME}"
                                WHERE "{UNIQUE_ID_COL}" IN (SELECT "{UNIQUE_ID_COL}" FROM "{temp_table}")
                            ''')
                            result = conn.execute(delete_query)
                            deleted_count = result.rowcount
                            if deleted_count > 0:
                                st.write(f"🗑️ Deleted {deleted_count} old records from main table")

                            # Get column list and build cast expressions for timestamp columns
                            columns = list(df.columns)
                            select_parts = []
                            for col in columns:
                                if col in dtype_mapping:
                                    # Cast text to timestamp for date columns
                                    select_parts.append(f'"{col}"::timestamp')
                                else:
                                    select_parts.append(f'"{col}"')

                            select_clause = ', '.join(select_parts)
                            column_list = ', '.join([f'"{col}"' for col in columns])

                            # Insert all records from temp table with proper casting
                            insert_query = text(f'''
                                INSERT INTO "{TABLE_NAME}" ({column_list})
                                SELECT {select_clause} FROM "{temp_table}"
                            ''')
                            conn.execute(insert_query)

                            # Drop temp table
                            drop_query = text(f'DROP TABLE "{temp_table}"')
                            conn.execute(drop_query)

                            conn.commit()

                        st.success(f"✅ Successfully processed {len(df):,} rows ({new_records:,} new, {updated_records:,} updated)")
                    else:
                        df.to_sql(TABLE_NAME, engine, if_exists='replace', index=False)
                        st.success(f"✅ Created new table '{TABLE_NAME}' with {len(df):,} rows")

                    # Check total count
                    with engine.connect() as conn:
                        total = conn.execute(text(f'SELECT COUNT(*) FROM "{TABLE_NAME}"')).scalar()
                        st.success(f"📈 Total rows in '{TABLE_NAME}': {total:,}")

                    # Log the update
                    try:
                        log_update(engine, TABLE_NAME, len(df), new_records, updated_records)
                    except Exception as e:
                        st.warning(f"⚠️ Could not log update: {e}")

                    st.balloons()
                    st.success(f"🎉 Upload complete for {BANK_NAME}")

                else:
                    st.warning("⚠️ No rows to process.")

            except Exception as e:
                st.error(f"❌ Error processing upload: {e}")
                with st.expander("🔍 View Error Details"):
                    st.exception(e)


def log_update(engine, table_name, record_count, new_records, updated_records):
    """Log the MIS update to MIS_Update_Log table"""
    try:
        log_entry = pd.DataFrame([{
            'table_name': table_name,
            'record_count': record_count,
            'updated_at': datetime.now(),
            'updated_by': 'Streamlit Dashboard',
            'notes': f'New: {new_records}, Updated: {updated_records}'
        }])
        log_entry.to_sql('MIS_Update_Log', engine, if_exists='append', index=False)
    except Exception as e:
        # Silently fail if log table doesn't exist
        pass


if __name__ == "__main__":
    st.set_page_config(page_title="MIS Upload", layout="wide", page_icon="📤")

    # Test mode - create database engine
    try:
        username = "postgres"
        password = "112406"
        host = "localhost"
        port = "5432"
        database = "Nxtify"
        engine = create_engine(f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}")
    except:
        engine = None

    render_mis_upload_module(engine)
