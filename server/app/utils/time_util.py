from datetime import datetime, timezone

def human_time(dt: datetime) -> str:
    """Convert datetime to friendly 'x mins ago', 'Yesterday', etc."""
    
    # Fix: ensure dt is timezone-aware
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)
    diff = now - dt

    seconds = diff.total_seconds()
    minutes = seconds // 60
    hours = seconds // 3600
    days = diff.days

    if seconds < 60:
        return "Just now"
    if minutes < 60:
        return f"{int(minutes)} min ago" if minutes == 1 else f"{int(minutes)} mins ago"
    if hours < 24:
        return f"{int(hours)} hr ago" if hours == 1 else f"{int(hours)} hrs ago"
    if days == 1:
        return "Yesterday"
    if days < 7:
        return f"{days} days ago"

    weeks = days // 7
    if weeks < 4:
        return f"{weeks} week ago" if weeks == 1 else f"{weeks} weeks ago"

    months = days // 30
    return f"{months} month ago" if months == 1 else f"{months} months ago"
