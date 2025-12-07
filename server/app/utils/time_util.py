from datetime import datetime, timezone

def human_time(dt: datetime) -> str:
    """Convert a datetime to a human-readable relative time string."""
    now = datetime.now(timezone.utc)
    diff = now - dt

    if diff.days == 0:
        return "Today"
    elif diff.days == 1:
        return "Yesterday"
    return f"{diff.days} days ago"