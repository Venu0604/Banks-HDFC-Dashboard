"""
Database Configuration
Centralized database connection configuration
"""

# Database Connection Settings
DB_CONFIG = {
    "username": "postgres",
    "password": "112406",
    "host": "localhost",
    "port": "5432",
    "database": "Nxtify"
}

# Table Names
TABLES = {
    "MIS_DATA": "HDFC_MIS_Data",
    "CAMPAIGN_DATA": "Campaign_Data",
    "MIS_UPDATE_LOG": "MIS_Update_Log"
}

# Database Connection String
def get_connection_string():
    """Generate database connection string"""
    return f"postgresql+psycopg2://{DB_CONFIG['username']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
