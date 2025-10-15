# HDFC Analytics Dashboard

A comprehensive analytics dashboard for HDFC credit card campaigns, MIS data analysis, and performance tracking.

## 📁 Project Structure

```
HDFC Dashboard/
│
├── main_dashboard.py          # Main application entry point
├── requirements.txt           # Python dependencies
├── README.md                  # This file
│
├── config/                    # Configuration files
│   ├── __init__.py
│   ├── app_config.py         # Application settings
│   └── database_config.py     # Database connection settings
│
├── modules/                   # Analysis modules
│   ├── __init__.py
│   ├── HDFC_campaign.py      # Campaign performance analysis
│   ├── google_summary.py     # Google Ads summary
│   ├── status_analysis.py    # Final status analysis
│   ├── Input_MIS.py          # MIS data upload module
│   ├── phone_numbers.py      # Phone number extraction
│   └── sql_console.py        # SQL console interface
│
├── database/                  # Database utilities
│   ├── __init__.py
│   ├── connection.py         # Database connection manager
│   └── setup_database.py     # Database setup script
│
├── utils/                     # Utility functions
│   ├── __init__.py
│   ├── date_utils.py         # Date parsing utilities
│   ├── dataframe_utils.py    # DataFrame helper functions
│   └── optimize_images.py    # Image optimization utility
│
├── assets/                    # Static assets
│   └── images/               # Image files (logos, banners)
│
└── docs/                      # Documentation
    ├── SETUP_INSTRUCTIONS.md  # Setup guide
    └── OPTIMIZATION_SUMMARY.md # Optimization notes
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL database
- Required Python packages (see requirements.txt)

### Installation

1. **Clone or navigate to the project:**
   ```bash
   cd "/Users/venugopal/Desktop/Work/Projects/HDFC/HDFC Dashboard"
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure database:**
   - Edit `config/database_config.py`
   - Update database credentials

4. **Setup database tables:**
   ```bash
   python database/setup_database.py
   ```

5. **Run the application:**
   ```bash
   streamlit run main_dashboard.py
   ```

## 📊 Modules

### Campaign Analysis
- Multi-channel campaign performance tracking
- Cost efficiency analysis
- Conversion funnel visualization
- Custom filters for each chart

### Status Analysis
- Final decision tracking (Card Out, Declined, Inprogress)
- Conversion rate metrics
- Custom breakdown by any column
- Date-based filtering

### Google Ads Summary
- Google Ads campaign tracking
- MIS data matching
- Pivot analysis with trends
- Custom visualizations

### MIS Upload
- File upload interface
- Automatic duplicate detection
- Upsert functionality (update existing, insert new)
- Date validation and cleaning

### Phone Numbers Extraction
- Extract phone numbers from MIS data
- Database integration

### SQL Console
- Interactive SQL query interface
- Direct database access

## ⚙️ Configuration

### Application Settings (`config/app_config.py`)
- Application title and branding
- Campaign cost configurations
- Status color mappings
- Google Sheets integration URLs

### Database Settings (`config/database_config.py`)
- Database connection parameters
- Table name configurations
- Connection string generation

## 🎨 Features

### Custom Chart Filters
Every chart includes individual customization options:
- **Column Selection**: Choose which metrics to display
- **Category Filters**: Filter specific categories
- **Sort Options**: Ascending/Descending/Default
- **Chart Types**: Bar/Pie/Donut/Horizontal
- **Top N Selection**: Limit results

### Global Filters
- Date range filtering across all modules
- Final decision status filtering
- Channel-specific filtering

### Data Management
- Upload from Excel files
- Load from PostgreSQL database
- Real-time data filtering
- Export capabilities (Excel, CSV)

## 🔧 Development

### Adding a New Module

1. Create module file in `modules/` directory
2. Implement `render_<module_name>_module(df_mis, db_engine)` function
3. Add import in `modules/__init__.py`
4. Update `main_dashboard.py` navigation

### Utility Functions
- **Date utilities**: `utils/date_utils.py`
- **DataFrame operations**: `utils/dataframe_utils.py`
- Add new utilities as needed in `utils/` directory

## 📝 Database Schema

### Main Tables
- **HDFC_MIS_Data**: Main MIS data table
- **Campaign_Data**: Campaign tracking data
- **MIS_Update_Log**: Upload history tracking

## 🎯 Key Metrics

- **IPA Approval Rate**: Percentage of applications approved at IPA stage
- **Card Out Rate**: Percentage reaching Card Out status
- **Decline Rate**: Percentage of declined applications
- **Cost per Application**: Campaign cost efficiency
- **Conversion Rates**: Stage-to-stage conversion tracking

## 📄 License

Internal use only - HDFC Dashboard Project

## 👥 Support

For issues or questions, contact the development team.

---

**Version**: 2.0
**Last Updated**: October 2025
**Maintained by**: Venugopal
