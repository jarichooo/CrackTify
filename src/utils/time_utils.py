from datetime import datetime, timezone, timedelta

def convert_to_utc8(timestamp_str: str) -> str:
    """
    Convert a naive UTC timestamp string to UTC+8 ISO format.
    
    Args:
        timestamp_str (str): e.g. '2026-03-13T03:46:41.174536'
    
    Returns:
        str: ISO formatted timestamp with +08:00 offset
    """
    # Parse the naive timestamp
    dt_utc = datetime.fromisoformat(timestamp_str).replace(tzinfo=timezone.utc)
    
    # Convert to UTC+8
    dt_utc8 = dt_utc.astimezone(timezone(timedelta(hours=8)))
    
    return dt_utc8.isoformat()