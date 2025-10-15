# HDFC Dashboard - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Navigate to Project
```bash
cd "/Users/venugopal/Desktop/Work/Projects/HDFC/HDFC Dashboard"
```

### 2. Activate Virtual Environment
```bash
source .venv/bin/activate
```

### 3. Install Dependencies (if needed)
```bash
pip install -r requirements.txt
```

### 4. Configure Database
Edit `config/database_config.py` and update:
```python
DB_CONFIG = {
    "username": "postgres",
    "password": "YOUR_PASSWORD",  # Update this
    "host": "localhost",
    "port": "5432",
    "database": "Nxtify"
}
```

### 5. Run Application
```bash
streamlit run main_dashboard.py
```

The dashboard will open at: `http://localhost:8501`

## 📁 Project Structure Summary

```
HDFC Dashboard/
├── main_dashboard.py          # ← Start here
├── config/                    # Configuration
│   ├── app_config.py         # App settings
│   └── database_config.py    # DB credentials
├── modules/                   # Analysis modules
│   ├── HDFC_campaign.py      # Campaign analysis
│   ├── google_summary.py     # Google Ads
│   ├── status_analysis.py    # Status tracking
│   ├── Input_MIS.py          # Data upload
│   ├── phone_numbers.py      # Phone extraction
│   └── sql_console.py        # SQL interface
├── database/                  # DB utilities
├── utils/                     # Helper functions
└── assets/                    # Images, logos
```

## 🎯 Common Tasks

### Load MIS Data
1. Click "🗄️ Reload from Database" or "📁 Upload New File"
2. Data loads automatically
3. Use date filter to refine data

### View Campaign Analysis
1. Select "📈 Campaign Analysis" from dropdown
2. Customize charts using filter expanders
3. Download reports from "📥 Download" tab

### Upload New MIS Data
1. Select "📤 MIS Upload" from dropdown
2. Upload Excel/CSV file
3. Review and confirm upload

### Run SQL Queries
1. Select "💻 SQL Console" from dropdown
2. Write SQL query
3. Execute and view results

## 🔧 Configuration Quick Reference

### Change Database Password
`config/database_config.py` → Line 7

### Change App Title
`config/app_config.py` → Line 9

### Update Campaign Costs
`config/app_config.py` → Lines 16-26

### Add New Status Color
`config/app_config.py` → Lines 39-45

## 📊 Module Functions

Each module has a main render function:

```python
# Campaign Analysis
from modules import HDFC_campaign
HDFC_campaign.render_campaign_analysis_module(df_mis, engine)

# Status Analysis
from modules import status_analysis
status_analysis.render_status_analysis_module(df_mis, engine)

# Google Ads
from modules import google_summary
google_summary.render_google_ads_module(engine, df_mis)
```

## 🐛 Troubleshooting

### Database Connection Error
```
✅ Solution: Check config/database_config.py
- Verify PostgreSQL is running
- Check username/password
- Confirm database "Nxtify" exists
```

### Module Import Error
```
✅ Solution: Ensure you're in project root
cd "/Users/venugopal/Desktop/Work/Projects/HDFC/HDFC Dashboard"
python -c "from modules import HDFC_campaign"
```

### Missing Dependencies
```
✅ Solution: Reinstall requirements
pip install -r requirements.txt --upgrade
```

### File Not Found (Images)
```
✅ Solution: Check assets/images/ folder
Images should be in: assets/images/
Not in: Public/ (old location)
```

## 📞 Need Help?

1. **Check Documentation**: See `docs/` folder
2. **Read README**: See `README.md`
3. **Review Structure**: See `docs/PROJECT_STRUCTURE.md`

## 🎨 Custom Chart Filters

Every chart now has customization options:
- **Click ⚙️ Customize** expander above each chart
- **Select columns**, filters, sort options
- **Choose chart type** (Bar/Pie/Donut)
- **Filter categories** independently per chart

## 💡 Tips

1. **Use Global Filters** at top for dashboard-wide filtering
2. **Date Filter** works across all modules
3. **Each chart** has independent customization
4. **Export data** from Download tabs
5. **Save queries** in SQL Console for reuse

---

**Quick Reference**: Keep this guide handy for daily use!
