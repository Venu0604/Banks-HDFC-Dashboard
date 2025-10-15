"""
SQL Console Module
Interactive SQL query console with export functionality
"""

import pandas as pd
import streamlit as st
from datetime import datetime
from io import BytesIO
import re


def is_safe_query(query):
    """Check if query is safe (read-only)"""
    query_upper = query.strip().upper()

    # Dangerous keywords that modify data
    dangerous_keywords = [
        'DROP', 'DELETE', 'TRUNCATE', 'UPDATE', 'INSERT',
        'ALTER', 'CREATE', 'GRANT', 'REVOKE'
    ]

    for keyword in dangerous_keywords:
        if keyword in query_upper:
            return False, f"Dangerous keyword '{keyword}' detected. Only SELECT queries are allowed."

    return True, None


def execute_sql_query(query, engine):
    """Execute SQL query and return results"""
    try:
        # Check if query is safe
        is_safe, error_msg = is_safe_query(query)
        if not is_safe:
            return None, error_msg

        # Execute query
        df = pd.read_sql(query, engine)
        return df, None
    except Exception as e:
        return None, str(e)


def get_table_list(engine):
    """Get list of tables in database"""
    try:
        query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name
        """
        df = pd.read_sql(query, engine)
        return df['table_name'].tolist()
    except:
        return []


def get_table_columns(table_name, engine):
    """Get columns for a specific table"""
    try:
        query = f"""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = '{table_name}'
        ORDER BY ordinal_position
        """
        df = pd.read_sql(query, engine)
        return df
    except:
        return None


def render_sql_console_module(engine):
    """Main render function for SQL console module"""
    st.markdown("## 💻 SQL Console")
    st.info("🔍 Execute SQL queries and export data directly from the database")

    if not engine:
        st.error("❌ Database connection not available")
        return

    # Sidebar with table browser
    with st.sidebar:
        st.markdown("### 📋 Database Tables")

        with st.spinner("Loading tables..."):
            tables = get_table_list(engine)

        if tables:
            selected_table = st.selectbox(
                "Browse Tables:",
                options=["-- Select a table --"] + tables,
                key="table_browser"
            )

            if selected_table != "-- Select a table --":
                st.markdown(f"**Table:** `{selected_table}`")

                with st.spinner("Loading columns..."):
                    columns_df = get_table_columns(selected_table, engine)

                if columns_df is not None and len(columns_df) > 0:
                    st.markdown("**Columns:** (Click to copy)")

                    # Display columns in a scrollable container with copy buttons
                    for idx, row in columns_df.iterrows():
                        col_name = row['column_name']
                        col_type = row['data_type']

                        # Use expander for cleaner look
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.text(f"📋 {col_name}")
                            st.caption(f"   {col_type}")
                        with col2:
                            if st.button("➕", key=f"add_col_{selected_table}_{idx}", help="Add to query"):
                                # Add column to query
                                current_query = st.session_state.get('query_input', '')
                                if 'SELECT' not in current_query.upper():
                                    st.session_state.query_input = f'SELECT "{col_name}" FROM "{selected_table}" LIMIT 100'
                                else:
                                    # Insert column name at cursor position
                                    st.session_state.query_input = current_query + f', "{col_name}"'
                                st.rerun()

                    # Quick query buttons
                    st.markdown("---")
                    st.markdown("**Quick Queries:**")

                    if st.button("📊 SELECT * (100 rows)", use_container_width=True):
                        st.session_state.sql_query = f'SELECT * FROM "{selected_table}" LIMIT 100'
                        st.rerun()

                    if st.button("📈 COUNT rows", use_container_width=True):
                        st.session_state.sql_query = f'SELECT COUNT(*) as total_rows FROM "{selected_table}"'
                        st.rerun()

                    if st.button("🔍 Table schema", use_container_width=True):
                        st.session_state.sql_query = f"""
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = '{selected_table}'
ORDER BY ordinal_position
"""
                        st.rerun()
        else:
            st.warning("No tables found")

    # Main console area
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown("### ✍️ SQL Query Editor")
    with col2:
        st.markdown("### 🎯 Actions")

    # SQL Suggestions Panel (BEFORE text area)
    with st.expander("💡 SQL Query Suggestions & Snippets", expanded=False):
        st.markdown("**Common Query Patterns:**")

        suggestion_col1, suggestion_col2 = st.columns(2)

        with suggestion_col1:
            st.markdown("**Basic Queries:**")

            if st.button("📊 Select All Columns", use_container_width=True, key="suggest_select_all"):
                st.session_state.sql_query = 'SELECT * FROM "HDFC_MIS_Data" LIMIT 100'
                st.rerun()

            if st.button("🔢 Count Records", use_container_width=True, key="suggest_count"):
                st.session_state.sql_query = 'SELECT COUNT(*) as total_records FROM "HDFC_MIS_Data"'
                st.rerun()

            if st.button("🔍 Distinct Values", use_container_width=True, key="suggest_distinct"):
                st.session_state.sql_query = 'SELECT DISTINCT "FINAL_DECISION" FROM "HDFC_MIS_Data"'
                st.rerun()

            if st.button("📈 Group By Count", use_container_width=True, key="suggest_group"):
                st.session_state.sql_query = '''SELECT "FINAL_DECISION", COUNT(*) as count
FROM "HDFC_MIS_Data"
GROUP BY "FINAL_DECISION"
ORDER BY count DESC'''
                st.rerun()

        with suggestion_col2:
            st.markdown("**Filtering Queries:**")

            if st.button("✅ Approved Only", use_container_width=True, key="suggest_approved"):
                st.session_state.sql_query = '''SELECT * FROM "HDFC_MIS_Data"
WHERE "IPA_STATUS" = 'APPROVE'
LIMIT 100'''
                st.rerun()

            if st.button("📅 Recent Records", use_container_width=True, key="suggest_recent"):
                st.session_state.sql_query = '''SELECT * FROM "HDFC_MIS_Data"
WHERE "CREATION_DATE_TIME" >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY "CREATION_DATE_TIME" DESC
LIMIT 100'''
                st.rerun()

            if st.button("🔗 Join Tables", use_container_width=True, key="suggest_join"):
                st.session_state.sql_query = '''SELECT m.*, c."seqId"
FROM "HDFC_MIS_Data" m
LEFT JOIN "Campaign_Data" c ON m."LC2_CODE" = CONCAT('CG', c."seqId")
LIMIT 100'''
                st.rerun()

            if st.button("📊 Date Range Filter", use_container_width=True, key="suggest_date_range"):
                st.session_state.sql_query = '''SELECT * FROM "HDFC_MIS_Data"
WHERE "CREATION_DATE_TIME" BETWEEN '2024-01-01' AND '2024-12-31'
LIMIT 100'''
                st.rerun()

        st.markdown("---")
        st.markdown("**SQL Keywords:**")
        st.code("""
