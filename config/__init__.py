"""
Configuration Package
Application and database configuration
"""

from .app_config import *
from .database_config import *

__all__ = [
    'APP_TITLE',
    'APP_ICON',
    'PAGE_LAYOUT',
    'BANK_NAME',
    'CAMPAIGN_COSTS',
    'FINAL_STATUS_MAP',
    'STATUS_COLORS',
    'DB_CONFIG',
    'TABLES',
    'get_connection_string'
]
