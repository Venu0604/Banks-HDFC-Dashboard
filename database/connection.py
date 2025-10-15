"""
Database Connection Manager
Centralized database connection handling
"""

from sqlalchemy import create_engine
import streamlit as st
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database_config import get_connection_string


@st.cache_resource
def get_db_engine():
    """
    Initialize and return database engine
    Uses Streamlit caching to reuse connection

    Returns:
        tuple: (engine, error_message)
    """
    try:
        engine = create_engine(get_connection_string())
        # Test connection
        with engine.connect():
            pass
        return engine, None
    except Exception as e:
        return None, str(e)


def create_simple_engine():
    """
    Create a simple database engine without caching
    Useful for standalone scripts

    Returns:
        SQLAlchemy engine
    """
    return create_engine(get_connection_string())
