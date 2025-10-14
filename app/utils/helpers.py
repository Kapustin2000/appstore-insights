"""
Helper utilities.
"""

import time
from typing import Dict


def format_processing_time(start_time: float) -> int:
    """
    Format processing time in milliseconds.

    Args:
        start_time: Start time from time.time()

    Returns:
        Processing time in milliseconds
    """
    return int((time.time() - start_time) * 1000)


def create_analysis_stub() -> Dict[str, None]:
    """
    Create analysis stub for future features.

    Returns:
        Dictionary with null analysis fields
    """
    return {"sentiment": None, "topics": None, "insights": None}


def limit_response_data(data: list, limit: int = 50) -> list:
    """
    Limit response data to prevent large payloads.

    Args:
        data: List of data items
        limit: Maximum number of items to return

    Returns:
        Limited list of data items
    """
    return data[:limit] if data else []
