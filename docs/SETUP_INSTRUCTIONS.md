# HDFC Dashboard - Setup Instructions

## 🚀 New Features Added

### 1. **MIS Upload Module** 📤
Upload Excel files directly to update the HDFC_MIS_Data table in the database.

### 2. **SQL Console** 💻
Interactive SQL query editor with export functionality.

### 3. **Update Tracking** 🕐
Automatic tracking of database updates with timestamp and record counts.

---

## 📋 Setup Steps

### Step 1: Create Database Table

Run the database setup script to create the update log table:

```bash
python setup_database.py
```

This will create the `MIS_Update_Log` table to track all database updates.

### Step 2: Run the Dashboard

```bash
streamlit run main_dashboard.py
```

---

## 🎯 Using the New Features

### **MIS Upload Module**

1. Navigate to **📤 MIS Upload** from the dropdown menu
2. View the last update information at the top
3. Upload your Excel file
4. Preview the data (first 5 rows shown)
5. Click **🚀 Upload & Update Database**
6. Wait for the process to complete
7. All data in HDFC_MIS_Data table will be replaced

**Features:**
- ✅ File preview before upload
- ✅ Progress indicator
- ✅ Automatic update logging
- ✅ Record count validation
- ✅ Error handling

---

### **SQL Console**

1. Navigate to **💻 SQL Console** from the dropdown menu
2. Browse tables in the sidebar
3. Click on a table to see its columns
4. Use quick query buttons or write custom SQL
5. Click **▶️ Execute Query**
6. View results in the data table
7. Export results as Excel, CSV, or JSON

**Features:**
- ✅ Table browser with column info
- ✅ Quick query templates
- ✅ Syntax highlighting
- ✅ Query history (last 5 queries)
- ✅ Multiple export formats
- ✅ Safe query execution (read-only)

**Sample Queries:**
```sql
-- Get all data (limited)
SELECT * FROM "HDFC_MIS_Data" LIMIT 100

-- Filter by status
SELECT * FROM "HDFC_MIS_Data"
WHERE "IPA_STATUS" = 'APPROVE'

-- Count by decision
SELECT "FINAL_DECISION", COUNT(*) as count
FROM "HDFC_MIS_Data"
GROUP BY "FINAL_DECISION"

-- Date range filtering
SELECT * FROM "HDFC_MIS_Data"
WHERE "CREATION_DATE_TIME" >= '2024-01-01'
LIMIT 100
```

---

### **Last Update Information**

The dashboard now shows:
- **Current MIS Source**: File upload or database
- **Last DB Update**: Timestamp and record count of last database update
- **Update logs**: Complete history in MIS_Update_Log table

**Where to see:**
- Main dashboard: Top section shows current source and last update
- MIS Upload module: Full update history with metrics
- SQL Console: Query the MIS_Update_Log table directly

---

## 🔒 Security Features

### SQL Console Safety:
- ✅ **Read-only queries**: Only SELECT statements allowed
- ✅ **Blocked keywords**: DROP, DELETE, UPDATE, INSERT, etc.
- ✅ **Error messages**: Clear feedback on blocked queries
- ✅ **Query validation**: Automatic checking before execution

### Database Updates:
- ✅ **Transaction support**: Rollback on errors
- ✅ **Automatic logging**: Every update is tracked
- ✅ **Validation**: Data checks before upload

---

## 📊 Database Schema

### MIS_Update_Log Table:
```sql
CREATE TABLE "MIS_Update_Log" (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(255) NOT NULL,
    record_count INTEGER NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    updated_by VARCHAR(255),
    notes TEXT
);
```

**Purpose**: Track all updates to MIS data tables

**Columns:**
- `id`: Auto-increment primary key
- `table_name`: Name of table updated (e.g., 'HDFC_MIS_Data')
- `record_count`: Number of records in the update
- `updated_at`: Timestamp of update
- `updated_by`: User who performed update
- `notes`: Optional notes about the update

---

## 🎨 Navigation

The dashboard now includes:
- 🏠 **Home** (icon button) - Returns to main dashboard
- 📞 **Phone Numbers** - Phone extraction module
- 📈 **Campaign Analysis** - Campaign performance
- 🎯 **Google Ads** - Google Ads analysis
- 📤 **MIS Upload** - Database upload module
- 💻 **SQL Console** - Query editor

---

## 💡 Tips

1. **Before uploading**: Always check the preview to ensure data looks correct
2. **Backup recommendation**: Consider backing up existing data before large updates
3. **SQL queries**: Add LIMIT clause to avoid loading too much data
4. **Export frequently**: Use SQL Console to export filtered/analyzed data
5. **Check logs**: Use SQL Console to query MIS_Update_Log for update history

---

## 📝 Query Examples for Common Tasks

### Check update history:
```sql
SELECT * FROM "MIS_Update_Log"
ORDER BY updated_at DESC
LIMIT 10
```

### Get database statistics:
```sql
SELECT
    COUNT(*) as total_records,
    COUNT(DISTINCT "LC2_CODE") as unique_lc2,
    MIN("CREATION_DATE_TIME") as earliest_date,
    MAX("CREATION_DATE_TIME") as latest_date
FROM "HDFC_MIS_Data"
```

### Find recent applications:
```sql
SELECT * FROM "HDFC_MIS_Data"
WHERE "CREATION_DATE_TIME" >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY "CREATION_DATE_TIME" DESC
LIMIT 100
```

---

## 🆘 Troubleshooting

### Issue: "Database connection not available"
**Solution**: Check your database credentials in `main_dashboard.py`

### Issue: "Table MIS_Update_Log does not exist"
**Solution**: Run `python setup_database.py`

### Issue: "Query blocked"
**Solution**: SQL Console only allows SELECT queries for safety

### Issue: "Upload failed"
**Solution**: Check Excel file format and column names match database schema

---

## 📧 Support

For issues or questions, check the error messages in the dashboard or review the query/upload logs.

---

**Version**: 2.0
**Last Updated**: 2025-01-12
**Features**: MIS Upload, SQL Console, Update Tracking
