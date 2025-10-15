"""
Application Configuration
General application settings and constants
"""

# Application Settings
APP_TITLE = "HDFC Dashboard"
APP_ICON = "📊"
PAGE_LAYOUT = "wide"

# Bank Configuration
BANK_NAME = "HDFC"
UNIQUE_ID_COL = "APPLICATION_REFERENCE_NUMBER"

# Campaign Costs Configuration (₹ per unit)
CAMPAIGN_COSTS = {
    "SMS": 0.1,
    "RCS": 0.085,
    "Whatsapp Marketing": 0.8,
    "Whatsapp Utility": 0.115,
    "IVR Orbital": {
        "connected": 0.09,
        "sms": 0.1
    }
}

# Final Status Mapping
FINAL_STATUS_MAP = {
    "IPA APPROVED DROPOFF CASE": "Inprogress",
    "IPA REJECT": "Declined",
    "Decline": "Declined",
    "Approve": "Card Out",
    "approve": "Card Out",
    "APPROVE": "Card Out",
    "Inprocess": "Inprogress",
}

# Status Colors
STATUS_COLORS = {
    'Card Out': '#10B981',      # Green
    'Declined': '#EF4444',      # Red
    'Inprogress': '#3B82F6',    # Blue
    'IPA Approved': '#764ba2',  # Purple
    'Other': '#6B7280'          # Gray
}

# Google Sheets Configuration
GOOGLE_SHEETS_URL = "https://docs.google.com/spreadsheets/d/184yquIAWt0XyQEYhI3yv0djg9f6pUtZS7TZ4Un7NLXI/export?format=csv&gid=2141873222"
