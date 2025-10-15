"""
DataFrame Utility Functions
Helper functions for DataFrame operations
"""

import pandas as pd


def find_column(df, keywords):
    """
    Find column that contains any of the keywords (case insensitive)

    Args:
        df: Pandas DataFrame
        keywords: String or list of keywords to search

    Returns:
        Column name or None
    """
    if isinstance(keywords, str):
        keywords = [keywords]
    for col in df.columns:
        col_clean = str(col).strip().replace('*', '').lower()
        for keyword in keywords:
            if keyword.lower() in col_clean:
                return col
    return None


def find_col(df, candidate_names, fallback_index=None):
    """
    Find column by matching candidate names

    Args:
        df: Pandas DataFrame
        candidate_names: List of candidate column names
        fallback_index: Index to use if no match found

    Returns:
        Column name

    Raises:
        KeyError: If no match found and no fallback provided
    """
    lookup = {c.strip().lower(): c for c in df.columns}
    for cand in candidate_names:
        key = cand.strip().lower()
        if key in lookup:
            return lookup[key]
    for key, orig in lookup.items():
        for cand in candidate_names:
            if cand.strip().lower() in key:
                return orig
    if fallback_index is not None and 0 <= fallback_index < len(df.columns):
        return df.columns[fallback_index]
    raise KeyError(f"None of {candidate_names} found in columns")
