"""
Date Utility Functions
Helper functions for date parsing and manipulation
"""

import pandas as pd


def parse_dates_safely(date_series):
    """
    Parse dates with multiple format handling

    Args:
        date_series: Pandas Series containing date values

    Returns:
        Pandas Series with parsed dates
    """
    parsed_dates = []
    for date_val in date_series:
        if pd.isna(date_val):
            parsed_dates.append(pd.NaT)
            continue
        try:
            parsed = pd.to_datetime(date_val, dayfirst=True, format='mixed')
            parsed_dates.append(parsed)
        except:
            try:
                parsed = pd.to_datetime(date_val, dayfirst=True)
                parsed_dates.append(parsed)
            except:
                parsed_dates.append(pd.NaT)
    return pd.Series(parsed_dates)


def find_date_column(df):
    """
    Find a date column in the dataframe

    Args:
        df: Pandas DataFrame

    Returns:
        Column name or None
    """
    date_keywords = ['date', 'created', 'timestamp', 'time', 'dt']
    for col in df.columns:
        col_lower = str(col).lower()
        if any(keyword in col_lower for keyword in date_keywords):
            try:
                test_val = df[col].dropna().iloc[0] if len(df[col].dropna()) > 0 else None
                if test_val:
                    pd.to_datetime(test_val, dayfirst=True)
                    return col
            except:
                continue
    return None