SELECT - Choose columns
FROM - Specify table
WHERE - Filter rows
GROUP BY - Aggregate data
ORDER BY - Sort results
LIMIT - Restrict number of rows
JOIN - Combine tables
DISTINCT - Unique values only
COUNT, SUM, AVG, MAX, MIN - Aggregate functions
        """, language="sql")

    # Query editor (AFTER suggestions)
    default_query = st.session_state.get('sql_query', 'SELECT * FROM "HDFC_MIS_Data" LIMIT 10')

    query = st.text_area(
        "Enter your SQL query:",
        value=default_query,
        height=200,
        key="query_input",
        help="Only SELECT queries are allowed for safety"
    )

    # Action buttons
    action_col1, action_col2, action_col3, action_col4 = st.columns(4)

    with action_col1:
        execute_btn = st.button("▶️ Execute Query", type="primary", use_container_width=True)

    with action_col2:
        clear_btn = st.button("🗑️ Clear", use_container_width=True)
        if clear_btn:
            st.session_state.sql_query = ""
            st.rerun()

    with action_col3:
        if st.button("📋 Sample Query", use_container_width=True):
            st.session_state.sql_query = 'SELECT * FROM "HDFC_MIS_Data" WHERE "IPA_STATUS" = \'APPROVE\' LIMIT 50'
            st.rerun()

    with action_col4:
        if st.button("💡 Help", use_container_width=True):
            st.session_state.show_help = not st.session_state.get('show_help', False)

    # Help section
    if st.session_state.get('show_help', False):
        with st.expander("📖 SQL Query Help", expanded=True):
            st.markdown("""
            **Common SQL Patterns:**

            ```sql
            -- Select all columns (limit results)
            SELECT * FROM "HDFC_MIS_Data" LIMIT 100

            -- Select specific columns
            SELECT "APPLICATION_REFERENCE_NUMBER", "FINAL_DECISION"
            FROM "HDFC_MIS_Data"

            -- Filter by condition
            SELECT * FROM "HDFC_MIS_Data"
            WHERE "IPA_STATUS" = 'APPROVE'

            -- Count records
            SELECT COUNT(*) as total FROM "HDFC_MIS_Data"

            -- Group by and aggregate
            SELECT "FINAL_DECISION", COUNT(*) as count
            FROM "HDFC_MIS_Data"
            GROUP BY "FINAL_DECISION"

            -- Date filtering
            SELECT * FROM "HDFC_MIS_Data"
            WHERE "CREATION_DATE_TIME" >= '2024-01-01'

            -- Join tables
            SELECT m.*, c."seqId"
            FROM "HDFC_MIS_Data" m
            LEFT JOIN "Campaign_Data" c ON m."LC2_CODE" = CONCAT('CG', c."seqId")
            LIMIT 100
            ```

            **⚠️ Important:**
            - Only SELECT queries are allowed
            - Use double quotes for table and column names
            - Add LIMIT to avoid loading too much data
            - Use WHERE clauses to filter results
            """)

    # Execute query
    if execute_btn and query.strip():
        st.markdown("---")
        st.markdown("### 📊 Query Results")

        with st.spinner("🔄 Executing query..."):
            df_result, error = execute_sql_query(query, engine)

        if error:
            st.error(f"❌ Query Error: {error}")

            with st.expander("🔍 Query Details"):
                st.code(query, language="sql")
        else:
            # Success - show results
            st.success(f"✅ Query executed successfully! Retrieved {len(df_result):,} rows.")

            # Result metrics
            result_col1, result_col2, result_col3 = st.columns(3)

            with result_col1:
                st.metric("📝 Rows", f"{len(df_result):,}")
            with result_col2:
                st.metric("📋 Columns", len(df_result.columns))
            with result_col3:
                memory_mb = df_result.memory_usage(deep=True).sum() / (1024 * 1024)
                st.metric("💾 Memory", f"{memory_mb:.2f} MB")

            # Display results
            st.dataframe(df_result, use_container_width=True, height=400)

            # Export options
            st.markdown("### 📥 Export Results")

            export_col1, export_col2, export_col3 = st.columns(3)

            with export_col1:
                # Excel export
                output = BytesIO()
                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    df_result.to_excel(writer, index=False, sheet_name="Query Results")
                output.seek(0)

                st.download_button(
                    label="📊 Download as Excel",
                    data=output,
                    file_name=f"query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

            with export_col2:
                # CSV export
                csv = df_result.to_csv(index=False)
                st.download_button(
                    label="📄 Download as CSV",
                    data=csv,
                    file_name=f"query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

            with export_col3:
                # JSON export
                json = df_result.to_json(orient='records', indent=2)
                st.download_button(
                    label="📋 Download as JSON",
                    data=json,
                    file_name=f"query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )

            # Query info
            with st.expander("🔍 Query Details"):
                st.code(query, language="sql")

    # Query history (optional - can add later)
    st.markdown("---")
    st.markdown("### 📜 Recent Queries")

    if 'query_history' not in st.session_state:
        st.session_state.query_history = []

    # Add current query to history if executed
    if execute_btn and query.strip() and query not in st.session_state.query_history:
        st.session_state.query_history.insert(0, query)
        st.session_state.query_history = st.session_state.query_history[:5]  # Keep last 5

    if st.session_state.query_history:
        for i, hist_query in enumerate(st.session_state.query_history, 1):
            col1, col2 = st.columns([5, 1])
            with col1:
                st.text(f"{i}. {hist_query[:100]}..." if len(hist_query) > 100 else f"{i}. {hist_query}")
            with col2:
                if st.button("🔄", key=f"rerun_{i}"):
                    st.session_state.sql_query = hist_query
                    st.rerun()
    else:
        st.info("No query history yet. Execute a query to see it here.")


if __name__ == "__main__":
    st.set_page_config(page_title="SQL Console", layout="wide", page_icon="💻")

    # Test mode
    try:
        from sqlalchemy import create_engine
        engine = create_engine("postgresql+psycopg2://postgres:112406@localhost:5432/Nxtify")
    except:
        engine = None

    render_sql_console_module(engine)
